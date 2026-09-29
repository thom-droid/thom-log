(() => {
  const queryInput = document.getElementById("post-query");
  const tagSelect = document.getElementById("post-tag");
  const count = document.getElementById("search-count");
  const results = document.getElementById("search-results");
  if (!queryInput || !tagSelect || !count || !results) return;

  const indexUrl = new URL("../search-index.json", window.location.href);
  const params = new URLSearchParams(window.location.search);
  queryInput.value = params.get("q") || "";

  fetch(indexUrl)
    .then((response) => {
      if (!response.ok) throw new Error(`Search index returned ${response.status}`);
      return response.json();
    })
    .then((posts) => {
      tagSelect.value = params.get("tag") || "";

      function render() {
        const terms = queryInput.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
        const selectedTag = tagSelect.value;
        const matches = posts.filter((post) => {
          const searchable = [post.title, post.content, ...(post.tags || [])]
            .join(" ").toLocaleLowerCase();
          return (!selectedTag || (post.tags || []).includes(selectedTag)) &&
            terms.every((term) => searchable.includes(term));
        });

        const nextParams = new URLSearchParams();
        if (queryInput.value.trim()) nextParams.set("q", queryInput.value.trim());
        if (selectedTag) nextParams.set("tag", selectedTag);
        const nextUrl = `${window.location.pathname}${nextParams.size ? `?${nextParams}` : ""}`;
        window.history.replaceState(null, "", nextUrl);

        count.textContent = `${matches.length} ${matches.length === 1 ? "post" : "posts"} found`;
        results.replaceChildren();
        for (const post of matches) {
          const item = document.createElement("li");
          item.className = "post-card";
          const heading = document.createElement("h3");
          heading.className = "post-card__title";
          const link = document.createElement("a");
          link.href = post.url;
          link.textContent = post.title;
          heading.append(link);
          const tags = document.createElement("div");
          tags.className = "post-card__tags";
          tags.setAttribute("aria-label", "Tags");
          for (const tag of post.tags || []) {
            const tagLink = document.createElement("a");
            tagLink.className = "post-card__tag";
            tagLink.href = `${window.location.pathname}?tag=${encodeURIComponent(tag)}`;
            tagLink.textContent = tag;
            tags.append(tagLink);
          }
          item.append(heading, tags);
          results.append(item);
        }
      }

      queryInput.addEventListener("input", render);
      tagSelect.addEventListener("change", render);
      render();
    })
    .catch(() => {
      count.textContent = "Search is unavailable. Please use the Archive page.";
    });
})();
