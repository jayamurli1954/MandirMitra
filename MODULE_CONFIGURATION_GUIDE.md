# Module Configuration Guide

## Overview

The MandirSync system now supports **per-temple module configuration**, allowing temples to enable or disable specific modules based on their needs. This is especially useful for:

- **Demo/Showcase**: Show all features to prospective temple admins
- **Selective Installation**: Install only required modules at actual temples
- **Cost Optimization**: Pay only for modules you use
- **Simplified Interface**: Hide unused modules from menu

## Current Status

✅ **Tender Management** is now **visible in menu** (for demo/showcase purposes)
✅ **Module configuration** system implemented
✅ **Per-temple control** - each temple can enable/disable modules independently

## Available Modules

1. **Donations** (`module_donations_enabled`) - Default: Enabled
2. **Sevas** (`module_sevas_enabled`) - Default: Enabled
3. **Inventory Management** (`module_inventory_enabled`) - Default: Enabled
4. **Asset Management** (`module_assets_enabled`) - Default: Enabled
5. **Accounting** (`module_accounting_enabled`) - Default: Enabled
6. **Tender Management** (`module_tender_enabled`) - Default: **Enabled** (for demo)
7. **Panchang** (`module_panchang_enabled`) - Default: Enabled
8. **Reports** (`module_reports_enabled`) - Default: Enabled
9. **Token Seva** (`module_token_seva_enabled`) - Default: Enabled

## How It Works

### For Demo/Showcase

- **All modules are enabled by default** (including Tender Management)
- Menu shows all available features
- Prospective temple admins can see full capabilities

### For Production Installation

1. **Admin logs into Settings** (`/settings`)
2. **Navigates to "Module Configuration"** section
3. **Toggles modules** on/off as needed
4. **Saves settings**
5. **Menu automatically updates** - disabled modules are hidden

## Database Structure

Module configuration is stored in the `temples` table:

```sql
ALTER TABLE temples 
ADD COLUMN module_donations_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN module_sevas_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN module_inventory_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN module_assets_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN module_accounting_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN module_tender_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN module_panchang_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN module_reports_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN module_token_seva_enabled BOOLEAN DEFAULT TRUE;
```

## API Endpoints

### Get Module Configuration
```http
GET /api/v1/temples/modules/config
Authorization: Bearer <token>
```

**Response:**
```json
{
  "module_donations_enabled": true,
  "module_sevas_enabled": true,
  "module_inventory_enabled": true,
  "module_assets_enabled": true,
  "module_accounting_enabled": true,
  "module_tender_enabled": true,
  "module_panchang_enabled": true,
  "module_reports_enabled": true,
  "module_token_seva_enabled": true
}
```

### Update Module Configuration
```http
PUT /api/v1/temples/modules/config
Authorization: Bearer <token>
Content-Type: application/json

{
  "module_tender_enabled": false,
  "module_inventory_enabled": true
}
```

## Frontend Implementation

### Layout Component

The `Layout.js` component:
1. Fetches module configuration on mount
2. Filters menu items based on configuration
3. Only shows enabled modules in sidebar

**Code:**
```javascript
// Fetch module configuration
useEffect(() => {
  fetchModuleConfig();
}, []);

// Filter menu items
const menuItems = baseMenuItems.filter(item => {
  if (item.module === null) return true; // Always show
  return moduleConfig[item.module] !== false; // Show if enabled
});
```

### Settings Page

The Settings page (`/settings`) includes:
- **Module Configuration** section
- Toggle switches for each module
- Save button to persist changes
- Automatic menu refresh after save

## Migration

Run the migration to add module configuration fields:

```bash
cd backend
python run_module_config_migration.py
```

This will:
- Add 9 module configuration columns to `temples` table
- Set default values (all enabled except tender)
- Update existing temples

## Usage Examples

### Example 1: Small Temple (Basic Features Only)

**Configuration:**
- ✅ Donations
- ✅ Sevas
- ✅ Reports
- ❌ Inventory (not needed)
- ❌ Assets (not needed)
- ❌ Accounting (basic only)
- ❌ Tender Management (not needed)
- ✅ Panchang
- ❌ Token Seva (not used)

**Result:** Menu shows only enabled modules

### Example 2: Large Temple (Full Features)

**Configuration:**
- ✅ All modules enabled

**Result:** Full menu with all features

### Example 3: Demo/Showcase

**Configuration:**
- ✅ All modules enabled (including Tender Management)

**Result:** Complete feature showcase for prospective clients

## Benefits

1. **Flexibility**: Each temple can customize their system
2. **Cost Control**: Pay only for what you use
3. **Simplified UI**: Hide unused features
4. **Easy Onboarding**: Start with basic modules, add more later
5. **Demo Ready**: Show all features to prospects

## Technical Details

### Backend

- **Model**: `Temple` model in `backend/app/models/temple.py`
- **API**: `backend/app/api/temples.py`
- **Migration**: `backend/migrations/add_module_configuration.sql`

### Frontend

- **Layout**: `frontend/src/components/Layout.js`
- **Settings**: `frontend/src/pages/Settings.js`
- **API Integration**: Fetches config on mount, updates menu dynamically

## Default Values

For **new temples**:
- All modules enabled **except** Tender Management (optional)

For **demo/showcase**:
- All modules enabled **including** Tender Management

## Updating Configuration

### Via UI (Recommended)

1. Go to Settings (`/settings`)
2. Scroll to "Module Configuration"
3. Toggle modules on/off
4. Click "Save Settings"
5. Page refreshes, menu updates

### Via API

```bash
curl -X PUT http://localhost:8000/api/v1/temples/modules/config \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "module_tender_enabled": true,
    "module_inventory_enabled": false
  }'
```

## Notes

- **Dashboard** and **Settings** are always visible (no module requirement)
- **Devotees** is always visible (core feature)
- Module configuration is **temple-specific** (multi-tenant safe)
- Changes take effect immediately after save
- Menu updates automatically on page refresh

## Future Enhancements

- Module-level permissions (who can access which modules)
- Module usage analytics
- Module activation/deactivation history
- Bulk module configuration for multiple temples

---

**Status:** ✅ Complete and Ready
**Migration:** ✅ Run `python run_module_config_migration.py`
**Default:** All modules enabled (including Tender) for demo/showcase



