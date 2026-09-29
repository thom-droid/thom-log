# Thom's Dev Log

A low-maintenance tech blog built with Jekyll and hosted by GitHub Pages.

## The everyday workflow

### 1. Start a draft

Copy `_drafts/post-template.md` to a descriptive draft filename:

```bash
cp _drafts/post-template.md _drafts/spring-transaction-notes.md
```

Edit the front matter at the top and write the post in Markdown. Drafts are not
published by GitHub Pages.

### 2. Preview locally

Install and start Docker Desktop, then run the preview with Docker Compose.
Ruby and gems run inside Docker; no local Ruby installation is required.

```bash
docker compose up
```

Open <http://127.0.0.1:4000/thom-log/>. Stop it with `Ctrl+C`, or run
`docker compose down` from another terminal. Gems are cached in a named Docker
volume, while edits in the repository are rebuilt automatically.
Drafts are included. The first start downloads the image and installs gems.

### 3. Publish

Update the draft's `date`, then move it into `_posts`. The filename must begin
with the same publication date in `YYYY-MM-DD` format:

```bash
mv _drafts/spring-transaction-notes.md _posts/2026-08-22-spring-transaction-notes.md
git add _posts/2026-08-22-spring-transaction-notes.md
git commit -m "Add notes about Spring transactions"
git push origin gh-pages
```

GitHub Pages rebuilds the site after the push. The repository's Pages settings
should use **Deploy from a branch**, branch **gh-pages**, folder **/(root)**.

## Post front matter

Every published post starts with YAML metadata:

```yaml
---
layout: post
title: "Understanding Spring transactions"
date: 2026-08-22 09:00:00 +0900
categories: [backend]
tags: [spring, java, transactions]
excerpt: "The transaction rules I want to remember."
---
```

- `categories` gives a post a broad home; usually use one.
- `tags` are specific technologies or concepts; use a few consistent names.
- `excerpt` is the short description shown on the home page and feed.
- Images belong in `assets/images/`. Reference one with
  `![Alt text]({{ '/assets/images/file.png' | relative_url }})`.

## Site structure

- `_config.yml` — site-wide title, URL, navigation, and defaults
- `_drafts/` — unpublished writing
- `_posts/` and `project/_posts/` — published posts
- `database/index.md` — Database section and automatic post list
- `database/_posts/` — database posts with URLs under `/database/`
- `project/index.md` — Projects section, populated by the `project` tag
- `backend/index.md` and `learning/index.md` — additional tag-based sections
- `search.md`, `search-index.json`, and `assets/search.js` — browser search for
  titles, tags, and post text
- `_includes/header.html` — shared keyword and tag search form on every page
- `assets/main.scss` — small visual customizations
- `archive.md` — automatic chronological post index
- `about.markdown` — author page

Changes to `_config.yml` require restarting the local preview server. Files in
`_site/` are generated output and should never be edited or committed.

## Obsidian import pilot

The first adapted note is `MVCC; Multi Versioning Concurrency Control.md` from
`/Users/thomhs/log/thom-log/study/study plan/Arc1 - Booking System/Part1 - Transaction. MVCC. Lock/`.
Its blog version is
`database/_posts/2026-09-29-mvcc-snapshots-and-row-versions.md`.
The source vault is unchanged. The adaptation keeps the original English,
focuses the explanation on PostgreSQL, and adds a two-session SQL walkthrough.
The remaining nonempty notes from the `study` folder can be reproduced with
`python3 scripts/import_obsidian_study.py /path/to/vault/study`. Raw archive
posts preserve the source body, add section and topic tags, and record the
vault-relative path in `source_note`. The source file's last-modified time is
used for archive ordering; it is not a claimed original publication date.
The curated MVCC post replaces its raw source to avoid a duplicate.

## Sections and search

Posts appear in a navigation section when they carry its tag: `database` for
Database, `backend` for Backend, `project` for Projects, and `learning` for
Learning. Add topic tags such as `mvcc` or
`refactoring` to make posts easier to find. The Archive lists every published
post and links each tag to Search. The shared header lets readers search by
keyword and tag from any page. Results run in the browser from a static JSON
index generated at build time.

## A sustainable writing habit

Keep each post focused on one question. Capture the context, the smallest useful
example, what was confusing, and the takeaway. A short note you can search later
is already a successful post; it can always be expanded.
