import pytest
import io
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.api.journal_entries_day_cash_bank_books import get_day_book, get_cash_book, get_bank_book

# Note: You might need to adjust imports based on your conftest.py availability
# This test assumes a standard pytest-fastapi setup

client = TestClient(app)

def test_day_book_export_excel(client, test_db, normal_user_token_headers):
    # Prepare parameters
    today = date.today().isoformat()
    
    # Make request
    response = client.get(
        f"/api/v1/accounting/reports/day-book/export/excel?date={today}",
        headers=normal_user_token_headers
    )
    
    # Check assertions (status code might be 200 or 401 depending on auth fixture)
    # Ideally should be 200
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment; filename=DayBook_" in response.headers["content-disposition"]
    # Check partial content (Excel magic number)
    assert response.content[:2] == b'PK'

def test_day_book_export_pdf(client, test_db, normal_user_token_headers):
    today = date.today().isoformat()
    
    response = client.get(
        f"/api/v1/accounting/reports/day-book/export/pdf?date={today}",
        headers=normal_user_token_headers
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=DayBook_" in response.headers["content-disposition"]
    # Check partial content (PDF magic number)
    assert response.content[:4] == b'%PDF'

def test_cash_book_export_excel(client, test_db, normal_user_token_headers):
    today = date.today().isoformat()
    
    response = client.get(
        f"/api/v1/accounting/reports/cash-book/export/excel?from_date={today}&to_date={today}",
        headers=normal_user_token_headers
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment; filename=CashBook_" in response.headers["content-disposition"]

def test_seva_report_export_excel(client, test_db, normal_user_token_headers):
    today = date.today().isoformat()
    
    response = client.get(
        f"/api/v1/reports/sevas/detailed/export/excel?from_date={today}&to_date={today}",
        headers=normal_user_token_headers
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
