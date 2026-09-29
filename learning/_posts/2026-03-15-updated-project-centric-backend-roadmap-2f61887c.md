---
layout: post
title: "updated_project_centric_backend_roadmap"
date: 2026-03-15 08:04:34 +0000
categories: [learning]
tags: [learning, study-plan]
permalink: /learning/updated-project-centric-backend-roadmap-2f61887c/
source_note: "study plan/updated_project_centric_backend_roadmap.md"
---

[Learning]({{ '/learning/' | relative_url }}) / Study archive
# Project-Centric Backend Learning Roadmap — Synced Version

**Target:** Early–Mid Backend Engineer → Mid-level → Senior Trajectory  
**Primary Focus:** Databases, Concurrency, API Design, Architecture, Reliability, Security  
**Philosophy:** Category → Project → Reflection → Evaluation  
**Base Document:** Project-Centric roadmap  
**Synced With:** 12-week roadmap

---

## Current Position Snapshot

### Where You Are Now
You are currently in **ARC 1 — Data Correctness & Concurrency**.

Your present level appears to be:
- **ARC 1 overall:** about **60–70% complete**
- **MVCC / isolation / lock reasoning:** **strongly started**
- **Concurrency control strategies:** **actively completed at comparison level**
- **Indexes / planner reasoning:** **introduced, but not yet deep enough to call finished**
- **Spring transaction boundary mastery:** **partially covered, not yet fully consolidated**

### What Seems Already Learned
Based on your recent work and discussions, you have already meaningfully worked through:
- MVCC basics and snapshot thinking
- Transaction isolation concepts
- Lost update / blocking / locking intuition
- Pessimistic locking vs optimistic locking vs atomic update reasoning
- Deadlock and lock-order ideas
- Retry safety and concurrency failure scenarios
- Basic index concepts such as composite indexes, usefulness, and why some indexes are ignored

### Best Fit Checkpoint
If ARC 1 is divided into 4 internal checkpoints, your current position is best described as:

**ARC 1 — Checkpoint 3 / 4**
1. MVCC & isolation fundamentals — largely done  
2. Locking, deadlocks, and strategy comparison — largely done  
3. Transaction boundary + index/planner reinforcement — in progress  
4. Reservation project hardening and evaluation — next

### What Is Not Fully Done Yet
Before you move cleanly into ARC 2, you should still close these gaps:
- explain index usage decisions from execution plans more confidently
- connect index design with actual query predicates and sort patterns
- tighten Spring transaction boundary rules (`@Transactional`, self-invocation, propagation, rollback)
- finish one project-quality comparison of concurrency strategies using explicit trade-offs:
  - correctness
  - throughput
  - operational complexity
  - failure mode
- complete a final ARC 1 write-up in your own words

---

# Overview

Instead of studying disconnected topics, this roadmap is organized into **4 wide learning arcs**.  
Each arc is anchored by a **non-trivial toy project**, but now each arc also includes **micro-phases** so progress is easier to track.

> If a topic is not forced by a project, it will not stick.  
> If a project is not reflected on, the topic will not become yours.

---

# ARC 1 — Data Correctness & Concurrency
**Duration:** ~6–8 weeks  
**Mindset Shift:** “Does this still work under pressure?”

## Category Focus
- MVCC & transaction isolation
- Indexes & query planner basics
- Locking & deadlocks
- Transaction boundaries
- Idempotency & retries

## Toy Project — Concurrent Reservation System
Build a **reservation API** (seat / room / ticket) that:
- handles **high concurrency**
- prevents **double booking**
- survives **retries and partial failures**
- exposes behavior clearly through logs, DB state, and repeatable tests

No UI. API + DB only.

## ARC 1 Internal Phases

### Phase 1 — MVCC & Isolation
**Goal:** Predict data visibility under concurrency.

#### Must Know
- MVCC row versions & snapshots
- snapshot timing
- READ COMMITTED vs REPEATABLE READ
- non-repeatable read vs phantom read
- why MVCC does not remove locks

#### Experiments
- show different visibility under READ COMMITTED and REPEATABLE READ
- reproduce non-repeatable reads
- observe effects of long-running transactions

#### Exit Standard
- you can explain what each transaction sees and **why**

---

### Phase 2 — Indexes & Query Planner Foundations
**Goal:** Know why an index is used, ignored, or insufficient.

#### Must Know
- B+Tree access patterns
- selectivity & cardinality
- composite index ordering
- covering indexes
- why boolean-only indexes are often weak
- why `(A, B)` does not automatically help `WHERE B = ?`

#### Experiments
- break and fix an index using `EXPLAIN` / `EXPLAIN ANALYZE`
- compare single-column vs composite index behavior
- compare filtering and sorting patterns with and without index support

#### Exit Standard
- you can read a plan line-by-line and explain index choice in practical terms

---

### Phase 3 — Locks, Deadlocks, and Strategy Comparison
**Goal:** Predict blocking behavior and choose the least-wrong strategy.

#### Must Know
- row locks
- gap / next-key locks in MySQL mindset
- deadlock detection
- lock acquisition order
- hot-row contention

#### Mandatory Implementations
Implement and compare:
1. pessimistic DB locking
2. optimistic locking with version column
3. atomic update pattern where applicable
4. Redis-based locking

#### Compare By
- correctness guarantees
- throughput under contention
- operational complexity
- failure modes
- ease of reasoning

#### Exit Standard
- you can explain **why every strategy fails somewhere**

---

### Phase 4 — Spring Transaction Boundaries
**Goal:** Control commit/rollback behavior instead of assuming it.

#### Must Know
- proxy-based AOP
- `@Transactional` placement
- propagation types
- rollback rules
- self-invocation problem
- why controllers should not own transactions

#### Experiments
- demonstrate self-invocation failure
- compare `REQUIRED` vs `REQUIRES_NEW`
- reproduce rollback edge cases with checked vs unchecked exceptions

#### Exit Standard
- you can draw transaction boundaries before coding them

---

## ARC 1 Evaluation Checklist

### Database & Isolation
- [ ] I can explain MVCC using row versions and snapshots
- [ ] I can predict visibility in READ COMMITTED and REPEATABLE READ
- [ ] I can explain non-repeatable reads and phantom reads in practice
- [ ] I know why MVCC does not eliminate locking

### Indexes & Planner
- [ ] I can explain why an index is ignored
- [ ] I understand composite index ordering
- [ ] I can connect query predicates to index design
- [ ] I can read an execution plan without hand-waving

### Locks & Concurrency
- [ ] I can create and resolve a deadlock
- [ ] I understand lock acquisition order
- [ ] I can compare pessimistic, optimistic, atomic-update, and Redis locking
- [ ] I know when optimistic locking fails under high contention

### Transactions
- [ ] I understand self-invocation issues
- [ ] I can justify transaction boundaries
- [ ] I understand rollback rules and propagation choices

### Pass Criteria
> I can explain why each concurrency strategy succeeds, where it fails, and what trade-off it buys.

---

# ARC 2 — API Design & Backend Architecture
**Duration:** ~5–6 weeks  
**Mindset Shift:** “Will this survive change?”

## Category Focus
- API contracts & idempotency
- HTTP semantics
- pagination strategies
- error contracts
- domain-centered architecture

## Toy Project — Order Management API
Build an order system with:
- create / update / cancel
- paginated listing
- retry-safe writes
- clean domain separation

## ARC 2 Internal Phases

### Phase 1 — API Semantics
**Goal:** Design APIs that behave predictably under retries and scale.

#### Must Know
- idempotent POST design
- HTTP semantics
- cursor vs offset pagination
- stable error contracts

#### Exit Standard
- you can defend endpoint behavior under retry and concurrent usage

---

### Phase 2 — Application Structure
**Goal:** Put business logic where it can survive framework churn.

#### Must Know
- controllers as adapters
- domain vs application services
- dependency direction
- frameworks at the edge
- hexagonal architecture intuition

#### Required Constraints
- domain layer has **no Spring annotations**
- controllers contain **zero business logic**
- all writes are retry-safe

#### Exit Standard
- you can refactor a controller-heavy service into a cleaner architecture

---

## ARC 2 Evaluation Checklist

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

### Pass Criteria
> I can restructure a Spring project and defend every design choice.

---

# ARC 3 — Async, Events & Distributed Thinking
**Duration:** ~6–8 weeks  
**Mindset Shift:** “Things do not happen together.”

## Category Focus
- event-driven thinking
- eventual consistency
- message delivery semantics
- idempotent consumers
- compensation and failure handling

## Toy Project — Event-Driven Order Flow
Split the system into:
- Order Service
- Inventory Service
- Notification Service

Communicate via events.

## ARC 3 Internal Phases

### Phase 1 — Delivery Semantics
**Goal:** Assume duplication and delay.

#### Must Know
- at-least-once delivery
- duplicate messages
- out-of-order events
- event ordering assumptions

---

### Phase 2 — Consistency Boundaries
**Goal:** Replace fantasy rollback with realistic recovery.

#### Must Know
- compensation instead of distributed rollback
- idempotency boundary selection
- why exactly-once is rare

---

### Mandatory Experiments
- process duplicate messages safely
- kill a service mid-flow
- retry messages aggressively
- observe recovery and eventual consistency

## ARC 3 Evaluation Checklist
- [ ] I understand at-least-once delivery
- [ ] I do not assume message order
- [ ] I safely handle duplicates
- [ ] I enforce idempotency at the correct boundary
- [ ] I understand why exactly-once is rare
- [ ] I can explain compensation logic
- [ ] I can simulate crashes mid-flow
- [ ] I understand recovery behavior

### Pass Criteria
> I design systems assuming failure, duplication, and delay.

---

# ARC 4 — Observability, Security & Production Ownership
**Duration:** ~4–6 weeks  
**Mindset Shift:** “Can I own this at 3am?”

## Category Focus
- observability
- authentication & authorization
- deployment behavior
- reliability and failure modes

## Toy Project — Production-Ready Backend
Add to previous projects:
- structured logging
- correlation IDs
- metrics
- OAuth2 authentication
- graceful shutdown
- health checks

## ARC 4 Internal Phases

### Phase 1 — Observability
**Goal:** Debug production with signals, not hope.

#### Must Know
- logs vs metrics vs traces
- latency percentiles
- metric cardinality
- correlation IDs

---

### Phase 2 — Security
**Goal:** Understand attack paths, not just libraries.

#### Must Know
- OAuth2 flows
- token lifecycle
- CSRF vs CORS
- why JWT logout is hard

---

### Phase 3 — Deployment & Failure Engineering
**Goal:** Predict operational failure before it surprises you.

#### Must Know
- graceful shutdown
- liveness vs readiness
- rolling deployments
- retry storms
- cascading failures
- circuit breaker purpose

## ARC 4 Evaluation Checklist

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
- [ ] I understand token lifecycle and rotation
- [ ] I know why JWT logout is hard
- [ ] I clearly distinguish CSRF vs CORS

### Deployment & Reliability
- [ ] I understand graceful shutdown
- [ ] I distinguish liveness vs readiness
- [ ] I understand retry storms and cascading failures

### Pass Criteria
> I can explain how my system fails, how I detect it, and how I recover.

---

# Recommended Immediate Next Steps

## Finish ARC 1 Cleanly
Your next best sequence is:
1. **Consolidate concurrency strategies into one comparison note**  
   - pessimistic locking  
   - optimistic locking  
   - atomic update  
   - Redis lock  
   For each: correctness, contention behavior, operational burden, typical failure.

2. **Do an index-focused mini-chapter**  
   - composite indexes  
   - selectivity  
   - covering indexes  
   - planner decisions  
   - why a valid index may still be ignored

3. **Close transaction boundary gaps**  
   - self-invocation  
   - propagation  
   - rollback rules  
   - transaction boundary placement in service layer

4. **Run one final reservation-system evaluation**  
   - concurrent requests  
   - retry scenarios  
   - deadlock or lock-wait scenario  
   - explain final chosen strategy

## Then Move to ARC 2
Only move when you can confidently answer:
- Why is atomic update sometimes enough and sometimes not?
- When is optimistic locking better than pessimistic locking?
- Why can a correct transaction annotation still fail in Spring?
- Why is a composite index not just “more columns = better”?

---

# Final Self-Assessment

Answer honestly:
- [ ] I explain **why**, not just **how**
- [ ] I know my assumptions
- [ ] I understand trade-offs, not just best practices
- [ ] I am comfortable owning failures

If all are checked:
> You are operating at solid **mid-level → senior-ready** backend growth trajectory.

---

# Resources

## Databases
- _Designing Data-Intensive Applications_ — Martin Kleppmann  
  → mandatory for consistency, concurrency, distributed thinking
- _PostgreSQL Internals_ — Hironobu Suzuki
- PostgreSQL documentation:
  - MVCC
  - EXPLAIN
  - locking behavior

## Transactions & Concurrency
- _Java Concurrency in Practice_
- Spring documentation:
  - transaction management
- MySQL InnoDB locking documentation

## Backend Architecture
- _Clean Architecture_ — Robert C. Martin
- _Domain-Driven Design Distilled_
- Hexagonal Architecture — Alistair Cockburn

## Distributed Systems
- _Designing Data-Intensive Applications_
- Kafka documentation (concepts only)
- Martin Fowler on event-driven architecture

## Observability
- Google SRE Book
- OpenTelemetry docs (concepts only)
- Prometheus metric types documentation

## Security
- OAuth 2.0 RFC (flows only)
- OWASP Top 10
- Spring Security architecture docs

## Deployment & Reliability
- Google SRE Book
- Netflix engineering / resilience articles
- AWS Well-Architected Framework (Reliability)

---

# How to Use AI While Studying
- ask AI to explain trade-offs
- ask AI to generate failure cases
- ask AI to review design choices
- do **not** outsource:
  - transaction logic
  - security decisions
  - concurrency reasoning

---

# Closing Principle

> Depth creates seniority, not elapsed time.  
> Correctness under pressure is the first real backend milestone.
