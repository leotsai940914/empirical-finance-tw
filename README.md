# 實證金融學：從學術研究到個人投資

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)

> **For international visitors:** This is a Traditional Chinese empirical finance course for Taiwanese investors — Jupyter Notebooks covering pandas/matplotlib basics, behavioral finance, market valuation, factor investing (Fama-French), and personal financial planning. Each notebook connects Nobel Prize-winning research (Kahneman, Fama, Shiller) to real investment decisions, with Taiwan-specific data and examples. Feel free to star, fork, or open an issue in English.

用真實數據驗證每一個你聽過的金融「常識」。  
從 pandas 工具熱身到因子投資，每個結論都有論文出處和可以自己跑的程式碼。

有基礎 Python 能力、對投資有興趣但討厭「感覺派」建議的人，應該會喜歡這個。

---

## 課程地圖

### 入門工具
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [00_pandas_matplotlib](00_pandas_matplotlib.ipynb) | pandas 與資料視覺化：用股市資料學工具 | — |

### Part 0：為什麼散戶會虧錢？
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [01_intro](01_intro.ipynb) | 課程導覽與環境確認 | — |
| [02_behavioral_finance](02_behavioral_finance.ipynb) | 行為金融：散戶的七大認知偏誤 | Kahneman & Tversky (1979)；Odean (1998)；Barber & Odean (2000) |

### Part 1：市場如何定價？
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [03_shiller_cape](03_shiller_cape.ipynb) | CAPE 與長期報酬預測 | Shiller (2000) |
| [04_damodaran](04_damodaran.ipynb) | 行業估值數據庫 | Damodaran (年度更新) |
| [05_capm_reality](05_capm_reality.ipynb) | CAPM 的現實 & BAB | Black, Jensen & Scholes (1972)；Frazzini & Pedersen (2014) |

### Part 2：個人理財決策
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [06_trinity_study](06_trinity_study.ipynb) | 4% 退休提領法則 | Bengen (1994)；Cooley et al. (1998) |
| [07_dca_vs_lumpsum](07_dca_vs_lumpsum.ipynb) | 定期定額 vs 單筆投入 | Vanguard (2012) |

### Part 3：市場異象
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [08_january_effect](08_january_effect.ipynb) | 月份效應：一月效應與賣在五月 | Rozeff & Kinney (1976) |
| [09_factor_zoo](09_factor_zoo.ipynb) | 因子動物園與多重檢定問題 | Harvey, Liu & Zhu (2016) |

### Part 4：因子投資
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [10_fama_french](10_fama_french.ipynb) | 三因子模型：規模、價值、動能 | Fama & French (1993) |
| [11_ff5_quality](11_ff5_quality.ipynb) | 五因子：品質與保守投資 | Fama & French (2015) |
| [12_momentum](12_momentum.ipynb) | 動能效應：強者恆強 | Jegadeesh & Titman (1993) |

### 附錄
| Notebook | 主題 | 用途 |
|----------|------|------|
| [13_fire_calculator](13_fire_calculator.ipynb) | 財務自由計算機 & 指標速查 | 代入個人數字；CAPE/P/E 市場溫度計 |
| [14_conclusion](14_conclusion.ipynb) | 投資結論：把學術研究變成行動指南 | 課程總整理；四條人生軌跡模擬；個人投資評分 |

---

## 快速開始

```bash
# 安裝必要套件
pip install numpy pandas matplotlib scipy pandas-datareader openpyxl yfinance

# 啟動課程（從這裡開始）
jupyter notebook 00_pandas_matplotlib.ipynb
```

---

## 建議學習路徑

```
入門者    → 00 → 01 → 05 → 06 → 02
理論型    → 00 → 01 → 04 → 08 → 09 → 10 → 11
實務型    → 00 → 01 → 02 → 03 → 05 → 10
完整課程  → 00 → 01 → 02 → ... → 11
```

---

## 目錄結構

```
學術研究_教材/
├── 00_pandas_matplotlib.ipynb
├── 01_intro.ipynb
├── 02_behavioral_finance.ipynb
├── 03_shiller_cape.ipynb
├── 04_damodaran.ipynb
├── 05_capm_reality.ipynb
├── 06_trinity_study.ipynb
├── 07_dca_vs_lumpsum.ipynb
├── 08_january_effect.ipynb
├── 09_factor_zoo.ipynb
├── 10_fama_french.ipynb
├── 11_ff5_quality.ipynb
├── 12_momentum.ipynb
├── 13_fire_calculator.ipynb
├── 14_conclusion.ipynb
├── data/                 ← 快取數據（執行時自動下載）
└── scripts/              ← Notebook 生成腳本
```

---

## 數據來源

| 數據集 | 來源 | 時間範圍 | 用於 |
|--------|------|----------|------|
| Shiller CAPE | Robert Shiller (Yale) | 1871–今 | 02 |
| Fama-French 因子 | Kenneth French Data Library | 1926–今 | 04, 08, 09, 10, 11 |
| 行業估值 | Damodaran (NYU Stern) | 最新年度 | 03 |
| Odean 券商帳戶統計 | 論文公開數據（Table 1, 3, 5） | 1987–1993 | 01 |
| Barber & Odean 分組數據 | 論文公開數據（Table IV, V） | 1991–1997 | 01 |

---

## 貢獻與更新

這個 repo 我會持續更新——遇到有趣的實證研究就會加進來。

如果你有想新增的主題、發現哪裡的數據或邏輯有問題，或是想一起維護，歡迎開 Issue 或送 PR。沒有門檻，中英文都可以。

---

## 關於作者

**蔡晟郁 (Cheng-Yu Tsai)**  
國立中央大學 經濟學系

上課時發現 Fama、Shiller 這些人的研究很有用，
但從來沒人用中文把它們跟實際投資決策接起來。
就自己做了一套。

📬 聯絡：[chengyustudy0914@gmail.com](mailto:chengyustudy0914@gmail.com) 或開 [GitHub Issue](../../issues) 討論。

---

## 免責聲明

本課程純屬教育用途，所有內容僅供學習參考，**不構成任何投資建議**。
投資有風險，請依據個人財務狀況自行評估，作者不對任何投資損失負責。

---

## 授權

本課程採用 [CC BY-NC 4.0](LICENSE) 授權：  
✅ 可以分享與改作（須署名）  
❌ 不得用於商業目的
