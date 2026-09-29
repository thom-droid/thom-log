---
layout: post
title: "Throwing interface"
date: 2024-12-04 01:41:48 +0000
categories: [backend]
tags: [backend]
permalink: /backend/throwing-interface-586884a1/
source_note: "Throwing interface.md"
---

[Backend]({{ '/backend/' | relative_url }}) / Study archive
# 문제 상황
BiFunction과 같은 functional interface를 사용할 때 checked exception 처리를 직접 코드 상으로 해줄 수 없기 때문에 래핑하여 처리해주는 인터페이스를 따로 만들어 쓴다.

```java
public class TiberoDataTypeConverter extends AbstractDataTypeConverter {  
  
    public TiberoDataTypeConverter(String databaseProductName, MetaColumn metaColumn) throws IOException {  
        super(databaseProductName, metaColumn);  
    }
```

```java
private static final Map<String, BiFunction<String, MetaColumn, DataTypeConverter>> CONVERTER_MAP = new HashMap<>();

public void configureMap() {
	CONVERTER_MAP.put("TIBERO", TiberoDataTypeConverter::new); // 컴파일 오류 :  Unhandled exception: java. io. IOException
}
```

# 해결

## 인터페이스 래핑

위의 문제를 해결하려면 아래처럼 래핑해주는 인터페이스나 클래스를 만들어서 처리할 수 있다.

```java 
@FunctionalInterface  
public interface ThrowingBiFunction<T, U, R>  {  
    R apply(T t, U u) throws IOException;  
}
```


```java
CONVERTER_MAP.put("TIBERO", (databaseName, metaColumn) -> new TiberoDataTypeConverter(databaseName, metaColumn));
```

```java
CONVERTER_MAP.put("TIBERO", TiberoDataTypeConverter::new);
```

위 코드는 아래와 같고, 이것을 `ThrowingBiFunction`에서 해당 메서드를 호출하는 메서드에게 예외를 위임하므로 컴파일 에러가 해결된다. 다만 예외처리가 중요한 메서드라면 예외를 처리할 위치를 잘 잡아서 해결해야 할 것이다.


## 예외 직접 처리

- try-catch 문으로 직접 처리할 수도 있다
- 처리할 코드의 수가 적다면 괜찮지만, 여러 인스턴스를 세팅하는 코드이므로 try-catch가 중복으로 생긴다.

```java
private static final Map<String, BiFunction<String, MetaColumn, DataTypeConverter>> CONVERTER_MAP = new HashMap<>();

public void configureMap() {
	CONVERTER_MAP.put("TIBERO", 
	(databaseName, metaColumn) ->
		try {
			return new TiberoDataTypeConverter(databaseName, metaColumn));
		} catch (Excetpion e){
			// handle exception
		}
}
```
