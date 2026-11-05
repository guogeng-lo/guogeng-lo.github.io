import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATUS_LABEL = {"completed": "已完成", "prototype": "原型", "in_progress": "開發中"}
CONTEXT_LABEL = {"course": "課堂作業", "personal": "個人專案", "senior_project": "畢業專題"}
ORIGIN_LABEL = {"original": "自己建立", "course_starter": "沿用課程範例", "third_party_based": "使用他人素材"}
PERMISSION_LABEL = {"not_needed": "不需要另外取得許可", "granted": "依授權或許可使用", "unknown": "授權還沒確認", "pending": "還在等許可"}

GENERATED_FILES = ["index.html", "sitemap.xml", "assets/css/tokens.css"]
GENERATED_DIRS = ["works"]


def esc(text):
    return html.escape(str(text), quote=True)


def paragraphs(text):
    parts = [p.strip() for p in str(text).split("\n") if p.strip()]
    return "".join(f"<p>{esc(p)}</p>" for p in parts)


def bullet_list(items, cls="list"):
    if not items:
        return ""
    lis = "".join(f"<li>{esc(i)}</li>" for i in items)
    return f'<ul class="{cls}">{lis}</ul>'


def safe_url(url, prefix=""):
    url = str(url)
    if url.startswith("https://"):
        return esc(url)
    if re.fullmatch(r"[A-Za-z0-9_\-./]+", url) and not url.startswith("/") and ".." not in url:
        return esc(prefix + url)
    raise ValueError(f"不接受的連結：{url}")


def repo_file_url(site, path):
    return safe_url(site["repo_url"].rstrip("/") + "/blob/main/" + path)


def source_link(site, source, label):
    if "url" in source:
        href = safe_url(source["url"])
    else:
        href = repo_file_url(site, source["file"])
    return f'<a href="{href}" rel="noopener">{esc(label)}</a>'


def fill(template, slots):
    def replace(match):
        name = match.group(1)
        if name not in slots:
            raise KeyError(f"模板用到沒有提供的欄位：{name}")
        return slots[name]
    return re.sub(r"\{\{(\w+)\}\}", replace, template)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_works(root):
    works = []
    for path in sorted((root / "data" / "works").glob("*.json")):
        if path.name.startswith("_"):
            continue
        works.append(load_json(path))
    works.sort(key=lambda w: (w["order"], w["id"]))
    return works


def period_text(period):
    return period.replace("~", "～")


def tag(text, cls="tag"):
    return f'<span class="{cls}">{esc(text)}</span>'


def work_meta(work):
    parts = [CONTEXT_LABEL[work["context"]]]
    if work["context"] == "course":
        parts.append(work["course"])
    parts.append(period_text(work["period"]))
    return "".join(f"<span>{esc(p)}</span>" for p in parts)


def render_tokens(palette):
    lines = [":root {"]
    for key in sorted(palette["base"]):
        lines.append(f"  --{key.replace('_', '-')}: {palette['base'][key]};")
    lines.append("}")
    for name in sorted(palette["accents"]):
        accent = palette["accents"][name]
        lines.append("")
        lines.append(f'[data-accent="{name}"] {{')
        for role in ("text", "tag", "decor"):
            lines.append(f"  --accent-{role}: {accent[role]};")
        lines.append("}")
    return "\n".join(lines) + "\n"


def render_card(work, prefix, size):
    image = work["images"][0]
    techs = "".join(tag(t, "chip") for t in work["technologies"][:3])
    return (
        f'<article class="card card-{size} reveal" data-accent="{esc(work["accent"])}">'
        f'<a class="card-link" href="{safe_url("works/" + work["id"] + "/", prefix)}">'
        f'<figure class="card-image"><img src="{safe_url(image["file"], prefix)}" alt="{esc(image["alt"])}" loading="lazy"></figure>'
        f'<div class="card-body">'
        f'<p class="meta">{tag(STATUS_LABEL[work["status"]], "status status-" + work["status"])}<span>{esc(CONTEXT_LABEL[work["context"]])}</span><span>{esc(period_text(work["period"]))}</span></p>'
        f'<h3 class="card-title">{esc(work["title"])}</h3>'
        f'<p class="card-summary">{esc(work["summary"])}</p>'
        f'<p class="chips">{techs}</p>'
        f"</div></a></article>"
    )


def render_home(root, site, works, template):
    prefix = ""
    featured = [w for w in works if w["featured"]]
    others = [w for w in works if not w["featured"]]
    featured_html = "".join(render_card(w, prefix, "large") for w in featured)
    others_html = ""
    if others:
        others_html = (
            '<section class="section others"><div class="wrap"><h2 class="section-title">其他作品</h2>'
            '<div class="grid-small">' + "".join(render_card(w, prefix, "small") for w in others) + "</div></div></section>"
        )
    links = "".join(f'<a href="{safe_url(l["url"])}" rel="noopener">{esc(l["label"])}</a>' for l in site["links"])
    return fill(template, {
        "prefix": prefix,
        "site_name": esc(site["name"]),
        "site_name_en": esc(site["name_en"]),
        "page_title": esc(site["name"] + "｜作品集"),
        "description": esc(site["tagline"].replace("\n", "")),
        "canonical": safe_url(site["base_url"].rstrip("/") + "/"),
        "tagline": "<br>".join(esc(line) for line in site["tagline"].split("\n")),
        "intro": paragraphs(site["intro"]),
        "work_count": esc(len(works)),
        "latest_updated": esc(max([w["updated"] for w in works], default="")),
        "method": "<ol class=\"method\">" + "".join(f"<li>{esc(m)}</li>" for m in site.get("method", [])) + "</ol>",
        "featured": featured_html,
        "others": others_html,
        "links": links,
    })


def render_metrics(site, work):
    metrics = work.get("metrics", [])
    if not metrics:
        return ""
    items = ""
    for m in metrics:
        items += (
            '<div class="metric reveal">'
            f'<p class="metric-value">{esc(m["value"])}</p>'
            f'<p class="metric-label">{esc(m["label"])}</p>'
            f'<p class="metric-condition">{esc(m["condition"])}</p>'
            f'<p class="metric-source">{source_link(site, m["source"], "看紀錄")}</p>'
            "</div>"
        )
    return f'<div class="metrics">{items}</div>'


def render_gallery(work, prefix):
    figures = ""
    for i, image in enumerate(work["images"]):
        caption = f'<figcaption>{esc(image["caption"])}</figcaption>' if image.get("caption") else ""
        loading = "eager" if i == 0 else "lazy"
        figures += (
            f'<figure class="shot reveal"><img src="{safe_url(image["file"], prefix)}" alt="{esc(image["alt"])}" loading="{loading}">{caption}</figure>'
        )
    return f'<div class="gallery">{figures}</div>'


def render_links(work):
    links = work.get("links", [])
    return "".join(f'<a class="button" href="{safe_url(l["url"])}" rel="noopener">{esc(l["label"])}</a>' for l in links)


def section(title, body, cls=""):
    if not body:
        return ""
    return f'<section class="section {cls}"><div class="wrap split"><h2 class="section-title">{esc(title)}</h2><div class="section-body">{body}</div></div></section>'


def render_ai(work):
    ai = work.get("ai_collaboration")
    if not ai:
        return ""
    groups = [
        ("用到的AI工具", ai["tools"]),
        ("我做的判斷", ai["my_decisions"]),
        ("AI做的事", ai["ai_work"]),
        ("怎麼驗證", ai["verification"]),
    ]
    body = "".join(f'<div class="group"><h3>{esc(t)}</h3>{bullet_list(items)}</div>' for t, items in groups)
    return section("AI協作", f'<div class="groups">{body}</div>')


def render_tech(work):
    notes = work["tech_notes"]
    body = (
        f'<div class="group"><h3>架構</h3>{paragraphs(notes["architecture"])}</div>'
        f'<div class="group"><h3>做過的決定</h3>{bullet_list(notes["decisions"])}</div>'
        f'<div class="group"><h3>驗證過的部分</h3>{bullet_list(notes["verified"])}</div>'
        f'<div class="group"><h3>還沒做到的</h3>{bullet_list(notes["next"])}</div>'
    )
    return section("技術筆記", body)


def render_sources(site, work):
    origins = "".join(
        f'<li><strong>{esc(ORIGIN_LABEL[o["type"]])}</strong>：{esc(o["note"])}</li>' for o in work["origins"]
    )
    body = f'<h3>內容來源</h3><ul class="list">{origins}</ul>'
    credits = work.get("credits", [])
    if credits:
        items = ""
        for c in credits:
            name = esc(c["name"])
            if c.get("url"):
                name = f'<a href="{safe_url(c["url"])}" rel="noopener">{name}</a>'
            detail = []
            if c.get("creator"):
                detail.append(f'作者：{esc(c["creator"])}')
            if c.get("license"):
                detail.append(f'授權：{esc(c["license"])}')
            detail.append(esc(PERMISSION_LABEL[c["permission_status"]]))
            spans = "".join(f"<span>{d}</span>" for d in detail)
            items += f'<li><p class="credit-name">{name}</p><p class="meta">{spans}</p><p>{esc(c["usage"])}</p></li>'
        body += f'<h3>原作者與授權</h3><ul class="list">{items}</ul>'
    deps = work.get("dependencies", [])
    if deps:
        items = "".join(
            f'<li><a href="{safe_url(d["url"])}" rel="noopener">{esc(d["name"])}</a><span class="muted">（{esc(d["license"])}）</span></li>'
            for d in deps
        )
        body += f'<h3>用到的函式庫</h3><ul class="list">{items}</ul>'
    return section("來源與授權", body, "sources")


def render_evidence(site, work):
    evidence = work.get("status_evidence", [])
    if not evidence:
        return ""
    items = "".join(f"<li>{source_link(site, e, e['label'])}</li>" for e in evidence)
    return f'<div class="evidence"><h3>完成的證據</h3><ul class="list">{items}</ul></div>'


def render_work(root, site, work, template):
    prefix = "../../"
    return fill(template, {
        "prefix": prefix,
        "site_name": esc(site["name"]),
        "page_title": esc(work["title"] + "｜" + site["name"]),
        "description": esc(work["summary"]),
        "canonical": safe_url(site["base_url"].rstrip("/") + "/works/" + work["id"] + "/"),
        "accent": esc(work["accent"]),
        "title": esc(work["title"]),
        "summary": esc(work["summary"]),
        "meta": tag(STATUS_LABEL[work["status"]], "status status-" + work["status"]) + work_meta(work),
        "updated": esc(work["updated"]),
        "technologies": "".join(tag(t, "chip") for t in work["technologies"]),
        "links": render_links(work),
        "gallery": render_gallery(work, prefix),
        "metrics": render_metrics(site, work),
        "evidence": render_evidence(site, work),
        "problem": section("要解決的問題", paragraphs(work["problem"])),
        "solution": section("怎麼解決", paragraphs(work["solution"])),
        "contribution": section("我負責的部分", bullet_list(work["contribution"])),
        "ai": render_ai(work),
        "tech": render_tech(work),
        "sources": render_sources(site, work),
    })


def render_sitemap(site, works):
    base = site["base_url"].rstrip("/")
    latest = max([w["updated"] for w in works], default=None)
    rows = [f"  <url><loc>{esc(base)}/</loc>" + (f"<lastmod>{latest}</lastmod>" if latest else "") + "</url>"]
    for w in works:
        rows.append(f"  <url><loc>{esc(base)}/works/{esc(w['id'])}/</loc><lastmod>{esc(w['updated'])}</lastmod></url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def build(root, out):
    site = load_json(root / "data" / "site.json")
    palette = load_json(root / "data" / "palette.json")
    works = load_works(root)
    home_tpl = (root / "templates" / "home.html").read_text(encoding="utf-8")
    work_tpl = (root / "templates" / "work.html").read_text(encoding="utf-8")

    pages = {
        "index.html": render_home(root, site, works, home_tpl),
        "sitemap.xml": render_sitemap(site, works),
        "assets/css/tokens.css": render_tokens(palette),
    }
    for w in works:
        pages[f"works/{w['id']}/index.html"] = render_work(root, site, w, work_tpl)

    works_dir = out / "works"
    if works_dir.exists():
        shutil.rmtree(works_dir)
    for rel, text in pages.items():
        write(out / rel, text)
    return sorted(pages)


def main():
    try:
        written = build(ROOT, ROOT)
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"建置失敗：{e}")
        print("先跑python3 scripts/validate.py看哪裡有問題。")
        sys.exit(1)
    for rel in written:
        print(f"產生 {rel}")
    print(f"完成，共{len(written)}個檔案。接著跑python3 scripts/validate.py。")


if __name__ == "__main__":
    main()
