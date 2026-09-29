---
layout: post
title: "Final Exercise"
date: 2026-03-15 06:06:21 +0000
categories: [database]
tags: [database, booking-system, concurrency]
permalink: /database/final-exercise-9a6c9309/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Final Exercise.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
  
Design transaction boundary for:

> “User reserves multiple seats in one request.”


# My Answers

## Do you lock seats one by one?
- it can lock row one by one (in terms of acquiring row level lock) like a query as below
```sql
UPDATE seat
SET reserved = true
WHERE seat_id IN (1,2,3,4,,...) AND reserved = false;
```
- it can take advantage of atomic update since its invariant is changing only one state (true) and it does not span other tables.

## What order?
- in order the seat is given.

## What if seat 3 fails? Do you rollback all?
- it depends on the requirement. if it should roll back all if any reservation has failed, then it should check the updated count and compare requested number of seats

## How to prevent deadlock?
- rather than lock rows one by one, giving order (like in the WHERE seat_id IN (...)) will prevent deadlock

->
	- it is not enough to guarantee the order of locking
	- it should be ordered and must use lock keyword (like `FOR UPDATE`)

```sql
UPDATE seat
SET reserved = true
WHERE seat_id IN (1,2,3,4,,...) AND reserved = false
ORDER BY seat_id
FOR UPDATE;	  
```
##  Which strategy: atomic / pessimistic / optimistic?
- i will use atomic updates. because simple invariant is changing simple state of the rows.

-> but,
- when thinking the real production system, the order of reservation process would typically be like:
```code
BEGIN

lock seats (ordered)
validate availability
update seats
update quota
insert reservation rows

COMMIT
```
- in this case,, it is still possible and plausible to choose atomic update to control the flow. (like comparing count of the row updated to requested row count )
- But if invariants span across the multiple tables/columns (=more complex requirements) then it's difficult to control the transaction flow properly.
- So pessimistic locking seems more proper.




## **⭐ Senior-Level Insight**

  

Single-row invariant → atomic update

  

Multi-row invariant (same table) → atomic update + count check

  

Multi-table invariant → transaction + locking

  

Long workflow invariant → optimistic locking / saga pattern
