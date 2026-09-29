---
layout: post
title: "02. Step1- 1a. Experiment on Aggregation Query"
date: 2026-03-26 12:35:53 +0000
categories: [database]
tags: [database, booking-system, indexes, queries]
permalink: /database/02-step1-1a-experiment-on-aggregation-query-052d4170/
source_note: "study plan/Arc1 - Booking System/Part2 - Indexes/02. Step1- 1a. Experiment on Aggregation Query.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
# **Aggregation Experiment Note**


## **Query**

```
SELECT customer_id, SUM(amount)
FROM orders
WHERE status = 'CREATED'
  AND created_at >= '2025-01-01'
GROUP BY customer_id;
```

---

## **Topic 1. First plan: sequential scan**

  

### **Plan shape**

- Seq Scan on orders
    
- HashAggregate

### **What happened**

- about 175k rows matched
    
- PostgreSQL scanned the table and filtered rows
    
- then it grouped by customer_id and summed amount
    

  

### **What I learned**

  

A Seq Scan is not always a bad plan.

If many rows match and the query still needs row data for aggregation, scanning the table once can be reasonable.

  

### **My observation**

- many rows matched
    
- aggregation still needed real row data
    
- full scan was understandable
    

---

## Topic 2. Added composite index(status, created_at DESC)


### **Index**

```
CREATE INDEX idx_orders_status_created_at_desc
ON orders (status, created_at DESC);
```

### **Plan shape**

- Bitmap Index Scan
    
- Bitmap Heap Scan
    
- HashAggregate
    

  

### **What improved**

- PostgreSQL could find matching rows through the index
    
- row discovery became faster than the previous full scan
    

  

### **Why the improvement was only moderate**

- about 175k rows still matched
    
- PostgreSQL still had to fetch customer_id and amount from the heap
    
- aggregation still had to process many rows and groups
    

  

### **What I learned**

  

If a query still needs a large part of the dataset, indexing may help only moderately.

  

### **My observation**

1. bitmap index scan became much faster for row discovery
    
2. bitmap heap scan still had to fetch real rows
    
3. hash aggregate still did heavy work
    
4. total scanned working set was still large
    

  

### **Clarification**

There was no sort in this plan.

The expensive parts were mainly:

- heap fetches
    
- hash aggregation
    

---

## **Topic 3. Added covering-style index**


### **Index**

```
CREATE INDEX idx_orders_status_created_customer_inc
ON orders (status, created_at DESC, customer_id)
INCLUDE (amount);
```

### **Plan shape**

- Index Only Scan
    
- HashAggregate
    

  

### **What improved**

- PostgreSQL could satisfy the filter and needed columns directly from the index
    
- Heap Fetches: 0
    
- row access became very efficient
    

  

### **Why it was still not dramatic**

- about 175k rows still had to be aggregated
    
- about 48k groups were produced
    
- hash aggregate spilled to disk in batches
    

  

### **What I learned**

  

Once access path becomes efficient, the next bottleneck can become the aggregate operator itself.

  

### **My observation**

- row access became excellent
    
- the remaining cost moved to grouping and summing
    
- the query became fast enough, but the arithmetic work still remained
    

---

## **Topic 4. Main lesson**

  

There are two different costs in this query.

  

### **A. Row access cost**

  

How do I find qualifying rows?

- Seq Scan
    
- Bitmap Heap Scan
    
- Index Only Scan
    

  

### **B. Aggregation cost**

  

What still has to be computed?

- grouping by customer_id
    
- summing amount
    
- managing hash memory
    
- disk spill when memory is not enough
    

  

### **What I learned**

  

At first, row access was the problem.

After improving indexes, aggregation became the main problem.

---

## **Topic 5. What to try in production**

  

### **1. Reduce input rows**

- narrower date range
    
- more selective filters
    
- smaller reporting scope
    

  

### **2. Avoid aggregate spill to disk**

Try session memory tuning:

```
SET work_mem = '64MB';
```

Then check:

- Batches
    
- Disk Usage
    

### **3. Partition by time**

  

If the table keeps growing and most queries filter by created_at, partitioning by month or quarter may reduce the active dataset.

  

### **4. Pre-aggregated tables or materialized views**

  

If the same aggregation is asked repeatedly, summary tables can be more effective than recalculating from raw rows every time.

  

### **5. Separate analytics from OLTP**

  

If reporting queries become large and frequent, move them away from the transactional workload.

---

## **Final understanding**

  

I should not assume that the right index will make every aggregate query trivial.

A better index can make row access efficient, but the database may still need to do large grouping and arithmetic work.


A good summary is:

  

> Once index access becomes efficient, the next bottleneck may shift from row discovery to aggregation itself. At that point, the next optimizations come from reducing input rows, avoiding memory spill, partitioning by time, pre-aggregation, or separating analytics from OLTP.
