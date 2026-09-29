---
layout: post
title: "Step3 - Introduce Transaction Boundaries"
date: 2026-03-02 06:49:55 +0000
categories: [database]
tags: [database, booking-system, concurrency, transactions]
permalink: /database/step3-introduce-transaction-boundaries-c1f3eb0e/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Step3 - Introduce Transaction Boundaries.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive

# Where to set transaction boundaries ; Controller vs Service


```java
@PostMapping("/transaction-on-controller/{seatId}")  
@ResponseStatus(HttpStatus.CREATED)  
@Transactional  
public ResponseEntity<?> testTransactionBoundary(@PathVariable Long seatId, String title) {  
  
    Movie movie = new Movie();  
    movie.setTitle(title);  
  
    movieService.insertMovie(movie);  
    boolean reserved;  
  
    // 여기서 비즈니스 예외를 처리하면 위 movieSerivce.insertMovie와의 원자성이 깨지게 된다.  
    try {  
        reserved = seatService.reserveUnsafeWithoutTransactional(seatId);  
    } catch (IllegalStateException ex) {  
        reserved = false;  
    }  
    List<Movie> allMovies = movieService.getAllMovies();  
  
    Map<String, Object> test = Map.of("test", reserved, "movies", allMovies);  
    return ResponseEntity.ok().body(test);  
}
```

- When the first transaction `movieService.insertMovie(movie)` succeeds while the next one `seatService.reserve..` failing, the next one is not rolled back which breaks atomicity of the transaction (when fails, all should be failed).
- And controller should be in charge of handling request like parameters, and service being in charge of business logic.

# Transaction propagation ; REQUIRED vs. REQUIRES_NEW

inner:
```java
@Service
public class InnerService {

    private final AuditService audit;

    public InnerService(AuditService audit) { this.audit = audit; }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void innerNewTx() {
        audit.log("inner REQUIRES_NEW");
    }

}
```

outer:
```java
@Service
public class OuterService {
    private final AuditService audit;
    private final InnerService inner;
    public OuterService(AuditService audit, InnerService inner) {
        this.audit = audit;
        this.inner = inner;
    }
    
    @Transactional
    public void outerTx_thenFail() {
        audit.log("outer before inner");
        inner.innerNewTx();
        audit.log("outer after inner");
        throw new IllegalStateException("outer boom"); // it does not rollback inner.innerNewTx();
    }
}
```


# When @Transactional does not work; Self-invocation

- @Transactional is applied by a **proxy**.
- If a method calls another method **inside the same class** (via this.inner()), the proxy is bypassed and the annotation may be ignored.

```java
@Service
public class SeatService {
    // ... repositories injected
    public void outerCall(Long seatId) {
        innerTx(seatId); // self-invocation: bypasses proxy
    }

    @Transactional
    public void innerTx(Long seatId) {
        Seat seat = seatRepository.findById(seatId)
                .orElseThrow(NoSuchElementException::new);

        seat.setReserved(true);
        seatRepository.save(seat);

        // Force rollback if transaction is active
        throw new RuntimeException("boom");

    }

}
```

# Answer these, briefly:

1. Which exception type rolled back by default?
2. What happened when you caught the exception?
3. In the propagation test, which logs remained after outer failure and why?

---
1. Spring transaction rolls back unchecked exception by default unless specifically configured. Given any exceptions configured, exceptions including subclasses can be target of rollback.

2. Exceptions that are not thrown outside the transaction method boundary are considered not having caused exception; transactions are not rolled back except exceptions that mark the transaction rollback-only; hibernate/DB-specific exceptions like ConstraintViolationException or DataIntegrityException for example. 

3. InnerService's logging transaction only remains because it starts a new transaction which is separate from the ongoing transaction.
