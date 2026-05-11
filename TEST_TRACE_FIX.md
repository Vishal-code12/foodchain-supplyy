# Test the Trace ID Fix

## Quick Test Steps

### Step 1: Reset Database
```bash
cd backend
python reset_database.py
```

### Step 2: Create a Complete Supply Chain

**Farmer creates crop:**
- Name: "Tomatoes"
- Quantity: 100 kg
- Price: 50/unit
- Category: vegetables

**Retailer buys 50kg (partial):**
- Retailer purchases 50kg from farmer
- Retailer's price: 65/unit (with 30% markup)
- Note the new **trace_id** generated

**Distributor buys 25kg (partial) from retailer:**
- Distributor purchases 25kg from retailer
- Distributor's price: 81.25/unit (with 25% markup)
- Another new **trace_id** generated

**Customer buys 25kg:**
- Customer purchases 25kg from distributor
- Price: 81.25/unit
- Journey complete

### Step 3: Trace the Product

Get the **trace_id** of the final product the customer bought.

Open your browser and visit:
```
http://localhost:5000/api/trace/[trace_id]
```

Example (if trace_id is 4005615):
```
http://localhost:5000/api/trace/4005615
```

### Step 4: Verify the Complete Journey

You should see:
```json
{
  "crop": {
    "trace_id": "4005615",
    "name": "Tomatoes",
    "current_owner": "Customer User",
    "current_status": "delivered"
  },
  "journey": [
    {
      "step": 1,
      "action": "crop_created",
      "user_name": "John Farmer",
      "user_role": "farmer",
      "description": "Farmer added 100 kg of Tomatoes..."
    },
    {
      "step": 2,
      "action": "farmer_to_retailer",
      "from_user_name": "John Farmer",
      "from_user_role": "farmer",
      "to_user_name": "Retail Store",
      "to_user_role": "retailer",
      "quantity": 50,
      "price": 3250
    },
    {
      "step": 3,
      "action": "retailer_to_distributor",
      "from_user_name": "Retail Store",
      "from_user_role": "retailer",
      "to_user_name": "Distributor Co",
      "to_user_role": "distributor",
      "quantity": 25,
      "price": 2031.25
    },
    {
      "step": 4,
      "action": "distributor_to_customer",
      "from_user_name": "Distributor Co",
      "from_user_role": "distributor",
      "to_user_name": "Customer User",
      "to_user_role": "customer",
      "quantity": 25,
      "price": 2031.25
    }
  ],
  "total_steps": 4
}
```

### ✅ If You See This Structure:
- Step 1: Farmer creates
- Step 2: Farmer → Retailer
- Step 3: Retailer → Distributor
- Step 4: Distributor → Customer

**Then the fix is working!** ✅

---

## Verification Checklist

- ✅ Complete journey shows (not just first and last)
- ✅ All user names correct
- ✅ All quantities correct
- ✅ Pricing correct at each stage
- ✅ Timestamps in order
- ✅ Block hashes present
- ✅ Status shows 'delivered' for final product

---

## SQL Query to Verify

```sql
-- Find all crops created by farmer
SELECT id, trace_id, status, current_owner_id, quantity 
FROM crops 
WHERE farmer_id = 1
ORDER BY created_at;

-- Should show:
-- id=1: qty=50 (remaining with farmer)
-- id=2: qty=50 (with retailer) 
-- id=3: qty=25 (with distributor)
-- etc.

-- Check all transactions for these crops
SELECT t.id, t.crop_id, t.transaction_type, t.quantity,
       u_from.name as from_user, u_to.name as to_user
FROM transactions t
JOIN users u_from ON t.from_user_id = u_from.id
JOIN users u_to ON t.to_user_id = u_to.id
WHERE t.crop_id IN (SELECT id FROM crops WHERE farmer_id = 1)
ORDER BY t.timestamp;

-- Should show COMPLETE chain:
-- crop_id=1: farmer → retailer (50kg)
-- crop_id=2: retailer → distributor (25kg)
-- crop_id=3: distributor → customer (25kg)
```

---

## If Something Looks Wrong

### Only shows Farmer → Customer (not intermediate steps)
- ❌ Old code is still running
- Solution: Restart Flask server
  ```bash
  # Stop current server
  # In terminal with python app.py, press Ctrl+C
  
  # Then restart
  python app.py
  ```

### Shows error "Product not found"
- ❌ Trace_id doesn't exist in database
- Solution: Verify you're using the correct trace_id from the final product

### Shows only 2 steps instead of 4
- ❌ Middleware caching or old API response
- Solution: Clear browser cache, hard refresh (Ctrl+Shift+R)

---

## What Changed

The fix modifies `/api/trace/<trace_id>` endpoint to:
1. Find the crop with that trace_id
2. Get its farmer_id
3. Query ALL crops from that farmer
4. Get transactions for ALL those crops
5. Show complete journey

**Before**: Only showed transactions for one crop_id (incomplete)
**After**: Shows transactions for all related crops (complete chain)

---

## Success Criteria

✅ **Fix is successful when:**
- Trace ID path shows complete: Farmer → Retailer → Distributor → Customer
- All intermediate steps visible
- No missing transactions
- Pricing and quantities correct at each stage

**Test now and verify!** 🌾
