# In-Kind Donation Guide

This guide explains how to use the in-kind donation feature in the MandirSync system.

## Overview

The donation system now supports two types of donations:
1. **Cash Donations** (default) - Monetary donations via cash, card, UPI, etc.
2. **In-Kind Donations** - Non-monetary donations like goods, services, or assets

## In-Kind Donation Types

### 1. Inventory (Consumables)
- Rice, Dal, Oil, Sugar, etc.
- Automatically creates inventory items and stock movements
- Updates stock balances
- Examples: Food items for Annadanam, Pooja materials

### 2. Event Sponsorship
- Flower decoration, Lighting decoration, Tent setup, etc.
- Tracks event details and sponsorship category
- Examples: Festival decorations, event sponsorships

### 3. Assets
- Gold, Silver, Jewellery, Idols, Movable/Immovable assets
- Can be linked to asset register
- Supports appraisal details for precious items
- Examples: Gold chains, Silver articles, Idols, Furniture

## API Usage Examples

### Example 1: Cash Donation (Default)

```json
POST /api/v1/donations/
{
  "devotee_name": "John Doe",
  "devotee_phone": "1234567890",
  "amount": 1000,
  "category": "General",
  "donation_type": "cash",  // Optional - defaults to "cash"
  "payment_mode": "Cash"
}
```

### Example 2: Inventory Donation (Rice)

```json
POST /api/v1/donations/
{
  "devotee_name": "Jane Doe",
  "devotee_phone": "9876543210",
  "amount": 5000,
  "category": "Annadanam",
  "donation_type": "in_kind",
  "inkind_subtype": "inventory",
  "item_name": "Rice",
  "item_description": "Premium Basmati Rice for Annadanam",
  "quantity": 100,
  "unit": "kg",
  "value_assessed": 5000,
  "store_id": 1  // Optional - uses default store if not provided
}
```

**What happens:**
- Creates donation record
- Creates/links inventory item
- Creates stock movement (receipt)
- Updates stock balance
- Posts accounting entry: Dr. Inventory Asset, Cr. Donation Income

### Example 3: Asset Donation (Gold Chain)

```json
POST /api/v1/donations/
{
  "devotee_name": "Smith",
  "devotee_phone": "5555555555",
  "amount": 50000,
  "category": "General",
  "donation_type": "in_kind",
  "inkind_subtype": "asset",
  "item_name": "Gold Chain",
  "item_description": "22K Gold Chain for Temple Deity",
  "quantity": 1,
  "unit": "piece",
  "value_assessed": 50000,
  "purity": "22K",
  "weight_gross": 50,
  "weight_net": 45,
  "appraised_by": "Jewelry Appraiser Name",
  "appraisal_date": "2025-01-15",
  "photo_url": "https://example.com/gold-chain.jpg",
  "document_url": "https://example.com/appraisal-cert.pdf"
}
```

**What happens:**
- Creates donation record
- Can be linked to asset register (via asset_id)
- Posts accounting entry: Dr. Asset Account, Cr. Donation Income

### Example 4: Event Sponsorship (Flower Decoration)

```json
POST /api/v1/donations/
{
  "devotee_name": "Event Sponsor",
  "devotee_phone": "1111111111",
  "amount": 10000,
  "category": "Festival",
  "donation_type": "in_kind",
  "inkind_subtype": "event_sponsorship",
  "item_name": "Flower Decoration",
  "item_description": "Full temple flower decoration for Diwali",
  "quantity": 1,
  "unit": "event",
  "value_assessed": 10000,
  "event_name": "Diwali Festival",
  "event_date": "2025-11-12",
  "sponsorship_category": "flower_decoration"
}
```

**What happens:**
- Creates donation record
- Tracks event details
- Posts accounting entry: Dr. Prepaid Expense, Cr. Donation Income

## Field Requirements

### Required for All In-Kind Donations:
- `donation_type`: Must be `"in_kind"`
- `inkind_subtype`: `"inventory"`, `"event_sponsorship"`, or `"asset"`
- `item_name`: Name of donated item
- `quantity`: Quantity (must be > 0)
- `unit`: Unit of measurement (kg, grams, pieces, etc.)
- `amount`: Donation amount (same as `value_assessed` for in-kind)

### Optional Fields:
- `value_assessed`: Assessed value (defaults to `amount` if not provided)
- `item_description`: Detailed description
- `photo_url`: Photo of donated item
- `document_url`: Appraisal certificate, receipt, etc.

### For Precious Items (Assets):
- `purity`: 22K, 24K, 925 (for silver), etc.
- `weight_gross`: Gross weight in grams
- `weight_net`: Net weight in grams
- `appraised_by`: Name of appraiser
- `appraisal_date`: Date of appraisal

### For Event Sponsorship:
- `event_name`: Name of event
- `event_date`: Date of event
- `sponsorship_category`: flower_decoration, lighting, tent, etc.

### For Inventory Items:
- `inventory_item_id`: Link to existing inventory item (optional)
- `store_id`: Store location (optional - uses default if not provided)

## Accounting Integration

All donations (cash and in-kind) are automatically posted to accounting:

### Cash Donations:
- **Debit**: Cash/Bank Account (based on payment_mode)
- **Credit**: Donation Income Account

### In-Kind Inventory:
- **Debit**: Inventory Asset Account (1300)
- **Credit**: Donation Income Account

### In-Kind Assets:
- **Debit**: Asset Account (1400 for fixed assets, 1500 for precious assets)
- **Credit**: Donation Income Account

### Event Sponsorship:
- **Debit**: Prepaid Expense Account (5100)
- **Credit**: Donation Income Account

## Querying Donations

### Get All Donations:
```bash
GET /api/v1/donations/
```

### Filter by Donation Type:
```bash
GET /api/v1/donations/?donation_type=cash
GET /api/v1/donations/?donation_type=in_kind
```

### Filter by In-Kind Subtype:
```bash
GET /api/v1/donations/?inkind_subtype=inventory
GET /api/v1/donations/?inkind_subtype=asset
GET /api/v1/donations/?inkind_subtype=event_sponsorship
```

## Best Practices

1. **Always provide `value_assessed`** for in-kind donations to ensure accurate accounting
2. **Link to inventory items** when possible for better tracking
3. **Include photos and documents** for valuable assets (gold, silver, etc.)
4. **Use proper units** (kg, grams, pieces, etc.) for accurate quantity tracking
5. **Appraise precious items** before recording to ensure accurate valuation

## Migration Status

✅ Migration completed successfully
✅ All existing donations marked as 'cash' type
✅ All new columns and indexes created
✅ Backward compatible with existing code

## Support

For issues or questions, please refer to:
- API Documentation: `/docs` (Swagger UI)
- Database Schema: `DATABASE_SCHEMA.md`
- Model Definitions: `backend/app/models/donation.py`

