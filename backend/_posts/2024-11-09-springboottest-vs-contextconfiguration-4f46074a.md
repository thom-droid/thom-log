---
layout: post
title: "@SpringBootTest vs. @ContextConfiguration"
date: 2024-11-09 09:08:47 +0000
categories: [backend]
tags: [backend, spring]
permalink: /backend/springboottest-vs-contextconfiguration-4f46074a/
source_note: "@SpringBootTest vs. @ContextConfiguration.md"
---

[Backend]({{ '/backend/' | relative_url }}) / Study archive

`@SpringBootTest`가 스프링 풀 컨텍스트를 로딩하는 건 아는 내용.

`@ContextConfiguration` 은 특정한 빈만 설정하여 컨텍스트를 설정하는 어노테이션.

# 차이

`@SpringBootTest(classes = {...})` 와 `@ContextConfiguration(classes = {...})` 의 차이는 어떻게 되는걸까

| Aspect                       | `@SpringBootTest`                                             | `@ContextConfiguration`                             |
| ---------------------------- | ------------------------------------------------------------- | --------------------------------------------------- |
| **Scope**<br>                | Full Spring Boot context or specific Spring Boot classes<br>  | Basic Spring context, not Boot-specific<br>         |
| **Use Case**<br>             | Integration tests requiring Spring Boot features<br>          | Unit/component tests or basic Spring contexts<br>   |
| **Embedded Server**<br>      | Can start an embedded web server<br>                          | Cannot start an embedded server<br>                 |
| **Properties Loading**<br>   | Loads `application.properties`/`.yml` automatically<br>       | Does not load application properties by default<br> |
| **Test Complexity**<br>      | Suitable for more complex integration scenarios<br>           | Suitable for simpler unit or component tests<br>    |
| **Spring Boot Features**<br> | Supports features like auto-configuration, profiles, etc.<br> | No Spring Boot-specific features<br>                |

# 문제 상황

풀 컨텍스트 로딩을 줄이고자 각 도메인별로 필요한 컨텍스트를 분리해보고자 했다. Business 테스트에 필요한 빈들만 설정하는 컨피그 클래스를 만들었다.

```java
package com.millktea.api.config.domain.business;  
  
import org.springframework.boot.test.context.TestConfiguration;  
import org.springframework.context.annotation.ComponentScan;  
  
@TestConfiguration  
@ComponentScan(basePackages = {"com.millktea.api.domain.business", "com.millktea.core.domain.business"})  
public class BusinessTestConfig {  
}
```


그런데 `@ContextConfiguration` 은 정말 필요한 빈만 설정하여 컨텍스트를 만든다. 따라서 아래의 코드는 `BusinessRepository` 를 빈으로 주입해줄 수 없기 때문에 실패한다.

```java
@ContextConfiguration(classes = BusinessTestConfig.class)  
class BusinessServiceImplTest {  
  
    @MockBean  
    BusinessRepository businessRepository;   // null
  
    @MockBean  
    FileStorageService fileStorageService;  
  
    @Autowired  
    BusinessService businessService;  
  
    @Autowired  
    BusinessMapper businessMapper;
```

# 수정

아래와 같이 수정하면 api, core 모듈 내의 business 패키지를 스캔하여 컨텍스트가 세팅된다.

```java
@SpringBootTest(classes = BusinessTestConfig.class)  
class BusinessServiceImplTest {  
  
    @MockBean  
    BusinessRepository businessRepository;  
  
    @MockBean  
    FileStorageService fileStorageService;  
  
    @Autowired  
    BusinessService businessService;  
  
    @Autowired  
    BusinessMapper businessMapper;
```


# context 설정과 모듈 간 설정 문제

## core module
`@SpringBootTest`는 `@Configuration`을 통해 빈들을 설정하는데, 보통 메인 클래스에 `@SpringBootApplication`가 달려 있고 해당 어노테이션 내부에는 `@Configuration`이 포함되어 있기 때문에 간단히 설정이 된다.

그런데 현재 core 모듈은 라이브러리로서 필요한 엔티티와 db설정 등만을 제공할 목적으로 만들어진 모듈이므로 `@SpringBootApplication` 및 컨피그 클래스, 메인 클래스를 제거한 상태이다. 따라서 해당 모듈에서 테스트를 할 때 `@SpringBootTest`를 사용하면 컨피그 파일들을 찾을 수 없어 컨텍스트가 제대로 로드되지 않는 상태가 된다.

그래서 테스트 간에 컨텍스트를 설정할 때 `@Configuration`을 하나 포함한 클래스를 넣어주면 된다. 메인 클래스를 만들어도 되겠지만, 그러면 빌드하여 패키징할 때 설정을 해주어야 할 것 같아서 제외했다.

아래와 같이 설정을 하였다.

```java
package com.millktea.core.config.database.config;  
  
import org.springframework.boot.test.context.TestConfiguration;  
import org.springframework.context.annotation.ComponentScan;  
import org.springframework.context.annotation.Configuration;  
  
@Configuration  
@ComponentScan(basePackages = {"com.millktea.core.domain.business"})  
public class BusinessTestConfig {  
}
```

따라서 아래와 같이 설정한 테스트는 통과하게 된다.

```java
package com.millktea.core.config.database;  
  
import com.millktea.core.config.database.config.BusinessTestConfig;  
import com.millktea.core.config.database.config.DatabaseTestConfiguration;  
import org.junit.jupiter.api.Test;  
import org.springframework.beans.factory.annotation.Autowired;  
import org.springframework.boot.SpringBootConfiguration;  
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;  
import org.springframework.boot.test.context.SpringBootTest;  
import org.springframework.context.ApplicationContext;  
import org.springframework.core.env.Environment;  
import org.springframework.test.context.ContextConfiguration;  
import org.springframework.test.context.TestPropertySource;  
  
import javax.sql.DataSource;  
  
import static org.junit.jupiter.api.Assertions.assertNotNull;  
import static org.junit.jupiter.api.Assertions.fail;  
  
@SpringBootTest(classes =  {DatabaseTestConfiguration.class, BusinessTestConfig.class})  
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)  
class DatabaseConfigTest {  
  
    @Autowired  
    private ApplicationContext ctx;  
  
    @Autowired  
    DataSource dataSource;  
  
    @Test  
    void contextLoads() {  
        assertNotNull(ctx);  
    }  
  
    @Test  
    void dataSourceLoads() {  
        assertNotNull(dataSource);  
    }  
  
    @Test  
    void databaseConnection() {  
        try {  
            dataSource.getConnection();  
            System.out.println("dataSource = " + dataSource.getConnection().getMetaData().getDriverName());  
        } catch (Exception e) {  
            fail("Database connection failed");  
        }  
    }  
  
}
```


# `@ContextConfiguration` 을 사용할 때

필요한 컨텍스트만 설정하여 테스트할 수 있기 때문에 풀 컨텍스트를 로딩하는 `@SpringBootTest`보다 오버헤드가 적다. 하지만 정확히 컨텍스트에 필요한 빈들을 모르면 원하는 대로 동작하지 않게 된다. 또한 properties 파일들도 로드되지 않기 때문에 `@TestSourceProperty`로 추가적으로 설정해주어야 한다.

특히 둘 이상의 레이어가 포함되는 슬라이스 테스트 시에는 의존성 관계가 커지므로 테스트 설정이 복잡해질 수 있으므로 `@SpringBootTest`를 사용하는 것이 덜 골치아플 것 같다.
