# ESLint Setup - Development Mode

## Current Configuration

ESLint is configured to **warn** instead of **error** for most issues. This allows development to continue while you fix issues gradually.

## Environment Variable

Create `frontend/.env` file with:
```
ESLINT_NO_DEV_ERRORS=true
```

This tells `react-scripts` to not treat ESLint warnings as compilation errors.

## Quick Fixes

### 1. Remove Unused Imports (Easy wins)

Many files have unused imports. You can remove them:

```javascript
// Example: src/App.js line 38
// Remove: import StockAuditWastage from './pages/inventory/StockAuditWastage';
```

### 2. Fix Unused Variables

Prefix with underscore if intentionally unused:
```javascript
// Before
const [loading, setLoading] = useState(false); // Not used

// After
const [_loading, _setLoading] = useState(false); // Marked as intentionally unused
```

### 3. Fix React Hooks Dependencies (Important)

These can cause bugs:
```javascript
// Before
useEffect(() => {
  fetchEntries();
}, []); // Missing fetchEntries

// After - Option 1: Add dependency
useEffect(() => {
  fetchEntries();
}, [fetchEntries]);

// After - Option 2: Use useCallback
const fetchEntries = useCallback(async () => {
  // ...
}, [/* dependencies */]);

useEffect(() => {
  fetchEntries();
}, [fetchEntries]);
```

## Auto-Fix What You Can

```bash
cd frontend
npm run lint:fix
```

This will auto-fix:
- Formatting issues
- Some simple problems
- Import ordering

## Priority

**Fix these first (can cause bugs):**
1. React hooks dependency warnings
2. Unused variables that should be used

**Fix later (cosmetic):**
1. Unused imports
2. Console statements
3. Unescaped entities

## For Now

The frontend should compile. Fix issues as you work on each file.


