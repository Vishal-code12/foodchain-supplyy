# Database Reset Guide

## 🔄 Reset Tables

Clear data from `blocks`, `transactions`, and `crops` tables while keeping users and schema intact.

---

## Option 1: Using Python Script (Recommended)

### Run from backend directory:

```bash
cd backend
python reset_database.py
```

### Output:
```
🔄 Starting database reset...
  • Clearing blocks table...
  • Clearing transactions table...
  • Clearing crops table...

✅ Database reset complete!
   • blocks: 0 rows
   • transactions: 0 rows
   • crops: 0 rows

📝 Users table: UNCHANGED
📝 Schema: UNCHANGED
```

---

## Option 2: Using SQL Script

### Run MySQL directly:

```bash
mysql -u root -p foodchain_supply < database/reset_database.sql
```

### Or from MySQL CLI:

```sql
source database/reset_database.sql;
```

---

## What Gets Reset

✅ **blocks** table - Cleared (blockchain data)
✅ **transactions** table - Cleared (all transactions)
✅ **crops** table - Cleared (all crop records)
✅ AUTO_INCREMENT - Reset to 1

## What Stays

📝 **users** table - UNCHANGED (all farmer, retailer, distributor, customer accounts remain)
📝 **schema** - UNCHANGED (table structure intact)
📝 **foreign keys** - UNCHANGED (constraints still active)

---

## When to Use

- 🔄 Starting fresh for testing
- 🔄 Clearing old transaction history
- 🔄 Before demo/presentation
- 🔄 Between test runs
- 🔄 Resetting blockchain state

---

## After Reset

1. All users still exist - can log in
2. No crops available
3. No transaction history
4. Blockchain data cleared
5. Ready to create new crops

---

## Verification

Check that tables are empty:

```sql
SELECT COUNT(*) FROM blocks;       -- Should show 0
SELECT COUNT(*) FROM transactions; -- Should show 0
SELECT COUNT(*) FROM crops;        -- Should show 0
```

---

## ⚠️ Important Notes

- This operation **CANNOT BE UNDONE**
- Backup your database first if you need to preserve data
- User accounts are NOT deleted
- Schema structure is preserved
- You can re-create crops immediately after reset

---

## Backup Before Reset (Recommended)

```bash
# Backup entire database
mysqldump -u root -p foodchain_supply > backup_$(date +%Y%m%d_%H%M%S).sql

# Then run reset
python reset_database.py
```

---

**Use with caution!** ⚠️
