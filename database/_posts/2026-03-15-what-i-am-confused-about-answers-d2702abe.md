---
layout: post
title: "What I am confused about & Answers"
date: 2026-03-15 07:12:41 +0000
categories: [database]
tags: [database, booking-system, concurrency]
permalink: /database/what-i-am-confused-about-answers-d2702abe/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/What I am confused about & Answers.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive

# Atomic updates vs. Optimistic Locking

## Question
if i can just calculate the updated rows and compare with the request, then what's so different between atomic update and optimistic locking?

# Answer
They solve different correctness problems.

## Core difference
### **Atomic update**

**Atomic update protects a state transition.**

"Seat must still be unreserved if condition is not met"

```sql
UPDATE seat
SET reserved = true
WHERE id = 1
  AND reserved = false;
```

This only performs a state transition(`SET reserved`) when the real condition is true.
This is **domain invariant enforcement**.

### **Optimistic Locking**

**Optimistic locking prevents read-modify-write consistency.**

This means in other word it check

"Nobody must change the data now after I read it (nobody cannot update before I update)"

This is **write conflict detection**, not business invariant enforcement.

---

## **🔥 Key Concept**

Atomic update answers:
> “Is the state still valid for this action?”

Optimistic locking answers:
> “Has anything changed since I read?”

These are **not the same question**.


## Examples

Imagine seat table:
```code
id=1
reserved=false
price=100
version=5
```

### **Scenario**

User A reads seat → sees price 100
User B updates price → 120
User A now tries to reserve seat

### With atomic updates
```sql
UPDATE seat
SET reserved = true
WHERE id = 1
  AND reserved = false;
```
this **succeeds**.

Why? Because invariant is the seat must not be reserved, and the price does not matter.

### With Optimistic locking
```sql
UPDATE seat
SET reserved = true, version = version + 1
WHERE id = 1
  AND version = 5;
```
this **fails**.

because the version has changed due to the price.
So here optimistic is over-protective.

---

### **Another Scenario (reverse case)**

Suppose row contains:
- reservation state
- UI editable notes
- display order

Now a user edits the notes.
Atomic update cannot protect:

> “Do not overwrite someone else’s edits.”

Optimistic locking is perfect here.


---

## **⭐ Very Important Senior Insight**

Atomic update is **semantic concurrency control**.

Optimistic locking is **technical concurrency control**.


Final Statement

> Atomic update prevents **invalid state transitions**.
> Optimistic locking prevents lost updates after stale reads.
