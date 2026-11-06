import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COPY_FROM_REPO = ["AGENTS.md", "CLAUDE.md", ".gitignore", "scripts", "templates", "assets/css/style.css", "assets/js", "data/palette.json", "data/works/_template.json"]


def tiny_png():
    raw = b"\x00\xff\xff\xff"
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def fixture_works(accents):
    done = {
        "id": "fixture-done",
        "title": "測試用作品甲",
        "summary": "只用來測驗證程式的假作品，已完成。",
        "status": "completed",
        "status_evidence": [{"label": "測試紀錄", "file": "docs/test-log.md"}],
        "updated": "2026-11-05",
        "context": "personal",
        "period": "2026-10",
        "origins": [{"type": "original", "note": "全部自己寫的。", "credit_ids": []}],
        "featured": True,
        "order": 10,
        "accent": accents[0],
        "technologies": ["Python"],
        "problem": "假的問題。",
        "solution": "假的解法。",
        "contribution": ["假的貢獻"],
        "metrics": [{"value": "3題", "label": "測試", "condition": "假的條件", "source": {"file": "docs/test-log.md"}}],
        "images": [{"file": "assets/img/fixture-done/01-main.png", "alt": "一張白色的測試圖片"}],
        "tech_notes": {"architecture": "假的架構。", "decisions": ["假的決定"], "verified": ["假的驗證"], "next": ["假的下一步"]},
    }
    proto = {
        "id": "fixture-proto",
        "title": "測試用作品乙",
        "summary": "只用來測驗證程式的假作品，用了課程範例。",
        "status": "prototype",
        "status_evidence": [],
        "updated": "2026-11-05",
        "context": "course",
        "course": "測試課程",
        "period": "2026-09~2026-10",
        "origins": [
            {"type": "original", "note": "工具是自己寫的。", "credit_ids": []},
            {"type": "course_starter", "note": "環境設定沿用範例。", "credit_ids": ["starter-a"]},
        ],
        "dependencies": [{"name": "Gradio", "license": "Apache-2.0", "url": "https://github.com/gradio-app/gradio"}],
        "credits": [{
            "id": "starter-a", "name": "課程範例甲", "creator": None, "url": None, "license": None,
            "usage": "環境設定", "permission_status": "not_needed", "rights_basis": "測試用的依據",
        }],
        "featured": True,
        "order": 20,
        "accent": accents[1 % len(accents)],
        "technologies": ["Python", "Gradio"],
        "problem": "假的問題。",
        "solution": "假的解法。",
        "contribution": ["假的貢獻"],
        "ai_collaboration": {"tools": ["Claude"], "my_decisions": ["假的決定"], "ai_work": ["假的工作"], "verification": ["假的驗證"]},
        "metrics": [{"value": "5題", "label": "測試", "condition": "假的條件", "source": {"url": "https://github.com/guogeng-lo"}}],
        "links": [{"label": "原始碼", "url": "https://github.com/guogeng-lo"}],
        "images": [{"file": "assets/img/fixture-proto/01-main.png", "alt": "一張白色的測試圖片"}],
        "tech_notes": {"architecture": "假的架構。", "decisions": ["假的決定"], "verified": ["假的驗證"], "next": ["假的下一步"]},
    }
    return [done, proto]


def run(cmd, cwd):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env)


def git(root, *args):
    return run(["git", "-c", "user.email=test@example.invalid", "-c", "user.name=test", *args], root)


def make_site(root):
    for rel in COPY_FROM_REPO:
        src, dst = REPO / rel, root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy(src, dst)
    accents = sorted(json.loads((root / "data/palette.json").read_text(encoding="utf-8"))["accents"])
    site = {
        "name": "測試", "name_en": "Test", "tagline": "測試用的網站", "intro": "只給驗證程式的測試用。",
        "base_url": "https://guogeng-lo.github.io", "repo_url": "https://github.com/guogeng-lo/guogeng-lo.github.io",
        "links": [{"label": "GitHub", "url": "https://github.com/guogeng-lo"}],
    }
    write_json(root, "data/site.json", site)
    for work in fixture_works(accents):
        write_json(root, f"data/works/{work['id']}.json", work)
        image = root / work["images"][0]["file"]
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(tiny_png())
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs/test-log.md").write_text("測試紀錄\n", encoding="utf-8")
    run([sys.executable, "scripts/build.py"], root)
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "fixture")


def write_json(root, rel, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def edit_json(root, rel, change):
    path = root / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build(root):
    run([sys.executable, "scripts/build.py"], root)


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.parts}


PROTO = "data/works/fixture-proto.json"
DONE = "data/works/fixture-done.json"
CASES = []


def case(scenario, expect_exit, expect_text):
    def register(fn):
        CASES.append((scenario, expect_exit, expect_text, fn))
        return fn
    return register


@case("沒有動任何東西", 0, "錯誤0個")
def _(r):
    pass


@case("手動修改產生的index.html", 1, "內容和重新建置的結果不同")
def _(r):
    p = r / "index.html"
    p.write_text(p.read_text(encoding="utf-8").replace("<main", "<main data-hand-edit", 1), encoding="utf-8")


@case("作品刪掉後留下舊頁面", 1, "可能是刪掉的作品留下的舊頁面")
def _(r):
    (r / "works/old-work").mkdir(parents=True)
    (r / "works/old-work/index.html").write_text("old", encoding="utf-8")


@case("草稿的圖片放進公開的assets/img/", 1, "對應不到任何公開作品")
def _(r):
    (r / "assets/img/secret-draft").mkdir()
    (r / "assets/img/secret-draft/01.png").write_bytes(tiny_png())


@case("作品資料夾裡有沒被用到的圖片", 1, "這張圖片沒有被作品的images用到")
def _(r):
    (r / "assets/img/fixture-done/99-extra.png").write_bytes(tiny_png())


@case("授權還是unknown就放進公開資料", 1, "只能放在drafts/")
def _(r):
    edit_json(r, PROTO, lambda d: d["credits"][0].update(permission_status="unknown", rights_basis=None))
    build(r)


@case("not_needed卻沒寫rights_basis", 1, "一定要寫rights_basis")
def _(r):
    edit_json(r, PROTO, lambda d: d["credits"][0].update(rights_basis=None))
    build(r)


@case("course_starter沒有對應credits", 1, "至少要對應一筆credits")
def _(r):
    edit_json(r, PROTO, lambda d: d["origins"][1].update(credit_ids=[]))
    build(r)


@case("多出一筆沒被origins用到的credits", 1, "沒有被任何origins用到")
def _(r):
    edit_json(r, PROTO, lambda d: d["credits"].append(dict(d["credits"][0], id="unused-one")))
    build(r)


@case("改成completed但沒有證據", 1, "completed一定要有status_evidence")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(status="completed"))
    build(r)


@case("證據指向不存在的檔案", 1, "找不到檔案")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(status="completed", status_evidence=[{"label": "紀錄", "file": "docs/no-such-file.md"}]))
    build(r)


@case("有證據的升級：不擋，但要出警告", 0, "status從prototype升到completed")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(status="completed", status_evidence=[{"label": "紀錄", "file": "docs/test-log.md"}]))
    build(r)


@case("授權從unknown改成not_needed：不擋，但要出警告", 0, "請人工確認rights_basis是否成立")
def _(r):
    edit_json(r, PROTO, lambda d: d["credits"][0].update(permission_status="unknown", rights_basis=None))
    build(r)
    git(r, "add", "-A")
    git(r, "commit", "-qm", "unknown")
    edit_json(r, PROTO, lambda d: d["credits"][0].update(permission_status="not_needed", rights_basis="使用者提供的依據"))
    build(r)


@case("新增作品：不擋，但要出警告", 0, "新作品")
def _(r):
    data = json.loads((r / DONE).read_text(encoding="utf-8"))
    data.update(id="fixture-new", images=[{"file": "assets/img/fixture-new/01-main.png", "alt": "一張白色的測試圖片"}])
    write_json(r, "data/works/fixture-new.json", data)
    (r / "assets/img/fixture-new").mkdir()
    (r / "assets/img/fixture-new/01-main.png").write_bytes(tiny_png())
    build(r)


@case("標題裡放<script>：要被跳脫成純文字", 0, "跳脫正確")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(title="<script>alert(1)</script>作品"))
    build(r)
    html = (r / "works/fixture-proto/index.html").read_text(encoding="utf-8")
    return "跳脫正確" if "<script>alert(1)" not in html and "&lt;script&gt;alert(1)" in html else "沒有跳脫"


@case("連結用javascript:", 1, "連結只能是https://開頭")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(links=[{"label": "x", "url": "javascript:alert(1)"}]))
    build(r)


@case("drafts/的檔案被Git追蹤", 1, "drafts/的檔案被Git追蹤了")
def _(r):
    (r / "drafts").mkdir()
    (r / "drafts/secret.json").write_text("{}", encoding="utf-8")
    git(r, "add", "-f", "drafts/secret.json")


@case("中文和英文之間有空格", 1, "多餘的空格")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(summary="用 Python 寫的假作品"))
    build(r)


@case("文字裡有信箱和學號", 1, "像學號的9位數字")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(problem="聯絡someone@example.org，學號123456789"))
    build(r)


@case("範本的「待填」沒換掉", 1, "還留著範本的「待填」")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(problem="待填：要解決的問題"))
    build(r)


@case("數字沒有來源", 1, "要有source")
def _(r):
    edit_json(r, PROTO, lambda d: d["metrics"][0].pop("source"))
    build(r)


@case("重點色的文字對比不夠", 1, "至少要4.5:1")
def _(r):
    edit_json(r, "data/palette.json", lambda d: next(iter(d["accents"].values())).update(text="#F0F0F0"))
    build(r)


@case("style.css直接寫色碼", 1, "不能直接寫色碼")
def _(r):
    p = r / "assets/css/style.css"
    p.write_text(p.read_text(encoding="utf-8") + "\n.x { color: #ff0000; }\n", encoding="utf-8")


@case("欄位名稱拼錯", 1, "有規則裡沒有的欄位")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(sumary="打錯字"))
    build(r)


@case("改了資料但沒跑build.py", 1, "改了資料後沒有跑build.py")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(summary="改過的介紹"))


@case("產生的網頁被改成CRLF換行", 1, "只有換行不同")
def _(r):
    p = r / "index.html"
    p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))


@case("用底線檔名把草稿藏在data/works/", 1, "只有_template.json可以用底線開頭")
def _(r):
    data = json.loads((r / "data/works/_template.json").read_text(encoding="utf-8"))
    write_json(r, "data/works/_unreleased.json", data)


@case("範本留著「待填」：範本本來就是這樣，不能因此報錯", 0, "錯誤0個")
def _(r):
    pass


@case("範本的JSON格式壞掉", 1, "範本不是合法的JSON")
def _(r):
    p = r / "data/works/_template.json"
    p.write_text(p.read_text(encoding="utf-8").rstrip().rstrip("}"), encoding="utf-8")


@case("範本的授權被改成not_needed", 1, "範本的credits[0]要維持unknown")
def _(r):
    edit_json(r, "data/works/_template.json", lambda d: d["credits"][0].update(permission_status="not_needed"))


@case("證據指向drafts/裡的檔案", 1, "不能指向drafts/裡的檔案")
def _(r):
    (r / "drafts").mkdir()
    (r / "drafts/log.md").write_text("紀錄", encoding="utf-8")
    edit_json(r, PROTO, lambda d: d.update(status="completed", status_evidence=[{"label": "紀錄", "file": "drafts/log.md"}]))
    build(r)


@case("數字來源指向被.gitignore排除的檔案", 1, "這個檔案被.gitignore排除")
def _(r):
    (r / "docs/private-log.md").write_text("紀錄", encoding="utf-8")
    with open(r / ".gitignore", "a", encoding="utf-8") as f:
        f.write("docs/private-log.md\n")
    edit_json(r, DONE, lambda d: d["metrics"][0].update(source={"file": "docs/private-log.md"}))
    build(r)


@case("證據寫成電腦上的路徑", 1, "不能是電腦上的路徑")
def _(r):
    edit_json(r, PROTO, lambda d: d.update(status="completed", status_evidence=[{"label": "紀錄", "file": "C:/Users/me/log.md"}]))
    build(r)


def main():
    print("validate.py反向測試：每個情境都在系統的暫存資料夾裡建一個假的網站，故意弄壞一個地方，再跑validate.py，跑完自動刪掉。\n")
    failed = 0
    for number, (scenario, expect_exit, expect_text, fn) in enumerate(CASES, 1):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_site(root)
            extra = fn(root) or ""
            before = snapshot(root)
            result = run([sys.executable, "scripts/validate.py"], root)
            untouched = snapshot(root) == before
            output = result.stdout + extra
            ok = result.returncode == expect_exit and expect_text in output and untouched
            failed += not ok
            expect = f"exit {expect_exit}，訊息含「{expect_text}」"
            actual = f"exit {result.returncode}，{'有' if expect_text in output else '沒有'}這段訊息，專案檔案{'沒被改動' if untouched else '被改動了'}"
            print(f"{number:2d}. {'通過' if ok else '失敗'}｜{scenario}")
            print(f"    預期：{expect}")
            print(f"    實際：{actual}")
            if not ok:
                print("    validate.py輸出：")
                print("    " + result.stdout.replace("\n", "\n    "))
    print(f"\n共{len(CASES)}個情境，失敗{failed}個。")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
