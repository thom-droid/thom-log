---
layout: page
title: Archive
permalink: /archive/
---

Browse by [section]({{ '/database/' | relative_url }}) or [search keywords and tags]({{ '/search/' | relative_url }}).

{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
{% for year in posts_by_year %}
## {{ year.name }}

<ul class="post-card-grid">
{% for post in year.items %}
{% include post-card.html post=post %}
{% endfor %}
</ul>
{% endfor %}
