---
layout: post
title: "Step5 - Optimistic Locking"
date: 2026-03-14 15:17:42 +0000
categories: [database]
tags: [database, booking-system, concurrency, locking]
permalink: /database/step5-optimistic-locking-0119c663/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Step5 - Optimistic Locking.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
This strategy assumes the conflict are rare so it does not lock in the early stage of a transaction like pessimistic lock; instead it lets the transaction detect conflicts later.

This is extremely common in **high-throughput systems** because it does not prevent transactions from proceeding the statement like atomic update.

---

# Core Idea

Instead of locking rows, we attach a **version number**.

```sql
seat
---------
id
reserved
version
```


---
# Update Pattern

So update pattern will look like:
```sql
UPDATE seat
SET reserved = true,
    version = version + 1
WHERE id = 1
AND version = 3;
```

but if another transaction updates first then:
```code
version = 4
```

So the later transaction will update nothing:
```code
UPDATE 0
```

And this let the transaction know **someone modified the row.**
This is called **write conflict detection**.

---

# Implementation

The main idea is to check if the any other write execution ever happened before the first transaction attempts to execute.

So the process will be:
1. read the rows including version
2. attempt to update the row, using version as invariant
3. check the count of the updated row
4. if the 0 row updated, it means the target row is updated by other transaction

In Spring (without JPA support):
```java

@Transactional
public boolean reserveWithOptimisticLock(Long seatId) {
	SeatRow seat = jdbc.getForObject("""
			SELECT seat_id, reserved, version 
			FROM seat
			WHERE = ?
			""", (rs, rowNum) -> 
				new SeatRow(
					rs.getLong("seatId"), 
					rs.getBoolean("reserved"),
					rs.getLong("version")
				)
				, seatId);
	)
	
	if (seat.reserved()) return false;
	
	int updated = jdbc.update("""
		UPDATE seat
		SET reserved = true
		, version = version + 1
		WHERE seat_id = ?
		AND version = ?
		, seatId, seat.version();
	)
	
	return updated == 1; // checks if updated with target version
}

public record SeatRow (long seatId, boolean reserved, long version) {}
```


---

# What Happens During Concurrency

two transactions are trying to the same thing:
```code
T1 reads version = 3
T2 reads version = 3
```

then:
```code
T1 UPDATE version=3 → success
T2 UPDATE version=3 → fails
```

T2 updates 0 row. And T2 can:
- retry
- abort
- inform user
---

# Comparison With Previous Strategy

| **Strategy**     | **Behavior**          |
| ---------------- | --------------------- |
| Atomic update    | fail fast             |
| Pessimistic lock | wait                  |
| Optimistic lock  | detect conflict later |


---
# Quick Question

Suppose 100 concurrent requests try to reserve the **same seat** using optimistic locking.
What do you expect to happen to the **99 losing transactions**?
(Think about retries and system load.)

MyTh:
Losing transactions will be **aborted**. but there will be options we can choose either to retry; but 99 times of **retries** would be **expensive** too since then 98 transaction might be fail due to lock, and so on.


---

# Why Naive Retries Are Dangerous

if just retrying for 99 losing transactions, we'll have:
```code
100 → 99 fail (100 tx read version = 1 and only 1 succeeds to update)
99 → 98 fail (99 tx read version = 2 and only 1 succeeds to update)
98 → 97 fail (and so on)
...
```

This creates **retry amplification** and heavy database load.
So real systems do **not blindly retry**.

---

# What Real System Usually Do

## **Option 1 — Do not retry**
Just return with error like : "already booked"

This is common for:
- ticket booking
- reservations
- inventory

## **Option 2 — Retry with backoff**
Used when conflicts are **temporary**.

something like "retry after 10–50ms"

## **Option 3 — Re-read and merge**
Used for collaborative editing.
```code
User A edits document
User B edits document
```


---

# Key Insight

think of trade-offs of each strategy.

| **Workload**        | **Best strategy**   |
| ------------------- | ------------------- |
| Seat reservation    | atomic update       |
| Inventory decrement | atomic update       |
| Document editing    | optimistic locking  |
| Financial transfers | pessimistic locking |

---

# One Practical Refinement

For reservation specifically, I would still prefer:

```sql
UPDATE seat
SET reserved = true
WHERE id = :id
  AND reserved = false;
```

over version-based optimistic locking.

Why?  

Because your real invariant is not “version unchanged.”
It is “seat must still be unreserved.”

So:

- **version locking**(optimistic) detects generic row change
- **atomic conditional update** enforces the exact business invariant
