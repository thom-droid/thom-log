---
layout: post
title: "Chapter Summary"
date: 2026-03-15 06:33:49 +0000
categories: [database]
tags: [database, booking-system, concurrency]
permalink: /database/chapter-summary-2b8b907e/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Chapter Summary.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
## **🎯 Goal of this Arc**

  
Understand **how databases preserve correctness under concurrency** and how backend engineers design transaction boundaries and invariants.

---


# **1. MVCC (Multi-Version Concurrency Control)**

### **Core idea**
- Rows are **not overwritten** → new versions are created.
- Transactions read **snapshots** of committed data.

### **Snapshot timing**

| **Isolation**                     | **Snapshot**    |
| --------------------------------- | --------------- |
| READ COMMITTED (Postgres default) | per statement   |
| REPEATABLE READ                   | per transaction |

### **Important consequences**
- Readers **do not block writers**
- Writers **block writers**
- Visibility ≠ locking


## MyTh

	MVCC is a mechanism implemented in database system to keep consistent visibility of data under the concurrency situation. It does not solve the concurrency problems, but it should be used together with locking in order to get a proper control on the transaction flow.


---

# **2. Check-Then-Act Race**

### **Dangerous pattern**

```code
read state → decide → update
```

Two transactions may read same state → both update → invariant broken.

### **Correct pattern**

Encode invariant **inside the write**.
```sql
UPDATE seat
SET reserved = true
WHERE id = 1
  AND reserved = false;
```
Decision is made **atomically by database**. (invariant enforced by database)


---

# **3. Atomic Conditional Update**

### **Concept**

- Let all transactions try
- Only valid state transition succeeds

### **Signal**
```code
updated_rows == 1 → success
updated_rows == 0 → lost race
```

### **Best for**
- single-row invariants
- counters / quotas / inventory
- high throughput systems

---

# **4. Pessimistic Locking**

### **Concept**

Assume conflict likely → **lock early**
```sql
SELECT * FROM seat WHERE id = 1 FOR UPDATE;
```

### **Behavior**
- Competing writers **wait**
- Readers still read old snapshot (MVCC)
- Lock held until commit

### **Trade-offs**
- Easier procedural logic
- Stable working set
    − Blocking
    − Deadlock risk

---

# **5. Deadlocks**

### **Cause**
Transactions lock resources in **different order**.
```sql
T1 locks A → waits B  
T2 locks B → waits A
```

### **Prevention**
Always lock in **consistent deterministic order**.
```sql
SELECT * FROM seat
WHERE id IN (1,2)
ORDER BY id
FOR UPDATE;
```

---

# **6. Optimistic Locking**

### **Concept**
Assume conflicts are rare → detect at write time.
```sql
UPDATE seat
SET version = version + 1
WHERE id = ?
  AND version = ?
```

### **Behavior**
- No blocking
- Losers get conflict → retry or abort

### **Best for**
- rare conflicts
- long user workflows
- document/profile editing

---

# **7. Transaction Boundary Design**

### **Golden rule**
Transaction scope must match **business invariant scope**.

Not:
- controller boundary
- repository call

But:
- atomic business decision  

### **Good boundary example**
```code
BEGIN
update seats
update quota
insert reservation
COMMIT
```

### **Bad boundary example**
```code
update quota → commit
later reserve seat → commit
```

---

# **8. Strategy Selection Heuristic**

| **Situation**                    | **Strategy**             |
| -------------------------------- | ------------------------ |
| Simple state transition          | Atomic update            |
| Complex multi-row decision       | Pessimistic lock         |
| Rare conflicts / long think time | Optimistic lock          |
| Cross-table invariant            | Transaction coordination |

---

# **⭐ Senior Insight (Most Important)**

Databases guarantee:
- visibility rules
- lock safety
- conflict detection


But they **do NOT understand your business invariant**.

You must encode invariants through:
- SQL conditions
- lock orderin    
- transaction boundaries
