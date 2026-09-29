---
layout: post
title: "Project-Centric Backend Learning Roadmap"
date: 2025-12-16 10:16:30 +0000
categories: [learning]
tags: [learning, study-plan]
permalink: /learning/project-centric-backend-learning-roadmap-c9b38fc5/
source_note: "study plan/Project-Centric Backend Learning Roadmap.md"
---

[Learning]({{ '/learning/' | relative_url }}) / Study archive
**Target:** Early–Mid Backend Engineer → Senior Trajectory  
**Philosophy:** Category → Project → Reflection → Evaluation  
**Why this works:** Real systems force depth naturally. No artificial topic grinding.

---

## Overview

Instead of studying weekly micro-topics, this roadmap is organized into **4 wide learning arcs**.  
Each arc is anchored by a **non-trivial toy project** and ends with a **strict evaluation checklist**.

> If a topic is not *forced* by a project, it will not stick.

---

# ARC 1 — Data Correctness & Concurrency  
**Duration:** ~6–8 weeks  
**Mindset Shift:** “Does this still work under pressure?”

---

## 🎯 Category Focus
- MVCC & transaction isolation
- Locking & deadlocks
- Transaction boundaries
- Idempotency & retries

---

## 🧩 Toy Project — Concurrent Reservation System

### Project Brief
Build a **reservation API** (seat / room / ticket) that:
- Handles **high concurrency**
- Prevents **double booking**
- Survives **retries and failures**

No UI. API + DB only.

---

### What This Project Forces You to Learn

#### Database (Depth Boundary)
- MVCC row versions & snapshots
- READ COMMITTED vs REPEATABLE READ behavior
- Phantom reads in practice
- Why writers still need locks

#### Spring & Transactions
- Correct placement of `@Transactional`
- Propagation behaviors
- Rollback pitfalls

#### Concurrency Reality
- Hot-row contention
- Connection pool exhaustion
- Retry-induced corruption

---

### Mandatory Experiments
Implement and compare:
1. Pessimistic DB locking
2. Optimistic locking (version column)
3. Redis-based locking

Compare:
- Throughput
- Failure modes
- Operational complexity

---

## ✅ ARC 1 — Evaluation Checklist

### Database & Transactions
- [ ] I can explain MVCC using **row versions and snapshots**
- [ ] I can predict visibility in READ COMMITTED and REPEATABLE READ
- [ ] I understand why phantom reads still exist
- [ ] I know why readers and writers still block each other

### Locks & Concurrency
- [ ] I can create and resolve a deadlock
- [ ] I can explain lock acquisition order
- [ ] I understand why deadlocks are normal
- [ ] I know when optimistic locking fails

### Strategy Comparison
- [ ] I implemented DB pessimistic locking
- [ ] I implemented optimistic locking
- [ ] I implemented Redis locking
- [ ] I can explain trade-offs for each

### Spring Transactions
- [ ] I understand self-invocation issues
- [ ] I can justify transaction boundaries
- [ ] I understand rollback rules

**Pass Criteria**
> I can explain why *every* concurrency strategy fails in some scenario.

---

# ARC 2 — API Design & Backend Architecture  
**Duration:** ~5–6 weeks  
**Mindset Shift:** “Will this survive change?”

---

## 🎯 Category Focus
- API contracts & idempotency
- Pagination strategies
- HTTP semantics
- Domain-centered architecture

---

## 🧩 Toy Project — Order Management API

### Project Brief
Build an order system with:
- Create / update / cancel
- Paginated listing
- Retry-safe writes
- Clean domain separation

---

### What This Project Forces You to Learn

#### API Design
- Idempotent POST design
- Cursor vs offset pagination
- Stable error contracts

#### Architecture
- Controllers as adapters
- Domain vs application services
- Dependency direction
- Frameworks as edges

---

### Required Constraints
- Domain layer has **no Spring annotations**
- Controllers contain **zero business logic**
- All writes are retry-safe

---

## ✅ ARC 2 — Evaluation Checklist

### API Design
- [ ] I design idempotent POST endpoints
- [ ] I understand retry safety
- [ ] I can explain cursor vs offset pagination trade-offs
- [ ] I return structured, stable error responses

### Architecture
- [ ] Controllers contain no business logic
- [ ] Domain layer is framework-free
- [ ] Infrastructure depends on domain
- [ ] I distinguish domain vs application services

### Refactoring Skill
- [ ] I can refactor controller-heavy code confidently
- [ ] I can explain why the new structure is more resilient

**Pass Criteria**
> I can restructure a Spring project and defend every design choice.

---

# ARC 3 — Async, Events & Distributed Thinking  
**Duration:** ~6–8 weeks  
**Mindset Shift:** “Things don’t happen together.”

---

## 🎯 Category Focus
- Eventual consistency
- Message delivery semantics
- Idempotent consumers
- Failure handling

---

## 🧩 Toy Project — Event-Driven Order Flow

### Project Brief
Split the system into:
- Order Service
- Inventory Service
- Notification Service

Communicate via events.

---

### What This Project Forces You to Learn
- At-least-once delivery
- Duplicate & out-of-order events
- Compensation instead of rollback
- Consistency boundaries

---

### Mandatory Experiments
- Process duplicate messages safely
- Kill a service mid-flow
- Retry messages aggressively

---

## ✅ ARC 3 — Evaluation Checklist

### Event Semantics
- [ ] I understand at-least-once delivery
- [ ] I do not assume message order
- [ ] I safely handle duplicates

### Consistency
- [ ] I enforce idempotency at the correct boundary
- [ ] I understand why exactly-once is rare
- [ ] I can explain compensation logic

### Failure Handling
- [ ] I can simulate crashes mid-flow
- [ ] I understand recovery behavior
- [ ] I can draw the consistency boundary

**Pass Criteria**
> I design systems assuming failure, duplication, and delay.

---

# ARC 4 — Observability, Security & Production Ownership  
**Duration:** ~4–6 weeks  
**Mindset Shift:** “Can I own this at 3am?”

---

## 🎯 Category Focus
- Observability
- Authentication & authorization
- Deployment behavior
- Failure modes

---

## 🧩 Toy Project — Production-Ready Backend

### Project Brief
Add to previous projects:
- Structured logging
- Correlation IDs
- Metrics
- OAuth2 authentication
- Graceful shutdown

---

## ✅ ARC 4 — Evaluation Checklist

### Observability
- [ ] I distinguish logs, metrics, and traces
- [ ] I use structured logging
- [ ] I understand latency percentiles
- [ ] I avoid high-cardinality metrics

### Debugging
- [ ] I can debug production issues using signals
- [ ] I can trace requests across services
- [ ] I recognize DB vs network symptoms

### Security
- [ ] I understand OAuth2 flows
- [ ] I understand token lifecycle & rotation
- [ ] I know why JWT logout is hard
- [ ] I clearly distinguish CSRF vs CORS

### Deployment & Reliability
- [ ] I understand graceful shutdown
- [ ] I distinguish liveness vs readiness
- [ ] I understand retry storms and cascading failures

**Pass Criteria**
> I can explain how my system fails, how I detect it, and how I recover.

---

# FINAL SELF-ASSESSMENT

Answer honestly:

- [ ] I explain *why*, not just *how*
- [ ] I know my assumptions
- [ ] I understand trade-offs, not just best practices
- [ ] I am comfortable owning failures

If all are checked:
> You are operating at **solid mid-level → senior-ready** backend level.

---

**Reminder:**  
AI writes code.  
Only engineers own correctness, trade-offs, and failure.
