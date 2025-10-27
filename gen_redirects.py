#!/usr/bin/env python3
# gen_redirects.py
"""
Generate redirect pages in a site repo that redirect old blog URLs
(e.g. /2020/06/01/post/) to new blog location (/blog/2020/06/01/post/).

Fixes:
 - Will NOT generate a redirect for the blog root (i.e. when blog/public/index.html exists).
 - By default will NOT overwrite existing files in the site repo.
 - Can pass --overwrite to force overwrite.
 - Can pass --exclude to skip certain relative paths.
"""

import os
import argparse

REDIRECT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url={target}">
  <link rel="canonical" href="{target}">
  <title>Redirecting...</title>
</head>
<body>
  <p>Redirecting to <a href="{target}">{target}</a></p>
</body>
</html>
"""

def is_index_at_root(dirpath, blog_root):
    """
    Return True if dirpath is the blog_root itself (i.e. blog root).
    We want to skip generating redirect for blog root.
    """
    return os.path.normpath(os.path.abspath(dirpath)) == os.path.normpath(os.path.abspath(blog_root))

def normalize_rel(rel):
    if rel in (".", ""):
        return ""
    return rel.replace(os.sep, "/")

def main():
    parser = argparse.ArgumentParser(description="Generate redirect pages for legacy blog URLs into site repo.")
    parser.add_argument("--blog", required=True, help="Path to built blog output directory (e.g. blog/public)")
    parser.add_argument("--site", required=True, help="Path to homepage repo root (e.g. xxx.github.io)")
    parser.add_argument("--base", default="/blog/", help="Base URL prefix of the new blog (default: /blog/)")
    parser.add_argument("--overwrite", action="store_true", help="If set, overwrite existing redirect files in site")
    parser.add_argument("--exclude", action="append", default=[], help="Relative paths (from blog root) to exclude; can be used multiple times")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files; just print what would be done")
    args = parser.parse_args()

    blog_root = os.path.abspath(args.blog)
    site_root = os.path.abspath(args.site)
    base = args.base
    if not base.startswith("/"):
        base = "/" + base
    if not base.endswith("/"):
        base = base + "/"

    exclude_set = set([normalize_rel(x) for x in args.exclude])

    if not os.path.isdir(blog_root):
        print(f"Error: blog directory not found: {blog_root}")
        return
    if not os.path.isdir(site_root):
        print(f"Error: site directory not found: {site_root}")
        return

    created = 0
    skipped = 0
    overwritten = 0

    for dirpath, _, filenames in os.walk(blog_root):
        # We only consider directories that contain an index.html (typical static site page)
        if "index.html" not in filenames:
            continue

        # If this is the blog root dir (blog/public/), skip it (do NOT generate site root redirect).
        if is_index_at_root(dirpath, blog_root):
            print(f"⤴ Skipping blog root: {dirpath} (won't create site root redirect)")
            skipped += 1
            continue

        relpath = os.path.relpath(dirpath, blog_root)
        rel_norm = normalize_rel(relpath)  # e.g. "2020/06/01/post" or ""

        if rel_norm == "":
            # redundant safety: blog root already handled above
            print(f"⤴ Skipping empty relpath for {dirpath}")
            skipped += 1
            continue

        if rel_norm in exclude_set:
            print(f"⤴ Excluded by user: {rel_norm}")
            skipped += 1
            continue

        # target url: base + rel_norm + '/'
        target_url = base + rel_norm + "/"

        # Output redirect path inside the site repo
        redirect_dir = os.path.join(site_root, relpath)
        redirect_file = os.path.join(redirect_dir, "index.html")

        # Avoid clobbering important files unless --overwrite
        if os.path.exists(redirect_file) and not args.overwrite:
            print(f"⚠ Skipping (exists): {redirect_file} -> {target_url}")
            skipped += 1
            continue

        # Ensure parent dir exists
        if not args.dry_run:
            os.makedirs(redirect_dir, exist_ok=True)
            with open(redirect_file, "w", encoding="utf-8") as f:
                f.write(REDIRECT_TEMPLATE.format(target=target_url))

        if args.overwrite and os.path.exists(redirect_file):
            print(f"✏ Overwritten: {redirect_file} -> {target_url}")
            overwritten += 1
        else:
            print(f"✅ Generated redirect: {redirect_file} -> {target_url}")
            created += 1

    print("\nSummary:")
    print(f"  created: {created}")
    print(f"  overwritten: {overwritten}")
    print(f"  skipped: {skipped}")
    if args.dry_run:
        print("Note: dry-run mode; no files were written.")

if __name__ == "__main__":
    main()
