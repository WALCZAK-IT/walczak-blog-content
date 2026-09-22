# WALCZAK.IT blog content repository

The source of truth for the WALCZAK.IT blog. Articles are written here as Markdown,
in English and/or Polish, and a future blog engine will render from these files and
from `summary.json`. This is a content repository — no application code, no build
step for the articles themselves.

The initial 17 articles were imported from the old walczak.it site. That import is
finished and will not be repeated; nothing here is synced from the live site any
more. New articles are authored directly in this repository.

## Repository layout

```
posts/
  <english-slug>/          # one folder per article, named after the ENGLISH slug
    post-en.md             # English text (omit when there is no English version)
    post-pl.md             # Polish text (omit when there is no Polish version)
    media/                 # every image and downloadable file used by either language
summary.json               # generated index of all posts (see below)
.github/workflows/         # automation
scripts/generate_summary.py
```

Rules the tooling and the future renderer depend on:

- Every article lives in its own folder under `posts/`. Nothing else goes in there.
- The folder name is the article's **dir** key in `summary.json` and its stable
  identifier. It is always an English slug, even for articles written only in Polish
  (use an English translation of the title).
- Both language files of one article share a single `media/` folder. Assets are
  referenced with the relative path `media/<filename>` — never an absolute URL.
- A language file is simply absent when that translation does not exist. Do not
  create placeholder files.

## Front matter

Every `post-*.md` starts with a YAML block:

```yaml
---
title: "REST API versioning schemes"
slug: "rest-api-versioning-schemes"
publicationDate: "2024-10-05"
tags:
  - "REST"
  - "API design"
coverImage: "media/rest-versioning.drawio.png"
brief: "Versioning is crucial for maintaining a stable and evolving REST API. As your API matures, changes become inevitable, whether due to bug fixes, new features, or performance enhancements. This article explores several common REST API versioning strategies, discussing their pros and cons."
---
```

- `title` and `slug` are **per language** — the Polish file carries the Polish title
  and the Polish URL slug. All five keys are required in both files.
- `brief` is a short introduction in to the posts content
- `publicationDate` is ISO `YYYY-MM-DD`.
- `tags` are written in English in both language files, so the two versions stay
  linkable and tag pages don't fragment by language.
- `coverImage` is a repo-relative `media/...` path.

## Body conventions

- Headings inside the body start at `##` — `#` is reserved for the `title` field.
- Fence code blocks with a language hint (`json`, `java`, `sql`, `bash`, ...).
- In-page anchors are bare fragments: `[Summary](#summary)`.
- Images use the relative `media/` path; add the file to the article's `media/`
  folder rather than hotlinking anything external.
- Keep the two language files structurally parallel — same sections, same images —
  so a reader can switch languages mid-article.

## Writing a new article

1. Create a folder under `posts/`, named with the English slug.
2. Add `post-en.md` and/or `post-pl.md` with complete front matter.
3. Put every image and attachment in that folder's `media/`.
4. Commit and push to `main`. `summary.json` regenerates itself.

Renaming a folder changes the post's `dir` — treat it as a breaking change for
anything consuming `summary.json`. Changing a `slug` changes a published URL, so
prefer adding a redirect in the blog engine over editing a slug that has shipped.

## summary.json

Generated — **never edit by hand**. Regenerated on every push to `main` by
`.github/workflows/generate-summary.yml`, which runs `scripts/generate_summary.py`
and commits the result if it changed. Run it locally the same way:

```bash
python scripts/generate_summary.py
```

The script works with or without PyYAML installed, and warns on stderr about any post
missing a required front matter field.

Shape (one entry per folder under `posts/`, sorted by `dir`; a language key is `null`
when that translation is missing):

```json
{
  "posts": [
    {
      "dir": "rest-api-versioning-schemes",
      "title":        { "en": "...", "pl": "..." },
      "slugs":        { "en": "...", "pl": "..." },
      "coverImage":   { "en": "...", "pl": "..." },
      "brief":        { "en": "...", "pl": "..." },
      "publishDate":  { "en": "...", "pl": "..." }
    }
  ]
}
```

## Legacy quirks from the original import

Leave these alone unless the content itself is being rewritten:

- `posts/distributing-javafx-desktop-applications-without-requiring-jvm-using-jlink-and-jpackage/post-pl.md`
  is deliberately short — the Polish version was only ever an intro plus a pointer to
  the English article.
- A few Polish posts carry the same slug as their English counterpart (e.g.
  `integrating-business-systems-manufacturing-sme`) because that is the URL the old
  site published. New articles should get a properly translated Polish slug.
