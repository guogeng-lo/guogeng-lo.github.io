# 修改紀錄

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
