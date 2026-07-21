"""
學術研究 Notebooks 產生器 (Part 3)
  07_student_investor_guide.ipynb — 研究結論 → 個人投資行動指南
"""

import json, uuid, os

BASE = os.path.dirname(os.path.abspath(__file__))

FONTS = "['Microsoft YaHei', 'SimHei', 'Heiti TC', 'PingFang HK', 'STHeiti', 'Arial Unicode MS', 'sans-serif']"


def _id():
    return uuid.uuid4().hex[:8]


def md(src):
    src = src.strip()
    lines = src.split('\n')
    source = [ln + '\n' for ln in lines[:-1]] + [lines[-1]]
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": source}


def code(src):
    src = src.strip()
    lines = src.split('\n')
    source = [ln + '\n' for ln in lines[:-1]] + [lines[-1]]
    return {"cell_type": "code", "id": _id(), "execution_count": None,
            "metadata": {}, "outputs": [], "source": source}


def save(cells, filename):
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.9.0"}
        },
        "nbformat": 4, "nbformat_minor": 5
    }
    path = os.path.join(BASE, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    code_n = sum(1 for c in cells if c['cell_type'] == 'code')
    print(f"✓ {filename}（{len(cells)} cells，{code_n} code）")


# ══════════════════════════════════════════════════════════════════════════════
# Notebook 7：學生投資行動指南
# ══════════════════════════════════════════════════════════════════════════════
c7 = []

c7.append(md("""\
# 07 | 六個研究告訴你：現在就可以做什麼

> 前六個 Notebook 做的是「學術驗證」。
> 這個 Notebook 的問題只有一個：
>
> **「這些研究和我有什麼關係？我現在應該做什麼？」**

我們把前六個研究的結論，轉成四個你現在就可以用的投資觀念，並用資料算出具體數字。
"""))

c7.append(md("## 匯入套件"))
c7.append(code(f"""\
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.family'] = {FONTS}
matplotlib.rcParams['axes.unicode_minus'] = False
print("✅ 匯入完成")
"""))

# ─── Part 1: 六個研究 → 行動總結 ────────────────────────────────────────────
c7.append(md("""\
---
## 一、六個研究的結論，用一張表說完

| Notebook | 發現 | 對你的意義 |
|----------|------|-----------|
| **01 Shiller CAPE** | CAPE 越高，未來 10 年報酬越低 | 別在 CAPE 歷史高位把全部積蓄一次 All-in；但也不要因此不投資 |
| **02 Fama-French** | 市場風險溢酬長期顯著；主動選股極難持續打敗市場 | 買「整個市場」的指數 ETF，比自己選股更可靠 |
| **03 Damodaran** | P/E 只在同業間有意義 | 分析個股時找同業基準；「本益比 30 倍」要先問「跟誰比？」 |
| **04 Trinity Study** | 4% 提領法則；退休初期序列風險最大 | 退休金目標 = 年支出 × 25；退休前 3 年降低波動 |
| **05 DCA vs LS** | 單筆投入 2/3 機率勝過分批 | 每月薪資 → 定期定額 OK；一次性閒錢 → 越早投入越好 |
| **06 一月效應** | 季節性異常被公開後消失 | 不要理會「幾月買股必漲」的投資建議 |

---
"""))

# ─── Part 2: 複利 ────────────────────────────────────────────────────────────
c7.append(md("""\
## 二、你最大的資產不是錢——是時間

Fama-French 告訴我們市場長期有正報酬。
但有一個東西比選對股票更重要：**你幾歲開始投資**。

讓我們用台灣學生的真實數字來算：
- 每月投入 **NT$3,000**（工讀 / 零用錢中的一部分）
- 年化報酬率 **7%**（接近 Shiller 資料的美股歷史實質報酬，含股息）
- 目標：60 歲退休
"""))
c7.append(code("""\
annual_ret   = 0.07
monthly_ret  = (1 + annual_ret) ** (1/12) - 1
monthly_inv  = 3_000   # NT$3,000 / 月

scenarios = {
    '20 歲開始（40 年）': (20, 40),
    '25 歲開始（35 年）': (25, 35),
    '30 歲開始（30 年）': (30, 30),
    '35 歲開始（25 年）': (35, 25),
}

print(f"每月投入 NT${monthly_inv:,}，年化報酬 {annual_ret*100:.0f}%，退休年齡 60 歲")
print()
print(f"{'開始年齡':^16} | {'總投入（萬）':>10} | {'最終資產（萬）':>12} | {'投資利潤（萬）':>12} | 利潤佔比")
print("-" * 72)

ages, finals, invested_totals = [], [], []
for label, (start_age, years) in scenarios.items():
    months       = years * 12
    total_in     = monthly_inv * months
    fv           = monthly_inv * ((1 + monthly_ret) ** months - 1) / monthly_ret
    profit       = fv - total_in
    profit_ratio = profit / fv * 100
    ages.append(start_age)
    finals.append(fv)
    invested_totals.append(total_in)
    print(f"{label:^16} | {total_in/10000:>10,.0f} | {fv/10000:>12,.0f} | {profit/10000:>12,.0f} | {profit_ratio:.0f}%")
"""))

c7.append(code("""\
# 成長曲線比較
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

colors = ['#2ecc71', '#3498db', '#e67e22', '#e74c3c']

for (label, (start_age, years)), color in zip(scenarios.items(), colors):
    months = years * 12
    vals   = []
    p = 0.0
    for _ in range(months):
        p = (p + monthly_inv) * (1 + monthly_ret)
        vals.append(p / 10000)   # 轉換成萬元
    x = np.arange(1, months + 1) / 12 + start_age
    axes[0].plot(x, vals, label=label, color=color, linewidth=2)

axes[0].set_xlabel('年齡'); axes[0].set_ylabel('累積資產（萬元）')
axes[0].set_title(f'每月投入 NT$3,000，年化 {annual_ret*100:.0f}%\\n退休時資產比較', fontsize=11)
axes[0].legend(fontsize=9); axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}萬'))

# 每晚 5 年的代價
penalties = [finals[0] - f for f in finals]
start_labels = ['20 歲', '25 歲', '30 歲', '35 歲']
bars = axes[1].bar(start_labels, [f/10000 for f in finals], color=colors, alpha=0.85)
for bar, total, invest in zip(bars, finals, invested_totals):
    axes[1].bar(bar.get_x(), invest/10000, bar.get_width(), color='lightgray', alpha=0.6)
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f'{bar.get_height():.0f}萬', ha='center', fontsize=10, fontweight='bold')

from matplotlib.patches import Patch
axes[1].legend(handles=[
    Patch(color='lightgray', alpha=0.6, label='本金（實際投入）'),
    Patch(color='steelblue', alpha=0.85, label='複利利潤'),
], fontsize=9)
axes[1].set_ylabel('60 歲時退休資產（萬元）')
axes[1].set_title('「晚幾年開始」差多少？', fontsize=11)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}萬'))

plt.tight_layout(); plt.show()

delay_cost = (finals[0] - finals[1]) / 10000
print(f"\\n每晚 5 年開始的代價：少約 NT${delay_cost:.0f} 萬")
print(f"這相當於晚 5 年，讓本來可以有的資產少了 {(finals[0]-finals[1])/finals[0]*100:.0f}%")
"""))

# ─── Part 3: 費用率 ───────────────────────────────────────────────────────────
c7.append(md("""\
## 三、費用率：你看不見的最大敵人

Fama-French 研究證明：長期而言，主動選股很難持續打敗市場。
但很多人還是買主動型基金——理由往往是「這個基金去年報酬很好」。

問題是：**主動型基金的費用率通常是指數 ETF 的 10–20 倍**。
長期下來，費用的差距比短期表現的差距重要得多。

讓我們用數字看清楚。
"""))
c7.append(code("""\
monthly_inv_fee = 5_000   # 每月 NT$5,000（開始工作後）
years_fee       = 30
months_fee      = years_fee * 12
gross_return    = 0.07   # 市場年化報酬（費用前）

fee_scenarios = {
    '指數 ETF（0.1% / 年）':         0.001,
    '混合型 ETF（0.5% / 年）':       0.005,
    '主動型基金（1.5% / 年）':       0.015,
    '高費用主動基金（2.5% / 年）':   0.025,
}

print(f"每月投入 NT${monthly_inv_fee:,}，持續 {years_fee} 年，市場年化報酬 {gross_return*100:.0f}%")
print()
print(f"{'費用類型':^28} | {'費用率':>6} | {'30年後（萬）':>12} | {'費用吃掉（萬）':>12}")
print("-" * 68)

base_fv = None
finals_fee = {}
for label, fee in fee_scenarios.items():
    net_r   = gross_return - fee
    net_mr  = (1 + net_r) ** (1/12) - 1
    fv      = monthly_inv_fee * ((1 + net_mr) ** months_fee - 1) / net_mr
    if base_fv is None:
        base_fv = fv
    cost    = base_fv - fv
    finals_fee[label] = fv
    print(f"{label:^28} | {fee*100:>5.1f}% | {fv/10000:>12,.0f} | {cost/10000:>12,.0f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# 左：30年後資產比較
fee_labels = list(fee_scenarios.keys())
fee_colors = ['#2ecc71', '#3498db', '#e67e22', '#e74c3c']
vals_fee   = [finals_fee[l]/10000 for l in fee_labels]
bars = axes[0].bar(range(len(fee_labels)), vals_fee, color=fee_colors, alpha=0.85)
axes[0].set_xticks(range(len(fee_labels)))
axes[0].set_xticklabels([l.split('（')[0] for l in fee_labels], rotation=20, ha='right', fontsize=9)
axes[0].set_ylabel('30 年後資產（萬元）')
axes[0].set_title('費用率對最終資產的影響\\n（市場報酬相同，費用不同）', fontsize=11)
for bar, val in zip(bars, vals_fee):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f'{val:.0f}萬', ha='center', fontsize=10)

# 右：資產成長曲線
for label, fee, color in zip(fee_labels, fee_scenarios.values(), fee_colors):
    net_r  = gross_return - fee
    net_mr = (1 + net_r) ** (1/12) - 1
    vals   = []
    p = 0.0
    for _ in range(months_fee):
        p = (p + monthly_inv_fee) * (1 + net_mr)
        vals.append(p / 10000)
    short_label = label.split('（')[0]
    axes[1].plot(np.arange(1, months_fee + 1) / 12, vals,
                 label=f'{short_label}', color=color, linewidth=2)

axes[1].set_xlabel('投資年數'); axes[1].set_ylabel('累積資產（萬元）')
axes[1].set_title('費用率越高，差距隨時間擴大', fontsize=11)
axes[1].legend(fontsize=8)

plt.tight_layout(); plt.show()

etf_val  = list(finals_fee.values())[0]
high_val = list(finals_fee.values())[-1]
print(f"\\n指數 ETF vs 高費用基金：30 年後差 NT${(etf_val-high_val)/10000:.0f} 萬")
print(f"這些「損失」不是虧損，是每年悄悄流失的費用複利累積而成")
"""))

# ─── Part 4: 留在市場 ────────────────────────────────────────────────────────
c7.append(md("""\
## 四、留在市場 vs 試圖擇時

Trinity Study 和 DCA vs LS 研究都指向同一個結論：
**「Time in the market beats timing the market」（待在市場勝過擇時進出）**

來用 Shiller 資料算一個最著名的反面教材：
**如果你因為怕跌而錯過了最好的幾個月，結果會怎樣？**
"""))
c7.append(code("""\
import os

df = pd.read_csv("data/shiller_data.csv", parse_dates=['date'], index_col='date')
df['div_yield_m'] = df['dividend'] / df['price'] / 12
df['ret']         = df['real_price'].pct_change() + df['div_yield_m'].shift(1)
df = df.dropna(subset=['ret']).copy()

returns = df['ret'].values
n       = len(returns)

def final_wealth(returns_arr, exclude_n_best):
    sorted_idx = np.argsort(returns_arr)[::-1]
    excluded   = set(sorted_idx[:exclude_n_best])
    p = 1.0
    for i, r in enumerate(returns_arr):
        if i not in excluded:
            p *= (1 + r)
    return p

miss_scenarios = [0, 6, 12, 24, 36, 60]
results = {n_miss: final_wealth(returns, n_miss) for n_miss in miss_scenarios}

print(f"Shiller 資料期間：{df.index[0].year}–{df.index[-1].year}（共 {len(df)} 個月）")
print()
print(f"{'錯過最好幾個月':^16} | {'最終資產（$1→?）':>16} | {'與全程持有相比':>14}")
print("-" * 52)
full = results[0]
for n_miss, fv in results.items():
    ratio = fv / full * 100
    print(f"{n_miss:>6} 個月 ({n_miss/n*100:.1f}%) | {fv:>16,.0f} | {ratio:>13.1f}%")

print(f"\\n注意：錯過最好的 {miss_scenarios[-1]} 個月只佔 {miss_scenarios[-1]/n*100:.1f}% 的時間")
print(f"但資產卻只剩全程持有的 {results[miss_scenarios[-1]]/full*100:.0f}%")
"""))

c7.append(code("""\
# 視覺化
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# 左：錯過N個月的最終資產
miss_x   = miss_scenarios
miss_fv  = [results[n]/10000 for n in miss_x]   # 假設初始 NT$10,000
colors_m = ['#2ecc71' if n == 0 else '#e74c3c' for n in miss_x]
bars = axes[0].bar([str(n) for n in miss_x], miss_fv, color=colors_m, alpha=0.85)
axes[0].set_xlabel('錯過最好的幾個月')
axes[0].set_ylabel(f'最終資產（萬元，初始 NT$1）')
axes[0].set_title(f'錯過幾個好月份，就差這麼多\\n（{df.index[0].year}–{df.index[-1].year}，共 {n} 個月）', fontsize=11)
for bar, fv_val in zip(bars, miss_fv):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.02,
                 f'{fv_val:,.0f}', ha='center', fontsize=9, fontweight='bold')

# 右：歷史報酬分布，標記「最好的月份」長什麼樣
ret_pct = df['ret'].values * 100
top_threshold = np.sort(ret_pct)[::-1][60 - 1]   # 最好 60 個月的門檻

axes[1].hist(ret_pct, bins=80, color='steelblue', alpha=0.6, density=True, label='一般月份')
axes[1].hist(ret_pct[ret_pct >= top_threshold], bins=20, color='gold', alpha=0.9,
             density=False, label=f'最好 60 個月（佔 {60/n*100:.1f}%）')
axes[1].axvline(top_threshold, color='red', linestyle='--', linewidth=1.5,
                label=f'門檻 {top_threshold:.1f}%')
axes[1].set_xlabel('月報酬率（%）')
axes[1].set_title('「最好的月份」長什麼樣？\\n它們出現在市場最混亂的時候', fontsize=11)
axes[1].set_xlim(-20, 30)
axes[1].legend(fontsize=9)

plt.tight_layout(); plt.show()

print(f"\\n最好的 60 個月，月報酬門檻：>{top_threshold:.1f}%")
print(f"這些月份通常緊接在市場恐慌、大跌之後——你最怕入市的時候，往往是反彈最大的時候")
"""))

# ─── Part 5: 起點建議 ─────────────────────────────────────────────────────────
c7.append(md("""\
## 五、從六個研究提煉出的最簡單起點

不需要預測市場，不需要選股，不需要看技術分析。
只需要做到下面這幾件事：

---

### ✅ 你現在可以做的四件事

**1. 越早開始越好（複利）**
→ 哪怕每月 NT$1,000，也比等到「有錢了再說」強

**2. 買整個市場，不要試圖選股（Fama-French）**
→ 台灣：0050（台灣 50 指數 ETF），費用率 0.43%
→ 全球：VOO / VT（美股 / 全球 ETF），費用率 0.03–0.07%
→ 主動型基金 vs 指數 ETF，長期差距由費用決定，不是由選股能力

**3. 薪資收入 → 定期定額，閒置資金 → 越早投入越好（DCA vs LS）**
→ 每月薪資扣款買 ETF：絕對正確
→ 繼承、獎金、工讀積蓄：早點投入比分 12 個月買稍微好一點

**4. 設定後不要動它（Trinity Study + 錯過好月份）**
→ 熊市時最想賣，但這時候的持有才是長期報酬的來源
→ 退休前才需要調整股債比例

---

### ❌ 六個研究告訴你不要做的事

| 常見行為 | 對應研究 | 為什麼錯 |
|---------|---------|---------|
| 在 CAPE 歷史高點全部賣出 | 01 CAPE | CAPE 無法預測短期；過早退出的代價 > 等待的收益 |
| 相信主動基金能長期打敗市場 | 02 Fama-French | 因子溢酬已在指數中，費用才是決定性差距 |
| 用不同產業的 P/E 互相比較 | 03 Damodaran | 軟體和銀行的 P/E 本來就不能直接比 |
| 退休後在股市大跌時大額賣出 | 04 Trinity | 序列風險：退休初期賣在低點是最大的傷害 |
| 把每月薪資攢到「時機好」再一次買入 | 05 DCA | 等待 = 錯過市場上漲；定期定額省心又有效 |
| 相信「一月必漲、五月必跌」 | 06 季節效應 | 效應已被套利，這些建議是在浪費你的交易成本 |
"""))

# ─── Part 6: 模擬你自己 ──────────────────────────────────────────────────────
c7.append(md("## 六、模擬你自己的退休計畫"))
c7.append(code("""\
# 🔧 改這幾個數字，看看你自己的情況
current_age     = 22      # 你現在幾歲？
retirement_age  = 60      # 預計幾歲退休？
monthly_amount  = 5_000   # 每月能存多少？（NT$）
annual_expense  = 600_000 # 預計退休後每年花多少？（NT$，600,000 = 每月 5 萬）
annual_return   = 0.07    # 假設年化報酬率（7% = 全市場 ETF 歷史水準）
expense_ratio   = 0.004   # 你選的 ETF 費用率（0050 約 0.43%，VOO 約 0.03%）

# ── 計算 ──────────────────────────────────────────
net_ret    = annual_return - expense_ratio
net_mr     = (1 + net_ret) ** (1/12) - 1
years      = retirement_age - current_age
months_inv = years * 12

fv = monthly_amount * ((1 + net_mr) ** months_inv - 1) / net_mr
target_4pct  = annual_expense / 0.04   # 4% 法則目標資產
target_3pct  = annual_expense / 0.03   # 保守版 3%

total_in = monthly_amount * months_inv
print(f"=== 你的退休試算 ===")
print(f"投資年期：{years} 年（{current_age} → {retirement_age} 歲）")
print(f"每月投入：NT${monthly_amount:,}（年費用率 {expense_ratio*100:.2f}% 後淨報酬 {net_ret*100:.2f}%）")
print()
print(f"預計退休資產：NT${fv:>15,.0f}  （{fv/10000:.0f} 萬）")
print(f"累計投入本金：NT${total_in:>15,.0f}  （{total_in/10000:.0f} 萬）")
print(f"累計複利利潤：NT${fv-total_in:>15,.0f}  （{(fv-total_in)/10000:.0f} 萬）")
print()
print(f"4% 法則目標（每年花 {annual_expense/10000:.0f} 萬）：NT${target_4pct:>12,.0f}  （{target_4pct/10000:.0f} 萬）")
print(f"3% 保守目標：                               NT${target_3pct:>12,.0f}  （{target_3pct/10000:.0f} 萬）")
print()
gap_4 = fv - target_4pct
if gap_4 >= 0:
    print(f"✅ 預計超過 4% 目標 NT${gap_4:,.0f}（{gap_4/10000:.0f} 萬）")
else:
    need_more = -gap_4 / ((((1 + net_mr) ** months_inv - 1) / net_mr))
    print(f"⚠️  預計不足 4% 目標 NT${-gap_4:,.0f}（{-gap_4/10000:.0f} 萬）")
    print(f"   若要達到 4% 目標，每月需再多投入 NT${need_more:,.0f}")
"""))

c7.append(md("""\
## 七、最後一件事

六個研究涵蓋了 1871 年到今天——145 年。
期間經歷了：兩次世界大戰、1929 大崩潰、1970 通膨危機、2000 科技泡沫、2008 金融海嘯、2020 疫情。

**每一次，人們都說「這次不一樣，市場完了」。每一次，市場都回來了。**

不是因為股市有魔法，而是因為「股市」代表的是全球人類的生產力——
只要人類還在工作、創新、消費，它就會繼續向上。

你唯一需要做的，是**待在裡面夠久**。

> 「The stock market is a device for transferring money from the impatient to the patient.」
> — Warren Buffett
"""))

save(c7, "07_student_investor_guide.ipynb")

print("\n✅ 完成！")
print("   07_student_investor_guide.ipynb")
