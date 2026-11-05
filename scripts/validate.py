import argparse
import filecmp
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build

ROOT = build.ROOT

STATUS_RANK = {"in_progress": 0, "prototype": 1, "completed": 2}
CONTEXTS = {"course", "personal", "senior_project"}
ORIGIN_TYPES = {"original", "course_starter", "third_party_based"}
PERMISSIONS = {"unknown", "pending", "not_needed", "granted"}
PUBLIC_PERMISSIONS = {"not_needed", "granted"}

WORK_FIELDS = {
    "id", "title", "summary", "status", "status_evidence", "updated", "context", "course", "period",
    "origins", "dependencies", "credits", "featured", "order", "accent", "technologies", "problem",
    "solution", "contribution", "ai_collaboration", "metrics", "links", "images", "tech_notes",
}
REQUIRED_FIELDS = {
    "id", "title", "summary", "status", "updated", "context", "period", "origins", "featured", "order",
    "accent", "technologies", "problem", "solution", "contribution", "images", "tech_notes",
}
CREDIT_FIELDS = {"id", "name", "creator", "url", "license", "usage", "permission_status", "rights_basis"}

ID_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
PERIOD_RE = re.compile(r"\d{4}(-(0[1-9]|1[0-2]))?(~\d{4}(-(0[1-9]|1[0-2]))?)?")
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")
CJK = r"　-〿一-鿿＀-￯"
SPACING_RE = re.compile(rf"[{CJK}] +[A-Za-z0-9]|[A-Za-z0-9] +[{CJK}]|[{CJK}] +[{CJK}]")
PERSONAL_PATTERNS = [
    (re.compile(r"(?<!\d)\d{9}(?!\d)"), "像學號的9位數字"),
    (re.compile(r"09\d{2}-?\d{3}-?\d{3}"), "像手機號碼的數字"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "像信箱的字串"),
]
PLACEHOLDERS = ["待填", "example.com", "example-work", "example-starter"]
COLOR_IN_CODE_RE = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?(?:[0-9a-fA-F]{2})?\b|\brgba?\(|\bhsla?\(")

errors = []
warnings = []


def error(where, msg):
    errors.append(f"[錯誤] {where}：{msg}")


def warn(where, msg):
    warnings.append(f"[警告] {where}：{msg}")


def is_text(value):
    return isinstance(value, str) and value.strip() != ""


def is_text_list(value):
    return isinstance(value, list) and len(value) > 0 and all(is_text(v) for v in value)


def all_strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from all_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from all_strings(v, f"{path}[{i}]")


def check_url(where, url):
    try:
        build.safe_url(url)
    except ValueError:
        error(where, f"連結只能是https://開頭，或站內相對路徑：{url}")
        return False
    return True


def check_repo_file(where, path):
    if not isinstance(path, str) or path.startswith("/") or ".." in path or ":" in path or "\\" in path:
        error(where, f"檔案路徑要是repo裡的相對路徑，不能是電腦上的路徑：{path}")
        return
    if path.split("/")[0] == "drafts":
        error(where, f"不能指向drafts/裡的檔案，那裡不會公開，別人點開會看不到：{path}")
        return
    if not (ROOT / path).is_file():
        error(where, f"找不到檔案：{path}")
        return
    if (ROOT / ".git").exists() and git("check-ignore", "-q", path).returncode == 0:
        error(where, f"這個檔案被.gitignore排除，不會上傳，別人點開會看不到：{path}")


def check_template():
    path = ROOT / "data" / "works" / "_template.json"
    where = "data/works/_template.json"
    if not path.is_file():
        error(where, "找不到範本")
        return
    try:
        template = build.load_json(path)
    except json.JSONDecodeError as e:
        error(where, f"範本不是合法的JSON：{e}")
        return
    if not isinstance(template, dict):
        error(where, "範本最外層要是物件")
        return
    missing = REQUIRED_FIELDS - set(template)
    extra = set(template) - WORK_FIELDS
    if missing:
        error(where, f"範本少了必填欄位：{'、'.join(sorted(missing))}")
    if extra:
        error(where, f"範本有規則裡沒有的欄位：{'、'.join(sorted(extra))}")
    for i, c in enumerate(template.get("credits", [])):
        if not isinstance(c, dict) or set(c) != CREDIT_FIELDS:
            error(where, f"範本的credits[{i}]欄位要跟第6節一致")
        elif c.get("permission_status") != "unknown":
            error(where, f"範本的credits[{i}]要維持unknown，避免照抄就變成可以公開")


def check_source(where, source):
    if not isinstance(source, dict) or len([k for k in ("url", "file") if k in source]) != 1:
        error(where, "要有url或file其中一個")
        return
    if "url" in source:
        check_url(where, source["url"])
    else:
        check_repo_file(where, source["file"])


def luminance(hex_color):
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(a, b):
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check_palette(palette):
    where = "data/palette.json"
    base = palette.get("base", {})
    accents = palette.get("accents", {})
    needed = ["bg", "surface", "text", "muted", "line", "hero_bg", "hero_text", "hero_muted"]
    for key in needed:
        if key not in base:
            error(where, f"base少了{key}")
    for key, value in base.items():
        if not re.fullmatch(r"[a-z_]+", key):
            error(where, f"base的名稱只能用小寫英文和底線：{key}")
        if not isinstance(value, str) or not HEX_RE.fullmatch(value):
            error(where, f"base.{key}要是#加6位色碼：{value}")
    if not accents:
        error(where, "accents至少要有一個重點色")
    for name, accent in accents.items():
        if not ID_RE.fullmatch(name):
            error(where, f"重點色名稱只能用英文小寫、數字和連字號：{name}")
        for role in ("text", "tag", "decor"):
            value = accent.get(role)
            if not isinstance(value, str) or not HEX_RE.fullmatch(value):
                error(where, f"accents.{name}.{role}要是#加6位色碼：{value}")
    if any(e.startswith(f"[錯誤] {where}") for e in errors):
        return
    pairs = [
        ("base.text", base["text"], "base.bg", base["bg"]),
        ("base.muted", base["muted"], "base.bg", base["bg"]),
        ("base.text", base["text"], "base.surface", base["surface"]),
        ("base.muted", base["muted"], "base.surface", base["surface"]),
        ("base.hero_text", base["hero_text"], "base.hero_bg", base["hero_bg"]),
        ("base.hero_muted", base["hero_muted"], "base.hero_bg", base["hero_bg"]),
    ]
    for name, accent in accents.items():
        pairs.append((f"{name}.text", accent["text"], "base.bg", base["bg"]))
        pairs.append((f"{name}.text", accent["text"], "base.surface", base["surface"]))
        pairs.append((f"{name}.text", accent["text"], f"{name}.tag", accent["tag"]))
    for fg_name, fg, bg_name, bg in pairs:
        ratio = contrast(fg, bg)
        if ratio < 4.5:
            error(where, f"{fg_name}放在{bg_name}上的對比只有{ratio:.2f}:1，至少要4.5:1")


def check_site(site):
    where = "data/site.json"
    for key in ("name", "name_en", "tagline", "intro", "base_url", "repo_url"):
        if not is_text(site.get(key)):
            error(where, f"{key}要填")
    for key in ("base_url", "repo_url"):
        if is_text(site.get(key)) and not site[key].startswith("https://"):
            error(where, f"{key}要是https://開頭")
    links = site.get("links")
    if not isinstance(links, list):
        error(where, "links要是清單")
    else:
        for i, link in enumerate(links):
            if not is_text(link.get("label")) or not is_text(link.get("url")):
                error(where, f"links[{i}]要有label和url")
            else:
                check_url(f"{where} links[{i}]", link["url"])
    check_text_rules(where, site)


def check_text_rules(where, data):
    for path, text in all_strings(data):
        is_address = path.endswith(".url") or path.endswith(".file") or path in ("url", "base_url", "repo_url")
        for pattern, label in ([] if is_address else PERSONAL_PATTERNS):
            if pattern.search(text):
                error(where, f"{path}裡有{label}，網站不能放個資")
        m = SPACING_RE.search(text)
        if m:
            error(where, f"{path}裡中文和英文、數字之間有多餘的空格：「{m.group(0)}」")
        for word in PLACEHOLDERS:
            if word in text:
                error(where, f"{path}還留著範本的「{word}」")


def check_credits(where, work, public):
    credits = work.get("credits", [])
    if not isinstance(credits, list):
        error(where, "credits要是清單")
        return {}
    by_id = {}
    for i, c in enumerate(credits):
        w = f"{where} credits[{i}]"
        if not isinstance(c, dict):
            error(w, "要是物件")
            continue
        missing = CREDIT_FIELDS - set(c)
        extra = set(c) - CREDIT_FIELDS
        if missing:
            error(w, f"少了欄位：{'、'.join(sorted(missing))}")
        if extra:
            error(w, f"有規則裡沒有的欄位：{'、'.join(sorted(extra))}")
        cid = c.get("id")
        if not isinstance(cid, str) or not ID_RE.fullmatch(cid):
            error(w, f"id只能用英文小寫、數字和連字號：{cid}")
        elif cid in by_id:
            error(w, f"id重複：{cid}")
        else:
            by_id[cid] = c
        for key in ("name", "usage"):
            if not is_text(c.get(key)):
                error(w, f"{key}要填")
        for key in ("creator", "license"):
            if c.get(key) is not None and not is_text(c.get(key)):
                error(w, f"{key}要填文字，不知道就寫null")
        if c.get("url") is not None:
            check_url(w, c["url"])
        status = c.get("permission_status")
        if status not in PERMISSIONS:
            error(w, f"permission_status只能是{'、'.join(sorted(PERMISSIONS))}：{status}")
        elif status in PUBLIC_PERMISSIONS:
            if not is_text(c.get("rights_basis")):
                error(w, f"permission_status是{status}，一定要寫rights_basis說明依據")
        else:
            if c.get("rights_basis") is not None:
                error(w, f"permission_status是{status}時，rights_basis要寫null")
            if public:
                error(w, f"permission_status是{status}，這個作品只能放在drafts/，不能公開")
    return by_id


def check_origins(where, work, credits_by_id):
    origins = work.get("origins")
    if not isinstance(origins, list) or not origins:
        error(where, "origins至少要有一筆")
        return
    used = set()
    for i, o in enumerate(origins):
        w = f"{where} origins[{i}]"
        if not isinstance(o, dict):
            error(w, "要是物件")
            continue
        if set(o) != {"type", "note", "credit_ids"}:
            error(w, "要剛好有type、note、credit_ids三個欄位")
        if o.get("type") not in ORIGIN_TYPES:
            error(w, f"type只能是{'、'.join(sorted(ORIGIN_TYPES))}：{o.get('type')}")
        if not is_text(o.get("note")):
            error(w, "note要寫清楚是哪一部分")
        ids = o.get("credit_ids")
        if not isinstance(ids, list):
            error(w, "credit_ids要是清單")
            continue
        if o.get("type") in ("course_starter", "third_party_based") and not ids:
            error(w, f"{o.get('type')}至少要對應一筆credits")
        for cid in ids:
            if cid not in credits_by_id:
                error(w, f"credit_ids裡的{cid}在credits裡找不到")
            used.add(cid)
    for cid in credits_by_id:
        if cid not in used:
            error(where, f"credits裡的{cid}沒有被任何origins用到")


def check_images(where, work):
    images = work.get("images")
    if not isinstance(images, list) or not images:
        error(where, "images至少要一張真實截圖，沒有的話先放drafts/")
        return set()
    files = set()
    for i, image in enumerate(images):
        w = f"{where} images[{i}]"
        path = image.get("file") if isinstance(image, dict) else None
        if not isinstance(path, str) or not path.startswith(f"assets/img/{work.get('id')}/"):
            error(w, f"圖片要放在assets/img/{work.get('id')}/裡：{path}")
            continue
        check_repo_file(w, path)
        full = ROOT / path
        if full.is_file() and full.stat().st_size > 500 * 1024:
            error(w, f"圖片超過500KB：{full.stat().st_size // 1024}KB")
        alt = image.get("alt")
        if not is_text(alt) or alt.strip() in ("截圖", "圖片", "screenshot", "image"):
            error(w, "alt要描述畫面內容，不能空著或只寫「截圖」")
        if "caption" in image and not is_text(image["caption"]):
            error(w, "caption不用的話就刪掉，不要留空")
        files.add(path)
    return files


def check_work(path, palette, seen_ids):
    where = f"data/works/{path.name}"
    try:
        work = build.load_json(path)
    except json.JSONDecodeError as e:
        error(where, f"不是合法的JSON：{e}")
        return None
    if not isinstance(work, dict):
        error(where, "最外層要是物件")
        return None
    missing = REQUIRED_FIELDS - set(work)
    extra = set(work) - WORK_FIELDS
    if missing:
        error(where, f"少了必填欄位：{'、'.join(sorted(missing))}")
    if extra:
        error(where, f"有規則裡沒有的欄位：{'、'.join(sorted(extra))}")
    wid = work.get("id")
    if not isinstance(wid, str) or not ID_RE.fullmatch(wid):
        error(where, f"id只能用英文小寫、數字和連字號：{wid}")
    elif wid != path.stem:
        error(where, f"id是{wid}，但檔名是{path.stem}，要一致")
    elif wid in seen_ids:
        error(where, f"id和別的作品重複：{wid}")
    seen_ids.add(wid)

    for key in ("title", "summary", "problem", "solution"):
        if not is_text(work.get(key)):
            error(where, f"{key}要填")
    if is_text(work.get("summary")) and len(work["summary"]) > 60:
        error(where, f"summary有{len(work['summary'])}字，要60字以內")

    status = work.get("status")
    if status not in STATUS_RANK:
        error(where, f"status只能是completed、prototype、in_progress：{status}")
    evidence = work.get("status_evidence", [])
    if not isinstance(evidence, list):
        error(where, "status_evidence要是清單")
        evidence = []
    if status == "completed" and not evidence:
        error(where, "completed一定要有status_evidence")
    for i, e in enumerate(evidence):
        w = f"{where} status_evidence[{i}]"
        if not isinstance(e, dict) or not is_text(e.get("label")):
            error(w, "要有label")
            continue
        check_source(w, {k: v for k, v in e.items() if k != "label"})

    try:
        date.fromisoformat(work.get("updated", ""))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", work["updated"]):
            raise ValueError
    except (TypeError, ValueError):
        error(where, f"updated要是YYYY-MM-DD：{work.get('updated')}")
    if not isinstance(work.get("period"), str) or not PERIOD_RE.fullmatch(work["period"]):
        error(where, f"period要是YYYY-MM、YYYY-MM~YYYY-MM，或只寫年份：{work.get('period')}")

    if work.get("context") not in CONTEXTS:
        error(where, f"context只能是course、personal、senior_project：{work.get('context')}")
    if work.get("context") == "course" and not is_text(work.get("course")):
        error(where, "課堂作業要填course")

    credits_by_id = check_credits(where, work, public=True)
    check_origins(where, work, credits_by_id)
    if any(o.get("type") != "original" for o in work.get("origins", []) if isinstance(o, dict)) and not credits_by_id:
        error(where, "origins不只original時，credits一定要填")

    for i, d in enumerate(work.get("dependencies", [])):
        w = f"{where} dependencies[{i}]"
        if not all(is_text(d.get(k)) for k in ("name", "license", "url")):
            error(w, "要有name、license、url")
        else:
            check_url(w, d["url"])

    if not isinstance(work.get("featured"), bool):
        error(where, "featured要是true或false")
    if not isinstance(work.get("order"), int) or isinstance(work.get("order"), bool):
        error(where, "order要是整數")
    if work.get("accent") not in palette.get("accents", {}):
        error(where, f"accent要是palette.json裡有的重點色：{work.get('accent')}")
    for key in ("technologies", "contribution"):
        if not is_text_list(work.get(key)):
            error(where, f"{key}至少要有一條")

    ai = work.get("ai_collaboration")
    if ai is not None:
        if not isinstance(ai, dict) or set(ai) != {"tools", "my_decisions", "ai_work", "verification"}:
            error(where, "ai_collaboration要剛好有tools、my_decisions、ai_work、verification")
        else:
            for key, value in ai.items():
                if not is_text_list(value):
                    error(where, f"ai_collaboration.{key}至少要有一條")

    for i, m in enumerate(work.get("metrics", [])):
        w = f"{where} metrics[{i}]"
        if not isinstance(m, dict) or not all(is_text(m.get(k)) for k in ("value", "label", "condition")):
            error(w, "要有value、label、condition")
            continue
        if "source" not in m:
            error(w, "要有source，沒有來源的數字不放")
        else:
            check_source(w, m["source"])

    for i, link in enumerate(work.get("links", [])):
        w = f"{where} links[{i}]"
        if not isinstance(link, dict) or not is_text(link.get("label")) or not is_text(link.get("url")):
            error(w, "要有label和url")
        else:
            check_url(w, link["url"])

    notes = work.get("tech_notes")
    if not isinstance(notes, dict) or set(notes) != {"architecture", "decisions", "verified", "next"}:
        error(where, "tech_notes要剛好有architecture、decisions、verified、next")
    else:
        if not is_text(notes["architecture"]):
            error(where, "tech_notes.architecture要填")
        for key in ("decisions", "verified", "next"):
            if not is_text_list(notes[key]):
                error(where, f"tech_notes.{key}至少要有一條")

    image_files = check_images(where, work)
    check_text_rules(where, work)
    return work, image_files


def check_image_folders(works, used_files):
    img_root = ROOT / "assets" / "img"
    if not img_root.exists():
        return
    ids = {w.get("id") for w in works}
    for folder in sorted(p for p in img_root.iterdir() if p.is_dir()):
        if folder.name not in ids:
            error(f"assets/img/{folder.name}/", "對應不到任何公開作品，草稿的圖片要放在drafts/")
            continue
        for f in sorted(p for p in folder.rglob("*") if p.is_file()):
            rel = f.relative_to(ROOT).as_posix()
            if rel not in used_files:
                error(rel, "這張圖片沒有被作品的images用到，會被公開，要用就寫進images，不用就移到drafts/")


def check_code_colors():
    targets = list((ROOT / "templates").glob("*.html")) + [ROOT / "assets" / "css" / "style.css"]
    targets += list((ROOT / "assets" / "js").glob("*.js"))
    for path in targets:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for n, line in enumerate(text.splitlines(), 1):
            if COLOR_IN_CODE_RE.search(line):
                error(f"{path.relative_to(ROOT).as_posix()}第{n}行", "不能直接寫色碼，顏色要用palette.json產生的變數")


def generated_files(base):
    files = set()
    for rel in build.GENERATED_FILES:
        if (base / rel).is_file():
            files.add(rel)
    for d in build.GENERATED_DIRS:
        if (base / d).exists():
            files |= {p.relative_to(base).as_posix() for p in (base / d).rglob("*") if p.is_file()}
    return files


def check_rebuild():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        try:
            build.build(ROOT, tmp)
        except (KeyError, ValueError) as e:
            error("建置", f"在暫存資料夾重新建置失敗：{e}")
            return
        expected = generated_files(tmp)
        actual = generated_files(ROOT)
        for rel in sorted(expected - actual):
            error(rel, "應該要有這個產出，但找不到，請跑build.py")
        for rel in sorted(actual - expected):
            error(rel, "重新建置不會產生這個檔案，可能是刪掉的作品留下的舊頁面，請跑build.py")
        for rel in sorted(expected & actual):
            if not filecmp.cmp(tmp / rel, ROOT / rel, shallow=False):
                error(rel, "內容和重新建置的結果不同：可能被手動改過，或改了資料後沒有跑build.py")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")


def check_git(base_ref, works):
    if not (ROOT / ".git").exists():
        warn("git", "這裡還不是git repo，略過drafts/和狀態變化的檢查")
        return
    gitignore = ROOT / ".gitignore"
    lines = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
    if not any(l.strip() in ("drafts/", "/drafts/", "drafts") for l in lines):
        error(".gitignore", "要有drafts/這一行")
    tracked = git("ls-files", "drafts").stdout.split()
    for f in tracked:
        error(f, "drafts/的檔案被Git追蹤了，會被公開，要用git rm --cached移除")
    history = git("log", "--all", "--format=%h", "--", "drafts").stdout.split()
    if history:
        warn("git歷史", f"有{len(history)}個commit碰過drafts/，裡面的內容可能已經公開過，請人工確認")

    if git("rev-parse", "--verify", base_ref).returncode != 0:
        warn("git", f"找不到{base_ref}（可能還沒有任何commit），略過狀態變化的檢查")
        return
    for w in works:
        rel = f"data/works/{w['id']}.json"
        old_text = git("show", f"{base_ref}:{rel}")
        old = None
        if old_text.returncode == 0:
            try:
                old = json.loads(old_text.stdout)
            except json.JSONDecodeError:
                old = None
        if old is None:
            warn(rel, f"新作品（{base_ref}裡沒有），狀態是{w['status']}，請人工確認")
            old_status, old_perm = None, {}
        else:
            old_status = old.get("status")
            old_perm = {c.get("id"): c.get("permission_status") for c in old.get("credits", []) if isinstance(c, dict)}
        if old_status in STATUS_RANK and STATUS_RANK[w["status"]] > STATUS_RANK[old_status]:
            warn(rel, f"status從{old_status}升到{w['status']}，請人工確認證據是否真的足夠")
        for c in w.get("credits", []):
            now = c.get("permission_status")
            before = old_perm.get(c.get("id"))
            if now in PUBLIC_PERMISSIONS and before != now:
                warn(rel, f"credits的{c.get('id')}從{before or '沒有'}變成{now}，請人工確認rights_basis是否成立")


def main():
    parser = argparse.ArgumentParser(description="檢查作品集的資料和產出。不修改專案裡的檔案，重新建置只在系統的暫存資料夾進行，跑完自動刪掉。")
    parser.add_argument("--base", default="HEAD", help="比對狀態變化用的commit，預設是HEAD")
    args = parser.parse_args()

    for name in ("AGENTS.md", "CLAUDE.md", ".gitignore"):
        if not (ROOT / name).is_file():
            error(name, "找不到這個檔案")

    try:
        palette = build.load_json(ROOT / "data" / "palette.json")
        site = build.load_json(ROOT / "data" / "site.json")
    except (OSError, json.JSONDecodeError) as e:
        error("data/", f"讀不到palette.json或site.json：{e}")
        palette, site = {}, {}
    if palette:
        check_palette(palette)
    if site:
        check_site(site)
    check_code_colors()

    check_template()
    works, used_files, seen = [], set(), set()
    for path in sorted((ROOT / "data" / "works").glob("*.json")):
        if path.name.startswith("_"):
            continue
        result = check_work(path, palette, seen)
        if result:
            works.append(result[0])
            used_files |= result[1]
    check_image_folders(works, used_files)

    if not errors:
        check_rebuild()
    else:
        errors.append("[略過] 資料有錯誤，先修好再比對產出")
    check_git(args.base, [w for w in works if isinstance(w.get("id"), str) and w.get("status") in STATUS_RANK])

    for line in errors + warnings:
        print(line)
    real_errors = [e for e in errors if e.startswith("[錯誤]")]
    print(f"\n{len(works)}個作品，錯誤{len(real_errors)}個，警告{len(warnings)}個。")
    if real_errors:
        print("有錯誤，還不算做完。修資料，不要改驗證程式。")
        sys.exit(1)
    if warnings:
        print("沒有錯誤，但有警告：照AGENTS.md第3節第7步，把警告原文回報給使用者；他還沒確認過的，要等他確認才能commit或push。")
    else:
        print("全部通過。")


if __name__ == "__main__":
    main()
