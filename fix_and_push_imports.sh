#!/bin/bash
# Script to fix and push BankReconciliation import errors

echo "🔍 Checking Git status..."
git status

echo ""
echo "📝 Staging fixed files..."
git add backend/app/main.py
git add backend/alembic/env.py
git add backend/seed_chart_of_accounts.py
git add backend/requirements.txt

echo ""
echo "✅ Files staged. Reviewing changes..."
git status

echo ""
echo "💾 Committing fixes..."
git commit -m "fix: Resolve BankReconciliation import errors

- Fix ImportError: cannot import name 'BankReconciliation' from 'app.models.upi_banking'
- Update app/main.py to import BankReconciliation from app.models.bank_reconciliation
- Update alembic/env.py with correct imports
- Fix seed_chart_of_accounts.py imports
- Reorder email-validator in requirements.txt before pydantic[email]

All files now correctly import BankReconciliation from app.models.bank_reconciliation
instead of app.models.upi_banking."

echo ""
echo "📤 Pushing to remote repository..."
echo "⚠️  Note: This will push to your current branch. Make sure you're on the correct branch!"
echo ""
read -p "Press Enter to continue pushing, or Ctrl+C to cancel..."

git push origin HEAD

echo ""
echo "✅ Done! The fixes have been pushed."
echo ""
echo "📋 Next steps:"
echo "   1. If you're on a feature branch, merge/rebase from main to update other branches"
echo "   2. If you're on main, update your feature branches with:"
echo "      git checkout feature-branch"
echo "      git rebase origin/main"
echo "      git push origin feature-branch --force-with-lease"
