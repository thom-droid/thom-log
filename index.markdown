---
layout: page
title: Home
---

Welcome to my development log. I use this space to turn things I learn into
notes I can find again: debugging stories, project decisions, and small
technical guides.

## Posts

<ul class="post-card-grid">
{% for post in site.posts %}
{% include post-card.html post=post %}
{% endfor %}
</ul>
