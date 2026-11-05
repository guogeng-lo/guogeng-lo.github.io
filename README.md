# guogeng-lo.github.io

羅國耕的作品集：https://guogeng-lo.github.io

這個repo除了網站本身，也是一套讓AI照規則新增作品頁的做法：

- 規則寫在`AGENTS.md`，`CLAUDE.md`只叫AI先去讀它
- 每個作品一份`data/works/<id>.json`，`scripts/build.py`照模板產生網頁
- `scripts/validate.py`檢查資料、來源授權、個資、顏色對比，也會重新建置一次比對產出
- `tests/test_validate.py`故意弄壞資料，確認驗證程式真的會擋
- `docs/extension-test.md`記錄用全新的AI對話照規則新增作品的結果

```
python3 scripts/build.py
python3 scripts/validate.py
python3 tests/test_validate.py
```

只用Python標準函式庫，不用安裝套件。
