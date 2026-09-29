---
layout: page
title: Projects
permalink: /projects/
---

Project notes and decisions.

{% assign project_posts = site.tags.project | sort: 'date' | reverse %}
<ul class="post-card-grid">
{% for post in project_posts %}
{% include post-card.html post=post %}
{% endfor %}
</ul>
