# Change Request: CR-TEST-001
**Change Water Billing in MandirMitra**

**CR ID:** CR-TEST-001  
**Project:** MandirMitra - Temple Management System  
**Submitted By:** [To be filled]  
**Date Submitted:** 2026-01-06  
**Priority:** [To be determined]  
**Type:** Feature Enhancement / Modification  
**Status:** Submitted

---

## 1. CHANGE SUMMARY

### Current Situation
[To be documented - Current water billing implementation or lack thereof]

**Note:** MandirMitra is a temple management system. Water billing functionality may need to be:
- Added as a new feature (if not existing)
- Modified (if already exists)
- Clarified in context (water seva charges, temple facility water charges, etc.)

### Requested Change
**Change water billing in MandirMitra**

**Specific Requirements:**
- [To be clarified with stakeholder]
- What exactly needs to change?
- Is this for:
  - Water seva charges?
  - Temple facility water supply charges?
  - Donation category for water-related offerings?
  - Other water-related billing?

### Reason for Change
- [ ] Bug/Error correction
- [ ] Security vulnerability
- [ ] Performance issue
- [ ] Regulatory compliance
- [x] User feedback / Business requirement
- [ ] Technology upgrade
- [ ] Data integrity issue

### Urgency Level
**To be determined based on business impact**

---

## 2. CLARIFICATION NEEDED

### Questions for Stakeholder:

1. **What is "water billing" in MandirMitra context?**
   - Water seva charges (charges for water-related religious services)?
   - Temple facility water supply charges?
   - Donation category for water offerings?
   - Other?

2. **Does water billing currently exist in MandirMitra?**
   - If yes, where is it located?
   - If no, should this be a new feature?

3. **What specific changes are needed?**
   - Calculation method change?
   - Pricing structure change?
   - UI/UX changes?
   - Integration with accounting?

4. **Scope of Change:**
   - Which modules are affected?
   - Which user roles can access/modify?
   - Any dependencies on other features?

---

## 3. PROPOSED IMPLEMENTATION APPROACH

### Option A: Water Seva Charges (Most Likely)
If this refers to charges for water-related sevas (like Abhishekam, Jal Seva, etc.):

**Changes Required:**
- Modify seva booking system to handle water charges
- Update seva pricing structure
- Add water-specific billing fields
- Update accounting integration

### Option B: Temple Facility Water Charges
If this refers to water supply charges for temple facilities:

**Changes Required:**
- Add new expense/billing category
- Create water charge management module
- Integrate with accounting system
- Add reporting for water expenses

### Option C: Donation Category for Water Offerings
If this refers to donations for water-related offerings:

**Changes Required:**
- Add water donation category
- Update donation tracking
- Modify receipt generation
- Update accounting codes

---

## 4. NEXT STEPS

1. **Clarify Requirements:**
   - Schedule meeting with stakeholder
   - Document exact change requirements
   - Identify affected modules

2. **Impact Analysis:**
   - Review current codebase
   - Identify integration points
   - Assess technical complexity

3. **Implementation Plan:**
   - Create detailed technical specification
   - Design database changes (if needed)
   - Plan UI/UX modifications
   - Schedule development timeline

---

## 5. FILES TO REVIEW

Based on MandirMitra structure, potential files to modify:

- `backend/app/api/sevas.py` - Seva booking and charges
- `backend/app/models/seva.py` - Seva data model
- `backend/app/schemas/seva.py` - Seva API schemas
- `backend/app/api/donations.py` - Donation tracking
- `backend/app/models/donation.py` - Donation model
- `backend/app/api/accounting.py` - Accounting integration
- Frontend components (if UI changes needed)

---

## 6. STATUS

**Current Status:** Awaiting Clarification

**Action Required:**
- [ ] Clarify what "water billing" means in MandirMitra context
- [ ] Document specific change requirements
- [ ] Identify affected modules
- [ ] Create detailed implementation plan

---

**Note:** This CR document will be updated once requirements are clarified.



