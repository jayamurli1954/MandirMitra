from app.api import backup_restore
from app.core.security import get_password_hash
from app.models.accounting import Account
from app.models.temple import Temple
from app.models.user import User
from app.services import backup_scheduler


def _login(client, email: str, password: str) -> None:
    response = client.post(
        "/api/v1/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"


def test_onboard_temple_with_admin(client, db_session):
    super_admin = User(
        email="superadmin@example.com",
        password_hash=get_password_hash("SuperPass123!"),
        full_name="Platform Admin",
        role="super_admin",
        is_active=True,
        is_superuser=True,
    )
    db_session.add(super_admin)
    db_session.commit()

    _login(client, "superadmin@example.com", "SuperPass123!")

    response = client.post(
        "/api/v1/temples/onboard",
        json={
            "temple_name": "Sri Rama Temple",
            "trust_name": "Sri Rama Trust",
            "temple_slug": "sri-rama-temple",
            "primary_deity": "Lord Rama",
            "city": "Bengaluru",
            "state": "Karnataka",
            "phone": "9876543210",
            "email": "office@srirama.org",
            "admin_full_name": "Temple Admin",
            "admin_email": "admin@srirama.org",
            "admin_password": "TempleAdmin123!",
        },
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["temple_name"] == "Sri Rama Temple"
    assert data["trust_name"] == "Sri Rama Trust"
    assert data["admin_role"] == "admin"

    temple = db_session.query(Temple).filter(Temple.slug == "sri-rama-temple").first()
    assert temple is not None
    admin_user = db_session.query(User).filter(User.email == "admin@srirama.org").first()
    assert admin_user is not None
    assert admin_user.role == "admin"
    assert admin_user.is_superuser is False
    assert admin_user.temple_id == temple.id


def test_manual_backup_endpoint(authenticated_client, tmp_path, monkeypatch):
    monkeypatch.setattr(backup_restore, "BACKUP_DIR", tmp_path)
    response = authenticated_client.post("/api/v1/backup-restore/backup")
    assert response.status_code == 200, response.text
    data = response.json()
    assert tmp_path.joinpath(data["backup_file"]).exists()

    status_response = authenticated_client.get("/api/v1/backup-restore/status")
    assert status_response.status_code == 200, status_response.text
    status_data = status_response.json()
    assert status_data["total_backups"] >= 1


def test_auto_backup_retention(authenticated_client, db_session, tmp_path, monkeypatch):
    monkeypatch.setattr(backup_scheduler, "BACKUP_DIR", tmp_path)
    temple_id = authenticated_client.get("/api/v1/users/me").json()["temple_id"]
    for _ in range(7):
        backup_scheduler.create_auto_backup_for_temple(temple_id)

    auto_files = list(tmp_path.glob(f"backup_temple_{temple_id}_auto_*.json"))
    assert len(auto_files) == 5


def test_import_opening_balances_from_csv(authenticated_client, db_session):
    response = authenticated_client.post(
        "/api/v1/opening-balances/import",
        files={
            "file": (
                "opening_balances.csv",
                "account_code,opening_balance_debit,opening_balance_credit\n11001,1500,0\n21003,0,2500\n",
                "text/csv",
            )
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["updated_count"] == 2

    cash_account = db_session.query(Account).filter(Account.account_code == "11001").first()
    liability_account = db_session.query(Account).filter(Account.account_code == "21003").first()
    assert cash_account.opening_balance_debit == 1500
    assert liability_account.opening_balance_credit == 2500


def test_import_legacy_accounts_from_csv(authenticated_client, db_session):
    response = authenticated_client.post(
        "/api/v1/accounts/import-legacy",
        files={
            "file": (
                "legacy_accounts.csv",
                "legacy_code,account_name,account_type,description,opening_balance\n5519,Legacy Festival Expense,expense,Imported from old books,3250\n",
                "text/csv",
            )
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["created_count"] == 1

    imported_account = db_session.query(Account).filter(Account.account_code == "55109").first()
    assert imported_account is not None
    assert imported_account.account_name == "Legacy Festival Expense"
    assert imported_account.opening_balance_debit == 3250
