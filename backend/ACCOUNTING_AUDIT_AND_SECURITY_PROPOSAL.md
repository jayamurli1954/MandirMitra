# Accounting System - Audit Trail & Security Proposal

## Executive Summary

This proposal outlines a comprehensive audit trail and security system for the Quick Expense module and all accounting operations to prevent misappropriation of funds and ensure complete accountability.

---

## 1. Multi-User System (Desktop Version)

### Current State
- System already supports multiple users with roles
- Users: Admin, Temple Manager, Accountant, Counter Staff, Priest

### Implementation
✅ **Already Implemented** - The system supports multiple user logins. Each user must:
- Login with username/password
- Have assigned role and permissions
- All actions are logged with user ID

### User Roles for Accounting Module

| Role | Permissions |
|------|-------------|
| **Counter Staff** | Create expenses, View reports, No edit/delete |
| **Accountant** | Create expenses, Edit same-day entries, View all reports |
| **Temple Manager** | Full access except sensitive operations |
| **Admin** | Full access including approval workflows |

---

## 2. Audit Trail System

### 2.1 Immutable Audit Log Table

**Key Principle: Audit logs CANNOT be deleted or modified. Ever.**

```python
class AccountingAuditLog(Base):
    """
    Immutable audit log for all accounting operations
    This table cannot be modified or deleted by any user
    """
    __tablename__ = "accounting_audit_logs"
    
    id = Column(Integer, primary_key=True)
    
    # What was changed
    entity_type = Column(String(50), nullable=False)  # 'journal_entry', 'account', etc.
    entity_id = Column(Integer, nullable=False)  # ID of the journal entry
    action = Column(String(50), nullable=False)  # 'CREATED', 'EDITED', 'DELETED', 'APPROVED', 'REJECTED', 'POSTED', 'CANCELLED'
    
    # Who did it
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_name = Column(String(200))  # Denormalized for reporting
    user_role = Column(String(50))  # Denormalized for reporting
    
    # When
    action_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Why (mandatory for edits/deletes)
    reason = Column(Text, nullable=True)  # Required for EDIT, DELETE, CANCEL actions
    
    # What changed (JSON snapshot)
    old_values = Column(JSON, nullable=True)  # Before state
    new_values = Column(JSON, nullable=True)  # After state
    changed_fields = Column(JSON, nullable=True)  # List of changed field names
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_status = Column(String(20), nullable=True)  # 'PENDING', 'APPROVED', 'REJECTED'
    rejection_reason = Column(Text, nullable=True)
    
    # Additional context
    ip_address = Column(String(50))  # For security tracking
    session_id = Column(String(100))  # For tracking user sessions
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approved_by])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_user', 'user_id', 'action_timestamp'),
        Index('idx_audit_date', 'action_timestamp'),
    )
```

### 2.2 Audit Log Triggers

All audit logs are created automatically via:
- **Database triggers** (preferred - cannot be bypassed)
- **Application-level hooks** (backup - logged in code)

```python
# Example: Audit log creation
def create_audit_log(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    user: User,
    reason: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    requires_approval: bool = False
):
    """Create immutable audit log entry"""
    audit_log = AccountingAuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id=user.id,
        user_name=user.full_name or user.email,
        user_role=user.role,
        reason=reason,
        old_values=old_values,
        new_values=new_values,
        changed_fields=_get_changed_fields(old_values, new_values),
        requires_approval=requires_approval,
        ip_address=request.client.host if request else None,
        session_id=request.cookies.get('session_id') if request else None
    )
    db.add(audit_log)
    db.commit()  # Commit immediately - cannot rollback
```

---

## 3. Approval Workflow for Financial Operations

### 3.1 Operations Requiring Approval

| Operation | Counter Staff | Accountant | Temple Manager | Admin |
|-----------|---------------|------------|----------------|-------|
| Create Expense < ₹5,000 | ✅ Direct | ✅ Direct | ✅ Direct | ✅ Direct |
| Create Expense ≥ ₹5,000 | ⚠️ Needs Approval | ✅ Direct | ✅ Direct | ✅ Direct |
| Edit Same-Day Entry | ❌ Not Allowed | ⚠️ Needs Approval | ✅ Direct | ✅ Direct |
| Edit Previous Day | ❌ Not Allowed | ⚠️ Needs Approval | ⚠️ Needs Approval | ✅ Direct |
| Delete Entry | ❌ Not Allowed | ⚠️ Needs Approval | ⚠️ Needs Approval | ⚠️ Needs Approval |
| Cancel Posted Entry | ❌ Not Allowed | ❌ Not Allowed | ⚠️ Needs Approval | ✅ Direct |
| Fund Transfer | ❌ Not Allowed | ⚠️ Needs Approval | ⚠️ Needs Approval | ✅ Direct |

### 3.2 Approval Request Table

```python
class ApprovalRequest(Base):
    """Approval requests for financial operations"""
    __tablename__ = "approval_requests"
    
    id = Column(Integer, primary_key=True)
    
    # What needs approval
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # 'EDIT', 'DELETE', 'CANCEL', 'CREATE'
    
    # Who requested
    requested_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow)
    request_reason = Column(Text, nullable=False)  # Mandatory
    
    # Current values (for edits)
    current_values = Column(JSON)
    proposed_values = Column(JSON)
    
    # Approval status
    status = Column(String(20), default='PENDING')  # 'PENDING', 'APPROVED', 'REJECTED'
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    rejected_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Priority
    priority = Column(String(20), default='NORMAL')  # 'LOW', 'NORMAL', 'HIGH', 'URGENT'
    amount = Column(Float, nullable=True)  # For amount-based priority
    
    # Relationships
    requester = relationship("User", foreign_keys=[requested_by])
    approver_user = relationship("User", foreign_keys=[approved_by])
    rejector_user = relationship("User", foreign_keys=[rejected_by])
```

---

## 4. Quick Expense Module - Revised Flow

### 4.1 Create Expense (Immediate Posting)

**Flow:**
1. User fills form → Clicks "Record Expense"
2. System validates → Creates journal entry
3. **Auto-posts immediately** (no draft)
4. Audit log: `CREATED` action
5. If amount ≥ threshold → Creates approval request
6. Entry visible but marked "PENDING APPROVAL" if needed

### 4.2 Edit Expense (Reversal + Correction)

**Flow:**
1. User clicks "Edit" → System checks permissions
2. If allowed → Opens edit dialog with reason field (mandatory)
3. User enters reason → Submits
4. System checks if approval needed:
   - Same day, same user, < ₹1,000 → Direct edit (reversal+correction)
   - Otherwise → Creates approval request
5. On approval → Creates reversal + correction entries
6. Audit logs: `EDITED` (original), `CREATED` (reversal), `CREATED` (correction)

### 4.3 Delete Expense

**Flow:**
1. User clicks "Delete" → System checks permissions
2. Always requires approval → Creates approval request
3. Approval request includes:
   - Original entry details
   - Reason for deletion
   - Impact analysis (which accounts affected)
4. On approval → Creates reversal entry (not actual deletion)
5. Original entry status: `CANCELLED`
6. Audit log: `DELETED` (cancelled) + `CREATED` (reversal)

---

## 5. Anti-Misappropriation Controls

### 5.1 Dual Authorization for Large Amounts

**Rule:** Any expense ≥ ₹10,000 requires two approvals:
- First approver: Accountant or Temple Manager
- Second approver: Temple Manager or Admin

**Implementation:**
- Approval request workflow supports multi-level approvals
- Both approvals must be from different users
- System tracks approval chain

### 5.2 Daily Reconciliation Requirements

**Cash Account:**
- Counter staff records all cash expenses
- End of day: Physical cash count
- Admin/Temple Manager reconciles: Opening + Receipts - Expenses = Closing
- Mismatch → Cannot close day until resolved
- Audit log: `DAILY_RECONCILIATION`

**Bank Account:**
- All bank transactions recorded
- Weekly: Bank statement import/reconciliation
- Mismatch → Alert admin, cannot proceed

**Hundi:**
- Opening count (previous day closing)
- All hundi deposits recorded
- Closing count (end of day)
- System validates: Opening + Deposits = Closing
- Mismatch → Alert, requires investigation

### 5.3 Fund Transfer Restrictions

**Rules:**
- Cash → Bank: Requires approval if ≥ ₹5,000
- Bank → Cash: Requires dual approval if ≥ ₹10,000
- Hundi → Bank: Always requires approval
- Any transfer between fund accounts: Full audit trail

### 5.4 Entry Locking After Period Close

**Rule:** Once a financial period is closed:
- Entries in that period cannot be edited or deleted
- Only reversal+correction allowed (with admin approval)
- Audit log includes period close date

### 5.5 Suspicious Activity Detection

**Alerts triggered for:**
- Multiple edits to same entry (>2 edits)
- Large amounts deleted within 24 hours of creation
- Entries created outside business hours (configurable)
- Same user creating and approving their own entries
- Rapid succession of large transactions
- Expenses without proper documentation (reference number missing)

---

## 6. Audit Report Module

### 6.1 Comprehensive Audit Trail Report

**Report Features:**
- **Cannot be deleted** - System-protected
- **Filterable by:**
  - Date range
  - User (who performed action)
  - Action type (CREATED, EDITED, DELETED, etc.)
  - Entity type (journal_entry, account, etc.)
  - Entry number
  - Amount range
  - Approval status

**Report Columns:**
- Timestamp
- User Name & Role
- Action (CREATED, EDITED, etc.)
- Entity Type & ID
- Entry Number
- Reason (for edits/deletes)
- Old Values → New Values
- Approval Status
- Approved By & When
- IP Address (for security)

**Export Options:**
- PDF (read-only, timestamped)
- Excel (with all details)
- CSV (for external analysis)

### 6.2 User Activity Report

Shows all actions by a specific user:
- Login/logout times
- All entries created/edited/deleted
- Approval actions taken
- Suspicious patterns

### 6.3 Approval Pending Report

Shows all pending approvals:
- What needs approval
- Who requested
- How long pending
- Priority level

### 6.4 Reconciliation Report

Shows reconciliation history:
- Daily cash reconciliations
- Bank reconciliations
- Hundi reconciliations
- Mismatches and resolutions

---

## 7. Database Security

### 7.1 Audit Log Table Protection

**Database-level protection:**
```sql
-- Prevent deletion (RDBMS dependent)
-- PostgreSQL: Revoke DELETE permission
REVOKE DELETE ON accounting_audit_logs FROM ALL;

-- SQLite: Application-level (no DELETE queries allowed)
-- Application code: Raise exception if DELETE attempted on audit_logs
```

**Application-level protection:**
```python
# In database session/ORM
def prevent_audit_log_deletion():
    """Prevent any deletion of audit logs"""
    # Check in delete operations
    # Raise exception if attempting to delete audit logs
    pass
```

### 7.2 Read-Only Access for Certain Roles

- Counter Staff: Cannot view audit logs
- Accountant: Can view but not export
- Temple Manager/Admin: Full access

---

## 8. Implementation Phases

### Phase 1: Multi-User & Basic Audit Trail (Week 1)
- ✅ Multi-user system (already exists)
- Create audit log table
- Auto-create audit logs for all operations
- Basic audit report

### Phase 2: Approval Workflow (Week 2)
- Approval request table
- Approval workflow for edits/deletes
- Approval pending report
- Notification system for approvals

### Phase 3: Enhanced Controls (Week 3)
- Dual authorization for large amounts
- Daily reconciliation module
- Suspicious activity alerts
- Entry locking after period close

### Phase 4: Advanced Reports (Week 4)
- Comprehensive audit trail report
- User activity report
- Reconciliation history report
- Export functionality

---

## 9. User Interface Changes

### 9.1 Quick Expense Form
- Show current user and role
- Display approval status if pending
- Show "Requires Approval" badge for large amounts

### 9.2 Edit Dialog
- **Mandatory reason field** (cannot proceed without it)
- Show approval status if needed
- Display previous edit history

### 9.3 Approval Dashboard (New Page)
- List of pending approvals
- Quick approve/reject
- Filter by priority, amount, requester
- Bulk actions

### 9.4 Audit Trail Viewer (New Page)
- Timeline view of all changes
- Filter and search capabilities
- Export options
- Read-only (no editing possible)

---

## 10. Additional Recommendations

### 10.1 Mandatory Fields for Financial Integrity
- **Reference Number**: Always required for expenses > ₹1,000
- **Supporting Document**: Upload receipt/bill (future enhancement)
- **Vendor/Supplier**: Link to vendor master (future enhancement)

### 10.2 Segregation of Duties
- **Counter Staff**: Only create expenses, view own entries
- **Accountant**: Create, edit, reconcile, view reports
- **Temple Manager**: Approve, view all, generate reports
- **Admin**: Full access, manage users, system config

### 10.3 Regular Review Processes
- **Daily**: Cash reconciliation
- **Weekly**: Bank reconciliation, review pending approvals
- **Monthly**: Audit trail review, unusual transaction analysis
- **Quarterly**: Comprehensive audit report review

### 10.4 Backup & Recovery
- Daily automated backups (including audit logs)
- Audit logs stored separately (cannot be lost)
- Point-in-time recovery capability

---

## 11. Testing Checklist

- [ ] Create expense → Verify audit log created
- [ ] Edit expense → Verify audit log with old/new values
- [ ] Delete expense → Verify approval required
- [ ] Approve request → Verify audit log for approval
- [ ] Reject request → Verify audit log for rejection
- [ ] Large amount → Verify dual approval required
- [ ] View audit report → Verify all entries visible
- [ ] Attempt to delete audit log → Verify prevented
- [ ] Export audit report → Verify data integrity
- [ ] Daily reconciliation → Verify workflow
- [ ] Period close → Verify entry locking

---

## 12. Questions for Review

1. **Approval Thresholds**: What amounts require approval? (Suggested: ₹5,000 single, ₹10,000 dual)
2. **Edit Time Window**: How long can entries be edited? (Suggested: Same day free, previous day needs approval)
3. **Audit Retention**: How long to keep audit logs? (Recommended: Permanent)
4. **Reconciliation Frequency**: Daily for cash? Weekly for bank?
5. **Suspicious Activity**: What thresholds for alerts?
6. **Backup Frequency**: Daily automated backups sufficient?

---

## Conclusion

This comprehensive audit and security system ensures:
- ✅ Complete accountability (who did what, when, why)
- ✅ Prevents misappropriation through approvals and controls
- ✅ Immutable audit trail (cannot be deleted)
- ✅ Segregation of duties (role-based access)
- ✅ Regular reconciliation (catch discrepancies early)
- ✅ Suspicious activity detection (proactive monitoring)

All changes are practical and implementable with the current technology stack.







