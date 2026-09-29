---
layout: post
title: "circular dependency 를 피하면서 유연한 구조"
date: 2024-11-19 11:21:29 +0000
categories: [backend]
tags: [backend]
permalink: /backend/circular-dependency-6bca2a2c/
source_note: "circular dependency 를 피하면서 유연한 구조.md"
---

[Backend]({{ '/backend/' | relative_url }}) / Study archive

# 문제 상황
- Business : User = 1 : N 구조
- 각 서비스 레이어에서 서로가 빈으로 의존성을 갖는 상황 -> circular depdency 이슈
- BusinessService <- UserRepository 와 같이 각 서비스에서 repository로 의존성을 주입하는 것은 지양 -> repository 레이어는 해당 도메인에 맞는 서비스에 종속되어야 함

# 생각해본 옵션

##  interface segregation
- 다른 빈에서도 쉽게 의존성을 주입할 수 있도록 필요한 기능만 따로 인터페이스로 분리
```java
@Service
public class UserInfoService {
    private final UserRepository userRepository;

    public UserInfoService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User getUserById(Long userId) {
        return userRepository.findById(userId)
            .orElseThrow(() -> new EntityNotFoundException("User not found"));
    }
}

@Service
public class BusinessInfoService {
    private final BusinessRepository businessRepository;

    public BusinessInfoService(BusinessRepository businessRepository) {
        this.businessRepository = businessRepository;
    }

    public Business getBusinessById(Long businessId) {
        return businessRepository.findById(businessId)
            .orElseThrow(() -> new EntityNotFoundException("Business not found"));
    }
}

```

필요한 곳에서 의존성을 주입받아 사용
```java
@Service
public class UserService {
    private final UserInfoService userInfoService;
    private final BusinessInfoService businessInfoService;

    public UserService(UserInfoService userInfoService, BusinessInfoService businessInfoService) {
        this.userInfoService = userInfoService;
        this.businessInfoService = businessInfoService;
    }

    public void performUserBusinessOperation(Long userId, Long businessId) {
        User user = userInfoService.getUserById(userId);
        Business business = businessInfoService.getBusinessById(businessId);
        // Perform business logic here
    }
}
```
