# 🌾 Crop Supply Chain Flow Analysis

## Overview
This document traces the complete journey of crops through the FoodChain Supply system from farmer to customer, including status transitions, pricing, and ownership changes.

---

## 1. FARMER: Crop Creation → 'available' status

### Endpoint
`POST /api/farmer/crops`

### What Happens
1. **Farmer adds crop** to the system with:
   - Name, description, quantity, unit
   - Price per unit (or bulk total price)
   - Category, harvest date, expiry date, location
   - Image upload (optional)

2. **Unique Trace ID Generated**
   - 6-8 digit random ID created via `generate_trace_id()`
   - Ensures uniqueness in database
   - Used for supply chain traceability

3. **Initial Values Set**
   - `farmer_id` = Farmer's user ID
   - `current_owner_id` = Farmer's user ID (farmer owns their own crop initially)
   - `status` = 'available'
   - `price_per_unit` = Farmer's base price
   - `trace_id` = Generated unique ID

4. **Blockchain Entry Created**
   - Action: `CROP_ADDED`
   - Records: crop_id, farmer_id, name, quantity

### Status
✅ **'available'** - Crop is available for purchase by retailers

### Database State
```
crops table:
- id: Auto-generated
- farmer_id: John Farmer (ID: 1)
- current_owner_id: 1 (Farmer)
- name: Tomatoes
- quantity: 100.00 kg
- price_per_unit: 50.00 (farmer's price)
- status: available
- trace_id: 8018890 (unique)
```

---

## 2. RETAILER: Purchase from Farmer → 'sold' status (with markup)

### Endpoint
`POST /api/retailer/buy`

### What Happens
1. **Retailer initiates purchase**
   - Provides: `crop_id`, `quantity` (optional, defaults to full amount)
   - Example: 50 kg from 100 kg available

2. **Full Purchase** (quantity == all available)
   - Original crop record updated:
     - `current_owner_id` = Retailer's ID
     - `status` = 'sold'
     - `price_per_unit` = Farmer price × (1 + RETAILER_MARKUP)
       - e.g., 50 × 1.30 = **65.00** (30% markup)

3. **Partial Purchase** (quantity < available)
   - Original crop reduced:
     - `quantity` = 100 - 50 = 50 kg (remaining)
     - `status` stays 'available' (farmer can sell remaining)
   
   - NEW crop record created for purchased portion:
     - `farmer_id` = Original farmer ID
     - `current_owner_id` = Retailer's ID
     - `quantity` = 50 kg (purchased amount)
     - `price_per_unit` = 50 × 1.30 = **65.00** (with markup)
     - `status` = 'sold'
     - `trace_id` = **NEW unique ID generated** ⭐ (fixes duplicate key error!)

4. **Transaction Record Created**
   - Type: `farmer_to_retailer`
   - Records: quantity, total_price (50 × 65 = 3250)
   - Block hash stored for blockchain verification

5. **Blockchain Entry**
   - Action: `FARMER_TO_RETAILER`
   - Immutable record of transaction

### Status Transition
✅ **'available'** → **'sold'** (for purchased portion)

### Pricing Evolution
- Farmer: 50.00/unit
- Retailer sees: 65.00/unit (+30% markup)

---

## 3. DISTRIBUTOR: Purchase from Retailer → 'shipped' status (with markup)

### Endpoint
`POST /api/distributor/buy`

### What Happens
1. **Distributor purchases from retailer's inventory**
   - Looks for crops with:
     - `status` = 'sold'
     - `current_owner_id` = Retailer's ID

2. **Full Purchase**
   - Crop transferred to distributor:
     - `current_owner_id` = Distributor's ID
     - `status` = 'shipped'
     - `price_per_unit` = Retailer price × (1 + DISTRIBUTOR_MARKUP)
       - e.g., 65 × 1.25 = **81.25** (25% markup)

3. **Partial Purchase**
   - Original reduced, new record created with:
     - `current_owner_id` = Distributor's ID
     - `status` = 'shipped'
     - `price_per_unit` = 65 × 1.25 = **81.25**
     - `trace_id` = **NEW unique ID generated** ⭐

4. **Transaction & Blockchain**
   - Type: `retailer_to_distributor`
   - Total: quantity × 81.25

### Status Transition
✅ **'sold'** → **'shipped'**

### Pricing Evolution
- Farmer: 50.00/unit
- Retailer: 65.00/unit (+30%)
- Distributor sees: 81.25/unit (+25% on retailer price)

---

## 4. CUSTOMER: Purchase from Distributor → 'delivered' status

### Endpoint
`POST /api/customer/buy`

### What Happens
1. **Customer purchases from distributor**
   - Looks for crops with:
     - `status` = 'shipped'
     - `current_owner_id` = Distributor's ID

2. **Ownership Transfer**
   - Crop transferred to customer:
     - `current_owner_id` = Customer's ID
     - `status` = 'delivered'
     - `price_per_unit` = **No additional markup** (customer pays distributor's price)
       - Customer pays: 81.25/unit (same as distributor's price)

3. **Transaction & Blockchain**
   - Type: `distributor_to_customer`
   - Records: final transaction at distributor's price

4. **End of Supply Chain**
   - Crop has reached final consumer
   - Full journey traceable via trace_id

### Status Transition
✅ **'shipped'** → **'delivered'**

### Final Pricing
- Farmer received: 50.00/unit
- Retailer paid: 65.00/unit
- Distributor paid: 81.25/unit
- Customer paid: 81.25/unit

---

## Complete Status Transitions Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CROP LIFECYCLE                              │
└─────────────────────────────────────────────────────────────────────┘

FARMER
  ↓ add_crop()
  ├─ status: 'available'
  ├─ owner: Farmer
  ├─ price: 50.00
  ├─ trace_id: 8018890
  └─ blockchain: CROP_ADDED

       ↓ retailer.buy(quantity)
       
RETAILER (Full/Partial Purchase)
  ├─ Original crop:
  │  ├─ status: 'sold'
  │  ├─ owner: Retailer
  │  ├─ price: 65.00 (markup applied)
  │  └─ [if partial] quantity reduced
  │
  ├─ New crop record (if partial):
  │  ├─ status: 'sold'
  │  ├─ owner: Retailer
  │  ├─ quantity: purchased amount
  │  ├─ price: 65.00
  │  ├─ trace_id: NEW UNIQUE ID ⭐
  │  └─ blockchain: FARMER_TO_RETAILER
  │
       ↓ distributor.buy(quantity)
       
DISTRIBUTOR (Full/Partial Purchase)
  ├─ status: 'shipped'
  ├─ owner: Distributor
  ├─ price: 81.25 (markup applied)
  ├─ trace_id: NEW UNIQUE ID if partial ⭐
  └─ blockchain: RETAILER_TO_DISTRIBUTOR

       ↓ customer.buy(quantity)
       
CUSTOMER (Final Purchase)
  ├─ status: 'delivered'
  ├─ owner: Customer
  ├─ price: 81.25 (NO markup - final price)
  └─ blockchain: DISTRIBUTOR_TO_CUSTOMER

       ↓ JOURNEY COMPLETE
       
TRACEABILITY
  ├─ Track via trace_id or crop_id
  ├─ View complete journey: /api/trace/<trace_id>
  ├─ See all transactions in order
  ├─ Verify blockchain hashes
  └─ Confirm authenticity
```

---

## Key Features

### ✅ Trace ID Management
- **Generation**: Unique 6-8 digit ID at farmer level
- **Propagation**: Copied to new crop records during purchases
- **Fix Applied**: New records generate NEW trace_id (prevents duplicate key errors)
- **Uniqueness**: Enforced by database UNIQUE constraint

### ✅ Pricing Evolution
- Markup applied at each transition
- Prices stored in crop records
- Each buyer sees the price from their seller
- Transparent pricing chain for audit

### ✅ Ownership Tracking
- `current_owner_id` changes with each purchase
- `farmer_id` remains constant (original source)
- Easy to find who currently owns a crop

### ✅ Status Progression
```
available → sold → shipped → delivered
```
No skipped stages or backwards transitions allowed.

### ✅ Quantity Handling
- Partial purchases create new crop records
- Original quantity reduced for remaining inventory
- Each record has independent trace_id
- No quantity loss in transactions

### ✅ Blockchain Integration
- Every transaction recorded with:
  - Block hash
  - Previous hash
  - Timestamp
  - All parties involved
- Immutable audit trail

---

## Potential Issues & Fixes

### ❌ Issue: Duplicate Trace ID on Partial Purchase
**Status**: ✅ **FIXED**
- **Cause**: Code was copying parent trace_id to new record
- **Fix**: Generate NEW unique trace_id for each new crop record
- **Implementation**: Added `generate_trace_id()` call in partial purchase logic

### ⚠️ Issue: Remaining Stock After Partial Purchase
**Status**: ✅ **HANDLED**
- Original crop quantity reduced
- Status stays 'available' for remaining inventory
- Can be sold again by farmer

### ⚠️ Issue: Partial Purchase from Partial Purchase
**Status**: ✅ **WORKS**
- Each new record is independent
- Can be partially purchased again
- Each gets unique trace_id
- Creates audit trail of all splits

---

## Database Verification

### Check Crop Journey
```sql
-- Find all instances of a crop by original ID
SELECT id, trace_id, farmer_id, current_owner_id, 
       status, quantity, price_per_unit 
FROM crops 
WHERE farmer_id = 1 
ORDER BY created_at;

-- Find all transactions for a crop
SELECT * FROM transactions 
WHERE crop_id = 1 
ORDER BY timestamp;

-- Get complete journey
SELECT 
  c.id, c.trace_id, c.name,
  u_farmer.name as farmer,
  u_owner.name as current_owner,
  c.status, c.quantity, c.price_per_unit
FROM crops c
JOIN users u_farmer ON c.farmer_id = u_farmer.id
JOIN users u_owner ON c.current_owner_id = u_owner.id
WHERE c.trace_id = '8018890';
```

### Verify Pricing Chain
```sql
SELECT 
  t.id,
  t.transaction_type,
  u_from.name as from_user,
  u_to.name as to_user,
  t.quantity,
  t.price as total_price,
  ROUND(t.price / t.quantity, 2) as price_per_unit,
  t.timestamp
FROM transactions t
JOIN users u_from ON t.from_user_id = u_from.id
JOIN users u_to ON t.to_user_id = u_to.id
WHERE t.crop_id = 1
ORDER BY t.timestamp;
```

---

## Summary

The crop flow is **complete and functional** with:
- ✅ Full supply chain from farmer to customer
- ✅ Correct status transitions (available → sold → shipped → delivered)
- ✅ Proper markup application at each stage
- ✅ Unique trace IDs for traceability
- ✅ Blockchain records for audit
- ✅ Quantity management for partial purchases
- ✅ Bug fixes applied (duplicate trace_id resolved)

**All endpoints working correctly with dynamic pricing and ownership tracking!**
