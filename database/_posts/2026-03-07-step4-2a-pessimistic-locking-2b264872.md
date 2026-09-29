---
layout: post
title: "Step4 - 2a. Pessimistic Locking"
date: 2026-03-07 07:30:48 +0000
categories: [database]
tags: [database, booking-system, concurrency, locking]
permalink: /database/step4-2a-pessimistic-locking-2b264872/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Step4 - 2a. Pessimistic Locking.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
Assuming other transactions are trying to modify the same data, it introduces an idea that locks those rows immediately(early).

Contrasting to it, detecting conflicts later in the some other point of the time is **Optimistic Locking**.

---

# How it works

```sql
SELECT * FROM seat WHERE id = 1 FOR UPDATE;
```

- It acquires a **row-level exclusive lock**
- It holds the lock until the transaction commits or rolls back.

In the meanwhile if the other transaction tries to get an access to the row:

```SQL
UPDATE seat SET reserved = true WHERE id = 1;
```

Then it must wait the previous transaction holding the lock release it to proceed.

---

# What's Different Than Atomic Update
## Atomic Update
- Loser fail fast (0 rows matched) by **enforced invariant**
- Minimal waiting
- High throughput

## Pessimistic Lock
- Losers block, then fails
- Lower throughput
- Can cause request pile-ups; bottleneck
- Deadlock risk


---

# Implementation In Java

```java
/**  
 * pessimistic lock 으로 로우를 읽어온다  
 * SELECT * FROM ... FOR UPDATE와 동일  
 *  
 * PESSIMISTIC_READ 는 FOR SHARE 와 동일  
 *  
 */@Lock(LockModeType.PESSIMISTIC_WRITE)  
@Query("SELECT s FROM Seat s WHERE s.id = :id")  
Optional<Seat> findByIdForUpdate(@Param("id") Long id);
```


```java
@Transactional  
public boolean reservePessimisticLock(Long seatId) {  
    Seat seat = seatRepository.findByIdForUpdate(seatId).orElseThrow(NoSuchElementException::new);  
    if (seat.isReserved()) { return false; }  
    seat.setReserved(true);  
    seatRepository.save(seat);  
    return true;}
```

---

# Observation From My Mistake

in two manual transactions, I mistakenly missed `FOR UPDATE`clause at the end in Tx2 and what I saw was:

TX1:
```sql
BEGIN;
SELECT * FROM seat WHERE id=1 FOR UPDATE;
UPDATE seat SET reserved=true WHERE id=1;
```

TX2:
```sql
SELECT * FROM seat WHERE id=1;
```

TX2 succeeds.

because MVCC **only blocks WRITER, not READER.**
Even though TX1 holds a lock, TX2 can see because MVCC can read it from the old version snapshot.
