#!/usr/bin/env python3
"""Builds the GetFileClean blog: blog/index.html, one page per post, blog/blog.css, sitemap.xml, robots.txt."""
import glob, html, json, os, re, sys

SITE = "https://getfileclean.com"
DATE = "2026-11-25"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "blog")
CAT_ORDER = ["Metadata Basics", "Photo Privacy", "Sharing & Social Media", "Documents", "PDF",
             "Video & Audio", "Professionals", "Ecommerce & Business", "Privacy & Security", "Technical", "GetFileClean Guides"]

def parse():
    posts = []
    for f in sorted(glob.glob(os.path.join(ROOT, "posts", "b*.txt"))):
        for chunk in open(f, encoding="utf-8").read().split("=== ")[1:]:
            head, body = chunk.split("\n---\n", 1)
            lines = head.strip().split("\n")
            p = {"slug": lines[0].strip(), "body": body.strip()}
            for ln in lines[1:]:
                k, v = ln.split(":", 1)
                p[k.strip()] = v.strip()
            p["kws"] = [k.strip() for k in p["kw"].split(",")]
            posts.append(p)
    return posts

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t

def md(src):
    out, para, lst, code = [], [], None, None
    def flush():
        nonlocal para, lst
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para = []
        if lst: out.append(f"<{lst[0]}>" + "".join(f"<li>{inline(i)}</li>" for i in lst[1]) + f"</{lst[0]}>"); lst = None
    for ln in src.split("\n"):
        if code is not None:
            if ln.startswith("```"): out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>"); code = None
            else: code.append(ln)
            continue
        if ln.startswith("```"): flush(); code = []; continue
        s = ln.strip()
        if not s: flush(); continue
        if s.startswith("## "): flush(); out.append(f'<h2 id="{re.sub("[^a-z0-9]+","-",s[3:].lower()).strip("-")}">{inline(s[3:])}</h2>'); continue
        if s.startswith("### "): flush(); out.append(f"<h3>{inline(s[4:])}</h3>"); continue
        m = re.match(r"^(- |\d+\. )(.*)", s)
        if m:
            kind = "ul" if m.group(1) == "- " else "ol"
            if para: flush()
            if not lst or lst[0] != kind: flush(); lst = [kind, []]
            lst[1].append(m.group(2)); continue
        if lst: flush()
        para.append(s)
    flush()
    return "\n".join(out)

def clean(h):
    """Pretty URLs: drop .html from internal links (the server maps /page to page.html)."""
    h = re.sub(r'href="((?:\.\./)?(?:blog/)?)index\.html', lambda m: 'href="' + (m.group(1) or './'), h)
    return re.sub(r'href="(?!https?:|//|mailto:|#)([^"#?]+)\.html', r'href="\1', h)

def words(t): return len(re.findall(r"\w+", t))

NAV = '''<nav><a class="logo" href="../index.html" aria-label="GetFileClean home"><svg viewBox="0 0 30 30" aria-hidden="true"><rect width="30" height="30" rx="7" fill="var(--teal)"/><path d="M9 5h9.5l4.5 4.5V24a1.6 1.6 0 0 1-1.6 1.6H9A1.6 1.6 0 0 1 7.4 24V6.6A1.6 1.6 0 0 1 9 5z" fill="#fff"/><path d="M18.5 5v4.5H23" fill="none" stroke="var(--teal)" stroke-width="1.3"/><path d="m10.6 17 2.9 2.9 5.6-6.1" fill="none" stroke="var(--teal)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg><span class="wm">GetFile<em>Clean</em></span></a>
<div class="links"><a href="../index.html">Metadata remover</a><a href="index.html">Blog</a><a href="../index.html#formats">Formats</a><a href="../index.html#faq">FAQ</a></div></nav>'''
FOOT = '''<footer><div class="wrap"><b>GetFileClean</b><span>Free metadata remover. Files never leave your device.</span><span class="sp"></span><a href="../index.html">Remove metadata</a><a href="index.html">Blog</a><a href="../about.html">About</a><a href="../contact.html">Contact</a><a href="../privacy-policy.html">Privacy Policy</a><a href="../terms.html">Terms</a><a href="../cookie-policy.html">Cookies</a><a href="../disclaimer.html">Disclaimer</a><span>© 2026 GetFileClean, owned by AR ECOM SERVICE LLC</span></div></footer>'''
PAGES = ["about", "contact", "privacy-policy", "terms", "cookie-policy", "disclaimer"]

def build_pages():
    txt = open(os.path.join(ROOT, "pages.txt"), encoding="utf-8").read()
    nav = NAV.replace('href="index.html"', 'href="blog/index.html"').replace("../", "").replace('href="blog.css"', 'href="blog/blog.css"')
    foot = FOOT.replace('href="index.html"', 'href="blog/index.html"').replace("../", "")
    for chunk in txt.split("=== ")[1:]:
        head_, body = chunk.split("\n---\n", 1)
        lines = head_.strip().split("\n"); slug = lines[0].strip()
        meta = dict(l.split(":", 1) for l in lines[1:]); title = meta["title"].strip(); desc = meta["desc"].strip()
        canon = f"{SITE}/{slug}"
        page = head(title + " | GetFileClean", desc, ["getfileclean", title.lower(), "metadata remover"], canon).replace('href="blog.css"', 'href="blog/blog.css"').replace('content="article"', 'content="website"')
        page += nav + f'<main class="band"><article class="post"><p class="crumb"><a href="index.html">Home</a> › {html.escape(title)}</p><h1>{html.escape(title)}</h1><div class="body" style="margin-top:24px">{md(body.strip())}</div></article></main>' + foot + "</body></html>\n"
        open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8").write(clean(page))

def head(title, desc, kws, canon, extra=""):
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('consent','default',{{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied',wait_for_update:500,region:['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE','IS','LI','NO','GB','CH']}});
gtag('js',new Date());
</script>
<script async src="https://www.googletagmanager.com/gtm.js?id=GTM-MB9R7WBH"></script>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="keywords" content="{html.escape(", ".join(kws))}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="article"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{canon}"><meta property="og:site_name" content="GetFileClean">
<meta name="twitter:card" content="summary">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="blog.css"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon-48.png" sizes="48x48" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">{extra}</head><body>'''

def related(p, posts):
    def score(q):
        s = 3 if q["cat"] == p["cat"] else 0
        a = set(" ".join(p["kws"]).split()); b = set(" ".join(q["kws"]).split())
        return s + len(a & b) - (0.01 * posts.index(q))
    linked = set(re.findall(r"\]\(([a-z0-9-]+)\.html\)", p["body"]))
    cands = [q for q in posts if q is not p]
    cands.sort(key=score, reverse=True)
    picks = [q for q in cands if q["slug"] not in linked][:3]
    return picks

def build():
    posts = parse()
    slugs = [p["slug"] for p in posts]
    errs = []
    if len(posts) < 100: errs.append(f"expected at least 100 posts, got {len(posts)}")
    if len(set(slugs)) != len(slugs): errs.append("duplicate slugs: " + str({s for s in slugs if slugs.count(s) > 1}))
    for p in posts:
        for l in re.findall(r"\]\(([^)]+)\)", p["body"]):
            if l.startswith("../"):
                if not os.path.exists(os.path.join(ROOT, l[3:].split("#")[0])): errs.append(f"{p['slug']}: broken link {l}")
                continue
            if l.endswith(".html") and l[:-5] not in slugs: errs.append(f"{p['slug']}: broken link {l}")
        if p["cat"] not in CAT_ORDER: errs.append(f"{p['slug']}: unknown category {p['cat']}")
        if not (110 <= len(p["desc"]) <= 165): errs.append(f"{p['slug']}: description length {len(p['desc'])}")
    if errs: print("\n".join(errs)); sys.exit(1)

    os.makedirs(OUT, exist_ok=True)
    for p in posts:
        body = md(p["body"]); mins = max(2, round(words(p["body"]) / 200))
        canon = f"{SITE}/blog/{p['slug']}"
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "BlogPosting", "headline": p["title"], "description": p["desc"], "keywords": ", ".join(p["kws"]),
             "datePublished": DATE, "dateModified": DATE, "mainEntityOfPage": canon, "articleSection": p["cat"],
             "author": {"@type": "Organization", "name": "GetFileClean Team", "url": SITE + "/about", "logo": SITE + "/logo.png"}, "publisher": {"@type": "Organization", "name": "GetFileClean", "url": SITE}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": canon}]}]}
        extra = '\n<script type="application/ld+json">' + json.dumps(ld).replace("<", "\\u003c") + "</script>"
        rel = "".join(f'<a class="rc" href="{q["slug"]}.html"><span class="cat">{html.escape(q["cat"])}</span><b>{html.escape(q["title"])}</b></a>' for q in related(p, posts))
        tags = "".join(f"<li>{html.escape(k)}</li>" for k in p["kws"])
        page = head(p["title"] + " | GetFileClean", p["desc"], p["kws"], canon, extra) + NAV + f'''
<main class="band"><article class="post">
<p class="crumb"><a href="../index.html">Home</a> › <a href="index.html">Blog</a> › <a href="index.html#{re.sub('[^a-z0-9]+','-',p['cat'].lower())}">{html.escape(p["cat"])}</a></p>
<h1>{html.escape(p["title"])}</h1>
<div class="author"><img class="av" src="../favicon.svg" width="40" height="40" alt="GetFileClean Team avatar"><div><a class="an" href="../about.html" rel="author">GetFileClean Team</a><span class="am">{html.escape(p["cat"])} · {mins} min read · Updated {DATE}</span></div></div>
<div class="body">{body}</div>
<aside class="cta"><div><h2>Free metadata remover &amp; cleaner</h2><p>Remove metadata from photos, documents, PDFs, videos and audio with Get File Clean. No upload, no limits.</p></div><a class="btn" href="../index.html">Clean my files</a></aside>
<section class="kw"><h2>Topics in this guide</h2><ul>{tags}</ul></section>
<section class="rel"><h2>Related metadata guides</h2><div class="rg">{rel}</div></section>
</article></main>
''' + FOOT + "</body></html>\n"
        open(os.path.join(OUT, p["slug"] + ".html"), "w", encoding="utf-8").write(clean(page))

    # blog index
    cats = [c for c in CAT_ORDER if any(p["cat"] == c for p in posts)]
    data = [{"s": p["slug"], "t": p["title"], "d": p["desc"], "c": p["cat"], "k": " ".join(p["kws"])} for p in posts]
    chips = '<button class="chip on" data-c="">All topics</button>' + "".join(f'<button class="chip" data-c="{html.escape(c)}">{html.escape(c)}</button>' for c in cats)
    sections = ""
    for c in cats:
        cards = "".join(f'<a class="card" href="{p["slug"]}.html" data-k="{html.escape((p["title"]+" "+p["desc"]+" "+" ".join(p["kws"])).lower())}"><b>{html.escape(p["title"])}</b><span>{html.escape(p["desc"])}</span></a>' for p in posts if p["cat"] == c)
        sections += f'<section class="grp" id="{re.sub("[^a-z0-9]+","-",c.lower())}" data-c="{html.escape(c)}"><h2>{html.escape(c)}</h2><div class="grid">{cards}</div></section>'
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "GetFileClean Blog", "url": SITE + "/blog/",
          "description": "Guides on how to remove metadata from photos, documents, PDFs, videos and audio.",
          "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}"} for p in posts]}
    idx = head("Metadata Blog: Guides to Remove Metadata from Any File | GetFileClean",
               "Free guides on how to remove metadata from photos, PDFs, Word files, videos and audio, plus EXIF, GPS and document privacy explained simply.",
               ["metadata blog", "remove metadata guide", "exif data", "metadata privacy", "metadata remover"], SITE + "/blog/",
               '\n<script type="application/ld+json">' + json.dumps(ld).replace("<", "\\u003c") + "</script>") + NAV + f'''
<main><section class="band intro"><div class="wrap">
<h1>Metadata guides</h1>
<p class="sub">{len(posts)} plain-English guides to finding and removing metadata from photos, documents, PDFs, videos and audio.</p>
<label class="search"><span class="vh">Search guides</span><input id="q" type="search" placeholder="Search, e.g. remove metadata from PDF" autocomplete="off"></label>
<div class="chips" id="chips">{chips}</div>
<p class="count" id="count" aria-live="polite"></p>
</div></section>
<div class="band list"><div class="wrap" id="groups">{sections}<p class="none" id="none" hidden>No guides match that search. Try "photo", "PDF" or "Word".</p></div></div></main>
''' + FOOT + '''
<script>{
const q=document.getElementById('q'),chips=[...document.querySelectorAll('.chip')],groups=[...document.querySelectorAll('.grp')];let cat='';
function run(){const t=q.value.trim().toLowerCase().split(/\\s+/).filter(Boolean);let n=0;
 for(const g of groups){let v=0;const ok=!cat||g.dataset.c===cat;
  for(const c of g.querySelectorAll('.card')){const show=ok&&t.every(w=>c.dataset.k.includes(w));c.hidden=!show;if(show)v++}
  g.hidden=!v;n+=v}
 document.getElementById('count').textContent=n+(n===1?' guide':' guides');document.getElementById('none').hidden=n>0}
q.addEventListener('input',run);
chips.forEach(c=>c.addEventListener('click',()=>{cat=c.dataset.c;chips.forEach(x=>x.classList.toggle('on',x===c));run()}));
run();}</script></body></html>
'''
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(clean(idx))

    build_pages()
    urls = [SITE + "/", SITE + "/blog/"] + [f"{SITE}/{s}" for s in PAGES] + [f"{SITE}/blog/{s}" for s in slugs]
    open(os.path.join(ROOT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f"  <url><loc>{u}</loc><lastmod>{DATE}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

    # report
    tot = sum(words(p["body"]) for p in posts)
    miss = [p["slug"] for p in posts if not any(w in p["title"].lower() for w in p["kws"][0].split()[:2])]
    print(f"OK: {len(posts)} posts, {tot} words (avg {tot//len(posts)}), categories: " + ", ".join(f"{c}={sum(p['cat']==c for p in posts)}" for c in cats))
    print("focus keyword weakly in title:", miss or "none")
    return posts

if __name__ == "__main__":
    build()
