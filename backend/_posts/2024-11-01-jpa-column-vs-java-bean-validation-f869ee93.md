---
layout: post
title: "JPA @Column vs. Java Bean Validation"
date: 2024-11-01 11:25:59 +0000
categories: [backend]
tags: [backend, jpa]
permalink: /backend/jpa-column-vs-java-bean-validation-f869ee93/
source_note: "JPA @Column vs. Java Bean Validation.md"
---

[Backend]({{ '/backend/' | relative_url }}) / Study archive


### 1. **Purpose and Functionality**

- **`@Column` (JPA Annotation):**
    
    - Specifies the mapping between the entity field and the database column.
    - Allows setting column properties, like `nullable`, `length`, and `unique`, that control the **database schema**.
    - For instance, `@Column(nullable = false, length = 50)` tells the database to enforce non-null and maximum character length, but it does not provide any runtime validation when handling Java objects.
- **Validation Annotations (Bean Validation):**
    
    - Used to **validate data at runtime** against defined constraints.
    - Common annotations include `@NotNull`, `@Size`, `@Min`, `@Max`, etc., and are primarily used to enforce constraints when the object is created or modified in your application.
    - These annotations work with the validation framework, like Jakarta Bean Validation (JSR 380), to perform validation checks before persisting data. This is useful for ensuring data correctness **before interacting with the database**.

### 2. **Example Comparison**

Consider the following example where both `@Column` and validation annotations are used for a `String` field:

java

``` java

@Entity 
public class User {          
	// Using only @Column for database-level constraints     
	@Column(nullable = false, length = 50)     
	private String username;          // Using validation annotations for runtime validation     
	@NotNull     
	@Size(max = 50)     
	private String email;          // Using both together     
	
	@Column(nullable = false, length = 50)     
	@NotNull     
	@Size(max = 50)     
	private String password;          // Getters and setters 

}
```

- For `username`, `@Column` sets the database constraints. This will create a column that does not allow `null` values and has a max length of 50 characters. However, no runtime validation is enforced.
- For `email`, the validation annotations will check that the value is not `null` and does not exceed 50 characters **at runtime**. However, if only `@Size` and `@NotNull` are used without `@Column`, there is no guarantee that these rules are enforced at the database level.
- For `password`, using both ensures that the **constraints are applied both at runtime and at the database level**.

### 3. **Key Differences**

|Feature|`@Column`|Validation Annotations|
|---|---|---|
|**Level**|Database constraint|Application runtime validation|
|**Scope**|Enforced by database schema|Enforced by validation framework|
|**Runtime Validation**|No|Yes|
|**Database Schema Change**|Yes (e.g., `nullable = false`)|No|
|**Purpose**|Data mapping, schema constraint|Data validation before persisting|

### 4. **When to Use Which**

- Use `@Column` when you want to define constraints directly in the database schema, such as `nullable`, `unique`, and `length`.
- Use validation annotations to ensure data correctness at the application level before persisting it, giving more immediate feedback to users.
- In cases where both application-level and database-level constraints are important, use both together.\


TL;DR 

- application runtime vs. database layer
