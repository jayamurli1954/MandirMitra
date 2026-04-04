"""
Production smoke tests for the MandirMitra contract surface.

These tests focus on the exact fields and endpoints the frontend uses.
If one of these breaks, the production flow is not reliable even if the
older generic API tests still pass.
"""

from datetime import date, timedelta

import pytest
from fastapi import status


def _assert_account_row(row):
    assert isinstance(row, dict)
    assert row.get("account_code")
    assert row.get("account_name")
    assert row.get("account_type")
    assert "is_active" in row


def _assert_payment_account_row(row):
    assert isinstance(row, dict)
    assert row.get("account_id") is not None
    assert row.get("account_code")
    assert row.get("account_name")


@pytest.mark.api
@pytest.mark.accounting
class TestMandirAccountingSmoke:
    def test_initialize_default_accounts_exposes_core_chart_rows(self, authenticated_client):
        response = authenticated_client.post("/api/v1/accounts/initialize-default")

        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        payload = response.json()
        assert isinstance(payload, dict)
        assert any(key in payload for key in ("created", "message", "accounts", "data"))

        hierarchy_response = authenticated_client.get("/api/v1/accounts/hierarchy")
        assert hierarchy_response.status_code == status.HTTP_200_OK

        accounts = hierarchy_response.json()
        assert isinstance(accounts, list)
        assert accounts, "Expected initialized chart of accounts to return rows"

        for row in accounts:
            if isinstance(row, dict):
                _assert_account_row(row)

        names = [str(row.get("account_name", "")).lower() for row in accounts if isinstance(row, dict)]
        assert any("cash" in name for name in names), "Expected at least one cash account"
        assert any("bank" in name for name in names), "Expected at least one bank account"
        assert any("donation" in name for name in names), "Expected at least one donation income account"
        assert any("seva" in name for name in names), "Expected at least one seva income account"
        assert any("expense" in name for name in names), "Expected at least one expense account"

    def test_initialize_default_accounts_reactivates_inactive_defaults(
        self, authenticated_client, db_session, test_user
    ):
        from app.models.accounting import Account, AccountSubType, AccountType

        temple_id = test_user.temple_id
        inactive_cash = (
            db_session.query(Account)
            .filter(Account.temple_id == temple_id, Account.account_code == "11001")
            .first()
        )
        assert inactive_cash is not None, "Expected default cash account to exist in fixture"

        inactive_cash.account_name = "Cash in Hand - Counter (Disabled)"
        inactive_cash.account_type = AccountType.ASSET
        inactive_cash.account_subtype = AccountSubType.CASH_BANK
        inactive_cash.description = "Temporarily inactive for smoke test"
        inactive_cash.is_active = False
        db_session.commit()

        response = authenticated_client.post("/api/v1/accounts/initialize-default")
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        payload = response.json()
        assert payload.get("reactivated", 0) >= 1

        reactivated_cash = (
            db_session.query(Account)
            .filter(Account.temple_id == temple_id, Account.account_code == "11001")
            .first()
        )
        assert reactivated_cash is not None
        db_session.refresh(reactivated_cash)
        assert reactivated_cash.is_active is True
        assert reactivated_cash.account_name == "Cash in Hand - Counter"

        hierarchy_response = authenticated_client.get("/api/v1/accounts/hierarchy")
        assert hierarchy_response.status_code == status.HTTP_200_OK
        accounts = hierarchy_response.json()
        names = [str(row.get("account_name", "")).lower() for row in accounts if isinstance(row, dict)]
        assert any("cash" in name for name in names), "Expected reactivated cash account to appear"

    def test_payment_account_endpoints_expose_frontend_contract(self, authenticated_client):
        for endpoint in (
            "/api/v1/donations/payment-accounts",
            "/api/v1/sevas/payment-accounts",
        ):
            response = authenticated_client.get(endpoint)
            assert response.status_code == status.HTTP_200_OK

            payload = response.json()
            assert isinstance(payload, dict)

            cash_accounts = payload.get("cash_accounts") or []
            bank_accounts = payload.get("bank_accounts") or []

            assert cash_accounts, f"Expected cash accounts from {endpoint}"
            assert bank_accounts, f"Expected bank accounts from {endpoint}"

            for row in cash_accounts[:2] + bank_accounts[:2]:
                _assert_payment_account_row(row)
    def test_payment_account_endpoints_recover_inactive_cash_defaults(
        self, authenticated_client, db_session, test_user
    ):
        from app.models.accounting import Account

        temple_id = test_user.temple_id
        cash_account = (
            db_session.query(Account)
            .filter(Account.temple_id == temple_id, Account.account_code == "11001")
            .first()
        )
        assert cash_account is not None, "Expected default cash account to exist in fixture"

        cash_account.is_active = False
        db_session.commit()

        for endpoint in (
            "/api/v1/donations/payment-accounts",
            "/api/v1/sevas/payment-accounts",
        ):
            response = authenticated_client.get(endpoint)
            assert response.status_code == status.HTTP_200_OK
            payload = response.json()
            cash_accounts = payload.get("cash_accounts") or []
            assert cash_accounts, f"Expected cash accounts from {endpoint} after recovery"
            assert any(
                str(row.get("account_code")) == "11001" for row in cash_accounts if isinstance(row, dict)
            ), f"Expected default cash account 11001 from {endpoint}"

        db_session.refresh(cash_account)
        assert cash_account.is_active is True

    def test_pincode_lookup_uses_remote_fallback_when_csv_is_empty(self, monkeypatch):
        from app.api import pincode as pincode_api

        monkeypatch.setattr(pincode_api, "load_pincode_data", lambda: {})

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return [
                    {
                        "Status": "Success",
                        "PostOffice": [
                            {
                                "District": "Chennai",
                                "State": "Tamil Nadu",
                                "Name": "Mylapore",
                            }
                        ],
                    }
                ]

        monkeypatch.setattr(pincode_api.requests, "get", lambda *args, **kwargs: FakeResponse())

        result = pincode_api.lookup_pincode("600004")
        assert result["found"] is True
        assert result["city"] == "Chennai"
        assert result["state"] == "Tamil Nadu"
        assert result["source"] == "india_post"

    def test_cash_donation_booking_accepts_payment_account_id(self, authenticated_client):
        payment_accounts_response = authenticated_client.get("/api/v1/donations/payment-accounts")
        assert payment_accounts_response.status_code == status.HTTP_200_OK
        payment_accounts = payment_accounts_response.json()
        cash_accounts = payment_accounts.get("cash_accounts") or []
        assert cash_accounts, "Expected at least one cash account for donation booking"
        cash_account_id = cash_accounts[0]["account_id"]

        donation_payload = {
            "devotee_first_name": "Smoke",
            "devotee_last_name": "Donor",
            "devotee_phone": "9998887776",
            "amount": 251.0,
            "payment_mode": "Cash",
            "payment_account_id": cash_account_id,
            "category": "general",
            "donation_type": "cash",
            "donation_date": str(date.today()),
            "name_prefix": "Sri",
            "notes": "production smoke test",
        }

        response = authenticated_client.post("/api/v1/donations", json=donation_payload)
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        payload = response.json()
        assert payload.get("id") is not None
        assert payload.get("receipt_number")
        assert float(payload.get("amount", 0)) == 251.0

    def test_bank_donation_booking_accepts_bank_account_id(self, authenticated_client):
        payment_accounts_response = authenticated_client.get("/api/v1/donations/payment-accounts")
        assert payment_accounts_response.status_code == status.HTTP_200_OK
        payment_accounts = payment_accounts_response.json()
        bank_accounts = payment_accounts.get("bank_accounts") or []
        assert bank_accounts, "Expected at least one bank account for donation booking"

        bank_account = bank_accounts[0]
        donation_payload = {
            "devotee_first_name": "Bank",
            "devotee_last_name": "Donor",
            "devotee_phone": "9998887775",
            "amount": 551.0,
            "payment_mode": "Bank",
            "payment_account_id": bank_account["account_id"],
            "bank_account_id": bank_account.get("bank_account_id"),
            "payment_sub_mode": "UPI",
            "sender_upi_id": "smoke@upi",
            "upi_reference_number": "UTR-SMOKE-001",
            "category": "general",
            "donation_type": "cash",
            "donation_date": str(date.today()),
            "name_prefix": "Sri",
            "notes": "production smoke test",
        }

        response = authenticated_client.post("/api/v1/donations", json=donation_payload)
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        payload = response.json()
        assert payload.get("id") is not None
        assert payload.get("receipt_number")
        assert float(payload.get("amount", 0)) == 551.0

    def test_seva_booking_accepts_string_ids_and_payment_account_id(self, authenticated_client):
        seva_response = authenticated_client.post(
            "/api/v1/sevas/",
            json={
                "name_english": "Smoke Test Seva",
                "category": "pooja",
                "amount": 500.0,
                "duration_minutes": 30,
                "is_active": True,
            },
        )
        assert seva_response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        seva_id = seva_response.json()["id"]

        devotee_response = authenticated_client.post(
            "/api/v1/devotees/",
            json={
                "first_name": "Smoke",
                "last_name": "Sevak",
                "phone": "9998887774",
                "name_prefix": "Sri",
                "address": "12 Temple Street",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "pincode": "600001",
            },
        )
        assert devotee_response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        devotee_id = devotee_response.json()["id"]

        payment_accounts_response = authenticated_client.get("/api/v1/sevas/payment-accounts")
        assert payment_accounts_response.status_code == status.HTTP_200_OK
        payment_accounts = payment_accounts_response.json()
        cash_accounts = payment_accounts.get("cash_accounts") or []
        assert cash_accounts, "Expected at least one cash account for seva booking"
        cash_account_id = cash_accounts[0]["account_id"]

        booking_payload = {
            "seva_id": str(seva_id),
            "devotee_id": str(devotee_id),
            "booking_date": str(date.today() + timedelta(days=1)),
            "booking_time": "08:00",
            "amount_paid": 500.0,
            "payment_method": "Cash",
            "payment_account_id": cash_account_id,
            "devotee_names": "Smoke Sevak",
            "gotra": "Bharadwaja",
            "nakshatra": "Rohini",
            "rashi": "Mesha",
            "special_request": "production smoke test",
        }

        response = authenticated_client.post("/api/v1/sevas/bookings/", json=booking_payload)
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        payload = response.json()
        assert payload.get("id") is not None
        assert payload.get("receipt_number")
        assert str(payload.get("seva_id")) == str(seva_id)
        assert str(payload.get("devotee_id")) == str(devotee_id)
        assert float(payload.get("amount_paid", 0)) == 500.0




