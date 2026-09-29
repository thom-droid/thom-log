---
layout: post
title: "Step4 - 1b. Fitfall Of Conceptional Atomicity"
date: 2026-03-02 08:21:26 +0000
categories: [database]
tags: [database, booking-system, concurrency, atomic-update]
permalink: /database/step4-1b-fitfall-of-conceptional-atomicity-7afb76c3/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Step4 - 1b. Fitfall Of Conceptional Atomicity.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
# "Why Business Logic Check First" Feels Correct

Business Logic checks:
```java

Seat seat = findById(id);
if (!seat.isReserved()) {
    seat.setReserved(true);
    save(seat);
}
```

This feels reasonable because:
- It matches business language.
- It works in single-threaded thinking.    
- It reads clearly.

But it assumes something very dangerous:
> “Between my check and my update, nothing changes.”

In concurrent systems, that assumption is false.

---
# The Core Problem: Time Gap

> Your business rule was split into two separate operations.

- Check (read)
- Act (write)

And the world can change between them. And this time gap is called **The Race Window**. Application logic coordination always has a race window unless you eliminate it.

---
# What Atomic Version Does

```SQL
UPDATE seat
SET reserved = true
WHERE id = ? AND reserved = false;
```

Now the database executes:
- check condition
- update
- row matching
- row locking

**as one indivisible operation**. And check-then-act inside the database.

---
# Why Application-Level Check Is Dangerous

### **❌ It assumes isolation guarantees business invariants**

MVCC guarantees:
- snapshot visibility
- no dirty reads
  
It does NOT guarantee:
- “only one transaction sees this state”
- “no one else will update after I check”

---

### **❌ It does not scale under concurrency**

Under heavy load:
- Many threads pass the check
- Many threads attempt update
- You get logical duplicates

You are depending on timing luck.

---

### **❌ It leaks correctness responsibility to code**

When logic is in application:
- Every developer must understand concurrency
- Every call site must use correct transaction boundaries
- Refactoring can break invariants

When invariant is enforced in SQL:
- DB guarantees it regardless of calling pattern
- Harder to accidentally bypass

---
# **When Application Logic Is Still Valid**

Application logic checking is fine when:
- No concurrency
- Single-threaded system
- Data is read-only
- Business rule doesn’t require exclusivity

But once you require:

> “Only one winner globally”

Application coordination is fragile.

---
#  Important Caveat (Don’t Overgeneralize)

Atomic update is not always better:
- Complex invariants across rows
- Cross-table constraints
- Multi-step workflows

In those cases you may need:
- Pessimistic locking
- Optimistic versioning
- Unique constraints
- Serializable isolation

But the principle stays:

> Business invariants should be enforced at the lowest reliable layer.


---
# Intuition

Imagine this atomic update:
```sql
UPDATE seat
SET reserved = true
WHERE id = 1 AND reserved = false;
```

Two transactions run this at the exact same time.
Why does only one succeed?

## Answer
- Because database uses a **row level lock** for ensuring the atomic updates.
- When two transaction attempt to update the same row (id=1), database need to make sure updating a row at a time. So it uses **row-level lock**.
- One transaction acquires the lock first updates `reserved` to true, them commits.
- The other transaction waits for the transaction holding the lock to finish its work, then re-check the `WHERE id = 1 AND reserved = false` against **the latest committed version** of the row and finds **0 rows match**, so it updates 0 rows.
