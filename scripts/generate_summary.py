#!/usr/bin/env python3
"""Regenerate summary.json from the front matter of every post-*.md file.

One entry per article folder under posts/, keyed by the folder name. Language keys
are null when that translation does not exist. See CLAUDE.md for the layout.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "posts")
OUTPUT = os.path.join(ROOT, "summary.json")
LANGS = ("en", "pl")

try:
    import yaml
except ImportError:
    yaml = None


def parse_front_matter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        raise ValueError("%s: missing YAML front matter" % path)
    block = m.group(1)
    if yaml is not None:
        data = yaml.safe_load(block)
        if not isinstance(data, dict):
            raise ValueError("%s: front matter is not a mapping" % path)
        return data
    return _parse_minimal(block, path)


def _parse_minimal(block, path):
    """Fallback parser for the flat subset of YAML this repo uses."""
    data = {}
    key = None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(("  - ", "- ")):
            if key is None:
                raise ValueError("%s: list item outside a key" % path)
            data.setdefault(key, []).append(_scalar(line.split("- ", 1)[1]))
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            raise ValueError("%s: cannot parse front matter line %r" % (path, line))
        key, value = m.group(1), m.group(2).strip()
        data[key] = _scalar(value) if value else []
    return data


def _scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        body = value[1:-1]
        return body.replace('\\"', '"').replace("\\\\", "\\") if value[0] == '"' else body
    return value


def build():
    posts = []
    problems = []
    if not os.path.isdir(POSTS):
        sys.stderr.write("error: posts/ directory not found at %s\n" % POSTS)
        raise SystemExit(1)
    for entry in sorted(os.listdir(POSTS)):
        folder = os.path.join(POSTS, entry)
        if entry.startswith(".") or not os.path.isdir(folder):
            continue
        found = {lang: os.path.join(folder, "post-%s.md" % lang) for lang in LANGS}
        found = {lang: p for lang, p in found.items() if os.path.isfile(p)}
        if not found:
            continue

        post = {
            "dir": entry,
            "title": {},
            "slugs": {},
            "coverImage": {},
            "brief": {},
            "publishDate": {},
        }
        for lang in LANGS:
            path = found.get(lang)
            if path is None:
                for field in ("title", "slugs", "coverImage", "brief", "publishDate"):
                    post[field][lang] = None
                continue
            fm = parse_front_matter(path)
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            for field in ("title", "slug", "publicationDate", "coverImage", "brief"):
                if not fm.get(field):
                    problems.append("%s: missing '%s'" % (rel, field))
            post["title"][lang] = fm.get("title")
            post["slugs"][lang] = fm.get("slug")
            post["coverImage"][lang] = fm.get("coverImage")
            post["brief"][lang] = fm.get("brief")
            post["publishDate"][lang] = fm.get("publicationDate")
        posts.append(post)

    if problems:
        for p in problems:
            sys.stderr.write("warning: %s\n" % p)
    return {"posts": posts}


def main():
    summary = build()
    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s (%d posts)" % (os.path.basename(OUTPUT), len(summary["posts"])))


if __name__ == "__main__":
    main()
