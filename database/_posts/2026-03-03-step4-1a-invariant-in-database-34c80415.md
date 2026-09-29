---
layout: post
title: "Step4 - 1a. Invariant In Database"
date: 2026-03-03 13:29:05 +0000
categories: [database]
tags: [database, booking-system, concurrency, invariants]
permalink: /database/step4-1a-invariant-in-database-34c80415/
source_note: "study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/Step4 - 1a. Invariant In Database.md"
---

[Database]({{ '/database/' | relative_url }}) / Study archive
# **1️⃣ Invariant(불변 조건)란 무엇인가?**


**Invariant = 시스템이 항상 지켜야 하는 조건**

예시:
- 한 좌석은 동시에 한 명만 예약 가능
- 재고(stock)는 0보다 작아질 수 없다    
- 한 이메일은 유저 테이블에서 유일해야 한다    
- 주문 상태는 SHIPPED 이후 CANCEL 될 수 없다
  

이건 “코드 로직”이 아니라,

**데이터 상태가 항상 만족해야 하는 규칙**이다.

---

# **2️⃣ 그럼 “DB가 invariant를 강제한다”는 게 무슨 뜻인가?**


의미는 이것이다:

> 애플리케이션이 실수해도,
> 동시에 여러 요청이 와도,
> DB 레벨에서 조건이 깨지지 않도록 보장한다.


즉,
애플리케이션이 체크하는 게 아니라,
**DB가 조건을 만족할 때만 상태 변경을 허용한다**는 뜻이다.


---

# **3️⃣ DB에서 invariant가 강제되는 위치**

DB에서 invariant를 강제하는 방법은 여러 계층이 있다.

---

## **① WHERE 조건 + 원자적 UPDATE**  

예시:

```sql
UPDATE seat
SET reserved = true
WHERE id = 1 AND reserved = false;
```

이 경우 invariant는:

> “reserved=false 인 경우에만 true로 바뀔 수 있다”


이 invariant는 어디에서 강제되나?

- DB 엔진이 UPDATE를 실행할 때
- row lock을 잡고
- 현재 커밋된 값이 조건을 만족하는지 검사하고
- 조건이 맞을 때만 변경  

즉,
> **엔진 내부에서 check + act가 하나의 원자적 연산으로 처리됨**


---
## **② UNIQUE 제약조건**

```sql
ALTER TABLE user ADD CONSTRAINT uq_email UNIQUE(email);
```
Invariant:


> 이메일은 중복될 수 없다.

이건 애플리케이션이 체크하는 게 아니라

- 인덱스 레벨에서 중복 insert를 차단
- 동시에 두 요청이 들어와도 한 쪽은 실패

여기서는 **인덱스 구조(B+Tree)** 가 invariant를 강제한다.

---
## **③ CHECK 제약조건**
```sql
ALTER TABLE product ADD CONSTRAINT chk_stock CHECK (stock >= 0);
```

Invariant:


> 재고는 음수가 될 수 없다.
애플리케이션이 실수해도 DB가 거부한다.

---
## **④ FOREIGN KEY**

```sql
ALTER TABLE order
ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES user(id);
```

Invariant:
> 존재하지 않는 유저의 주문은 불가능

DB가 참조 무결성을 강제한다.


---
## **⑤ 트랜잭션 + 락 + MVCC**
조금 더 깊은 레벨에서:

- 동일 row에 대한 동시 update는 row-level lock이 보장
- snapshot isolation이 visibility를 통제
- write-write conflict가 직렬화 보장

즉,

> 엔진의 동시성 제어 시스템 자체가 invariant를 지키는 장치

---
# **더 깊은 개념: Invariant는 결국 “상태 전이 규칙”**

좌석 예약을 예로 들면:

```sql
false → true (가능)
true → true (불가)
```

이걸 애플리케이션이 판단하면
- 여러 트랜잭션이 동시에 판단 가능

DB가 판단하면

- 하나만 성공
    
- 나머지는 0 row affected
    


즉,

> Invariant는 상태 전이를 통제하는 규칙이며

> DB는 상태 전이를 원자적으로 처리할 수 있다.\

---
# **한 문장으로 정리**


“DB가 invariant를 강제한다”는 말은:

> 데이터의 상태 변경이 일어나는 그 순간,
> 그 조건을 DB 엔진이 원자적으로 검사하고 허용/거부한다는 뜻이다.


---
# **왜 이게 senior-level 사고인가?**

Junior 사고:
 “내 코드가 체크했으니 안전하다.”

Mid 사고:
“트랜잭션 있으니까 안전하다.”

Senior 사고: **“이 invariant는 어느 계층이 책임지는가?”**


> **Does the database detect a conflict that prevents two transactions from both succeeding?**
