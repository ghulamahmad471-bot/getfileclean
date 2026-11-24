# GetFileClean site: how to work in this repo

GetFileClean (getfileclean.com, also "Get File Clean") is a free browser-based metadata remover owned by AR ECOM SERVICE LLC. Contact: admin@arecomservice.com. This repo IS the live website: every push to `main` is deployed to Hostinger (public_html) automatically.

## Layout
- `index.html` – the tool (all cleaning runs in the browser; never add uploads or tracking without updating the Privacy Policy).
- `posts/b*.txt` – blog source. Each post is a block:
  ```
  === slug-with-focus-keyword
  title: Title containing the focus keyword
  cat: one of the categories in CAT_ORDER in build_blog.py
  kw: focus keyword, 3-4 related keywords
  desc: meta description, 110-165 characters, contains the focus keyword
  ---
  Markdown body (## headings, - lists, 1. lists, **bold**, `code`, [links](other-slug.html))
  ```
- `pages.txt` – About/Contact/Privacy/Terms/Cookie/Disclaimer source.
- `build_blog.py` – builds `blog/*.html`, the policy pages, `sitemap.xml`, `robots.txt`. It fails on broken internal links, unknown categories, wrong description length or duplicate slugs. Never hand-edit generated HTML; edit the source and rebuild.

## Daily article routine
1. `git pull`. Read `posts/` to list existing slugs and avoid duplicates. Check `posts/plan.md` for the next unpublished topic (mark it done after publishing).
2. Pick ONE topic: a real search people make about metadata/file privacy that no existing post answers. Prefer specific, lower-competition searches.
3. Research anything that describes current software, menus or platform behaviour with web search before writing it. Hedge where behaviour varies by version. Never invent statistics, quotes, studies or testimonials.
4. Write 1,000-1,500 words of genuinely useful content: direct answer first, real steps, a short FAQ (3-4 questions) at the end, and 2-4 internal links to existing posts. Mention GetFileClean only where it truly helps. Focus keyword in slug, title, desc, first paragraph and one heading.
5. Append the post to the newest `posts/bNN.txt` (start a new file every 10 posts). Optionally add a link to the new post from 1-2 related older posts.
6. `python3 build_blog.py` must print OK. Then commit (`Add guide: <title>`) and push to `main`.
7. After the push, verify the live page returns 200 at https://getfileclean.com/blog/<slug>.html (allow a few minutes for deploy).
8. Report the title, URL and focus keyword.

## Target keywords (owner's priority)
The main keywords the whole site must rank for are **metadata remover** and **metadata cleaner** (also "meta data remover", "meta data cleaner", "remove metadata", plus the brand "Get File Clean").
- Every article links to the home page (`../index.html`) once, in a natural sentence, using one of these as the link text: "metadata remover", "metadata cleaner", "free metadata remover", "online metadata cleaner".
- Where it fits naturally, use "metadata remover" or "metadata cleaner" once in the body and once in the FAQ. Never stuff keywords or repeat them unnaturally.
- Topics at the top of `posts/plan.md` target these keywords directly; do them first.

## Rules
- Quality over volume: Google penalises scaled low-value content. If a topic would be thin or duplicate, pick another.
- Don't change policy pages, the tool, or site structure in the daily run.
- Keep "owned by AR ECOM SERVICE LLC" in footers.
