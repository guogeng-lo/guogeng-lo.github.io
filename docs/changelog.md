# 修改紀錄

## 2026-11-06 修改：AGENTS.md、validate.py（擴充測試1之後）
- 擴充測試1（Codex新增終焉之刃，PR #1）發現三件事，照著修規則：
  - Windows的Git把產生的網頁改成CRLF換行，validate.py逐檔比對報錯：新增.gitattributes固定LF；validate.py遇到只有換行不同時，改成直接說明原因
  - 作品頁出現「依素材筆記」這類整理過程的話：第8節規定頁面只寫作品本身，來源記在changelog
  - 「還沒做到的」有一部分是AI自己訂的計畫：第8節規定next每一條都要有素材或使用者講過的根據
- tests/test_validate.py加一個CRLF的情境
- validate.py結果：錯誤0個、警告0個
- 誰做的：Claude依使用者同意修改

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
