---
layout: post
title: "Backend Deepening Roadmap (12 Weeks)"
date: 2025-12-15 11:36:13 +0000
categories: [learning]
tags: [learning, study-plan]
permalink: /learning/backend-deepening-roadmap-12-weeks-a8689efa/
source_note: "study plan/Backend Deepening Roadmap (12 Weeks).md"
---

[Learning]({{ '/learning/' | relative_url }}) / Study archive
**Target Level:** Mid-level Web Backend Engineer  
**Focus:** Databases, Architecture, Concurrency, Reliability, Security  
**Philosophy:** Depth > Breadth, Trade-offs > Tools

---

## Week 1 — MVCC & Transaction Isolation
**Goal:** Predict data visibility under concurrency.

### Must Know
- MVCC tuple versioning
- Snapshot timing
- READ COMMITTED vs REPEATABLE READ
- Phantom reads in practice

### Checklist
- [ ] Explain how Postgres chooses visible row versions
- [ ] Demonstrate non-repeatable reads
- [ ] Explain why MVCC does not remove locks

### Interview Questions
- Why doesn’t MVCC eliminate locking?
- How does Postgres prevent dirty reads?
- What problems do long-running transactions cause?

---

## Week 2 — Indexes & Query Planner
**Goal:** Know why an index is ignored.

### Must Know
- B+Tree access patterns
- Selectivity & cardinality
- Composite index ordering
- Covering indexes

### Checklist
- [ ] Break and fix an index using EXPLAIN ANALYZE
- [ ] Explain index usage decisions line-by-line

### Interview Questions
- Why are boolean indexes often useless?
- Why does `(A, B)` not help `WHERE B = ?`?
- What makes an index covering?

---

## Week 3 — Locks & Deadlocks
**Goal:** Predict blocking behavior.

### Must Know
- Row / gap / next-key locks (MySQL)
- Deadlock detection
- Lock ordering

### Checklist
- [ ] Create and analyze a deadlock
- [ ] Identify blocking sessions

### Interview Questions
- Why are deadlocks normal?
- Why can SELECT block UPDATE?
- How does MySQL prevent phantom reads?

---

## Week 4 — Spring Transaction Boundaries
**Goal:** Control commit/rollback behavior.

### Must Know
- Proxy-based AOP
- Propagation types
- Rollback rules
- Self-invocation issue

### Checklist
- [ ] Demonstrate why self-calls break @Transactional
- [ ] Compare REQUIRED vs REQUIRES_NEW

### Interview Questions
- Why shouldn’t controllers be transactional?
- Why doesn’t @Transactional always work?

---

## Week 5 — API Design
**Goal:** Build retry-safe, scalable APIs.

### Must Know
- Idempotency
- HTTP semantics
- Cursor vs offset pagination
- Error contracts

### Checklist
- [ ] Design idempotent POST
- [ ] Implement cursor pagination

### Interview Questions
- Why is POST not idempotent?
- Why does offset pagination fail at scale?

---

## Week 6 — Backend Architecture
**Goal:** Domain-centered code.

### Must Know
- Dependency direction
- Hexagonal architecture
- Domain vs application services

### Checklist
- [ ] Remove framework dependencies from domain
- [ ] Invert infrastructure dependencies

### Interview Questions
- Why is business logic in controllers dangerous?
- What problem does hexagonal architecture solve?

---

## Week 7 — Async & Event-Driven Systems
**Goal:** Expect failures and duplicates.

### Must Know
- At-least-once delivery
- Idempotent consumers
- Event ordering

### Checklist
- [ ] Handle duplicate messages
- [ ] Implement retry-safe consumer

### Interview Questions
- Why is exactly-once rare?
- Where should idempotency be enforced?

---

## Week 8 — Stateless Systems
**Goal:** Remove hidden state.

### Must Know
- Statelessness
- Session affinity
- Correlation IDs

### Interview Questions
- Why does session-based auth not scale?
- What breaks when load balancing?

---

## Week 9 — Observability
**Goal:** Debug production issues.

### Must Know
- Logs vs metrics vs traces
- Latency percentiles
- Cardinality

### Interview Questions
- Why is average latency misleading?
- Why don’t logs scale?

---

## Week 10 — Security
**Goal:** Understand attack paths.

### Must Know
- OAuth2 flows
- Token lifecycle
- CSRF vs CORS

### Interview Questions
- Why is JWT logout hard?
- What does CSRF protect against?

---

## Week 11 — Deployment
**Goal:** Understand real deploy behavior.

### Must Know
- Graceful shutdown
- Health checks
- Rolling deployments

### Interview Questions
- Why do requests fail during deploy?
- Liveness vs readiness?

---

## Week 12 — Failure Engineering
**Goal:** Predict system failure.

### Must Know
- Partial failures
- Retry storms
- Circuit breakers

### Interview Questions
- Why is retry dangerous?
- What causes cascading failures?

---

## Final Benchmark
If you can answer these without memorization:
- You are mid-level+ backend engineer
- Ready for senior trajectory

--- 

# Resources

## **Databases**

- 📘 _Designing Data-Intensive Applications_ — Martin Kleppmann
    
    → **Mandatory** (MVCC, replication, consistency)
    
- 📘 _PostgreSQL Internals_ (Hironobu Suzuki)
    
- PostgreSQL Docs:
    
    - MVCC
        
    - EXPLAIN
        
    - Locking Behavior
        
    

---

## **Transactions & Concurrency**

- _Java Concurrency in Practice_
    
- Spring Docs:
    
    - Transaction Management
        
    
- MySQL InnoDB Locking Docs
    

---

## **Backend Architecture**

- 📘 _Clean Architecture_ — Robert C. Martin
    
- 📘 _Domain-Driven Design Distilled_
    
- Hexagonal Architecture (Alistair Cockburn article)
    

---

## **Distributed Systems**

- 📘 _Designing Data-Intensive Applications_
    
- Kafka Documentation (Concepts section only)
    
- Martin Fowler: Event-driven architecture
    

---

## **Observability**

- Google SRE Book (free online)
    
- OpenTelemetry Docs (concepts only)
    
- Prometheus “Metric Types” doc
    

---

## **Security**

- OAuth 2.0 RFC (Flows only)
    
- OWASP Top 10
    
- Spring Security Architecture Docs
    

---

## **Deployment & Reliability**

- Google SRE Book
    
- Netflix Tech Blog (Resilience, Chaos Engineering)
    
- AWS Well-Architected Framework (Reliability section)
    

---

## **How to Use AI While Studying**

- Ask AI to:
    
    - Explain trade-offs
        
    - Generate failure cases
        
    - Review designs
        
    
- Never outsource:
    
    - Transaction logic
        
    - Security decisions
        
    - Concurrency reasoning
        
    

---

## **Final Advice**

  

> **Depth creates seniority, not years.**
