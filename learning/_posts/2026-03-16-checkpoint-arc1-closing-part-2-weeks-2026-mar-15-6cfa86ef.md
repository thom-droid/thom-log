---
layout: post
title: "Checkpoint; ARC1 closing part (2 Weeks)  2026 Mar 15"
date: 2026-03-16 11:28:38 +0000
categories: [learning]
tags: [learning, study-plan]
permalink: /learning/checkpoint-arc1-closing-part-2-weeks-2026-mar-15-6cfa86ef/
source_note: "study plan/Checkpoint; ARC1 closing part (2 Weeks)  2026 Mar 15.md"
---

[Learning]({{ '/learning/' | relative_url }}) / Study archive
  

## **Current Position**

- ARC 1 status: about **75% complete**
    
- Solid: MVCC, isolation, locks, deadlocks, concurrency strategy comparison
    
- Partial: indexes, planner behavior, stale statistics, plan change
    
- Needs consolidation: Spring transaction boundary, propagation, rollback rules, retry safety, idempotency
    

---

## **Main Goal**

  

Close ARC 1 by turning scattered concepts into **selection criteria**.

  
At the end of these 2 weeks, I should be able to answer:

1. Why did the DB choose this access path?
    
2. Why did this transaction partially succeed or fail?
    
3. Which concurrency strategy fits this write path?
    
4. How do transaction safety and retry safety differ?
    

---

# **Week 1 — Indexes + Planner**

  

## **Weekly Goal**

Build practical judgment for why an index is or is not used.


## **Focus Concepts**

- B+Tree
    
- selectivity / cardinality
    
- composite index ordering
    
- covering index
    
- sargability
    
- stale statistics
    
- execution plan change
    

  

## **Day 1 — When indexes work / when they do not**

  

### **Study**

- Single-column index vs composite index (A, B)
    
- Leftmost prefix rule
    
- Why WHERE B = ? usually cannot fully benefit from (A, B)
    
- Function on indexed column and leading wildcard cases
    

  

### **Practice**

- Compare these queries:
    
    - WHERE A = ?
        
    - WHERE A = ? AND B = ?
        
    - WHERE B = ?
        
    - WHERE A LIKE '%x'
        
    - WHERE UPPER(A) = ?
        
    

  

### **Notes**

- **Concept summary:**
    
- **What surprised me:**
    
- **What I can now explain in my own words:**
    

  

### **Self-check**

- Can I explain the leftmost prefix rule without using the term itself?
    
- Can I explain why some predicates break efficient index lookup?
    

---

## **Day 2 — Reading execution plans**

  

### **Study**

- EXPLAIN / EXPLAIN ANALYZE
    
- access path vs actual runtime behavior
    
- estimated rows vs actual rows
    

  

### **Practice**

- Run the same query with small condition changes
    
- Record how the plan changes
    
- Identify where the planner made a good or bad estimate
    

  

### **Notes**

- **Plan snippet:**
    
- **Why I think this path was chosen:**
    
- **Estimate vs actual difference:**
    
- **What this implies:**
    

  

### **Self-check**

- Can I explain why the DB did not choose the index I expected?
    

---

## **Day 3 — Selectivity / low-cardinality indexes**

  

### **Study**

- Why boolean-like columns are often weak standalone indexes
    
- When they become useful inside composite indexes
    

  

### **Practice**

- Think through examples like:
    
    - delete_yn
        
    - status
        
    - gender
        
    
- Redesign them into more realistic composite indexes
    

  

### **Notes**

- **Low-cardinality example:**
    
- **Why standalone index is weak:**
    
- **Better composite alternative:**
    

  

### **Self-check**

- Can I explain why “has index” does not mean “good index”?
    

---

## **Day 4 — Covering index / ordering / pagination**

  

### **Study**

- Covering index idea
    
- WHERE + ORDER BY + LIMIT
    
- Offset pagination cost growth
    

  

### **Practice**

- Compare:
    
    - filtering only
        
    - filtering + sorting
        
    - filtering + sorting + pagination
        
    
- Think about which columns should appear in an index and in what order
    

  

### **Notes**

- **Query pattern:**
    
- **Best index candidate:**
    
- **Why this order makes sense:**
    

  

### **Self-check**

- Can I explain why pagination becomes slower as offset grows?
    

---

## **Day 5 — Why dev is fast but prod is slow**

  

### **Study**

- stale statistics
    
- plan change
    
- cache effects
    
- lock waits
    
- pool bottlenecks
    
- environment differences
    

  

### **Practice**

  

Write a short note:

**Why the same SQL can behave differently across environments**

  

### **Notes**

- **Possible cause 1:**
    
- **Possible cause 2:**
    
- **Possible cause 3:**
    
- **How to distinguish them:**
    

  

### **Self-check**

- Can I separate plan problem from lock-wait problem?
    
- Can I explain why “it used to be fast” does not automatically mean application code changed?
    

---

## **Week 1 Wrap-up**

  

### **What I learned**

  

### **What still feels blurry**

  

### **3 quiz questions for myself**

1.   
    
2.   
    

  

### **Pass criteria**

- I can explain at least 3 reasons an index is not used
    
- I can explain stale statistics and plan change in plain language
    
- I can reason about index order instead of guessing
    

---

# **Week 2 — Spring Transaction Boundary + Retry Safety**

  

## **Weekly Goal**

  

Treat transactions as **business consistency boundaries**, not just annotations.

  

## **Focus Concepts**

- transaction boundary
    
- service-layer transaction design
    
- self-invocation
    
- Spring proxy / AOP
    
- rollback rules
    
- propagation
    
- retry-safe write
    
- idempotency key
    

  

## **Day 1 — Where transaction boundaries belong**

  

### **Study**

- Controller vs Service vs Repository transaction ownership
    
- One use case, one consistency boundary
    

  

### **Practice**

- Pick one business flow and mark where the transaction should begin and end
    
- Explain why controller-level transaction is often too wide
    

  

### **Notes**

- **Chosen use case:**
    
- **Best transaction boundary:**
    
- **Why:**
    

  

### **Self-check**

- Can I explain why transaction scope should follow business invariants rather than method count?
    

---

## **Day 2 — Self-invocation / proxy behavior**

  

### **Study**

- Why @Transactional relies on proxy interception
    
- Why internal method calls can bypass the proxy
    

  

### **Practice**

- Write a tiny example:
    
    - external bean call
        
    - same-class internal call
        
    
- Predict which one opens a transaction
    

  

### **Notes**

- **Code sketch:**
    
- **What actually happens:**
    
- **Why annotation alone is not enough:**
    

  

### **Self-check**

- Can I explain why a transaction annotation may appear correct but still not work?
    

---

## **Day 3 — Rollback rules / exceptions / try-catch**

  

### **Study**

- checked vs unchecked exceptions
    
- swallowing exceptions
    
- manual rollback vs Spring-managed rollback
    

  

### **Practice**

- Connect to my legacy MyBatis usage
    
- Write one bad example and one corrected example
    

  

### **Notes**

- **Failure scenario:**
    
- **Why rollback did not happen:**
    
- **How to redesign it:**
    

  

### **Self-check**

- Can I explain 3 reasons partial data may remain after an error?
    

---

## **Day 4 — Propagation choices**

  

### **Study**

- REQUIRED vs REQUIRES_NEW
    
- which operations must live and die together
    
- which operations may be isolated
    

  

### **Practice**

- ## **Use examples:**
