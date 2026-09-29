---
layout: page
title: Database
permalink: /database/
---

Notes on database behavior, built from experiments with a movie booking system.

## Transactions, MVCC, and locking

The first part of my database study: understanding what concurrent transactions
can see before deciding how to protect a reservation.

{% assign database_posts = site.tags.database | sort: 'date' | reverse %}
<ul class="post-card-grid">
{% for post in database_posts %}
{% include post-card.html post=post %}
{% endfor %}
</ul>
