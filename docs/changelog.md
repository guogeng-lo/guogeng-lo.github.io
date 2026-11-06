# 修改紀錄

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
