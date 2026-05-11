# Supply Chain Flow Diagram

## Visual Flow: Crop Journey

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│                    🌾 CROP SUPPLY CHAIN FLOW 🌾                        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘


STAGE 1: FARMER ADDS CROP
═══════════════════════════════════════════════════════════════════════

    Farmer Dashboard
         │
         ├─ Fill Form: Name, Qty, Price, Category, Image
         │
         ├─ API: POST /api/farmer/crops
         │
         └─ Database INSERT:
              ┌──────────────────────────────────┐
              │ id: 1                            │
              │ farmer_id: 1                     │
              │ current_owner_id: 1              │
              │ name: "Tomatoes"                 │
              │ quantity: 100.00 kg              │
              │ price_per_unit: 50.00            │
              │ status: 'available' ✓            │
              │ trace_id: '8018890' ✓ UNIQUE    │
              └──────────────────────────────────┘
              
    📊 Blockchain: CROP_ADDED event recorded



STAGE 2A: RETAILER - FULL PURCHASE (100 kg)
═══════════════════════════════════════════════════════════════════════

    Retailer Views Available Crops
         │
         ├─ API: GET /api/retailer/available-crops
         │ └─ Shows crops where status='available' & current_owner=farmer
         │
         ├─ Selects Tomatoes, Qty: 100
         │
         ├─ API: POST /api/retailer/buy
         │   payload: { crop_id: 1, quantity: 100 }
         │
         └─ UPDATE crops SET:
              ┌──────────────────────────────────┐
              │ current_owner_id: 5 (Retailer)   │
              │ status: 'sold' ✓                 │
              │ price_per_unit: 65.00 ✓          │
              │   (50 × 1.30 = +30% markup)      │
              └──────────────────────────────────┘
              
    📊 Blockchain: FARMER_TO_RETAILER recorded
    💾 Transaction: qty=100, price=6500 (100×65)



STAGE 2B: RETAILER - PARTIAL PURCHASE (50 kg from 100 kg)
═══════════════════════════════════════════════════════════════════════

    Retailer selects Tomatoes, Qty: 50
         │
         ├─ API: POST /api/retailer/buy
         │   payload: { crop_id: 1, quantity: 50 }
         │
         ├─ ORIGINAL CROP RECORD UPDATED:
         │   ┌──────────────────────────────────┐
         │   │ id: 1                            │
         │   │ quantity: 50.00 (reduced) ✓      │
         │   │ status: 'available' (stays)      │
         │   │ price_per_unit: 50.00 (unchanged)│
         │   └──────────────────────────────────┘
         │   └─ Farmer can still sell 50 kg
         │
         └─ NEW CROP RECORD CREATED:
              ┌──────────────────────────────────┐
              │ id: 2 (new)                      │
              │ farmer_id: 1 (same)              │
              │ current_owner_id: 5 (Retailer)   │
              │ quantity: 50.00 ✓ (purchased)    │
              │ price_per_unit: 65.00 ✓          │
              │ status: 'sold' ✓                 │
              │ trace_id: '7429056' ✓ NEW ID!    │
              │   └─ UNIQUE generated, NOT copy  │
              └──────────────────────────────────┘
              
    📊 Blockchain: FARMER_TO_RETAILER recorded
    💾 Transaction: qty=50, price=3250 (50×65)
    
    
    
STAGE 3A: DISTRIBUTOR - FULL PURCHASE FROM RETAILER
═══════════════════════════════════════════════════════════════════════

    Distributor Views Retailer Inventory
         │
         ├─ API: GET /api/distributor/available-crops
         │ └─ Shows crops where status='sold' & current_owner=retailer
         │
         ├─ Selects Tomato record (id: 2, 50 kg @ 65/unit)
         │
         ├─ API: POST /api/distributor/buy
         │   payload: { crop_id: 2, quantity: 50 }
         │
         └─ UPDATE crops SET:
              ┌──────────────────────────────────┐
              │ current_owner_id: 7 (Distributor)│
              │ status: 'shipped' ✓              │
              │ price_per_unit: 81.25 ✓          │
              │   (65 × 1.25 = +25% markup)      │
              └──────────────────────────────────┘
              
    📊 Blockchain: RETAILER_TO_DISTRIBUTOR recorded
    💾 Transaction: qty=50, price=4062.50 (50×81.25)
    
    
    
STAGE 3B: DISTRIBUTOR - PARTIAL PURCHASE (25 kg from 50 kg)
═══════════════════════════════════════════════════════════════════════

    Distributor selects Tomato, Qty: 25
         │
         ├─ API: POST /api/distributor/buy
         │   payload: { crop_id: 2, quantity: 25 }
         │
         ├─ ORIGINAL CROP RECORD UPDATED:
         │   ┌──────────────────────────────────┐
         │   │ id: 2                            │
         │   │ quantity: 25.00 (reduced) ✓      │
         │   │ status: 'sold' (still with ret.)  │
         │   │ current_owner_id: 5 (Retailer)   │
         │   └──────────────────────────────────┘
         │   └─ Retailer can still sell 25 kg
         │
         └─ NEW CROP RECORD CREATED:
              ┌──────────────────────────────────┐
              │ id: 3 (new)                      │
              │ farmer_id: 1 (original)          │
              │ current_owner_id: 7 (Distributor)│
              │ quantity: 25.00 ✓                │
              │ price_per_unit: 81.25 ✓          │
              │ status: 'shipped' ✓              │
              │ trace_id: '9154632' ✓ NEW ID!    │
              └──────────────────────────────────┘
              
    📊 Blockchain: RETAILER_TO_DISTRIBUTOR recorded
    💾 Transaction: qty=25, price=2031.25 (25×81.25)
    
    
    
STAGE 4: CUSTOMER - FINAL PURCHASE FROM DISTRIBUTOR
═══════════════════════════════════════════════════════════════════════

    Customer Views Available Products
         │
         ├─ API: GET /api/customer/available-crops
         │ └─ Shows crops where status='shipped' & current_owner=distributor
         │
         ├─ Selects Tomato (id: 3, 25 kg @ 81.25/unit)
         │
         ├─ API: POST /api/customer/buy
         │   payload: { crop_id: 3, quantity: 25 }
         │
         ├─ UPDATE crops SET:
         │   ┌──────────────────────────────────┐
         │   │ current_owner_id: 10 (Customer)  │
         │   │ status: 'delivered' ✓            │
         │   │ price_per_unit: 81.25 (same)     │
         │   │   NO ADDITIONAL MARKUP           │
         │   └──────────────────────────────────┘
         │
         └─ END OF SUPPLY CHAIN ✓
         
    📊 Blockchain: DISTRIBUTOR_TO_CUSTOMER recorded
    💾 Transaction: qty=25, price=2031.25 (25×81.25)
    
    
    
STAGE 5: TRACEABILITY - VIEW JOURNEY
═══════════════════════════════════════════════════════════════════════

    Customer scans QR Code → Trace ID: '9154632'
         │
         ├─ API: GET /api/trace/9154632
         │
         └─ Response shows complete journey:
         
              Step 1: Crop Created
              └─ Farmer: John Farmer
                 Time: 2025-11-02 10:00:00
                 Action: Added 100 kg tomatoes @ 50/kg
                 
              Step 2: Sold to Retailer (Partial: 50 kg)
              └─ From: John Farmer → To: Retail Store
                 Quantity: 50 kg
                 Price: 3250 (65/kg) = +30% markup
                 Block Hash: abc123...
                 
              Step 3: Distributed (Partial: 25 kg)
              └─ From: Retail Store → To: Distributor Co
                 Quantity: 25 kg
                 Price: 2031.25 (81.25/kg) = +25% markup
                 Block Hash: def456...
                 
              Step 4: Delivered to Customer (Final)
              └─ From: Distributor Co → To: Customer User
                 Quantity: 25 kg
                 Price: 2031.25 (81.25/kg) = No markup
                 Block Hash: ghi789...
                 
              ✓ Authentic Product Verified
              ✓ Blockchain Verified
              ✓ All Parties Transparent


PRICING EVOLUTION TIMELINE
═══════════════════════════════════════════════════════════════════════

100 kg Tomatoes - Price per Unit:

    Farmer Level:           50.00 $/kg
         ↓ +30% Markup
    Retailer Level:         65.00 $/kg  (Farmer gets 50, Retailer margin = 15)
         ↓ +25% Markup
    Distributor Level:      81.25 $/kg  (Retailer gets 65, Distributor margin = 16.25)
         ↓ No Markup
    Customer Level:         81.25 $/kg  (Final price - No retailer margin)


QUANTITY TRACKING
═══════════════════════════════════════════════════════════════════════

Start: 100 kg (Farmer's crop)
         │
         ├─ Retailer takes 50 kg (Partial)
         │  └─ New record: 50 kg @ Retailer
         │  └─ Remaining: 50 kg @ Farmer (still available)
         │
         ├─ Retailer takes 0 kg more
         │  └─ 50 kg stays at Retailer
         │
         └─ Distributor takes 25 kg (Partial)
            └─ New record: 25 kg @ Distributor
            └─ Remaining: 25 kg @ Retailer (still available)

Total Accounted: 50 + 25 = 75 kg (with Retailer/Distributor)
Remaining: 25 kg (at Retailer) + could go to another distributor


TRACE ID UNIQUENESS VERIFICATION
═══════════════════════════════════════════════════════════════════════

Original Crop ID 1 (100 kg):
  ├─ trace_id: '8018890' ✓ UNIQUE in DB

Partial Purchase → New Crop ID 2 (50 kg):
  └─ trace_id: '7429056' ✓ NEW UNIQUE ID (not copy!)

Partial from ID 2 → New Crop ID 3 (25 kg):
  └─ trace_id: '9154632' ✓ NEW UNIQUE ID (not copy!)

❌ NO DUPLICATES - Each record has own trace ID
✅ Database UNIQUE constraint satisfied
✅ Full audit trail maintained


DATABASE RELATIONSHIPS
═══════════════════════════════════════════════════════════════════════

crops table:
  id (PK) → trace_id (UNIQUE INDEX)
       ↓
  farmer_id (FK) → users table (farmer)
       ↓
  current_owner_id (FK) → users table (current owner)

transactions table:
  crop_id (FK) → crops table
       ├─ from_user_id (FK) → users table
       ├─ to_user_id (FK) → users table
       ├─ block_hash (FK) → blocks table (implicit)
       └─ Records every transfer


STATUS TRANSITION VALIDITY
═══════════════════════════════════════════════════════════════════════

ALLOWED TRANSITIONS:
  'available' → 'sold'      ✓ (Farmer to Retailer)
  'sold' → 'shipped'        ✓ (Retailer to Distributor)
  'shipped' → 'delivered'   ✓ (Distributor to Customer)

INVALID TRANSITIONS:
  'sold' → 'available'      ✗ No backwards
  'shipped' → 'sold'        ✗ No backwards
  'delivered' → anything    ✗ Final state
  'available' → 'shipped'   ✗ Skipping stage

All API handlers check current status before allowing transition.
```

---

## API Endpoints Summary

| Endpoint | Role | Method | Status Flow |
|----------|------|--------|-------------|
| `/api/farmer/crops` | Farmer | POST | Create (available) |
| `/api/farmer/available-crops` | All | GET | Read available |
| `/api/retailer/available-crops` | Retailer | GET | Find farmer crops |
| `/api/retailer/buy` | Retailer | POST | available → sold |
| `/api/retailer/inventory` | Retailer | GET | Read sold crops |
| `/api/distributor/available-crops` | Distributor | GET | Find retailer crops |
| `/api/distributor/buy` | Distributor | POST | sold → shipped |
| `/api/distributor/inventory` | Distributor | GET | Read shipped crops |
| `/api/customer/available-crops` | Customer | GET | Find distributor crops |
| `/api/customer/buy` | Customer | POST | shipped → delivered |
| `/api/trace/<trace_id>` | All | GET | View journey |

---

## Error Prevention

✅ **Role validation** - Only allowed roles can perform actions
✅ **Status checks** - Can't buy from wrong status
✅ **Ownership checks** - Can't buy what isn't owned by seller
✅ **Quantity validation** - Can't buy more than available
✅ **Trace ID uniqueness** - Database constraint + generation logic
✅ **Blockchain immutability** - Hash chain prevents tampering
✅ **Transaction logging** - Every action recorded

---

**Status: COMPLETE & VERIFIED ✅**
