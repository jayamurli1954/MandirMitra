from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.coa_bootstrap import ensure_default_coa_for_temple
from app.models.accounting import (
    Account,
    AccountSubType,
    JournalEntry,
    JournalEntryStatus,
    JournalLine,
    TransactionType,
)
from app.models.donation import Donation, DonationType, InKindDonationSubType
from app.models.temple import Temple


def get_payment_accounts_for_temple(db: Session, temple_id: Optional[int]) -> dict:
    """Fetch active cash and bank accounts for payment selection."""
    from app.models.upi_banking import BankAccount

    if not temple_id:
        return {"cash_accounts": [], "bank_accounts": []}

    seed_result = ensure_default_coa_for_temple(db, temple_id, raise_on_error=False)
    if seed_result.get("error"):
        print(
            f"WARNING: Could not auto-initialize COA for temple {temple_id} while loading payment accounts: {seed_result['error']}"
        )

    cash_accounts = (
        db.query(Account)
        .filter(
            Account.temple_id == temple_id,
            Account.is_active == True,
            Account.account_subtype == AccountSubType.CASH_BANK,
            Account.account_code.like("11%"),
        )
        .order_by(Account.account_code.asc())
        .all()
    )
    if not cash_accounts:
        cash_accounts = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.is_active == True,
                Account.account_code.like("11%"),
            )
            .order_by(Account.account_code.asc())
            .all()
        )

    bank_accounts = (
        db.query(BankAccount)
        .filter(BankAccount.temple_id == temple_id, BankAccount.is_active == True)
        .order_by(BankAccount.is_primary.desc(), BankAccount.account_name.asc())
        .all()
    )

    bank_results = []
    for bank_acc in bank_accounts:
        chart_account = (
            db.query(Account)
            .filter(
                Account.id == bank_acc.chart_account_id,
                Account.temple_id == temple_id,
                Account.is_active == True,
            )
            .first()
        )
        if not chart_account:
            continue
        bank_results.append(
            {
                "id": bank_acc.id,
                "bank_account_id": bank_acc.id,
                "account_id": chart_account.id,
                "account_code": chart_account.account_code,
                "account_name": chart_account.account_name,
                "name": bank_acc.account_name,
                "bank_name": bank_acc.bank_name,
                "account_number": bank_acc.account_number,
                "ifsc_code": bank_acc.ifsc_code,
                "is_primary": bank_acc.is_primary,
            }
        )

    if not bank_results:
        fallback_bank_ledgers = (
            db.query(Account)
            .filter(
                Account.temple_id == temple_id,
                Account.is_active == True,
                Account.account_code.like("12%"),
            )
            .order_by(Account.account_code.asc())
            .all()
        )
        for ledger in fallback_bank_ledgers:
            bank_results.append(
                {
                    "id": f"coa-{ledger.id}",
                    "bank_account_id": None,
                    "account_id": ledger.id,
                    "account_code": ledger.account_code,
                    "account_name": ledger.account_name,
                    "name": ledger.account_name,
                    "bank_name": None,
                    "account_number": None,
                    "ifsc_code": None,
                    "is_primary": False,
                }
            )

    cash_results = [
        {
            "account_id": acc.id,
            "account_code": acc.account_code,
            "account_name": acc.account_name,
        }
        for acc in cash_accounts
    ]

    return {"cash_accounts": cash_results, "bank_accounts": bank_results}


def post_donation_to_accounting(db: Session, donation: Donation, temple_id: int):
    """Create journal entry for donation in accounting system."""
    try:
        seed_result = ensure_default_coa_for_temple(db, temple_id, raise_on_error=False)
        if seed_result.get("created", 0) > 0:
            print(
                f"  INFO: Initialized {seed_result['created']} default COA account(s) for temple {temple_id}"
            )
        if seed_result.get("error"):
            print(
                f"  WARNING: Could not auto-initialize COA for temple {temple_id}: {seed_result['error']}"
            )

        if donation.donation_type == DonationType.IN_KIND:
            debit_account_code = None
            if donation.inkind_subtype == InKindDonationSubType.INVENTORY:
                debit_account_code = "14003"
            elif donation.inkind_subtype == InKindDonationSubType.ASSET:
                item_name_lower = (donation.item_name or "").lower()
                is_precious_metal = (
                    donation.purity
                    or "silver" in item_name_lower
                    or "gold" in item_name_lower
                    or "jewellery" in item_name_lower
                    or "ornament" in item_name_lower
                )

                if is_precious_metal:
                    debit_account_code = "15010"
                else:
                    debit_account_code = "15002"
            elif donation.inkind_subtype == InKindDonationSubType.EVENT_SPONSORSHIP:
                debit_account_code = "11020"
            else:
                debit_account_code = "14003"

            debit_account = (
                db.query(Account)
                .filter(Account.temple_id == temple_id, Account.account_code == debit_account_code)
                .first()
            )

            if not debit_account:
                from app.models.accounting import AccountSubType as _AccountSubType

                if donation.inkind_subtype == InKindDonationSubType.INVENTORY:
                    debit_account = (
                        db.query(Account)
                        .filter(
                            Account.temple_id == temple_id,
                            Account.account_subtype == _AccountSubType.INVENTORY,
                        )
                        .first()
                    )
                elif donation.inkind_subtype == InKindDonationSubType.ASSET:
                    debit_account = (
                        db.query(Account)
                        .filter(
                            Account.temple_id == temple_id,
                            Account.account_subtype == _AccountSubType.PRECIOUS_ASSET,
                        )
                        .first()
                    )
        else:
            debit_account = None
            payment_mode_upper = (donation.payment_mode or "").strip().upper()
            bank_payment_modes = {"UPI", "ONLINE", "CARD", "NETBANKING", "BANK", "CHEQUE", "DD"}

            selected_payment_account_id = getattr(donation, "payment_account_id", None)
            if selected_payment_account_id:
                selected_account = (
                    db.query(Account)
                    .filter(
                        Account.id == selected_payment_account_id,
                        Account.temple_id == temple_id,
                        Account.is_active == True,
                    )
                    .first()
                )
                if not selected_account:
                    raise ValueError(
                        f"Selected payment account {selected_payment_account_id} was not found."
                    )

                is_cash_mode = payment_mode_upper in {"CASH", "COUNTER"} or "HUNDI" in payment_mode_upper
                is_bank_mode = payment_mode_upper in bank_payment_modes
                if is_cash_mode and not selected_account.account_code.startswith("11"):
                    raise ValueError(
                        "Selected payment account is not a cash account (expected code starting with 11)."
                    )
                if is_bank_mode and not selected_account.account_code.startswith("12"):
                    raise ValueError(
                        "Selected payment account is not a bank account (expected code starting with 12)."
                    )

                debit_account = selected_account
                print(
                    f"  Using selected payment account: {debit_account.account_code} - {debit_account.account_name}"
                )

            if not debit_account and hasattr(donation, "bank_account_id") and donation.bank_account_id:
                from app.models.upi_banking import BankAccount

                bank_account = (
                    db.query(BankAccount)
                    .filter(
                        BankAccount.id == donation.bank_account_id,
                        BankAccount.temple_id == temple_id,
                        BankAccount.is_active == True,
                    )
                    .first()
                )

                if bank_account:
                    debit_account = (
                        db.query(Account)
                        .filter(
                            Account.id == bank_account.chart_account_id,
                            Account.temple_id == temple_id,
                        )
                        .first()
                    )

                    if debit_account:
                        print(
                            f"  Using selected bank account: {debit_account.account_code} - {debit_account.account_name}"
                        )

            if not debit_account:
                debit_account_code = None
                if payment_mode_upper in ["CASH", "COUNTER"]:
                    from app.core.bank_account_helper import get_cash_account_for_payment

                    debit_account = get_cash_account_for_payment(db, temple_id, "CASH", hundi=False)
                    if not debit_account:
                        debit_account_code = "11001"
                        debit_account = (
                            db.query(Account)
                            .filter(
                                Account.temple_id == temple_id,
                                Account.account_code == debit_account_code,
                            )
                            .first()
                        )
                elif payment_mode_upper in bank_payment_modes:
                    from app.core.bank_account_helper import get_bank_account_for_payment

                    debit_account, fallback_code = get_bank_account_for_payment(
                        db,
                        temple_id,
                        payment_mode_upper,
                        bank_account_id=getattr(donation, "bank_account_id", None),
                    )
                    if debit_account:
                        print(
                            f"  Using bank account: {debit_account.account_code} - {debit_account.account_name}"
                        )
                    elif fallback_code:
                        debit_account = (
                            db.query(Account)
                            .filter(
                                Account.temple_id == temple_id,
                                Account.account_code == fallback_code,
                            )
                            .first()
                        )
                    if not debit_account:
                        print(
                            f"  WARNING: No bank account found for payment mode {donation.payment_mode}. Please create a bank account in Bank Account Management."
                        )
                elif "HUNDI" in payment_mode_upper:
                    from app.core.bank_account_helper import get_cash_account_for_payment

                    debit_account = get_cash_account_for_payment(
                        db, temple_id, payment_mode_upper, hundi=True
                    )
                    if not debit_account:
                        debit_account_code = "11002"
                        debit_account = (
                            db.query(Account)
                            .filter(
                                Account.temple_id == temple_id,
                                Account.account_code == debit_account_code,
                            )
                            .first()
                        )
                else:
                    from app.core.bank_account_helper import get_cash_account_for_payment

                    debit_account = get_cash_account_for_payment(
                        db,
                        temple_id,
                        payment_mode_upper if payment_mode_upper else "CASH",
                        hundi=False,
                    )
                    if not debit_account:
                        debit_account_code = "11001"
                        debit_account = (
                            db.query(Account)
                            .filter(
                                Account.temple_id == temple_id,
                                Account.account_code == debit_account_code,
                            )
                            .first()
                        )

        credit_account = None

        if donation.category and hasattr(donation.category, "account_id") and donation.category.account_id:
            credit_account = db.query(Account).filter(Account.id == donation.category.account_id).first()
            if credit_account:
                print(
                    f"  Using category-linked account: {credit_account.account_code} - {credit_account.account_name}"
                )

        if not credit_account:
            credit_account_code = "44001"
            credit_account = (
                db.query(Account)
                .filter(Account.temple_id == temple_id, Account.account_code == credit_account_code)
                .first()
            )

            if credit_account:
                print(
                    f"  INFO: Category '{donation.category.name if donation.category else 'Unknown'}' not linked to account. Using default donation income account: {credit_account_code}"
                )
            else:
                print(
                    f"  ERROR: Default donation income account {credit_account_code} not found. Please ensure '44001 - General Donations' exists in Chart of Accounts."
                )

        if not debit_account:
            from app.core.bank_account_helper import (
                get_bank_account_for_payment,
                get_cash_account_for_payment,
            )

            payment_mode_upper = (donation.payment_mode or "CASH").strip().upper()
            bank_payment_modes = {"UPI", "ONLINE", "CARD", "NETBANKING", "BANK", "CHEQUE", "DD"}
            if payment_mode_upper in bank_payment_modes:
                debit_account, fallback_code = get_bank_account_for_payment(
                    db,
                    temple_id,
                    payment_mode_upper,
                    bank_account_id=getattr(donation, "bank_account_id", None),
                )
                if not debit_account and fallback_code:
                    debit_account = (
                        db.query(Account)
                        .filter(
                            Account.temple_id == temple_id,
                            Account.account_code == fallback_code,
                        )
                        .first()
                    )
                if not debit_account:
                    raise ValueError(
                        f"Debit account not found for non-cash payment mode '{donation.payment_mode}' "
                        f"for temple {temple_id}. Please configure Bank Account Management or "
                        "ensure bank ledgers (e.g., 12001/12002/12003) exist."
                    )
            elif "HUNDI" in payment_mode_upper:
                debit_account = get_cash_account_for_payment(db, temple_id, "HUNDI", hundi=True)
                if not debit_account:
                    raise ValueError(
                        f"Debit account not found for hundi payment mode '{donation.payment_mode}' "
                        f"for temple {temple_id}. Please create '11002 - Cash in Hand - Hundi'."
                    )
            else:
                debit_account = get_cash_account_for_payment(db, temple_id, "CASH", hundi=False)
                if not debit_account:
                    raise ValueError(
                        f"Debit account not found for cash payment mode '{donation.payment_mode}' "
                        f"for temple {temple_id}. Please create '11001 - Cash in Hand - Counter'."
                    )

        if not credit_account:
            error_msg = (
                f"Credit account not found for donation category '{donation.category.name if donation.category else 'Unknown'}'. "
                "Please link an account to the donation category or create default income accounts."
            )
            raise ValueError(error_msg)

        is_anonymous_donation = donation.is_anonymous if hasattr(donation, "is_anonymous") else False
        donor_name = (
            "Anonymous Donor"
            if is_anonymous_donation
            else (donation.devotee.name if donation.devotee else "Anonymous")
        )

        if donation.donation_type == DonationType.IN_KIND:
            item_desc = donation.item_name or "In-kind donation"
            narration = f"In-kind donation from {donor_name}: {item_desc}"
            if donation.category:
                narration += f" - {donation.category.name}"
        else:
            narration = f"Donation from {donor_name}"
            if donation.category:
                narration += f" - {donation.category.name}"

        year = donation.donation_date.year
        prefix = f"JE/{year}/"

        from sqlalchemy.orm import load_only

        last_entry = (
            db.query(JournalEntry)
            .options(load_only(JournalEntry.id, JournalEntry.entry_number, JournalEntry.temple_id))
            .filter(
                JournalEntry.temple_id == temple_id,
                JournalEntry.entry_number.like(f"{prefix}%"),
            )
            .order_by(JournalEntry.id.desc())
            .first()
        )

        if last_entry:
            try:
                last_num = int(last_entry.entry_number.split("/")[-1])
                new_num = last_num + 1
            except Exception:
                new_num = 1
        else:
            new_num = 1

        entry_number = f"{prefix}{new_num:04d}"

        receipt_date = donation.donation_date
        if isinstance(receipt_date, date):
            entry_date = datetime.combine(receipt_date, datetime.min.time())
        else:
            entry_date = datetime.combine(date.today(), datetime.min.time())

        created_by = donation.created_by if donation.created_by else 1

        journal_entry = JournalEntry(
            temple_id=temple_id,
            entry_date=entry_date,
            entry_number=entry_number,
            narration=narration,
            reference_type=TransactionType.DONATION,
            reference_id=donation.id,
            total_amount=donation.amount,
            status=JournalEntryStatus.POSTED,
            created_by=created_by,
            posted_by=created_by,
            posted_at=datetime.utcnow(),
        )
        db.add(journal_entry)
        db.flush()

        if donation.donation_type == DonationType.IN_KIND:
            debit_description = f"In-kind donation: {donation.item_name or 'Item'}"
            if donation.quantity and donation.unit:
                debit_description += f" - {donation.quantity} {donation.unit}"
        else:
            debit_description = f"Donation received via {donation.payment_mode or 'Cash'}"

        debit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=debit_account.id,
            debit_amount=donation.amount,
            credit_amount=0,
            description=debit_description,
        )

        credit_description = f"Donation income - {donation.category.name if donation.category else 'General'}"
        if donation.donation_type == DonationType.IN_KIND:
            credit_description += f" (In-kind: {donation.item_name or 'Item'})"

        credit_line = JournalLine(
            journal_entry_id=journal_entry.id,
            account_id=credit_account.id,
            debit_amount=0,
            credit_amount=donation.amount,
            description=credit_description,
        )

        db.add(debit_line)
        db.add(credit_line)

        return journal_entry

    except Exception as e:
        print(f"Error posting donation to accounting: {str(e)}")
        raise e
