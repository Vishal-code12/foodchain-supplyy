# Crop Flow - Database State Example

## Real-World Example: Tomatoes from John Farmer

This document shows exactly how database tables change as crops move through the supply chain.

---

## INITIAL STATE - Farmer Creates Crop

### Transaction: Farmer John adds 100 kg tomatoes @ 50/unit

```sql
-- Frontend: FarmerDashboard.jsx
Farmer fills form:
  - name: "Tomatoes"
  - quantity: 100
  - price_per_unit: 50
  - category: "vegetables"
  
-- Backend: POST /api/farmer/crops
generate_trace_id() → '8018890'
```

### Database Changes

**crops table after INSERT:**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status    | trace_id
----|-----------|------------------|----------|----------|----------------|-----------|----------
1   | 1 (John)  | 1 (John)         | Tomatoes | 100.00   | 50.00          | available | 8018890
```

**transactions table:**
(None yet - blockchain only records transfers, not creation)

**blocks table:**
```
index | action      | data_json                    | hash   | previous_hash
------|-------------|------------------------------|--------|----------------
1     | CROP_ADDED  | {...crop details...}         | abc123 | 0
```

---

## PARTIAL PURCHASE #1 - Retailer Buys 50 kg

### Transaction: Retailer Store purchases 50 kg @ auto-calculated 65/unit (+30% markup)

```
Calculation:
- Farmer price: 50/unit
- Markup: 30% (Config.RETAILER_MARKUP = 0.30)
- Retailer pays: 50 × 1.30 = 65/unit
- Total transaction: 50 kg × 65 = 3250 rupees
```

### Database Changes

**crops table BEFORE:**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status
----|-----------|------------------|----------|----------|----------------|----------
1   | 1         | 1 (John)         | Tomatoes | 100.00   | 50.00          | available
```

**crops table AFTER (UPDATE original):**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status    | trace_id
----|-----------|------------------|----------|----------|----------------|-----------|----------
1   | 1         | 1 (John)         | Tomatoes | 50.00    | 50.00          | available | 8018890
                                                 ↑ REDUCED
```

**crops table AFTER (INSERT new):**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status | trace_id
----|-----------|------------------|----------|----------|----------------|--------|----------
2   | 1         | 5 (Retail)       | Tomatoes | 50.00    | 65.00          | sold   | 7429056
    ↑ NEW                           ↑ unchanged               ↑ MARKUP APPLIED          ↑ NEW ID!
```

**transactions table INSERT:**
```
id | crop_id | from_user_id | to_user_id | transaction_type    | quantity | price | block_hash
---|---------|--------------|------------|---------------------|----------|-------|----------
1  | 1       | 1 (Farmer)   | 5 (Retail) | farmer_to_retailer  | 50.00    | 3250  | def456
```

**blocks table INSERT:**
```
index | action              | data_json                                    | hash   | previous_hash
------|---------------------|----------------------------------------------|--------|---------------
2     | FARMER_TO_RETAILER  | {...qty: 50, price: 3250, ...}              | def456 | abc123
```

### State After Partial Purchase #1
```
Crop ID 1: 50 kg remaining @ Farmer (available to sell)
Crop ID 2: 50 kg @ Retailer (can be sold to distributor)
```

---

## PARTIAL PURCHASE #2 - Another Retailer Takes Last 50 kg

### Transaction: Different Retailer buys remaining 50 kg from Farmer

### Database Changes

**crops table UPDATE (original crop, second time):**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status
----|-----------|------------------|----------|----------|----------------|----------
1   | 1         | 1 (John)         | Tomatoes | 0.00     | 50.00          | available
                                                 ↑ NOW ZERO (out of stock)
```

**crops table INSERT (new record for different retailer):**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status | trace_id
----|-----------|------------------|----------|----------|----------------|--------|----------
3   | 1         | 6 (Retail2)      | Tomatoes | 50.00    | 65.00          | sold   | 5847291
```

**transactions table INSERT:**
```
id | crop_id | from_user_id | to_user_id | transaction_type    | quantity | price | block_hash
---|---------|--------------|------------|---------------------|----------|-------|----------
2  | 1       | 1 (Farmer)   | 6 (Retail2)| farmer_to_retailer  | 50.00    | 3250  | ghi789
```

### State After Partial Purchase #2
```
Crop ID 1: 0 kg @ Farmer (SOLD OUT - stock exhausted)
Crop ID 2: 50 kg @ Retailer Store (can be resold)
Crop ID 3: 50 kg @ Retailer2 (can be resold)
```

---

## DISTRIBUTOR PURCHASE #1 - Full Purchase of Crop ID 2

### Transaction: Distributor Co buys entire 50 kg from Retail Store @ auto-calculated 81.25/unit

```
Calculation:
- Retailer price: 65/unit
- Markup: 25% (Config.DISTRIBUTOR_MARKUP = 0.25)
- Distributor pays: 65 × 1.25 = 81.25/unit
- Total: 50 × 81.25 = 4062.50
```

### Database Changes

**crops table UPDATE (Crop ID 2):**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status  | trace_id
----|-----------|------------------|----------|----------|----------------|---------|----------
2   | 1         | 7 (Distributor)  | Tomatoes | 50.00    | 81.25          | shipped | 7429056
                 ↑ CHANGED                                   ↑ MARKED UP      ↑ CHANGED
```

**transactions table INSERT:**
```
id | crop_id | from_user_id | to_user_id  | transaction_type      | quantity | price    | block_hash
---|---------|--------------|-------------|------------------------|----------|----------|----------
3  | 2       | 5 (Retail)   | 7 (Distrib) | retailer_to_distributor| 50.00    | 4062.50  | jkl012
```

### State After Distributor Purchase #1
```
Crop ID 1: 0 kg @ Farmer (exhausted)
Crop ID 2: 50 kg @ Distributor (can be resold to customers)
Crop ID 3: 50 kg @ Retailer2 (still available)
```

---

## DISTRIBUTOR PURCHASE #2 - Partial Purchase (25 kg from 50)

### Transaction: Distributor Co buys 25 kg of Crop ID 3 from Retail Store @ 81.25/unit

### Database Changes

**crops table UPDATE (Crop ID 3, reduce quantity):**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status | trace_id
----|-----------|------------------|----------|----------|----------------|--------|----------
3   | 1         | 6 (Retail2)      | Tomatoes | 25.00    | 65.00          | sold   | 5847291
                                                 ↑ REDUCED FROM 50 TO 25
```

**crops table INSERT (new record):**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status  | trace_id
----|-----------|------------------|----------|----------|----------------|---------|----------
4   | 1         | 7 (Distributor)  | Tomatoes | 25.00    | 81.25          | shipped | 9154632
    ↑ NEW ID                                                                           ↑ NEW TRACE ID
```

**transactions table INSERT:**
```
id | crop_id | from_user_id | to_user_id  | transaction_type      | quantity | price   | block_hash
---|---------|--------------|-------------|------------------------|----------|---------|----------
4  | 3       | 6 (Retail2)  | 7 (Distrib) | retailer_to_distributor| 25.00    | 2031.25 | mno345
```

### State After Distributor Purchase #2
```
Crop ID 1: 0 kg @ Farmer (exhausted)
Crop ID 2: 50 kg @ Distributor (ready for customers)
Crop ID 3: 25 kg @ Retailer2 (still available)
Crop ID 4: 25 kg @ Distributor (ready for customers)
```

---

## CUSTOMER PURCHASE - Final Delivery

### Transaction: Customer buys 25 kg of Crop ID 4 @ 81.25/unit (NO markup)

```
Note: Customer pays Distributor's price, no additional markup
Distributor receives: 25 × 81.25 = 2031.25
Profit margin built into 81.25 already includes all markups
```

### Database Changes

**crops table UPDATE (Crop ID 4, final owner):**
```
id  | farmer_id | current_owner_id | name     | quantity | price_per_unit | status    | trace_id
----|-----------|------------------|----------|----------|----------------|-----------|----------
4   | 1         | 10 (Customer)    | Tomatoes | 25.00    | 81.25          | delivered | 9154632
                 ↑ CHANGED TO CUSTOMER               ↑ STATUS FINAL
```

**transactions table INSERT:**
```
id | crop_id | from_user_id | to_user_id  | transaction_type        | quantity | price   | block_hash
---|---------|--------------|-------------|--------------------------|----------|---------|----------
5  | 4       | 7 (Distrib)  | 10 (Cust)   | distributor_to_customer | 25.00    | 2031.25 | pqr678
```

### State After Customer Purchase
```
Crop ID 1: 0 kg @ Farmer (exhausted)
Crop ID 2: 50 kg @ Distributor (ready for more customers)
Crop ID 3: 25 kg @ Retailer2 (can still be sold)
Crop ID 4: 25 kg @ Customer (FINAL - journey complete)
```

---

## TRACEABILITY - Query Customer's Product

### Customer scans QR code with Trace ID: 9154632

```sql
-- Backend: GET /api/trace/9154632
SELECT 
  c.id, c.trace_id, c.name, c.status,
  u_f.name as farmer_name,
  u_o.name as current_owner_name
FROM crops c
JOIN users u_f ON c.farmer_id = u_f.id
JOIN users u_o ON c.current_owner_id = u_o.id
WHERE c.trace_id = '9154632';
```

**Result:**
```
id | trace_id  | name     | status    | farmer_name | current_owner_name
---|-----------|----------|-----------|-------------|------------------
4  | 9154632   | Tomatoes | delivered | John Farmer | Customer User
```

### Get Complete Journey

```sql
SELECT 
  t.id,
  t.transaction_type,
  u_from.name as from_user,
  u_to.name as to_user,
  t.quantity,
  t.price as total_price,
  ROUND(t.price / t.quantity, 2) as price_per_unit,
  t.timestamp,
  t.block_hash
FROM transactions t
JOIN users u_from ON t.from_user_id = u_from.id
JOIN users u_to ON t.to_user_id = u_to.id
WHERE t.crop_id = 3  -- Crop ID 3 is parent of crop 4
ORDER BY t.timestamp;
```

**Results showing journey:**
```
Step 1:
  From: John Farmer → To: Retail Store 2
  farmer_to_retailer | 50 kg | 3250 total (65/kg)

Step 2:
  From: Retail Store 2 → To: Distributor Co
  retailer_to_distributor | 25 kg | 2031.25 total (81.25/kg)

Step 3:
  From: Distributor Co → To: Customer User
  distributor_to_customer | 25 kg | 2031.25 total (81.25/kg)
```

---

## PRICING VERIFICATION

### Trace the markup chain for Crop ID 4

| Stage | Owner | Price/Unit | Margin | Calculation |
|-------|-------|-----------|--------|-------------|
| 1 | Farmer | 50.00 | - | Base price |
| 2 | Retailer | 65.00 | +15.00 | 50 × 1.30 |
| 3 | Distributor | 81.25 | +16.25 | 65 × 1.25 |
| 4 | Customer | 81.25 | - | Final price (no markup) |

```
Customer paid: 2031.25 for 25 kg
├─ Distributor margin: 25 × 16.25 = 406.25
├─ Retailer margin: 25 × 15.00 = 375.00
├─ Farmer received: 25 × 50.00 = 1250.00
                     TOTAL: 2031.25 ✓
```

---

## COMPLETE CROP LINEAGE

### All crops originated from Farmer John's batch of 100 kg

```
CROP ID 1 (Original, 100 kg)
├─ Status: available (0 kg remaining)
├─ Created: 2025-11-02 10:00
├─ Trace ID: 8018890
├─ Sold to Retailer Store: 50 kg
└─ Sold to Retailer2: 50 kg

  ├─ CROP ID 2 (From original, 50 kg)
  │  ├─ Retailer Store ownership
  │  ├─ Status: shipped
  │  ├─ Trace ID: 7429056
  │  ├─ Sold to Distributor Co: 50 kg (full)
  │  └─ CROP ID 5 (if partially purchased, would create new)
  │
  └─ CROP ID 3 (From original, 50 kg)
     ├─ Retailer2 ownership
     ├─ Status: sold
     ├─ Trace ID: 5847291
     ├─ Remaining: 25 kg
     ├─ Sold to Distributor Co: 25 kg (partial)
     └─ CROP ID 4 (From crop 3, 25 kg)
        ├─ Distributor ownership
        ├─ Status: delivered
        ├─ Trace ID: 9154632
        └─ Sold to Customer: 25 kg (full) ✓ JOURNEY COMPLETE
```

---

## Final Statistics

```
Original Input (Farmer): 100 kg @ 50/unit
                         Total: 5000

Final Output (Customer): 25 kg @ 81.25/unit
                         Total: 2031.25

Distribution:
├─ Crop ID 2: 50 kg @ Distributor (awaiting customers)
├─ Crop ID 3: 25 kg @ Retailer2 (awaiting resale)
└─ Crop ID 4: 25 kg @ Customer (DELIVERED)

Accounting:
├─ Farmer received: 5000 (for original 100 kg)
├─ Distributed through chain: 50 + 50 = 100 kg ✓
└─ All inventory accounted for
```

---

## Key Observations

✅ **Trace IDs Are Unique**
- Original: 8018890
- Splits: 7429056, 5847291, 9154632, etc.
- NO duplicates despite multiple partial purchases

✅ **Pricing Increases at Each Stage**
- Farmer: 50 → Retailer: 65 (+30%) → Distributor: 81.25 (+25%) → Customer: 81.25

✅ **Status Transitions Are Correct**
- available → sold → shipped → delivered
- Each stage locked to its role

✅ **Ownership Changes Recorded**
- Farmer → Retailer → Distributor → Customer
- Full audit trail in transactions table

✅ **Partial Purchases Create Independent Records**
- Each new crop record gets unique trace_id
- Can be partially sold again
- Maintains complete audit trail

✅ **Blockchain Immutable**
- All transfers recorded with hash chain
- Can verify authenticity
- Customer can trace back to farmer

---

**Database demonstrates complete supply chain integrity and traceability! ✅**
