---
layout: page
title: Backend
permalink: /backend/
---

Backend development notes from the study archive.

{% assign backend_posts = site.tags.backend | sort: 'date' | reverse %}
<ul class="post-card-grid">
{% for post in backend_posts %}
{% include post-card.html post=post %}
{% endfor %}
</ul>
