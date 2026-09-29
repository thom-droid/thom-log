---
layout: post
title: "03. Step1 - Stage 2 - index on join"
date: 2026-03-31 10:56:53 +0000
categories: [database]
tags: [database, booking-system, indexes]
permalink: /database/03-step1-stage-2-index-on-join-a3a4500a/
source_note: "study plan/Arc1 - Booking System/Part2 - Indexes/03. Step1 - Stage 2 - index on join.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
# Index & Planner Lab — Session Wrap-up

## 1. Composite indexes and access paths
I learned that indexes help only when the query shape matches the index structure.

### Key ideas
- Composite index order should follow the filter / range / order pattern.
- `(customer_id, created_at)` is strong for recent orders of one customer.
- Low-cardinality standalone indexes are often weak.
- `ORDER BY ... LIMIT` can make a matching index much more powerful.

### What became clearer
- An index can exist and still not be chosen.
- `Index Cond` is much stronger than `Filter`.
- The planner chooses the cheapest access path, not the most “indexed” one.

---

## 2. Execution plan reading
I practiced reading plans from the bottom and understanding scan/access nodes.

### Important nodes
- `Seq Scan`
- `Parallel Seq Scan`
- `Index Scan`
- `Index Only Scan`
- `Bitmap Index Scan`
- `Bitmap Heap Scan`
- `Nested Loop`
- `Hash Join`
- `Gather`
- `Gather Merge`

### Key understanding
- `cost` is optimizer estimate, not milliseconds.
- `rows` estimate vs actual rows is important.
- `Index Cond` means the predicate participates in access.
- `Filter` means the condition is applied after rows reach the node.

---

## 3. Stage 1 join — one join, one filter
### Query shape
- One customer
- Recent orders
- Ordered by time
- Limited result

### Before index
- PostgreSQL scanned all of `orders2`.
- Customer lookup was cheap.
- The real problem was finding the order rows.

### After adding index
```sql
CREATE INDEX idx_orders2_customer_created
    ON orders2 (customer_id, created_at DESC);
```

- PostgreSQL could jump directly to that customer’s orders.
- Execution time dropped sharply.
- The real gain was the improved access path on `orders2`.

### Key lesson
The main bottleneck was row discovery, not the join itself.

---

## 4. Aggregation experiment
### Query
```sql
SELECT customer_id, SUM(amount)
FROM orders
WHERE status = 'CREATED'
  AND created_at >= '2025-01-01'
GROUP BY customer_id;
```

### Step 1 — Without matching index
Plan:
- `Seq Scan`
- `HashAggregate`

What I learned:
- `Seq Scan` is not always a bad plan.
- If many rows match, scanning once can be reasonable.

### Step 2 — Added filter index
```sql
CREATE INDEX idx_orders_status_created_at_desc
ON orders (status, created_at DESC);
```

Plan:
- `Bitmap Index Scan`
- `Bitmap Heap Scan`
- `HashAggregate`

What I learned:
- Row discovery improved.
- But the gain was only moderate because many rows still qualified and heap fetches still mattered.

### Step 3 — Added covering-style index
```sql
CREATE INDEX idx_orders_status_created_customer_inc
ON orders (status, created_at DESC, customer_id)
INCLUDE (amount);
```

Plan:
- `Index Only Scan`
- `HashAggregate`
- `Heap Fetches: 0`

What I learned:
- Row access became very efficient.
- The bottleneck shifted to the aggregate itself.

### Main lesson from aggregation
There are two costs:
1. **Row access cost**
2. **Aggregation cost**

At first, row access was the problem.  
After improving indexes, aggregation became the main problem.

### Production takeaways
- Narrow the input range if possible.
- Reduce aggregate spill with `work_mem`.
- Partition by time if the table keeps growing.
- Use summary tables or materialized views for repeated aggregate workloads.
- Separate analytics from OLTP when necessary.

---

## 5. Stage 2 join — filter parent, join child
### Query shape
- Filter `orders2`
- Join to `order_items`

### Broad filter case
```sql
WHERE o.status = 'SHIPPED'
  AND o.created_at >= '2025-01-01'
```

Plan:
- Filtered `orders2`
- Built hash table
- Scanned all `order_items`
- Used `Hash Join`

What I learned:
- Improving the parent side helped, but total speedup stayed small because `order_items` still dominated the work.
- A join-key index on the child table is not always used just because it exists.

### Narrow filter case
```sql
WHERE o.status = 'SHIPPED'
  AND o.created_at >= '2025-12-01'
```

Plan:
- `Parallel Seq Scan` on `orders2`
- `Nested Loop`
- `Index Scan` on `order_items(order_id)`

What I learned:
- When the parent result set became small enough, PostgreSQL switched from:
  - broad child scan + hash join
  to:
  - nested loop + indexed child lookup

### Key lesson
Join method depends strongly on selectivity.

- Broader parent result -> `Hash Join`
- Smaller parent result -> `Nested Loop`

---

## 6. What I understand now
Planner decisions are not just “use index or not.”

They depend on:
- How many rows are likely to match
- Whether broad scan or repeated lookup is cheaper
- Whether heap fetches dominate
- Whether aggregation becomes the bottleneck
- Whether join selectivity is small enough for nested loop to win

---

## 7. Final summary
A good summary of this session is:

> Index tuning is really access-path tuning. A good index can drastically improve row discovery, but total query speed depends on the dominant remaining cost. In joins, that may be the other table or the join method. In aggregates, that may be the grouping work itself. The planner changes strategies based on selectivity, row counts, and total estimated cost, not just on whether a matching index exists.
