---
layout: post
title:  "Kubernetes · Docker 네트워크 정리 — dev MySQL 접속을 계기로"
date:   2026-09-28 14:00:00 +0900
categories: [devops, kubernetes, docker]
---

dev 서버의 MySQL 에 접속하려다 막혀서, 그 과정에서 헷갈렸던 Kubernetes · Docker 네트워크 개념을 정리했다. 잘못 알고 있던 것, 부족하게 알고 있던 것, 새로 알게 된 것 순서로 적는다.

예시 프로젝트는 dev 환경을 Windows 의 Rancher Desktop(Kubernetes)으로 띄우고, 로컬 개발은 docker compose 로 한다. 배포 스크립트 `dev.sh` 가 `dev.env` 의 값을 매니페스트 템플릿(`.tpl`)에 채워 넣어 클러스터에 적용하는 구조다. 글에서는 서버 IP 를 `<DEV_IP>`, 앱 이름을 `myapp` 으로 바꿔 적었다.

---

## 1. 잘못 알고 있었던 것

### ❌ "K8s 가 도는 PC 에서는 `myapp-mysql:3307` 로 접속할 수 있다"
- `myapp-mysql` 은 **클러스터 내부 DNS 이름**이라 같은 클러스터 안의 **Pod 끼리만** 이름이 풀린다.
- K8s 를 돌리는 개발 PC 라도 Windows 호스트는 **클러스터 밖**이다. 그래서 호스트에서는 이 이름으로 접속할 수 없다.
- 호스트에서 붙는 방법:
  - NodePort 로 접속: Rancher Desktop 이면 `[::1]:30307`
  - `kubectl port-forward svc/myapp-mysql 3307:3307 -n myapp-dev` 를 띄운 뒤 `localhost:3307`
- `dev.env` 의 `DB_HOST=myapp-mysql` 은 **앱 Pod 용 설정**이다.

### ❌ "`myapp-mysql` 은 Pod 이름이다"
- **Service 이름**이다. Pod 앞에 붙는 고정 주소라서 Pod 가 재시작돼 IP 가 바뀌어도 같은 이름으로 연결된다.
- Pod 는 StatefulSet `myapp-mysql` 이 띄운다.

### ❌ "`DEV_MYSQL_NODEPORT` 는 쿠버네티스 프로퍼티다"
- 이 프로젝트의 `dev.env` **변수**다. `dev.sh` 가 매니페스트 템플릿의 `nodePort: ${DEV_MYSQL_NODEPORT}` 자리에 값(30307)을 채워 넣고 K8s 에 적용한다.
- K8s 입장에서 실제 설정은 Service 의 **`nodePort` 필드**다.

### ❌ "Docker(compose)로 띄우면 localhost 에 포트가 원래 열린다"
- 컨테이너는 기본적으로 격리돼 있다. localhost 에서 보이는 건 compose 파일에 **`ports:`** 가 적혀 있기 때문이다(= `docker run -p`).
- `ports:` 가 없으면 다른 컨테이너에서는 보이지만 호스트 localhost 에서는 안 보인다.

---

## 2. 부족하게 알고 있었던 것

### Service 가 두 개다
NodePort 로 들어온 요청이 `myapp-mysql:3307` 이라는 주소로 넘어가는 게 아니다. **별도 Service 가 같은 Pod 의 3307 로 각각 연결**한다.

```
외부 PC ─▶ <DEV_IP>:30307   ─▶ Service myapp-mysql-nodeport (type: NodePort) ─▶ MySQL Pod :3307
앱 Pod  ─▶ myapp-mysql:3307 ─▶ Service myapp-mysql          (ClusterIP)      ─▶ MySQL Pod :3307
```

### 포트 세 개의 역할 (dev MySQL)

| 포트 | 변수 | 누가 쓰나 |
|---|---|---|
| `3307` | `DB_PORT` | 클러스터 **안**의 앱 Pod (`myapp-mysql:3307`) |
| `30307` | `DEV_MYSQL_NODEPORT` | 클러스터 **밖**에서 `<DEV_IP>:30307` |
| `3308` | `DB_LAN_PORT` | 30307 앞에 Windows portproxy 로 붙이는 선택용 별칭 (`dev.sh expose --db-lan` 을 했을 때만) |

앱도 같은 방식이다. `APP_NODEPORT=30081` 앞에 portproxy `8082` 를 붙여 `http://<DEV_IP>:8082` 로 연다.

### Rancher Desktop 특이사항
NodePort 가 `[::1]`(IPv6 localhost)에만 응답한다. 그래서 LAN 에서 접근하려면 Windows portproxy(v4tov6)로 LAN IP 의 포트를 `[::1]` 로 이어 줘야 한다. 이 프로젝트에서는 `dev.sh` 가 이 작업을 해 준다.

---

## 3. 이번에 알게 된 것

### NodePort 란
- 클러스터 안의 서비스를 **노드(서버 머신)의 포트**에 열어서 밖에서 접속할 수 있게 하는 Service 타입이다.
- 기본 포트 범위는 **30000–32767**이다. 그래서 30307 · 30081 같은 번호가 나온다.

| Service 타입 | 접근 범위 |
|---|---|
| ClusterIP (기본) | 클러스터 내부에서만 |
| NodePort | 노드 IP + 30000번대 포트로 외부 접근. 사내 dev 에 흔히 쓴다 |
| LoadBalancer | 클라우드 로드밸런서가 외부 IP 를 붙여 준다. 운영용 |

**Ingress 는 Service 타입이 아니다.** 별도 리소스로, 도메인 · 경로 기준으로 HTTP(S)(80/443) 요청을 받아 뒤의 Service(보통 ClusterIP)로 넘겨 준다. 클러스터에 ingress controller 가 있어야 동작한다. 이 프로젝트 dev 는 `SKIP_INGRESS=true` 로 Ingress 없이 NodePort 만 쓴다.

### Docker ↔ Kubernetes 개념 대응

| 하는 일 | Docker (compose) | Kubernetes |
|---|---|---|
| 컨테이너끼리 이름으로 부르기 | compose 서비스 이름 (`db:3306`) — 같은 네트워크 안에서만 | Service 이름 (`myapp-mysql:3307`) — 클러스터 안에서만 |
| 호스트 밖으로 열기 | `ports:` / `-p 호스트:컨테이너` | `type: NodePort` / `kubectl port-forward` |
| 포트 번호 | 아무 포트나 가능 (3306 등) | NodePort 는 30000–32767 |
| 컨테이너 앞의 고정 주소 | 내장 DNS 가 서비스 이름을 계속 풀어 준다. 다만 고정 가상 IP 나 로드밸런싱 계층은 없다 (여러 개면 DNS 가 IP 를 여러 개 돌려줄 뿐) | Service 가 고정 가상 IP(ClusterIP)와 로드밸런싱을 제공한다. Pod 재시작 · 여러 개 전제 |

> **Docker 의 `-p` ≈ K8s 의 NodePort.** 둘 다 "격리된 컨테이너 포트를 호스트 밖으로 여는 장치"다.

compose 서비스 이름(`db`)도 K8s 와 같다. 다른 컨테이너 안에서만 풀리고 호스트에서는 안 된다.

### compose 포트 관련 설정

| 설정 | 동작 |
|---|---|
| `ports: - "13306:3306"` | 호스트 포트를 연다 → localhost 로 접속 가능 |
| `expose: - "3306"` | **호스트에 안 연다.** 컨테이너끼리 쓴다는 표시일 뿐이다 |
| `network_mode: host` | 호스트 네트워크를 그대로 쓴다(Linux). 격리가 없어진다 |

로컬(`docker-compose.local.yml`) 예:
```yaml
db:
  container_name: myapp-local-mysql
  ports:
    - "${LOCAL_DB_PORT:-13306}:3306"      # 로컬 PC → localhost:13306
app:
  environment:
    DB_URL: jdbc:mysql://db:3306/myapp...  # 컨테이너끼리는 서비스이름:컨테이너포트
  ports:
    - "${LOCAL_APP_PORT:-18082}:8080"
```

### 보안 주의: `ports:` 는 기본으로 모든 인터페이스에 열린다
- `"13306:3306"` = `0.0.0.0:13306` 이라서 **같은 LAN 의 다른 PC 에서도** 접근될 수 있다.
- Linux 에서는 Docker 가 iptables 규칙을 직접 추가하기 때문에, ufw · firewalld 로 막아 둬도 **그대로 열려 있는 경우가 많다.** 방화벽보다 바인딩 주소로 막는 게 확실하다.
- 로컬 전용으로 쓰려면 `"127.0.0.1:13306:3306"` 으로 적는다.
- K8s 의 NodePort 도 기본 설정에서는 노드의 모든 인터페이스에 열린다.

### Docker Desktop / Rancher Desktop 이 localhost 로 보이는 이유
Windows · Mac 에서는 컨테이너가 Linux VM 안에서 돈다. 이 도구들이 VM 의 포트를 호스트 localhost 로 자동 중계해 주기 때문에 `ports:` 만 적어도 바로 localhost 로 보인다.

---

## 4. 원격 MySQL 에 붙을 때 쓴 팁

```bash
# PC 에 mysql 클라이언트가 없으면, 로컬에 떠 있는 MySQL 컨테이너의 클라이언트로 원격에 붙을 수 있다
docker exec -it myapp-local-mysql mysql --default-character-set=utf8mb4 \
  -h <DEV_IP> -P 30307 -u<USER> -p myapp
```

- `--default-character-set=utf8mb4` 를 빼면 한글이 깨진다.
- `-p` 뒤를 띄어 쓰면 비밀번호는 프롬프트로 묻고, 뒤의 `myapp` 은 접속할 DB 이름이 된다.
- 안 붙으면 포트부터 확인한다: `bash -c 'cat </dev/null >/dev/tcp/<DEV_IP>/30307'` (`/dev/tcp` 는 bash 기능이라 `bash -c` 로 감싼다)

---

## 정리
- Service 이름은 **클러스터 안에서만**, compose 서비스 이름은 **같은 네트워크 안에서만** 풀린다. 호스트는 둘 다 "밖"이다.
- 밖에서 붙으려면 Docker 는 `ports:`(`-p`), K8s 는 NodePort 나 `port-forward` 로 포트를 열어야 한다.
- 포트를 열 때는 어느 인터페이스에 열리는지도 같이 확인한다.
