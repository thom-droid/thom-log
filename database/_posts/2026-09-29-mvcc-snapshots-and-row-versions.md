---
layout: post
title: "MVCC: snapshots and row versions in PostgreSQL"
date: 2026-09-29 00:00:00 +0900
categories: [database]
tags: [database, postgresql, mvcc, transactions, isolation]
permalink: /database/mvcc-snapshots-and-row-versions/
excerpt: "Why two transactions can read different versions of the same seat, and how snapshot timing changes what they see."
---

[Database]({{ '/database/' | relative_url }}) / Transactions, MVCC, and locking

Before adding locks to a booking system, I wanted to understand a simpler
question: when one transaction reserves a seat, what does another transaction
see? My study notes started with a useful analogy: a database table is closer
to a history book than a whiteboard.

This post focuses on PostgreSQL. Other databases also use MVCC, but their
storage and isolation details differ.

## A row can have more than one version

MVCC stands for **Multi-Version Concurrency Control**. An update creates a new
row version, while an older version can remain available to transactions that
still need it. A snapshot determines which version a reader can see.

For a seat reservation, the conceptual history looks like this:

```text
Old version: seat 1, reserved = false
New version: seat 1, reserved = true
```

This is a visibility model, not an application audit log. Old versions are
eventually reclaimed rather than kept as permanent history.

An ordinary `SELECT` can read a visible version without waiting for a concurrent
row update to finish. That does not make the database lock-free: competing
writes and explicit locking reads such as `SELECT ... FOR UPDATE` can wait.
See PostgreSQL's [MVCC introduction](https://www.postgresql.org/docs/18/mvcc-intro.html).

## Snapshot timing changes the answer

For ordinary reads, PostgreSQL distinguishes these two isolation levels:

| Isolation level | Snapshot timing | A later read after another transaction commits |
| --- | --- | --- |
| Read Committed | At the start of each statement | Can see the newly committed value |
| Repeatable Read | At the first non-transaction-control statement | Keeps seeing the earlier snapshot |

`BEGIN` alone does not establish the Repeatable Read snapshot. Both levels also
allow a transaction to see its own earlier writes. These details come from the
[transaction isolation documentation](https://www.postgresql.org/docs/18/transaction-iso.html).

## Try it with two SQL sessions

Use a scratch database and two connections to it. Run this setup once and let
it commit before starting the experiment:

```sql
CREATE TABLE mvcc_demo_seat (
    id BIGINT PRIMARY KEY,
    reserved BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO mvcc_demo_seat (id) VALUES (1);
```

**1. Session A: read the available seat.**

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT reserved FROM mvcc_demo_seat WHERE id = 1;
-- Expected: false
```

**2. Session B: update the seat, leaving the transaction open.**

```sql
BEGIN;
UPDATE mvcc_demo_seat SET reserved = TRUE WHERE id = 1;
```

**3. Session A: read again while B has not committed.**

```sql
SELECT reserved FROM mvcc_demo_seat WHERE id = 1;
-- Expected: false; B's uncommitted version is not visible.
```

**4. Session B: commit.**

```sql
COMMIT;
```

**5. Session A: read again, then finish.**

```sql
SELECT reserved FROM mvcc_demo_seat WHERE id = 1;
-- Expected: true; this statement gets a new snapshot.
COMMIT;
```

To compare Repeatable Read, reset the seat in an autocommit session after both
transactions have finished:

```sql
UPDATE mvcc_demo_seat SET reserved = FALSE WHERE id = 1;
```

Repeat steps 1–5, changing A's opening command to
`BEGIN ISOLATION LEVEL REPEATABLE READ;`. Its final read should still return
`false`, even after B commits. These are expected results for the walkthrough,
not measurements from a benchmark.

## Old versions have a cost

Updates and deletes leave behind row versions that PostgreSQL may still need.
`VACUUM` reclaims dead versions when they are no longer needed; ordinary vacuuming
generally makes space reusable inside the table rather than returning it to
the operating system.

A long-lived snapshot can delay this cleanup. That is a reason to keep
transactions short and avoid holding them open while waiting for user input.
PostgreSQL's [vacuuming guide](https://www.postgresql.org/docs/18/routine-vacuuming.html)
explains the cleanup process.

## What I want to remember

Row versions explain how an older value can remain readable. Snapshots explain
which value a query sees. Isolation levels determine when those snapshots are
taken. Understanding visibility is the starting point for reasoning about the
booking system's concurrent requests.
