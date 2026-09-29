---
layout: post
title: "Step4 - 1c. Avoid check-then-act; Atomic Update"
date: 2026-03-04 13:42:12 +0000
categories: [database]
tags: [database, booking-system, concurrency, atomic-update]
permalink: /database/step4-1c-avoid-check-then-act-atomic-update-08d6ffaa/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Step4 - 1c. Avoid check-then-act; Atomic Update.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
# **Here’s the Real Senior Question**

Imagine this requirement:

> “User can reserve up to 3 seats per day.”

Now the invariant depends on:

- user_id
- date    

Can atomic update still handle it cleanly?

---

# My answer was

```sql
INSERT INTO reservation( user_id, date )
SELECT user_id, now()
FROM reservation 
WHERE EXISTS (SELECT 1 FROM reservation WHERE user_id = :userId GROUP BY user_id, date HAVING COUNT(CASE WHEN date = :today THEN 1 END ) < 3)
```

Problems:

- If multiple transactions run it concurrently, they may both pass the COUNT < 3 check based on their own snapshot, then both insert.
- Without additional locking/serialization, the invariant can still be violated.
- Performance can degrade because you’re counting within the same table repeatedly under concurrency (hot user).
  

So: ✅ you tried to “combine check + act”, but ❌ “one SQL statement” alone does **not** guarantee correctness across multiple rows unless the DB engine enforces the right conflicts.


---

# Then How to Solve

# **Option A (recommended):** 

# **Coordination row (counter/ledger table)**

```sql
CREATE TABLE user_daily_quota (
  user_id BIGINT NOT NULL,
  day DATE NOT NULL,
  used_count INT NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, day),
  CHECK (used_count >= 0 AND used_count <= 3)
);
```

```sql
UPDATE user_daily_quota
SET used_count = used_count + 1
WHERE user_id = :userId
  AND day = :today
  AND used_count < 3;
```


---

# The Point 

**Avoid “check-then-act” when the check and the act must be true as one indivisible decision under concurrency.**

In other words, when you need a **single winner** (or a strict invariant), you must remove the race window.

### **What to do instead**

Use one of these “atomic” patterns:

1. **Guarded write (preferred when possible)**    
- UPDATE ... WHERE condition
- decide success by **affected rows**

2. **Unique constraint as the gate**
- INSERT with a unique key (duplicate fails)

1. **Locking** (when invariant spans multiple steps/rows)
- SELECT ... FOR UPDATE (pessimistic)  
- or **optimistic version** checks

4. **Serializable + retry** (when you can’t redesign easily)
    

### **The mental model**

- “Check-then-act” = **two separate moments in time**
- Atomic enforcement = **one moment** (the DB decides)


# How does it look like in Java code

the point here is that atomically execute transaction, enforcing invariant.

```java
@Service
public class ReservationService {

    private final JdbcTemplate jdbc;

    public ReservationService(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Transactional
    public boolean reserveWithDailyLimit(long userId, long seatId, LocalDate day) {

        // 1) Ensure quota row exists (no-op if already exists)
        jdbc.update("""
            INSERT INTO user_daily_quota(user_id, day, used_count)
            VALUES (?, ?, 0)
            ON CONFLICT (user_id, day) DO NOTHING
        """, userId, day);

        // 2) Try to consume quota atomically
        int updated = jdbc.update("""
            UPDATE user_daily_quota
            SET used_count = used_count + 1
            WHERE user_id = ? AND day = ? AND used_count < 3
        """, userId, day);

        if (updated == 0) {
            // quota exceeded -> rollback whole transaction
            // throwing unchecked is simplest
            throw new IllegalStateException("Daily reservation limit reached");
        }

        // 3) Reserve the seat (example: atomic seat update)
        int seatUpdated = jdbc.update("""
            UPDATE seat
            SET reserved = true
            WHERE id = ? AND reserved = false
        """, seatId);

        if (seatUpdated == 0) {
            // seat already reserved -> rollback quota increment too
            throw new IllegalStateException("Seat already reserved");
        }

        // 4) Record reservation
        jdbc.update("""
            INSERT INTO reservation(user_id, seat_id, day, reserved_at)
            VALUES (?, ?, ?, now())
        """, userId, seatId, day);

        return true;
    }
}
```
