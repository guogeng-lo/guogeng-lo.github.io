# 修改紀錄

## 2026-11-06 修改：my-dungeon-game（依最新版規則修正PR #1）
- 合併main的6e87267ae123a3d5588bde1a34c2f2d6138f3e60並重讀AGENTS.md全文；保留main與PR原有的修改紀錄，解決changelog的合併衝突
- 修改`data/works/my-dungeon-game.json`：移除「依素材筆記」「素材筆記記錄」「這次作品頁整理」等整理過程文字；內容來源仍是`docs/raw/my-dungeon-game/notes.md`與該資料夾的5張試玩截圖，這次未重新編譯或執行遊戲
- `origins.note`只保留作品來源；程式的AI協作保留在`ai_collaboration`。刪除「沒有課堂作業的題目限制」等不必要的延伸說明
- 刪除原先由AI推定的測試紀錄、自動測試與效能量測計畫。`tech_notes.next`改成「目前沒有後續開發計畫。」，依據是使用者2026-11-06在本次對話的直接回覆「目前沒有後續開發計畫。」；筆記所述沒有自動測試的事實保留在驗證說明
- 執行既有`build.py`重新產生`works/my-dungeon-game/index.html`；沒有手動修改產出，也沒有修改其他作品資料、圖片、模板、共用樣式或色票
- 套用main新增的`.gitattributes`固定LF；這次編輯的文字檔與重新建置的產出均確認使用LF，沒有新增本機專用換行規則
- validate.py結果：預設比對HEAD為4個作品，錯誤0個、警告0個；另以`--base origin/main`檢查整份PR為錯誤0個、警告1個，警告原文：
  - `[警告] data/works/my-dungeon-game.json：新作品（origin/main裡沒有），狀態是prototype，請人工確認`
- 警告沿用使用者2026-11-06「幫我新增一個作品：終焉之刃」的指示確認；本次沒有修改prototype狀態或第三方授權狀態
- 執行main更新後的`tests/test_validate.py`：32個情境全部通過，包含CRLF換行錯誤訊息的新增情境；沒有另外修改建置、驗證或測試程式
- 瀏覽器確認：首頁與作品頁在電腦版1372像素及手機版375像素均無水平溢出，首頁連結可開啟作品頁
- 需要人工確認：作品描述、原型狀態、素材來源與截圖是否符合實際且沒有個資；後續計畫已依使用者直接回覆填寫
- 誰做的：Codex依使用者要求檢查並修正PR #1

## 2026-11-06 修改：AGENTS.md、validate.py（擴充測試1之後）
- 擴充測試1（Codex新增終焉之刃，PR #1）發現三件事，照著修規則：
  - Windows的Git把產生的網頁改成CRLF換行，validate.py逐檔比對報錯：新增.gitattributes固定LF；validate.py遇到只有換行不同時，改成直接說明原因
  - 作品頁出現「依素材筆記」這類整理過程的話：第8節規定頁面只寫作品本身，來源記在changelog
  - 「還沒做到的」有一部分是AI自己訂的計畫：第8節規定next每一條都要有素材或使用者講過的根據
- tests/test_validate.py加一個CRLF的情境
- validate.py結果：錯誤0個、警告0個
- 誰做的：Claude依使用者同意修改

## 2026-11-06 新增：my-dungeon-game
- 從main的9f61985735bedf250885ca7e8cafb05b52427a38開始，重新讀完最新版AGENTS.md
- 依`docs/raw/my-dungeon-game/notes.md`新增`data/works/my-dungeon-game.json`，整理終焉之刃的玩法、本人貢獻、Claude協作與技術筆記；狀態先沿用範本的prototype，未宣稱已完成
- 將5張使用者試玩的原始截圖完整複製到`assets/img/my-dungeon-game/`，補上描述畫面內容的alt與圖說；每張均小於500KB，未使用AI生成圖片
- 執行`python scripts/build.py`，產生`works/my-dungeon-game/index.html`並更新首頁與sitemap；其他作品的資料、圖片、產出內容沒有變更
- validate.py結果：4個作品，錯誤0個、警告1個，警告原文：
  - `[警告] data/works/my-dungeon-game.json：新作品（HEAD裡沒有），狀態是prototype，請人工確認`
- 警告確認依據：使用者2026-11-06在本次對話明確要求「幫我新增一個作品：終焉之刃」，並指定`docs/raw/my-dungeon-game/`的筆記與5張截圖；依第3節第7步引用這次新增指示，不再重複要求確認。沒有新增第三方credits或升級既有作品狀態
- 瀏覽器確認：首頁與新作品頁在電腦版1372像素、手機版375像素均無水平溢出，首頁的新作品連結可開啟，5張圖片均可載入；未修改模板、共用樣式、色票或建置／驗證程式
- 初次驗證曾因Windows下載時將6個產出檔轉成CRLF而出現逐檔比對錯誤；已確認只有換行差異，執行既有建置程式後消除，沒有修改驗證程式
- 需要人工確認：文字是否符合實際、原型狀態是否合適、素材筆記所述無第三方素材是否正確、截圖是否確為本人遊玩且沒有個資；原始碼未公開，這次沒有重新編譯或執行遊戲，單次通關截圖不等於完整驗收
- 誰做的：Codex依使用者本次指示整理作品頁並執行網站建置與驗證；遊戲原有的AI協作依素材筆記記為Claude

## 2026-11-06 新增素材：docs/raw/my-dungeon-game/
- 放進終焉之刃的素材筆記和5張使用者自己玩的截圖，給擴充測試用；使用者同意公開
- AGENTS.md第2、3節加上`docs/raw/<id>/`可以放素材，會公開
- validate.py結果：錯誤0個、警告0個
- 誰做的：Claude依使用者的指示整理

## 2026-11-06 修改：網站頁尾、LICENSE
- 新增LICENSE：著作權所有，未經同意不得重製或使用；標明出處的第三方內容依原本的授權
- templates/home.html、templates/work.html的頁尾加上「© 2026 羅國耕」，重新產生所有頁面
- AGENTS.md第2節的檔案結構加上LICENSE
- validate.py結果：錯誤0個、警告0個
- 誰做的：Claude依使用者的要求修改

## 2026-11-06 修改：AGENTS.md
- 第10節加上commit的規定：不要加AI署名，貢獻者只顯示使用者本人
- validate.py結果：錯誤0個、警告0個
- 誰做的：Claude依使用者的要求修改

## 2026-11-06 修改：contextmask、last-train
- 改了data/works/contextmask.json、data/works/last-train.json的contribution第一條：寫清楚作業只規定了什麼、題目是自己訂的；updated改成2026-11-06
- 重新產生index.html、works/contextmask/、works/last-train/、sitemap.xml
- validate.py結果：見下面commit前的檢查，錯誤0個、警告0個
- 需要人工確認：兩條寫的作業規定是否符合實際
- 誰做的：Claude依使用者指示修改，使用者2026-11-06在對話裡同意這兩條的寫法

## 2026-11-06 新增：contextmask、last-train、neon-paradox
- 建立網站：AGENTS.md、CLAUDE.md、模板、樣式、色票、scripts/build.py、scripts/validate.py、tests/test_validate.py
- 新增contextmask、last-train、neon-paradox三個作品的資料、截圖和docs/evidence/裡的紀錄
- validate.py結果：錯誤0個；警告1個「還沒有任何commit，略過狀態變化的檢查」，這是第一次commit本來就會有的
- 這次本來會被警告的內容，使用者都已經在對話裡確認過：
  - 三個作品的內容和狀態：2026-11-05～11-06逐項看過、修改後同意
  - last-train的demo-07b、demo-07c改成not_needed：使用者2026-11-06選了「拿掉Colab連結、逐項列出公開內容」的做法
  - neon-paradox改成completed：使用者2026-11-06提供從第一波打到通關的試玩影片
- tests/test_validate.py：31個情境全部通過
- 需要人工確認：GitHub Pages上線後，外部連結和圖片是不是都能正常打開
- 誰做的：Claude依使用者的指示建立，內容由使用者確認
