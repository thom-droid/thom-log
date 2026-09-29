---
layout: post
title: "API design core concepts"
date: 2026-04-26 07:33:18 +0000
categories: [backend]
tags: [backend, api-design]
permalink: /backend/api-design-core-concepts-14e9b236/
source_note: "study plan/Arc2 - API Design/API design core concepts.md"
---

[Backend]({{ '/backend/' | relative_url }}) / Study archive

## **Core concepts in plain language**

  

### **1. Business logic should not depend directly on frameworks**

  

Your core rule should still make sense even if:

- HTTP changes
    
- DB changes
    
- Spring changes
    

  

### **2. Controller is not business logic**

  

Controller handles:

- HTTP
    
- request/response mapping
    

  

It should not decide:

- state transitions
    
- totals
    
- stock rules
    
- retry rules
    

  

### **3. Application service orchestrates**

  

It says:

- load this
    
- call domain behavior
    
- save this
    
- return result
    

  

### **4. Domain expresses meaning**

  

Things like:

- confirm()
    
- cancel()
    
- allowed/disallowed transition
    

  

These belong closer to business meaning than to controller/repository code.

  

### **5. Query side and command side often look different**

  

This is the biggest practical lesson for you right now.

- **Command side** benefits from domain-centered structure
    
- **Query side** often benefits from efficient projections and simpler read shaping
    

  

You already saw that with OrderStore vs OrderQueryService.
