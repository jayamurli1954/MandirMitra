# Test Coverage Improvement Plan

**Current Coverage: 52.38%**  
**Target Coverage: 75%+**

## Priority 1: Critical Low-Coverage Modules (< 30%)

### 1. Accounts API (22.89% coverage)
**Missing Tests:**
- ✅ `list_accounts` - Basic test exists
- ❌ `get_account_hierarchy` - No tests
- ❌ `get_account` - No tests  
- ❌ `create_account` - No tests
- ❌ `update_account` - No tests
- ❌ `delete_account` - No tests
- ❌ `get_balance` - No tests
- ❌ `check_account_transactions` - No tests
- ❌ `build_account_hierarchy` helper - No tests

**Impact:** High - Core accounting functionality

### 2. Dashboard API (20.29% coverage)
**Missing Tests:**
- ❌ `get_dashboard_stats` - No tests

**Impact:** High - Main dashboard page

### 3. Bank Reconciliation (13.96% coverage)
**Missing Tests:**
- Most endpoints not tested
- Critical for accounting accuracy

**Impact:** High - Financial accuracy

### 4. Financial Closing (8.95% coverage)
**Missing Tests:**
- Most endpoints not tested
- Critical for period-end closing

**Impact:** High - Financial reporting

### 5. Purchase Orders (12.33% coverage)
**Missing Tests:**
- Most endpoints not tested

**Impact:** Medium - Inventory management

### 6. Hundi (16.82% coverage)
**Missing Tests:**
- Most endpoints not tested

**Impact:** Medium - Cash collection

### 7. In-Kind Donations (10.45% coverage)
**Missing Tests:**
- Most endpoints not tested

**Impact:** Medium - Donation management

## Priority 2: Medium-Coverage Modules (30-50%)

### 8. Devotees API (28.77% coverage)
**Missing Tests:**
- ❌ `search_devotee_by_mobile` - No tests
- ❌ `update_devotee` - No tests
- ❌ `delete_devotee` - No tests
- ❌ `find_duplicate_devotees` - No tests
- ❌ `merge_devotees` - No tests
- ❌ `get_upcoming_birthdays` - No tests
- ❌ `get_devotee_analytics` - No tests
- ❌ `link_family_member` - No tests
- ❌ `update_devotee_tags` - No tests
- ❌ `get_family_members` - No tests

**Impact:** High - Core CRM functionality

### 9. Sevas API (34.76% coverage)
**Missing Tests:**
- ❌ `get_dropdown_options` - No tests
- ❌ `get_seva` (single seva) - No tests
- ❌ `update_seva` - No tests
- ❌ `get_available_dates` - No tests
- ❌ `get_booking` - No tests
- ❌ `update_booking` - No tests
- ❌ `cancel_booking` - No tests
- ❌ `request_reschedule` - No tests
- ❌ `approve_reschedule` - No tests
- ❌ `get_priests` - No tests
- ❌ `assign_priest` - No tests
- ❌ `process_refund` - No tests
- ❌ `get_refund_status` - No tests

**Impact:** High - Core seva booking functionality

### 10. Journal Entries (27.05% coverage)
**Missing Tests:**
- Many endpoints not tested
- Critical for accounting

**Impact:** High - Accounting core

### 11. Inventory (27.47% coverage)
**Missing Tests:**
- Many endpoints not tested

**Impact:** Medium - Inventory management

## Priority 3: Service Layer Tests

### 12. Panchang Display Settings Service (15.46% coverage)
**Missing Tests:**
- Service methods not tested

**Impact:** Medium - Panchang display

### 13. Payment Gateway Service (26.24% coverage)
**Missing Tests:**
- Payment processing logic

**Impact:** High - Payment processing

## Implementation Strategy

### Phase 1: Critical APIs (Target: +10% coverage)
1. Add tests for Accounts API
2. Add tests for Dashboard API
3. Add tests for Bank Reconciliation
4. Add tests for Financial Closing

### Phase 2: Core Functionality (Target: +8% coverage)
1. Add missing Devotees API tests
2. Add missing Sevas API tests
3. Add missing Journal Entries tests

### Phase 3: Supporting Modules (Target: +5% coverage)
1. Add Purchase Orders tests
2. Add Hundi tests
3. Add Inventory tests
4. Add In-Kind Donations tests

## Test Structure

Each test file should include:
- ✅ Happy path tests
- ✅ Error handling tests
- ✅ Validation tests
- ✅ Edge cases
- ✅ Permission/authorization tests

## Expected Results

- **Current:** 52.38%
- **After Phase 1:** ~62%
- **After Phase 2:** ~70%
- **After Phase 3:** ~75%+

## Quick Wins (Easy to add, high impact)

1. Dashboard API - Single endpoint, easy test
2. Accounts API - Well-defined endpoints
3. Devotees search/update - Common operations
4. Sevas dropdown options - Simple endpoint
