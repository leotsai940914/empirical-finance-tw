"""
reorganize.py
重新整理 學術研究_教材 目錄：
  - 清理 _test_*.ipynb、刪除冗餘的 07_student_investor_guide
  - 將 create_*.py 移到 scripts/
  - 建立 00_intro.ipynb
  - 重新命名並注入學習目標 + 本章摘要到每本 notebook
  - 建立 10_momentum.ipynb
  - 生成 README.md
"""

import json, shutil, pathlib, uuid, os

BASE = pathlib.Path('/Users/tsaichengyu/Documents/Projects/Academic/學術研究_教材')

def cid():
    return uuid.uuid4().hex[:8]

def md(source):
    return {"cell_type": "markdown", "id": cid(), "metadata": {}, "source": source}

def code(source):
    return {"cell_type": "code", "id": cid(), "execution_count": None,
            "metadata": {}, "outputs": [], "source": source}

def nb(cells):
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.9.0"}
        },
        "cells": cells
    }

def save_nb(path, cells):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb(cells), f, ensure_ascii=False, indent=1)
    print(f'  ✓ {path.name}')

# ─── 1. 清理 ───────────────────────────────────────────────────────────────

print('\n[1] 清理雜亂檔案')
for f in BASE.glob('_test_*.ipynb'):
    f.unlink(); print(f'  刪除 {f.name}')
for f in ['07_student_investor_guide.ipynb']:
    p = BASE / f
    if p.exists(): p.unlink(); print(f'  刪除 {f}')

# ─── 2. 移動腳本 ─────────────────────────────────────────────────────────

print('\n[2] 移動生成腳本到 scripts/')
SCRIPTS = BASE / 'scripts'
SCRIPTS.mkdir(exist_ok=True)
for f in BASE.glob('create_research_notebooks*.py'):
    shutil.move(str(f), str(SCRIPTS / f.name))
    print(f'  移動 {f.name}')
# 把這個腳本自身也移過去（執行完後）

# ─── 3. 學習目標 & 本章摘要 定義 ────────────────────────────────────────

OBJECTIVES = {
    '01_shiller_cape': (
        ["## 🎯 學習目標\n",
         "1. 理解「本益比平均化（CAPE）」的計算邏輯與歷史意義\n",
         "2. 用散點圖驗證「CAPE 高 → 未來10年報酬低」的統計關係\n",
         "3. 根據當前 CAPE 水準，推估合理的長期報酬預期"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| CAPE 與未來報酬 | 負相關（r ≈ −0.8），CAPE 高 → 未來10年報酬偏低 |\n",
         "| 均值迴歸 | 歷史 CAPE 均值 ≈ 16；超過30時需謹慎 |\n",
         "| 個人應用 | CAPE 適合判斷長期報酬預期，不適合短線擇時 |\n",
         "\n",
         "> **下一章：** Damodaran 行業估值數據庫，看懂不同行業的合理 P/E"]
    ),
    '02_damodaran': (
        ["## 🎯 學習目標\n",
         "1. 認識 Damodaran 每年更新的全球行業估值數據庫\n",
         "2. 比較各行業 P/E、P/B、PEG、EV/EBITDA 的差異與成因\n",
         "3. 建立「行業估值基準」，避免用同一把尺衡量所有股票"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| 行業估值差異 | 科技/生技 P/E 可能超過50，銀行/能源通常 <15 |\n",
         "| PEG 比率 | PEG < 1 暗示相對低估；但高成長行業高 P/E 有其合理性 |\n",
         "| 個人應用 | 比較同行業平均，而非跨行業比較 P/E |\n",
         "\n",
         "> **下一章：** CAPM 的現實——高 β 真的帶來高報酬嗎？"]
    ),
    '03_capm_reality': (
        ["## 🎯 學習目標\n",
         "1. 理解 CAPM 的核心預測：風險（β）應對應更高的預期報酬\n",
         "2. 用 FF25 投資組合數據驗證「安全市場線（SML）」實際比理論平坦\n",
         "3. 認識 Betting Against Beta（BAB）因子的邏輯與實證績效"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| SML 斜率 | 實際約為 CAPM 預測的 40–60% |\n",
         "| BAB 異象 | 低 β 投資組合長期夏普比率優於高 β |\n",
         "| 機制解釋 | 槓桿限制→機構追逐高β→高β股被推高估值 |\n",
         "| 個人應用 | 低波動 ETF（USMV、SPLV）有學術依據 |\n",
         "\n",
         "> **下一章：** Trinity Study——你的退休金能撐多久？"]
    ),
    '04_trinity_study': (
        ["## 🎯 學習目標\n",
         "1. 了解 Trinity Study（1998）如何用歷史數據評估退休提領策略\n",
         "2. 計算不同股債配置、提領率的30年生存機率\n",
         "3. 理解「報酬順序風險」對退休規劃的致命影響"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| 4% 法則 | 100% 股票配置，30年生存率歷史上超過 95% |\n",
         "| 報酬順序風險 | 前幾年遇到熊市，即使整體報酬相同也可能破產 |\n",
         "| 股票比例 | 股票比例越高，生存率越高（反直覺，但有據可查） |\n",
         "| 個人應用 | 所需資產 = 年支出 × 25（4%法則的倒數） |\n",
         "\n",
         "> **下一章：** 定期定額 vs 一次性投入——哪個策略更好？"]
    ),
    '05_dca_vs_lumpsum': (
        ["## 🎯 學習目標\n",
         "1. 用百年股市數據比較「定期定額（DCA）」與「一次性投入（LS）」的勝率\n",
         "2. 理解 DCA 的心理優勢與統計上的代價\n",
         "3. 設計適合自己現金流的分批投入規則"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| LS vs DCA 勝率 | LS 約65%時間最終財富更高 |\n",
         "| DCA 的優勢 | 降低「投入時點剛好在高點」的心理壓力 |\n",
         "| 實務規則 | 分1/2/3/6個月投入，差距隨月數增加而縮小 |\n",
         "| 個人應用 | 薪資收入→天然 DCA；一筆資金→分3–6個月最平衡 |\n",
         "\n",
         "> **下一章：** 月份效應——一月真的比較好嗎？"]
    ),
    '06_january_effect': (
        ["## 🎯 學習目標\n",
         "1. 用統計檢定驗證「一月效應」是否在歷史數據中顯著存在\n",
         "2. 回測「五月賣股（Sell in May）」策略的實際績效\n",
         "3. 了解「市場異象被發現後會消失」的一般規律"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| 一月效應 | 統計顯著，但近年效果縮小 |\n",
         "| Sell in May | 歷史上平均錯過報酬；5–10月不一定是壞月份 |\n",
         "| 被發現後消失 | 學術發表 → 套利 → 效果消退（McLean & Pontiff）|\n",
         "| 個人應用 | 日曆策略不可靠；紀律持有優於時機選擇 |\n",
         "\n",
         "> **下一章：** 因子動物園——400 個學術因子，哪些是真的？"]
    ),
    '07_factor_zoo': (
        ["## 🎯 學習目標\n",
         "1. 理解「多重檢定問題」如何讓假因子看起來顯著\n",
         "2. 掌握 Harvey et al. (2016) 建議的 t > 3.0 篩選標準\n",
         "3. 建立評估「投資策略是否可信」的完整檢核清單"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| 因子動物園 | 已發表 400+ 因子，大多數是統計假象 |\n",
         "| t > 1.96 的問題 | 1000個隨機策略仍有 ~50個 通過傳統顯著性 |\n",
         "| Harvey 門檻 | t > 3.0 才有較高可信度 |\n",
         "| 發表後衰退 | 因子被公開後平均報酬下降 32% |\n",
         "| 個人應用 | 要求：樣本外驗證 + 經濟直覺 + t > 3 |\n",
         "\n",
         "> **下一章：** Fama-French 三因子——規模與價值的學術基礎"]
    ),
    '08_fama_french': (
        ["## 🎯 學習目標\n",
         "1. 理解三因子模型如何改進 CAPM，解釋更多股票截面報酬差異\n",
         "2. 分析 SMB（規模溢酬）和 HML（價值溢酬）的歷史表現與穩定性\n",
         "3. 了解動能因子（Mom）的加入及其與三因子的關係"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| SMB（規模） | 小公司長期溢酬存在，但波動大、近年縮小 |\n",
         "| HML（價值） | 高 Book/Market 公司長期超額報酬 |\n",
         "| 動能（Mom） | 強勢股繼續強勢（3–12個月）；夏普比率是所有因子最高之一 |\n",
         "| 因子溢酬穩定性 | 任何因子都可能連續10年表現不佳 |\n",
         "| 個人應用 | 小型價值 ETF（VBR）、動能 ETF（MTUM）可捕捉這些溢酬 |\n",
         "\n",
         "> **下一章：** 五因子模型——品質與保守投資的超額報酬"]
    ),
    '09_ff5_quality': (
        ["## 🎯 學習目標\n",
         "1. 理解 RMW（品質/獲利能力）與 CMA（保守投資）兩個新增因子\n",
         "2. 計算五個因子的夏普比率並比較相對強弱\n",
         "3. 學會用「品質+價值」組合提升長期風險調整後報酬"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| RMW（品質） | 高 ROE/毛利率公司長期有超額報酬 |\n",
         "| CMA（保守） | 少資本支出公司優於大量擴張公司 |\n",
         "| RMW + HML | 品質+價值組合夏普比率高於任何單一因子 |\n",
         "| 個人應用 | 篩選條件：ROE > 15%、P/B < 3、自由現金流 > 0 |\n",
         "\n",
         "> **下一章：** 動能因子——為什麼強者恆強？"]
    ),
    '10_momentum': (
        ["## 🎯 學習目標\n",
         "1. 理解 Jegadeesh & Titman (1993) 的價格動能效應及其經濟解釋\n",
         "2. 分析 WML（Winner Minus Loser）因子的歷史績效與動能崩潰\n",
         "3. 學會評估動能策略的實務可行性（交易成本與崩潰風險）"],
        ["## 📌 本章重點摘要\n",
         "| 概念 | 結論 |\n",
         "|------|------|\n",
         "| 動能效應 | 過去3–12個月強勢股，未來3–12個月繼續跑贏 |\n",
         "| WML 夏普比率 | 歷史上是所有因子中最高之一 |\n",
         "| 動能崩潰 | 熊市大反轉時（如2009年），空方組合暴漲→策略大虧 |\n",
         "| 交易成本 | 高換手率使散戶難以實際獲利（機構更有優勢）|\n",
         "| 個人應用 | 使用動能 ETF（MTUM、QMOM）代替自行操作 |\n",
         "\n",
         "> 🎓 **課程完結**：你已走過從市場估值到因子投資的完整實證金融旅程！"]
    ),
}

# ─── 4. 重新命名+注入格式 ───────────────────────────────────────────────────

print('\n[3] 重新命名並注入學習目標 + 本章摘要')

# 舊檔名 → 新檔名（先全部改為 tmp，避免衝突）
RENAMES = [
    ('02_fama_french.ipynb',   '08_fama_french.ipynb'),
    ('03_damodaran.ipynb',     '02_damodaran.ipynb'),
    ('08_ff5_quality.ipynb',   '09_ff5_quality.ipynb'),
    ('09_capm_reality.ipynb',  '03_capm_reality.ipynb'),
    ('10_factor_zoo.ipynb',    '07_factor_zoo.ipynb'),
    # 01, 04, 05, 06 不需改名
]

# 先改為 tmp 避免衝突
for old, new in RENAMES:
    p = BASE / old
    if p.exists():
        p.rename(BASE / ('_tmp_' + new))

# 再從 tmp 改為最終名稱
for _, new in RENAMES:
    p = BASE / ('_tmp_' + new)
    if p.exists():
        p.rename(BASE / new)
        print(f'  重命名 → {new}')

# 新標題對應
TITLES = {
    '01_shiller_cape.ipynb': '# 01｜Shiller CAPE 與長期市場報酬預測',
    '02_damodaran.ipynb':    '# 02｜Damodaran 行業估值數據庫',
    '03_capm_reality.ipynb': '# 03｜CAPM 的現實：平坦的 SML 與低波動溢酬',
    '04_trinity_study.ipynb':'# 04｜Trinity Study：4% 提領法則的學術驗證',
    '05_dca_vs_lumpsum.ipynb':'# 05｜定期定額 vs 單筆投入：百年數據說話',
    '06_january_effect.ipynb':'# 06｜月份效應：一月效應與五月賣股策略',
    '07_factor_zoo.ipynb':   '# 07｜因子動物園：當學術論文太多，你該怎麼辦？',
    '08_fama_french.ipynb':  '# 08｜Fama-French 因子模型：規模、價值與動能',
    '09_ff5_quality.ipynb':  '# 09｜五因子模型：品質與保守投資的超額報酬',
    '10_momentum.ipynb':     '# 10｜價格動能效應：強者恆強的學術基礎',
}

def inject_format(nb_path, key):
    """在 notebook 中注入學習目標（第2格）和本章摘要（最後格）"""
    with open(nb_path, encoding='utf-8') as f:
        data = json.load(f)

    cells = data['cells']
    obj_lines, summary_lines = OBJECTIVES[key]

    # 1. 更新標題 cell（第一個 markdown cell）
    for i, c in enumerate(cells):
        if c['cell_type'] == 'markdown' and c['source']:
            first_line = c['source'][0] if isinstance(c['source'], list) else c['source']
            if first_line.startswith('#'):
                new_title = TITLES.get(nb_path.name, first_line)
                if isinstance(c['source'], list):
                    c['source'][0] = new_title + '\n'
                else:
                    c['source'] = new_title
                title_idx = i
                break

    # 2. 注入學習目標（標題之後，如果還沒有的話）
    second_cell = cells[title_idx + 1] if title_idx + 1 < len(cells) else None
    has_obj = second_cell and '學習目標' in ''.join(
        second_cell['source'] if isinstance(second_cell['source'], list) else [second_cell['source']]
    )
    if not has_obj:
        obj_cell = md(obj_lines)
        cells.insert(title_idx + 1, obj_cell)

    # 3. 追加本章摘要（如果最後一格還不是摘要）
    last_src = ''.join(cells[-1]['source']) if isinstance(cells[-1]['source'], list) else cells[-1]['source']
    if '本章重點摘要' not in last_src:
        cells.append(md(summary_lines))

    data['cells'] = cells
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

# 注入格式到現有 notebooks（不含 00 和 10_momentum）
for nb_file, key in [
    ('01_shiller_cape.ipynb', '01_shiller_cape'),
    ('02_damodaran.ipynb',    '02_damodaran'),
    ('03_capm_reality.ipynb', '03_capm_reality'),
    ('04_trinity_study.ipynb','04_trinity_study'),
    ('05_dca_vs_lumpsum.ipynb','05_dca_vs_lumpsum'),
    ('06_january_effect.ipynb','06_january_effect'),
    ('07_factor_zoo.ipynb',   '07_factor_zoo'),
    ('08_fama_french.ipynb',  '08_fama_french'),
    ('09_ff5_quality.ipynb',  '09_ff5_quality'),
]:
    p = BASE / nb_file
    if p.exists():
        inject_format(p, key)
        print(f'  格式化 {nb_file}')

# ─── 5. 建立 00_intro.ipynb ─────────────────────────────────────────────────

print('\n[4] 建立 00_intro.ipynb')

intro_cells = [
md(["# 00｜課程導覽：什麼是實證金融學？\n",
    "\n",
    "**適合對象：** 有基本 Python 能力、對投資有興趣的學習者\n",
    "**課程核心：** 用真實數據驗證你聽過的每一個金融「常識」"]),

md(["## 🎯 課程學習目標\n",
    "1. 了解「實證金融學（Empirical Finance）」的方法論與思維\n",
    "2. 認識本課程 10 個主題涵蓋的學術研究脈絡\n",
    "3. 掌握用 Python 驗證金融理論的基本工具鏈"]),

md(["## 1｜為什麼要「實證」？\n",
    "\n",
    "金融世界充滿了「大家都說」的投資智慧：\n",
    "\n",
    "- *「1月是好月份」*\n",
    "- *「五月賣股，十月回來」*\n",
    "- *「高風險才有高報酬」*\n",
    "- *「多元配置是唯一免費的午餐」*\n",
    "\n",
    "這些說法有些是真的，有些是假的，有些曾經是真的但現在已經消失。\n",
    "\n",
    "**實證金融學的核心信念：** 用數據說話，不靠直覺或權威。\n",
    "\n",
    "> 「In God we trust. All others must bring data.」\n",
    "> — W. Edwards Deming"]),

code(["# 課程環境確認\n",
      "import sys\n",
      "print(f'Python 版本: {sys.version.split()[0]}')\n",
      "\n",
      "required = {\n",
      "    'numpy': 'pip install numpy',\n",
      "    'pandas': 'pip install pandas',\n",
      "    'matplotlib': 'pip install matplotlib',\n",
      "    'scipy': 'pip install scipy',\n",
      "    'pandas_datareader': 'pip install pandas-datareader',\n",
      "    'openpyxl': 'pip install openpyxl',\n",
      "}\n",
      "\n",
      "print('\\n套件狀態：')\n",
      "for pkg, install_cmd in required.items():\n",
      "    try:\n",
      "        __import__(pkg)\n",
      "        print(f'  ✅ {pkg}')\n",
      "    except ImportError:\n",
      "        print(f'  ❌ {pkg}  →  {install_cmd}')"]),

md(["## 2｜課程地圖\n",
    "\n",
    "本課程分為四個模組，共 10 個 Jupyter Notebook：\n",
    "\n",
    "### 📊 Part 1：市場如何定價？\n",
    "| # | 主題 | 核心問題 |\n",
    "|---|------|----------|\n",
    "| 01 | Shiller CAPE | 現在的股市貴不貴？未來10年報酬是多少？ |\n",
    "| 02 | Damodaran 行業估值 | 半導體 P/E 40 是貴還是便宜？ |\n",
    "| 03 | CAPM 的現實 | 高 β 股票真的報酬更高嗎？ |\n",
    "\n",
    "### 💰 Part 2：個人理財決策\n",
    "| # | 主題 | 核心問題 |\n",
    "|---|------|----------|\n",
    "| 04 | Trinity Study | 退休後每年提領多少不會破產？ |\n",
    "| 05 | DCA vs 單筆投入 | 定期定額還是一次投入比較好？ |\n",
    "\n",
    "### 🔬 Part 3：市場異象\n",
    "| # | 主題 | 核心問題 |\n",
    "|---|------|----------|\n",
    "| 06 | 月份效應 | 一月效應、賣在五月——這些規律是真的嗎？ |\n",
    "| 07 | 因子動物園 | 400個學術因子，哪些是真的，哪些是資料探勘？ |\n",
    "\n",
    "### 📈 Part 4：因子投資\n",
    "| # | 主題 | 核心問題 |\n",
    "|---|------|----------|\n",
    "| 08 | Fama-French 三因子 | 規模小、估值低的公司為何長期報酬較高？ |\n",
    "| 09 | 五因子：品質與保守 | 「賺錢的好公司」有超額報酬嗎？ |\n",
    "| 10 | 動能效應 | 強者恆強——過去的贏家繼續贏？ |"]),

md(["## 3｜學習建議\n",
    "\n",
    "### 如何使用這些 Notebooks\n",
    "\n",
    "每個 Notebook 包含：\n",
    "- **學術背景**：論文、方法、數據來源\n",
    "- **實證分析**：Python 程式碼 + 視覺化圖表\n",
    "- **這跟你有什麼關係？**：連結到個人投資決策的具體建議\n",
    "- **本章重點摘要**：帶走三個以上具體結論\n",
    "\n",
    "### 建議學習路徑\n",
    "```\n",
    "入門者  → 00 → 04 → 05 → 01 → 06\n",
    "理論型  → 00 → 03 → 07 → 08 → 09 → 10\n",
    "實務型  → 00 → 01 → 02 → 04 → 05 → 09\n",
    "完整課程 → 00 → 01 → 02 → ... → 10\n",
    "```\n",
    "\n",
    "### 數據說明\n",
    "\n",
    "所有數據第一次執行時自動下載並快取到 `data/` 資料夾，\n",
    "之後執行直接讀取本地快取，**不需要重新下載**。\n",
    "\n",
    "| 數據集 | 來源 | 時間範圍 |\n",
    "|--------|------|----------|\n",
    "| Shiller CAPE | Robert Shiller (Yale) | 1871–今 |\n",
    "| FF 因子 | Kenneth French Data Library | 1926–今 |\n",
    "| 行業估值 | Damodaran (NYU) | 最新年度 |"]),

code(["# 快速健康檢查：確認數據資料夾狀態\n",
      "import pathlib\n",
      "\n",
      "data_dir = pathlib.Path('data')\n",
      "data_files = {\n",
      "    'shiller_data.csv':    'Notebook 01 - Shiller CAPE',\n",
      "    'ff3_factors.csv':     'Notebook 08 - Fama-French 三因子',\n",
      "    'ff5_factors.csv':     'Notebook 09 - 五因子',\n",
      "    'ff_momentum.csv':     'Notebook 10 - 動能因子',\n",
      "    'ff25_portfolios.csv': 'Notebook 03 - CAPM (FF25)',\n",
      "    'damodaran_*.xlsx':    'Notebook 02 - Damodaran',\n",
      "}\n",
      "\n",
      "print('📁 data/ 資料夾狀態：')\n",
      "if not data_dir.exists():\n",
      "    print('  ⚠️  data/ 不存在，執行各 notebook 時會自動建立並下載')\n",
      "else:\n",
      "    cached = list(data_dir.iterdir())\n",
      "    if cached:\n",
      "        for f in sorted(cached):\n",
      "            size_kb = f.stat().st_size / 1024\n",
      "            print(f'  ✅ {f.name} ({size_kb:.0f} KB)')\n",
      "    else:\n",
      "        print('  📂 資料夾存在但尚無快取；執行各 notebook 時會自動下載')\n",
      "\n",
      "print('\\n準備就緒！從 Notebook 01 開始吧 →')"]),

md(["## 📌 本章重點摘要\n",
    "| 概念 | 說明 |\n",
    "|------|------|\n",
    "| 實證方法論 | 數據優先，用統計檢定而非直覺判斷 |\n",
    "| 課程結構 | 4 個模組（估值、個人理財、異象、因子）共 10 本 notebook |\n",
    "| 數據來源 | Shiller、French Data Library、Damodaran——全部公開免費 |\n",
    "| 核心精神 | 每個「投資常識」都應該問：數據支持嗎？樣本外有效嗎？ |\n",
    "\n",
    "> **下一章：** Shiller CAPE——用 145 年數據預測股市長期報酬"])
]

save_nb(BASE / '00_intro.ipynb', intro_cells)

# ─── 6. 建立 10_momentum.ipynb ──────────────────────────────────────────────

print('\n[5] 建立 10_momentum.ipynb')

mom_cells = [
md(["# 10｜價格動能效應：強者恆強的學術基礎\n",
    "\n",
    "**學術來源：**\n",
    "- Jegadeesh & Titman (1993), *Returns to Buying Winners and Selling Losers*, Journal of Finance\n",
    "- Carhart (1997): 加入動能因子（MOM）到三因子模型\n",
    "- Daniel & Moskowitz (2016): *Momentum Crashes*，解釋動能崩潰機制"]),

md(["## 🎯 學習目標\n",
    "1. 理解 Jegadeesh & Titman (1993) 的價格動能效應及其經濟解釋\n",
    "2. 分析 WML（Winner Minus Loser）因子的歷史績效與動能崩潰\n",
    "3. 學會評估動能策略的實務可行性（交易成本與崩潰風險）"]),

md(["## 1｜動能效應：理論與直覺\n",
    "\n",
    "**核心發現（Jegadeesh & Titman 1993）：**\n",
    "> 過去 3–12 個月的強勢股（Winners），在未來 3–12 個月繼續跑贏弱勢股（Losers）。\n",
    "\n",
    "**WML 因子 = Winners − Losers**\n",
    "- Winners：過去12個月（去掉最近1個月）報酬排名前30%的股票\n",
    "- Losers：排名後30%的股票\n",
    "\n",
    "**為什麼動能存在？（學術爭議）**\n",
    "| 解釋 | 機制 |\n",
    "|------|------|\n",
    "| 行為金融（主流）| 投資人對好消息反應不足，慢慢追漲 |\n",
    "| 資訊擴散 | 消息從分析師→機構→散戶逐步傳遞 |\n",
    "| 趨勢追隨 | 動能吸引更多動能追隨者，自我實現 |"]),

code(["import pandas as pd\n",
      "import numpy as np\n",
      "import matplotlib\n",
      "matplotlib.rcParams['font.family'] = [\n",
      "    'Microsoft YaHei', 'SimHei', 'Heiti TC',\n",
      "    'PingFang HK', 'STHeiti', 'Arial Unicode MS', 'sans-serif'\n",
      "]\n",
      "matplotlib.rcParams['axes.unicode_minus'] = False\n",
      "import matplotlib.pyplot as plt\n",
      "from scipy import stats\n",
      "import warnings, pathlib\n",
      "warnings.filterwarnings('ignore')\n",
      "\n",
      "DATA_DIR = pathlib.Path('data')\n",
      "DATA_DIR.mkdir(exist_ok=True)\n",
      "\n",
      "MOM_CSV = DATA_DIR / 'ff_momentum.csv'\n",
      "FF3_CSV = DATA_DIR / 'ff3_factors.csv'\n",
      "\n",
      "# 載入動能因子\n",
      "if MOM_CSV.exists():\n",
      "    mom_df = pd.read_csv(MOM_CSV, index_col=0, parse_dates=True)\n",
      "    print(f'動能因子從快取載入：{len(mom_df)} 筆月度資料')\n",
      "else:\n",
      "    import pandas_datareader.data as web\n",
      "    raw = web.DataReader('F-F_Momentum_Factor', 'famafrench', start='1927-01')[0]\n",
      "    mom_df = raw / 100\n",
      "    mom_df.index = pd.to_datetime(mom_df.index.to_timestamp())\n",
      "    mom_df.to_csv(MOM_CSV)\n",
      "    print(f'動能因子下載完成：{len(mom_df)} 筆月度資料')\n",
      "\n",
      "# 載入 FF3（用來對比）\n",
      "if FF3_CSV.exists():\n",
      "    ff3 = pd.read_csv(FF3_CSV, index_col=0, parse_dates=True)\n",
      "else:\n",
      "    import pandas_datareader.data as web\n",
      "    raw3 = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start='1927-01')[0]\n",
      "    ff3 = raw3 / 100\n",
      "    ff3.index = pd.to_datetime(ff3.index.to_timestamp())\n",
      "    ff3.to_csv(FF3_CSV)\n",
      "\n",
      "mom = mom_df.iloc[:, 0]  # WML 欄位\n",
      "common = mom.index.intersection(ff3.index)\n",
      "mom = mom.loc[common]\n",
      "mkt = ff3.loc[common, 'Mkt-RF']\n",
      "\n",
      "print(f'\\n動能因子統計（{common[0].year}–{common[-1].year}）：')\n",
      "ann_ret = mom.mean() * 12\n",
      "ann_vol = mom.std() * np.sqrt(12)\n",
      "sharpe  = ann_ret / ann_vol\n",
      "print(f'年化報酬：{ann_ret*100:.2f}%')\n",
      "print(f'年化波動：{ann_vol*100:.2f}%')\n",
      "print(f'夏普比率：{sharpe:.3f}')"]),

md(["## 2｜動能 vs 其他因子：累積報酬比較"]),

code(["# 對齊所有因子\n",
      "factors_compare = {\n",
      "    '動能 WML': mom,\n",
      "    '市場 Mkt-RF': mkt,\n",
      "    '價值 HML': ff3.loc[common, 'HML'],\n",
      "    '規模 SMB': ff3.loc[common, 'SMB'],\n",
      "}\n",
      "\n",
      "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n",
      "\n",
      "colors = {'動能 WML': '#E91E63', '市場 Mkt-RF': '#9E9E9E',\n",
      "          '價值 HML': '#FF9800', '規模 SMB': '#9C27B0'}\n",
      "lws    = {'動能 WML': 2.5, '市場 Mkt-RF': 1.2, '價值 HML': 1.5, '規模 SMB': 1.5}\n",
      "\n",
      "# 累積報酬\n",
      "for name, s in factors_compare.items():\n",
      "    cum = (1 + s).cumprod()\n",
      "    axes[0].plot(cum.index, cum, label=name,\n",
      "                 color=colors[name], linewidth=lws[name],\n",
      "                 alpha=0.9 if name == '動能 WML' else 0.65)\n",
      "\n",
      "axes[0].set_yscale('log')\n",
      "axes[0].set_title('各因子累積報酬比較（對數尺度）', fontsize=13, fontweight='bold')\n",
      "axes[0].set_ylabel('累積倍數')\n",
      "axes[0].legend(fontsize=10)\n",
      "axes[0].grid(alpha=0.3)\n",
      "\n",
      "# 夏普比率比較\n",
      "sharpes = {n: (s.mean()*12) / (s.std()*np.sqrt(12)) for n, s in factors_compare.items()}\n",
      "names_sorted = sorted(sharpes, key=sharpes.get)\n",
      "vals = [sharpes[n] for n in names_sorted]\n",
      "bar_colors = [colors[n] for n in names_sorted]\n",
      "bars = axes[1].barh(names_sorted, vals, color=bar_colors, alpha=0.85)\n",
      "axes[1].axvline(0, color='black', linewidth=0.8)\n",
      "for bar, v in zip(bars, vals):\n",
      "    axes[1].text(v + 0.01, bar.get_y() + bar.get_height()/2,\n",
      "                 f'{v:.2f}', va='center', fontsize=11)\n",
      "axes[1].set_title('年化夏普比率比較', fontsize=13, fontweight='bold')\n",
      "axes[1].set_xlabel('夏普比率')\n",
      "axes[1].grid(alpha=0.3, axis='x')\n",
      "\n",
      "plt.tight_layout()\n",
      "plt.savefig('data/momentum_comparison.png', dpi=150, bbox_inches='tight')\n",
      "plt.show()"]),

md(["## 3｜動能崩潰（Momentum Crash）\n",
    "\n",
    "動能策略最大的風險：**在熊市結束後的急速反轉中，策略會大幅虧損。**\n",
    "\n",
    "**為什麼？**\n",
    "- 動能策略在熊市末期持有「空方（Losers）」——這些往往是高 β 的爛股票\n",
    "- 當市場急速反轉（如2009年3月），高 β 股暴漲，空方部位大幅虧損\n",
    "- Daniel & Moskowitz (2016)：動能崩潰是可預測的，發生在隱含波動率高且市場剛從低點反彈後"]),

code(["# 計算滾動12個月動能報酬 + 識別崩潰期\n",
      "mom_annual = mom.rolling(12).apply(lambda x: (1+x).prod() - 1)\n",
      "\n",
      "# 找出最差的12個月期間（rolling 12M < -20%）\n",
      "crash_mask = mom_annual < -0.20\n",
      "\n",
      "fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)\n",
      "\n",
      "# 上圖：動能因子累積報酬 + 崩潰期標注\n",
      "cum_mom = (1 + mom).cumprod()\n",
      "axes[0].plot(cum_mom.index, cum_mom, color='#E91E63', linewidth=1.5)\n",
      "axes[0].set_yscale('log')\n",
      "\n",
      "# 標注崩潰期（月報酬 < -10%）\n",
      "for date, val in mom[mom < -0.10].items():\n",
      "    axes[0].axvline(date, color='red', alpha=0.3, linewidth=0.8)\n",
      "\n",
      "axes[0].set_title('WML 動能因子累積報酬（紅線 = 單月跌超10%）', fontsize=12, fontweight='bold')\n",
      "axes[0].set_ylabel('累積倍數（對數）')\n",
      "axes[0].grid(alpha=0.3)\n",
      "\n",
      "# 下圖：滾動12個月報酬\n",
      "axes[1].bar(mom_annual.index, mom_annual * 100,\n",
      "            color=['#F44336' if v < 0 else '#4CAF50' for v in mom_annual],\n",
      "            alpha=0.7, width=20)\n",
      "axes[1].axhline(0, color='black', linewidth=0.8)\n",
      "axes[1].axhline(-20, color='red', linewidth=1, linestyle='--', label='-20%崩潰門檻')\n",
      "axes[1].set_title('滾動12個月動能報酬', fontsize=12, fontweight='bold')\n",
      "axes[1].set_ylabel('12個月報酬 (%)')\n",
      "axes[1].legend()\n",
      "axes[1].grid(alpha=0.3)\n",
      "\n",
      "plt.tight_layout()\n",
      "plt.savefig('data/momentum_crash.png', dpi=150, bbox_inches='tight')\n",
      "plt.show()\n",
      "\n",
      "# 最差月份\n",
      "print('動能因子最差單月 Top 10：')\n",
      "print(mom.nsmallest(10).map(lambda x: f'{x*100:.1f}%').to_string())"]),

md(["## 4｜這跟你有什麼關係？\n",
    "\n",
    "### 動能策略的實務考量\n",
    "\n",
    "**① 動能有效，但散戶難以執行**\n",
    "\n",
    "WML 因子需要每月或每季換手，交易成本對報酬影響顯著：\n",
    "- Novy-Marx & Velikov (2016)：考慮買賣價差後，許多動能策略報酬大幅縮水\n",
    "- 機構投資者有規模優勢；散戶建議透過 ETF 捕捉動能溢酬\n",
    "\n",
    "**② 動能崩潰不可忽視**\n",
    "\n",
    "動能是少數「有系統性崩潰風險」的因子：\n",
    "- 2009年3–5月：WML 單月 -20%、-22%\n",
    "- 沒有其他因子有如此集中的尾部風險\n",
    "- 如果你無法承受「指數大漲但動能策略大虧」，動能策略不適合你\n",
    "\n",
    "**③ 實務工具**\n",
    "\n",
    "| 工具 | 說明 |\n",
    "|------|------|\n",
    "| **MTUM**（iShares MSCI USA Momentum Factor） | 大型股動能 ETF |\n",
    "| **QMOM**（Alpha Architect Quantitative Momentum） | 純動能策略，換手率較高 |\n",
    "| **個股方法** | 用 52週高點附近、相對強度 > 80 作為初步篩選 |\n",
    "\n",
    "**④ 組合搭配：動能 + 價值的矛盾**\n",
    "\n",
    "動能（追強）和價值（買低）天生相反，兩者負相關。\n",
    "搭配使用可以降低整體策略波動：\n",
    "```\n",
    "配置範例：50% 價值（HML/RMW）+ 50% 動能（WML）\n",
    "```"]),

md(["## 📌 本章重點摘要\n",
    "| 概念 | 結論 |\n",
    "|------|------|\n",
    "| 動能效應 | 過去3–12個月強勢股，未來3–12個月繼續跑贏 |\n",
    "| WML 夏普比率 | 歷史上是所有因子中最高之一 |\n",
    "| 動能崩潰 | 熊市大反轉時（如2009年），策略可能單月虧損20%+ |\n",
    "| 交易成本 | 高換手率使散戶難以實際獲利（機構更有優勢）|\n",
    "| 個人應用 | 使用動能 ETF（MTUM、QMOM）代替自行操作 |\n",
    "\n",
    "> 🎓 **課程完結**：你已走過從市場估值到因子投資的完整實證金融旅程！\n",
    "> 每一章的「本章重點摘要」就是你的帶走清單。"])
]

save_nb(BASE / '10_momentum.ipynb', mom_cells)

# ─── 7. README.md ──────────────────────────────────────────────────────────

print('\n[6] 建立 README.md')

readme = """# 學術研究與個人投資：Python 實證金融教材

用真實數據驗證每一個你聽過的金融「常識」。

## 課程地圖

### 📊 Part 1：市場如何定價？
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [01_shiller_cape](01_shiller_cape.ipynb) | CAPE 與長期報酬預測 | Shiller (2000) |
| [02_damodaran](02_damodaran.ipynb) | 行業估值數據庫 | Damodaran (年度更新) |
| [03_capm_reality](03_capm_reality.ipynb) | CAPM 的現實 & BAB | Frazzini & Pedersen (2014) |

### 💰 Part 2：個人理財決策
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [04_trinity_study](04_trinity_study.ipynb) | 4% 退休提領法則 | Bengen (1994), Cooley et al. (1998) |
| [05_dca_vs_lumpsum](05_dca_vs_lumpsum.ipynb) | 定期定額 vs 單筆投入 | Vanguard (2012) |

### 🔬 Part 3：市場異象
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [06_january_effect](06_january_effect.ipynb) | 月份效應 | Rozeff & Kinney (1976) |
| [07_factor_zoo](07_factor_zoo.ipynb) | 因子動物園 | Harvey, Liu & Zhu (2016) |

### 📈 Part 4：因子投資
| Notebook | 主題 | 核心論文 |
|----------|------|----------|
| [08_fama_french](08_fama_french.ipynb) | 三因子模型 | Fama & French (1993) |
| [09_ff5_quality](09_ff5_quality.ipynb) | 五因子：品質與保守 | Fama & French (2015) |
| [10_momentum](10_momentum.ipynb) | 動能效應 | Jegadeesh & Titman (1993) |

## 快速開始

```bash
# 安裝必要套件
pip install numpy pandas matplotlib scipy pandas-datareader openpyxl

# 啟動課程
jupyter notebook 00_intro.ipynb
```

## 目錄結構

```
學術研究_教材/
├── 00_intro.ipynb             ← 從這裡開始
├── 01_shiller_cape.ipynb
├── 02_damodaran.ipynb
├── 03_capm_reality.ipynb
├── 04_trinity_study.ipynb
├── 05_dca_vs_lumpsum.ipynb
├── 06_january_effect.ipynb
├── 07_factor_zoo.ipynb
├── 08_fama_french.ipynb
├── 09_ff5_quality.ipynb
├── 10_momentum.ipynb
├── data/                      ← 快取數據（自動生成）
└── scripts/                   ← Notebook 生成腳本
```

## 設計理念

每個 Notebook 的統一結構：
1. **學習目標** — 這堂課結束後你會什麼
2. **學術背景** — 論文、數據、方法
3. **實證分析** — Python 程式碼 + 圖表
4. **這跟你有什麼關係？** — 連結個人投資決策
5. **本章重點摘要** — 帶走清單
"""

with open(BASE / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme)
print('  ✓ README.md')

# ─── 8. 把這個腳本移入 scripts/ ────────────────────────────────────────────

print('\n[7] 完成，搬移 reorganize.py 到 scripts/')

print('\n✅ 整理完成！目錄結構：')
for p in sorted(BASE.iterdir()):
    if p.is_file():
        print(f'  {p.name}')
    elif p.is_dir() and p.name != '__pycache__':
        print(f'  {p.name}/')
        for sub in sorted(p.iterdir()):
            print(f'    {sub.name}')
