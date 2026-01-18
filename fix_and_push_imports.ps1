# PowerShell script to fix and push BankReconciliation import errors

Write-Host "🔍 Checking Git status..." -ForegroundColor Cyan
git status

Write-Host ""
Write-Host "📝 Staging fixed files..." -ForegroundColor Cyan
git add backend/app/main.py
git add backend/alembic/env.py
git add backend/seed_chart_of_accounts.py
git add backend/requirements.txt

Write-Host ""
Write-Host "✅ Files staged. Reviewing changes..." -ForegroundColor Green
git status

Write-Host ""
Write-Host "💾 Committing fixes..." -ForegroundColor Cyan
git commit -m "fix: Resolve BankReconciliation import errors

- Fix ImportError: cannot import name 'BankReconciliation' from 'app.models.upi_banking'
- Update app/main.py to import BankReconciliation from app.models.bank_reconciliation
- Update alembic/env.py with correct imports
- Fix seed_chart_of_accounts.py imports
- Reorder email-validator in requirements.txt before pydantic[email]

All files now correctly import BankReconciliation from app.models.bank_reconciliation
instead of app.models.upi_banking."

Write-Host ""
Write-Host "📤 Pushing to remote repository..." -ForegroundColor Cyan
Write-Host "⚠️  Note: This will push to your current branch. Make sure you're on the correct branch!" -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Press Enter to continue pushing, or Ctrl+C to cancel"

git push origin HEAD

Write-Host ""
Write-Host "✅ Done! The fixes have been pushed." -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   1. If you're on a feature branch, merge/rebase from main to update other branches"
Write-Host "   2. If you're on main, update your feature branches with:"
Write-Host "      git checkout feature-branch"
Write-Host "      git rebase origin/main"
Write-Host "      git push origin feature-branch --force-with-lease"
