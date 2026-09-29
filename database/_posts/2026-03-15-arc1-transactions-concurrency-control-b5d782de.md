---
layout: post
title: "Arc1 - Transactions & Concurrency Control"
date: 2026-03-15 06:07:18 +0000
categories: [database]
tags: [database, booking-system, concurrency, transactions]
permalink: /database/arc1-transactions-concurrency-control-b5d782de/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Arc1 - Transactions & Concurrency Control.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive

Before writing any code, you must set the _ground rules_ correctly; otherwise the learning becomes shallow.

  

Below is a **clear starting plan** for **ARC 1 (Data Correctness & Concurrency)** with **exact first steps**, **scope boundaries**, and **success criteria**.

---

# **ARC 1 — Where to Start (Week 0 → Week 1)**

## **Step 0 — Define the Battlefield (½–1 day)**

> _If you don’t control the environment, you won’t understand the behavior._

### **✅ Choose ONE DB First**
Do **not** start with multiple DBs.

**Recommended**
- **PostgreSQL** (best MVCC visibility + tooling)    
MySQL can come later for comparison.

### **✅ Local Setup (Minimum)**
- PostgreSQL (local or Docker)
- One Spring Boot app (MVC, not reactive)
- HikariCP (default config)
  

❌ Out of scope:
- Kubernetes
- Cloud
- ORMs beyond JPA basics
---

## **Step 1 — Understand MVCC Before Coding (Critical)**

> _You should know what the DB does_ **_before_** _you ask it to do something._

### **What You Should NOT Do Yet**

- No indexes
- No performance tuning
- No locks yet

### **Concrete Task**

1. Create a single table:
```sql
CREATE TABLE seat (
  id BIGSERIAL PRIMARY KEY,
  reserved BOOLEAN NOT NULL DEFAULT FALSE
);
```

2. Open **two SQL sessions**
    
3. Manually run:
    
    - BEGIN
        
    - SELECT
        
    - UPDATE
        
    - COMMIT

4. Observe:
    
    - Who sees what
    - When changes become visible
    
### **Success Criteria**  

> You can predict query results **before running them**.
If you can’t, do **not** proceed.

---

## **Step 2 — First Naive Implementation (Intentionally Wrong)**
> _You must fail once to understand why locks exist._

### **Build This First (Yes, It’s Wrong)**

- POST /reserve/{seatId}
    
- Logic:
    
    1. Read seat
    2. If reserved = false, update to true

No locks. No transaction tuning.

### **Test Case**

- Fire **20 concurrent requests**
    
- Observe:    
    - Double booking
    - Lost updates

### **Learning Outcome**

You should see:


> _“The database did exactly what I asked — not what I intended.”_

---

## **Step 3 — Introduce Transaction Boundaries (Week 1 Core)**


> _Transactions are about_ **_intent_**_, not syntax._

### **What to Learn Now**

- @Transactional placement
- Default isolation level
- Why “one request = one transaction” is a lie
### **Experiments**

- Put @Transactional on:
    - Controller    
    - Service
    
- Trigger rollback via:
    - Runtime exception
    - Checked exception
    

  

### **Success Criteria**

You can answer:

- Why controller-level transactions are dangerou    
- Why rollback is not guaranteed

---

## **Step 4 — Pessimistic Locking (Week 2 Start)**

  

> _Now you’re allowed to use locks — carefully._

  

### **Implement**

- SELECT ... FOR UPDATE
    
- Or JPA pessimistic lock
    

  

### **Measure**

- Throughput drop
    
- Blocking behavior
    
- Deadlock risk
    

  

### **Questions You Must Answer**

- Who is blocked?
    
- For how long?
    
- What happens under high contention?
    

---

## **Step 5 — Reflection Check (Mandatory)**

Before moving to optimistic locking, write **one short document**:

### **Document Title**  

> “Why naïve reservation logic fails under concurrency”


Must include:
- MVCC explanation
- Transaction scope mistake
- Lock necessity


If you can’t explain this cleanly, **do not continue**.

---

# **What NOT To Do Yet (Important)**

  

❌ Redis locks

❌ Optimistic locking

❌ Performance tuning

❌ Async processing

  

Those come **after** you respect the database.

---

# **ARC 1 Immediate Checklist (Day 1–3)**

- PostgreSQL running
    
- Two-session MVCC experiment done
    
- Naive reservation API implemented
    
- Double booking reproduced
    
- Transaction boundaries tested
    

---
