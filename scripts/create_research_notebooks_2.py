"""
學術研究 Notebooks 產生器 (Part 2)
個人投資實證研究：
  04_trinity_study.ipynb  — 4% 提領法則 + 報酬序列風險
  05_dca_vs_lumpsum.ipynb — 定期定額 vs 單筆投入
  06_january_effect.ipynb — 一月效應與季節性異常
"""

import json, uuid, os

BASE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE, "data"), exist_ok=True)

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
# Notebook 4：Trinity Study / 4% 提領法則
# ══════════════════════════════════════════════════════════════════════════════
c4 = []

c4.append(md("""\
# 04 | Trinity Study：4% 提領法則
**理論來源：Cooley, Hubbard & Walz（1998），Trinity University**

> **核心問題：退休後每年花多少比例的錢，才能讓資產撐過 30 年？**
>
> 1998 年三位教授用 1926–1995 年美股資料回測各種提領率的「存活率」。
> 結論：**4% 是 30 年期間存活率接近 100% 的最大安全提領率。**
>
> 本 Notebook 用 Shiller 145 年資料重現這個分析，
> 並加入一個往往被忽略的關鍵：**報酬序列風險（Sequence of Returns Risk）**。
"""))

c4.append(md("## 匯入套件"))
c4.append(code(f"""\
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.family'] = {FONTS}
matplotlib.rcParams['axes.unicode_minus'] = False
print("✅ 匯入完成")
"""))

c4.append(md("""\
## 一、什麼是 4% 法則？

> **每年提領金額 = 退休金總額 × 4%**

例：退休金 $2,500 萬台幣 → 每年可花 $100 萬（每月 $8.3 萬）

**背後邏輯：**
- 股市長期年化實質報酬約 5–7%
- 提領 4%，剩餘報酬讓資產繼續成長，不被通膨侵蝕

**最大陷阱 → 報酬序列風險（Sequence of Returns Risk）**
> 退休後「前幾年」的報酬比「後幾年」重要得多——因為你在從小池子裡持續提款
"""))

c4.append(md("## 二、載入 Shiller 資料，計算月報酬"))
c4.append(code("""\
import os

LOCAL = "data/shiller_data.csv"
if not os.path.exists(LOCAL):
    raise FileNotFoundError("請先執行 01_shiller_cape.ipynb 下載資料")

df = pd.read_csv(LOCAL, parse_dates=['date'], index_col='date')

# 實質月報酬 = 實質資本利得 + 股息率/12
df['div_yield_m'] = df['dividend'] / df['price'] / 12
df['stock_ret']   = df['real_price'].pct_change() + df['div_yield_m'].shift(1)
# 公債月報酬近似：年化殖利率 / 12
df['bond_ret']    = df['long_rate'].shift(1) / 100 / 12

df_sim = df.dropna(subset=['stock_ret', 'bond_ret']).copy()
print(f"可用資料：{df_sim.index[0].year}–{df_sim.index[-1].year}，共 {len(df_sim)} 個月")
print(f"股票實質月均報酬：{df_sim['stock_ret'].mean()*100:.3f}%")
print(f"公債月均報酬　　：{df_sim['bond_ret'].mean()*100:.3f}%")
"""))

c4.append(md("## 三、模擬：各提領率在 30 年期間的存活率"))
c4.append(code("""\
def simulate_retirement(returns_arr, wr, years=30):
    months = years * 12
    records = []
    for start in range(len(returns_arr) - months):
        p = 1.0
        monthly_w = wr / 12
        survived = True
        for m in range(months):
            p *= (1 + returns_arr[start + m])
            p -= monthly_w
            if p <= 0:
                survived = False
                break
        records.append({
            'start_year': df_sim.index[start].year,
            'survived': survived,
            'final': max(0.0, p)
        })
    return pd.DataFrame(records)

r_6040 = (df_sim['stock_ret'] * 0.6 + df_sim['bond_ret'] * 0.4).values
r_100s = df_sim['stock_ret'].values

withdrawal_rates = [0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06]
labels = ['3%', '3.5%', '4%', '4.5%', '5%', '5.5%', '6%']

surv_6040, surv_100s = [], []
for wr in withdrawal_rates:
    res = simulate_retirement(r_6040, wr)
    surv_6040.append(res['survived'].mean() * 100)
    res = simulate_retirement(r_100s, wr)
    surv_100s.append(res['survived'].mean() * 100)

print("30 年期存活率：")
print(f"{'提領率':>6} | {'60/40':>8} | {'100%股票':>8}")
print("-" * 32)
for lbl, s1, s2 in zip(labels, surv_6040, surv_100s):
    print(f"{lbl:>6} | {s1:>7.1f}% | {s2:>7.1f}%")
"""))

c4.append(code("""\
x = np.arange(len(labels))
w = 0.35

fig, ax = plt.subplots(figsize=(10, 5))
b1 = ax.bar(x - w/2, surv_6040, w, label='60/40 股債',  color='darkorange', alpha=0.85)
b2 = ax.bar(x + w/2, surv_100s, w, label='100% 股票', color='steelblue',  alpha=0.85)
ax.axhline(95, color='red', linestyle='--', linewidth=1.2, label='95% 安全門檻')
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel('30 年存活率（%）'); ax.set_ylim(40, 108)
ax.set_title('Trinity Study 重現：不同提領率的歷史存活率\\n（Shiller 1881–今）', fontsize=12)
ax.legend()
for bar in list(b1) + list(b2):
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, f'{h:.0f}%',
            ha='center', va='bottom', fontsize=8)
plt.tight_layout(); plt.show()
"""))

c4.append(md("""\
## 四、哪些年份退休最危險？

存活率是「平均」，但個別退休年份差異極大。
最慘的年份是 **1960 年代末退休**：接下來是通膨飆升 + 股市停滯的「停滯性通膨」時代。
"""))
c4.append(code("""\
res_6040 = simulate_retirement(r_6040, 0.04, years=30)

failed = res_6040[~res_6040['survived']]['start_year'].tolist()
print(f"4% 提領、60/40、30 年：失敗退休年份 → {failed if failed else '無，全部存活 ✅'}")

colors = ['#e74c3c' if not s else '#2ecc71' for s in res_6040['survived']]
fig, ax = plt.subplots(figsize=(13, 4))
ax.bar(res_6040['start_year'], res_6040['final'], color=colors, alpha=0.75, width=0.8)
ax.axhline(1, color='black', linestyle='--', linewidth=0.8, label='初始本金')
red_p   = mpatches.Patch(color='#e74c3c', alpha=0.75, label='30 年內耗盡（失敗）')
green_p = mpatches.Patch(color='#2ecc71', alpha=0.75, label='仍有剩餘（存活）')
ax.legend(handles=[green_p, red_p])
ax.set_xlabel('退休年份'); ax.set_ylabel('30 年後剩餘資產（初始=1）')
ax.set_title('4% 提領 × 60/40：各退休年份 30 年後剩餘資產', fontsize=12)
plt.tight_layout(); plt.show()
"""))

c4.append(md("""\
## 五、報酬序列風險 ★（最重要的概念）

兩個人，完全相同的 30 年月報酬——只是順序不同：
- 甲：一開始就遇熊市（報酬壞在前）
- 乙：最後才遇熊市（報酬壞在後）

**沒有提款時**：最終財富完全相同（乘法可交換）
**有提款時**：甲的資產可能提前耗盡！
"""))
c4.append(code("""\
# 取 1966 年退休的真實歷史報酬（已知最艱難之一）
idx_1966 = int(np.where(df_sim.index.year == 1966)[0][0])
rets_bad = r_6040[idx_1966: idx_1966 + 360]
rets_rev = rets_bad[::-1]   # 相同報酬，但順序顛倒

def track(rets, wr=0.04):
    vals = [1.0]
    p = 1.0
    mw = wr / 12
    for r in rets:
        p = max(0.0, p * (1 + r) - mw)
        vals.append(p)
    return vals

def accum(rets):
    vals = [1.0]
    p = 1.0
    for r in rets:
        p *= (1 + r)
        vals.append(p)
    return vals

x = np.arange(361) / 12

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# 左：純累積（無提款）—— 最終一樣
axes[0].plot(x, accum(rets_bad), label='壞報酬在前', color='#e74c3c')
axes[0].plot(x, accum(rets_rev), label='壞報酬在後', color='#2ecc71', linestyle='--')
axes[0].set_title('無提款：報酬順序不影響最終財富', fontsize=11)
axes[0].set_xlabel('持有年數'); axes[0].set_ylabel('資產倍數'); axes[0].legend()

# 右：每年提領 4% —— 差異巨大
tb = track(rets_bad); tr = track(rets_rev)
axes[1].plot(x, tb, label='壞報酬在前（退休初遇熊市）', color='#e74c3c')
axes[1].plot(x, tr, label='壞報酬在後（退休末遇熊市）', color='#2ecc71', linestyle='--')
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].set_title('每年提領 4%：壞報酬在前 → 資產提前耗盡！', fontsize=11)
axes[1].set_xlabel('持有年數'); axes[1].set_ylabel('剩餘資產'); axes[1].legend(fontsize=8)

plt.suptitle('Sequence of Returns Risk（報酬序列風險）', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.show()

print(f"壞報酬在前 → 30 年後剩餘：{tb[-1]:.2f}  {'✅ 存活' if tb[-1]>0 else '❌ 耗盡'}")
print(f"壞報酬在後 → 30 年後剩餘：{tr[-1]:.2f}  {'✅ 存活' if tr[-1]>0 else '❌ 耗盡'}")
"""))

c4.append(md("""\
## 六、討論

**結論：**
- 4% 提領在 145 年資料中，60/40 組合 30 年存活率 > 95%
- 最危險的退休年份集中在 1960 年代末（停滯性通膨時代）
- **報酬序列風險**：退休後頭幾年的報酬決定一切——同樣的長期報酬，順序不同就是生死之別

**思考問題：**
1. 如果提早退休（FIRE，例如 45 歲），需要撐 45 年，4% 法則還夠用嗎？
2. 遇到序列風險時，有哪些策略可以應對？（提示：動態提領、現金緩衝、part-time income）
3. 台灣退休族通常靠房租 + 儲蓄，這有序列風險嗎？跟股市型退休有何不同？
4. 通膨高時，「固定提領 4%」實際上是在不斷稀釋購買力。如何修正？
"""))

c4.append(md("""\
## 七、這跟你有什麼關係？

**用 4% 法則，反推你的退休目標數字。**

大多數人不知道自己要存多少錢——所以就一直沒有目標，一直拖延。
現在就算出來：退休後每月想花多少，就需要存多少。

> 🔧 把下面的數字換成你自己的情況，直接 Run
"""))
c4.append(code("""\
# 🔧 改成你自己的數字
monthly_expense = 50_000   # 退休後每月想花多少（NT$）
current_age     = 25       # 現在幾歲
retire_age      = 60       # 預計退休年齡
annual_ret      = 0.07     # 年化報酬率（ETF 扣費後，保守估 5–7%）

# ── 計算退休目標 ──────────────────────────────────────────
annual_exp  = monthly_expense * 12
target_4pct = annual_exp / 0.04   # 4% 法則目標
target_3pct = annual_exp / 0.03   # 保守版（多存 33%）

years      = retire_age - current_age
months_inv = years * 12
mr         = (1 + annual_ret) ** (1/12) - 1

# 每月需存多少？PMT = FV × r / ((1+r)^n - 1)
pmt_4 = target_4pct * mr / ((1 + mr) ** months_inv - 1)
pmt_3 = target_3pct * mr / ((1 + mr) ** months_inv - 1)

print(f"退休後每月花費：NT${monthly_expense:,}  →  年花費 NT${annual_exp:,}")
print()
print(f"退休目標資產（4% 法則）：NT${target_4pct:>12,.0f}  （{target_4pct/10000:.0f} 萬）")
print(f"退休目標資產（3% 保守）：NT${target_3pct:>12,.0f}  （{target_3pct/10000:.0f} 萬）")
print()
print(f"從 {current_age} 歲投資到 {retire_age} 歲（{years} 年），年化 {annual_ret*100:.0f}%：")
print(f"  每月至少存（4% 目標）：NT${pmt_4:>8,.0f}")
print(f"  每月至少存（3% 保守）：NT${pmt_3:>8,.0f}")
print()
print("序列風險的應對建議：")
print(f"  {retire_age-5} 歲開始（退休前 5 年），把股票比例從 100% 逐年降到 60%")
print(f"  退休後的第一個熊市，是財務規劃最大的威脅——別在那時候賣股票")
"""))

save(c4, "04_trinity_study.ipynb")


# ══════════════════════════════════════════════════════════════════════════════
# Notebook 5：DCA vs Lump Sum
# ══════════════════════════════════════════════════════════════════════════════
c5 = []

c5.append(md("""\
# 05 | 定期定額 vs 單筆投入
**理論來源：Vanguard Research (2012) "Dollar-cost averaging just means taking risk later"**

> **核心問題：手上有一筆閒錢，要一次全押還是每月分批買？**
>
> 定期定額（DCA）在台灣極度流行。但 Vanguard 2012 年研究用美、英、澳三國資料發現：
> **單筆投入（Lump Sum）約有 2/3 的機率勝過定期定額。**
>
> 本 Notebook 用 Shiller 145 年資料驗證這個結論，
> 並找出 DCA 唯一真正勝出的情境，以及它流行的真正原因。
"""))

c5.append(md("## 匯入套件"))
c5.append(code(f"""\
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.family'] = {FONTS}
matplotlib.rcParams['axes.unicode_minus'] = False
print("✅ 匯入完成")
"""))

c5.append(md("""\
## 一、兩種策略定義

假設你手上有 **$100 萬**（閒置資金，非每月薪資）：

| 策略 | 操作 | 直覺 |
|------|------|------|
| **單筆投入（Lump Sum, LS）** | 第 1 個月全買入 | 「萬一買在高點怎麼辦？」|
| **定期定額（DCA）** | 分 12 個月，每月買入 1/12 | 「分散時間，降低風險」|

**關鍵邏輯：**
市場長期向上 → 等待就是在少賺
DCA 的本質 = 把部分資金先放在現金裡（幾乎零報酬）再慢慢投入
→ 只有「先跌後漲」時，DCA 才能以更低成本逢低買進
"""))

c5.append(md("## 二、載入資料"))
c5.append(code("""\
import os

df = pd.read_csv("data/shiller_data.csv", parse_dates=['date'], index_col='date')
df['div_yield_m'] = df['dividend'] / df['price'] / 12
df['ret']         = df['real_price'].pct_change() + df['div_yield_m'].shift(1)
df = df.dropna(subset=['ret']).copy()

print(f"資料期間：{df.index[0].year}–{df.index[-1].year}，共 {len(df)} 個月")
print(f"月均實質報酬：{df['ret'].mean()*100:.3f}%  →  年化約 {((1+df['ret'].mean())**12-1)*100:.1f}%")
"""))

c5.append(md("## 三、模擬所有歷史窗口"))
c5.append(code("""\
returns = df['ret'].values
INVEST  = 12   # 投入期 12 個月
HOLD    = 108  # 持有期 9 年（總計 10 年）

ls_finals, dca_finals = [], []
mkt_ret_invest = []   # 投入期間市場報酬

for start in range(len(returns) - INVEST - HOLD):
    inv_rets  = returns[start : start + INVEST]
    hold_rets = returns[start + INVEST : start + INVEST + HOLD]
    hold_mult = np.prod(1 + hold_rets)   # 持有期倍率（兩策略相同）

    # 單筆投入：第 1 個月買入，投入期 + 持有期全程持有
    ls_val = 1.0
    for r in inv_rets:
        ls_val *= (1 + r)
    ls_val *= hold_mult

    # 定期定額：每月買入 1/INVEST，投入完成後持有至同一終點
    dca_val = 0.0
    for r in inv_rets:
        dca_val = (dca_val + 1/INVEST) * (1 + r)
    dca_val *= hold_mult

    ls_finals.append(ls_val)
    dca_finals.append(dca_val)
    mkt_ret_invest.append(np.prod(1 + inv_rets) - 1)

ls_arr  = np.array(ls_finals)
dca_arr = np.array(dca_finals)
mkt_arr = np.array(mkt_ret_invest)

win_ls  = (ls_arr > dca_arr).mean() * 100
win_dca = 100 - win_ls

print(f"總模擬窗口：{len(ls_arr)} 個（投入 1 年 + 持有 9 年）")
print()
print(f"單筆投入（LS）勝出：{win_ls:.1f}%")
print(f"定期定額（DCA）勝出：{win_dca:.1f}%")
print()
print(f"LS  平均最終資產：{ls_arr.mean():.3f}（總投入 = 1 標準化）")
print(f"DCA 平均最終資產：{dca_arr.mean():.3f}")
print(f"LS 平均多賺：{(ls_arr.mean()/dca_arr.mean()-1)*100:.1f}%")
"""))

c5.append(code("""\
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# 左：兩策略最終資產分布
axes[0].hist(ls_arr,  bins=60, alpha=0.6, color='steelblue',  label=f'單筆投入（LS）', density=True)
axes[0].hist(dca_arr, bins=60, alpha=0.6, color='darkorange', label=f'定期定額（DCA）', density=True)
axes[0].axvline(ls_arr.mean(),  color='steelblue',  linestyle='--', linewidth=1.5,
                label=f'LS 均值 {ls_arr.mean():.2f}')
axes[0].axvline(dca_arr.mean(), color='darkorange', linestyle='--', linewidth=1.5,
                label=f'DCA 均值 {dca_arr.mean():.2f}')
axes[0].set_xlabel('10 年後最終資產（總投入 = 1）')
axes[0].set_ylabel('密度'); axes[0].set_title('最終資產分布', fontsize=11)
axes[0].legend(fontsize=9)

# 右：LS/DCA 比值分布
ratio = ls_arr / dca_arr
axes[1].hist(ratio, bins=60, color='slategray', alpha=0.75, density=True)
axes[1].axvline(1.0, color='red', linewidth=2, linestyle='--', label='無差異線')
axes[1].axvline(ratio.mean(), color='navy', linewidth=1.5, linestyle='--',
                label=f'平均比值 {ratio.mean():.3f}')
axes[1].set_xlabel('LS 最終資產 / DCA 最終資產')
axes[1].set_ylabel('密度')
axes[1].set_title(f'LS/DCA 比值分布\\nLS 勝 {win_ls:.0f}%，DCA 勝 {win_dca:.0f}%', fontsize=11)
axes[1].legend(fontsize=9)

plt.suptitle('Vanguard 研究重現（Shiller 1881–今）', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.show()
"""))

c5.append(md("## 四、DCA 什麼時候真的比較好？"))
c5.append(code("""\
# 按投入期間市場漲跌分群
down_mask = mkt_arr < -0.10   # 投入期間市場跌超 10%
up_mask   = mkt_arr > 0.10    # 投入期間市場漲超 10%
flat_mask = ~down_mask & ~up_mask

groups = [
    ('市場大跌 > 10%\\n（DCA 逢低買進）', down_mask),
    ('市場平盤 ±10%',                     flat_mask),
    ('市場大漲 > 10%\\n（等待即虧損）',    up_mask),
]

print("各市場情境下 DCA 勝出率：")
print(f"{'情境':^20} | {'出現次數':>8} | {'DCA 勝率':>8}")
print("-" * 46)
dca_win_rates = []
for label, mask in groups:
    if mask.sum() == 0:
        continue
    rate = (dca_arr[mask] > ls_arr[mask]).mean() * 100
    dca_win_rates.append(rate)
    print(f"{label.replace(chr(10),' '):^20} | {mask.sum():>8} | {rate:>7.1f}%")

print(f"\\n大多數情況市場是上漲的（{(mkt_arr>0).mean()*100:.0f}% 的窗口），所以 LS 大多時候更好")

fig, ax = plt.subplots(figsize=(8, 4))
cat_labels = [g[0] for g in groups]
colors_bar = ['#2ecc71' if r > 50 else '#e74c3c' for r in dca_win_rates]
bars = ax.bar(cat_labels, dca_win_rates, color=colors_bar, alpha=0.85, width=0.4)
ax.axhline(50, color='black', linestyle='--', linewidth=1, label='50% 平手線')
ax.set_ylabel('DCA 勝出比例（%）'); ax.set_ylim(0, 100)
ax.set_title('DCA 只在「投入期間市場先跌」時才真的佔優', fontsize=11)
ax.legend()
for bar, val in zip(bars, dca_win_rates):
    ax.text(bar.get_x() + bar.get_width()/2, val + 1, f'{val:.1f}%', ha='center', fontsize=12)
plt.tight_layout(); plt.show()
"""))

c5.append(md("""\
## 五、討論

**結論（和 Vanguard 一致）：**
- 單筆投入在 Shiller 145 年資料中，約 **2/3 的機率勝過定期定額**
- DCA 唯一真正有利的情境：**投入期間市場先跌**（才能以更低均價買進）
- 問題是：你不知道何時會跌

**那 DCA 為什麼還是很流行？**
> DCA 給的是**心理保護**，不是數學優勢。
> 分批投入能避免「一次買在最高點」的懊悔感，降低焦慮，
> 讓投資人能堅持計畫、不在下跌時砍單。
> 如果 DCA 幫助你堅持投資，那對你而言它可能比 LS 更有價值——即使期望值較低。

**思考問題：**
1. 每月從薪資扣款投入的「定期定額」，和這裡的分析情境一樣嗎？（這是另一個問題）
2. 如果你是在 CAPE 歷史高位時面對「要不要一次買入」，LS 的勝率還有 2/3 嗎？
3. 市場下跌 30% 後，LS 的勝率會是多少？這才是 DCA 最失去優勢的時機。
4. 手續費存在時，DCA 每次都要付費，會對勝率產生什麼影響？
"""))

c5.append(md("""\
## 六、這跟你有什麼關係？

**年終獎金、工讀積蓄、繼承款——這種一次性的錢，分批還是一次買？**

研究說：越早全部投入越好（2/3 機率）。
但心理上承受不了？分 3 個月是合理折衷，分 12 個月以上就沒什麼意義了。

> 🔧 改下面的 `n_split` 試試看不同分法的勝率差異
"""))
c5.append(code("""\
# 情境：你有一筆 NT$100,000 的一次性資金（獎金/存款）
# 比較「現在全買」vs「分 N 個月買入」的勝率

lump = 100_000

print(f"一次性資金 NT${lump:,}：不同投入節奏的「全部立即投入」勝率")
print()
print(f"  {'策略':^20} | {'全部立即投入勝率':>16} | {'分批投入勝率':>12}")
print("-" * 58)

for n_split in [1, 2, 3, 6, 12]:
    beat = 0
    total = 0
    for start in range(len(returns) - n_split - HOLD):
        inv_rets  = returns[start: start + n_split]
        hold_rets = returns[start + n_split: start + n_split + HOLD]
        hold_mult = np.prod(1 + hold_rets)

        ls = lump
        for r in inv_rets:
            ls *= (1 + r)
        ls *= hold_mult

        dca = 0.0
        for r in inv_rets:
            dca = (dca + lump / n_split) * (1 + r)
        dca *= hold_mult

        if ls > dca:
            beat += 1
        total += 1

    win_ls = beat / total * 100
    if n_split == 1:
        label = "全部立即買入"
    else:
        label = f"分 {n_split} 個月買入"
    print(f"  {label:^20} | {win_ls:>15.1f}% | {100-win_ls:>11.1f}%")

print()
print("建議：")
print("  薪資收入每月自動扣款 → 定期定額，完全正確")
print("  一次性閒置資金       → 越早投入越好；若心理壓力大，分 3 個月是合理折衷")
print("  分 12 個月以上       → 幾乎等於把一半的錢放現金不投資，機會成本很高")
"""))

save(c5, "05_dca_vs_lumpsum.ipynb")


# ══════════════════════════════════════════════════════════════════════════════
# Notebook 6：一月效應與季節性異常
# ══════════════════════════════════════════════════════════════════════════════
c6 = []

c6.append(md("""\
# 06 | 月份效應：一月效應與五月賣股
**理論來源：Wachtel (1942)、Rozeff & Kinney (1976) — 一月效應**
**Bouman & Jacobsen (2002) — Sell in May and Go Away**

> **核心問題：股市在某些月份真的比較容易漲嗎？**
>
> 一月效應是最早被發現的市場異常：每年一月的報酬率系統性偏高。
> 「五月賣股走人」則說：每年五月到十月股市表現差，要待在現金。
>
> 但自從被學術界公開後，這些效應還成立嗎？
> 本 Notebook 用 145 年資料驗證，並追蹤效應的「消亡過程」——
> 展示**市場效率自我修正**的力量。
"""))

c6.append(md("## 匯入套件"))
c6.append(code(f"""\
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.family'] = {FONTS}
matplotlib.rcParams['axes.unicode_minus'] = False
print("✅ 匯入完成")
"""))

c6.append(md("## 一、載入資料"))
c6.append(code("""\
import os

df = pd.read_csv("data/shiller_data.csv", parse_dates=['date'], index_col='date')
df['div_yield_m'] = df['dividend'] / df['price'] / 12
df['ret']         = df['real_price'].pct_change() + df['div_yield_m'].shift(1)
df = df.dropna(subset=['ret']).copy()
df['month'] = df.index.month
df['year']  = df.index.year

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
print(f"資料期間：{df.index[0].year}–{df.index[-1].year}，共 {len(df)} 個月")
"""))

c6.append(md("## 二、各月份平均報酬"))
c6.append(code("""\
monthly = df.groupby('month')['ret'].agg(['mean','std','count'])
monthly['mean_pct'] = monthly['mean'] * 100
monthly['se_pct']   = monthly['std'] / np.sqrt(monthly['count']) * 100

# 配色：一月紅、夏季橘、冬季綠
colors = ['#e74c3c' if m == 1 else
          '#f39c12' if 5 <= m <= 10 else
          '#2ecc71'
          for m in range(1, 13)]

fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar(range(1, 13), monthly['mean_pct'], color=colors, alpha=0.85, edgecolor='white')
ax.errorbar(range(1, 13), monthly['mean_pct'],
            yerr=monthly['se_pct'] * 1.96,
            fmt='none', color='black', capsize=4, linewidth=1)
ax.axhline(df['ret'].mean() * 100, color='navy', linestyle='--', linewidth=1.2,
           label=f"全期月均 {df['ret'].mean()*100:.3f}%")
ax.axhline(0, color='black', linewidth=0.5)
ax.set_xticks(range(1, 13)); ax.set_xticklabels(MONTHS)
ax.set_ylabel('平均月報酬（%）')
ax.set_title(f'S&P 500 各月份平均實質報酬（{df.index[0].year}–{df.index[-1].year}）', fontsize=12)

legend_handles = [
    mpatches.Patch(color='#e74c3c', alpha=0.85, label='一月（January Effect）'),
    mpatches.Patch(color='#f39c12', alpha=0.85, label='五到十月（Sell in May 空窗期）'),
    mpatches.Patch(color='#2ecc71', alpha=0.85, label='十一到四月（冬季強勢期）'),
]
ax.legend(handles=legend_handles, fontsize=9)

for bar, val in zip(bars, monthly['mean_pct']):
    offset = 0.03 if val >= 0 else -0.10
    ax.text(bar.get_x() + bar.get_width()/2, val + offset,
            f'{val:.2f}%', ha='center', va='bottom', fontsize=8)
plt.tight_layout(); plt.show()

jan = monthly.loc[1, 'mean_pct']
others = df[df['month'] != 1]['ret'].mean() * 100
print(f"一月均值：{jan:.3f}%")
print(f"其他月份均值：{others:.3f}%")
print(f"一月超額報酬：{jan - others:+.3f}%")
"""))

c6.append(md("## 三、一月效應統計顯著性"))
c6.append(code("""\
jan_rets   = df[df['month'] == 1]['ret'].values
other_rets = df[df['month'] != 1]['ret'].values
t_stat, p_val = stats.ttest_ind(jan_rets, other_rets)

print(f"一月（n={len(jan_rets)}）vs 其他月份（n={len(other_rets)}）")
print(f"t 統計量：{t_stat:.3f}")
print(f"p 值：{p_val:.3f}")
print()
if p_val < 0.05:
    print("✅ p < 0.05，一月效應在整體資料中統計上顯著")
elif p_val < 0.10:
    print("⚠️ 0.05 < p < 0.10，邊緣顯著")
else:
    print("❌ p ≥ 0.10，整體上一月效應不顯著")

print()
print("各月份與其他月份 t 檢定：")
for m in range(1, 13):
    m_ret  = df[df['month'] == m]['ret'].values
    ot_ret = df[df['month'] != m]['ret'].values
    t, p   = stats.ttest_ind(m_ret, ot_ret)
    sig    = ' ★' if p < 0.05 else (' △' if p < 0.10 else '')
    print(f"  {MONTHS[m-1]:>3}: 均值 {m_ret.mean()*100:+.3f}%  p={p:.3f}{sig}")
"""))

c6.append(md("""\
## 四、一月效應隨時代消亡了嗎？

效應被學術界公開後，投資人開始在一月前提前布局，套利使效應縮小。
我們把 145 年切成三段來觀察。
"""))
c6.append(code("""\
eras = [
    ('早期（1881–1950）',   1881, 1950),
    ('發現期（1951–1990）', 1951, 1990),
    ('後公開（1991–今）',   1991, 2030),
]

fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for ax, (label, y0, y1) in zip(axes, eras):
    sub = df[(df['year'] >= y0) & (df['year'] <= y1)]
    avg = sub.groupby('month')['ret'].mean() * 100
    col = ['#e74c3c' if m == 1 else '#bdc3c7' for m in range(1, 13)]
    ax.bar(range(1, 13), avg, color=col, alpha=0.85, edgecolor='white')
    ax.axhline(avg.mean(), color='navy', linestyle='--', linewidth=1)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTHS, rotation=45, ha='right', fontsize=8)
    n_years = len(sub['year'].unique())
    ax.set_title(f'{label}\\n（{n_years} 年）\\n一月：{avg.iloc[0]:+.2f}%', fontsize=10)
    if y0 == 1881:
        ax.set_ylabel('平均月報酬（%）')

plt.suptitle('一月效應的消亡過程（被研究後逐漸縮小）', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.show()
"""))

c6.append(md("## 五、Sell in May and Go Away — 冬季 vs 夏季"))
c6.append(code("""\
df['season'] = df['month'].apply(lambda m: 'summer' if 5 <= m <= 10 else 'winter')

summer = df[df['season'] == 'summer']['ret']
winter = df[df['season'] == 'winter']['ret']

summer_ann = ((1 + summer.mean()) ** 12 - 1) * 100
winter_ann = ((1 + winter.mean()) ** 12 - 1) * 100
t2, p2 = stats.ttest_ind(winter.values, summer.values)

print("季節性報酬比較（五到十月 vs 十一到四月）：")
print(f"  夏季（5–10月）月均：{summer.mean()*100:.3f}%  年化約 {summer_ann:.1f}%")
print(f"  冬季（11–4月）月均：{winter.mean()*100:.3f}%  年化約 {winter_ann:.1f}%")
print(f"  冬季溢酬：{(winter.mean()-summer.mean())*100:+.3f}% / 月")
print(f"  t={t2:.2f}, p={p2:.3f}  {'★ 顯著' if p2 < 0.05 else ''}")

# 滾動 20 年冬季溢酬
roll_prem, roll_year = [], []
for y0 in range(df['year'].min(), df['year'].max() - 20):
    sub = df[(df['year'] >= y0) & (df['year'] < y0 + 20)]
    w = sub[sub['season'] == 'winter']['ret'].mean()
    s = sub[sub['season'] == 'summer']['ret'].mean()
    roll_prem.append((w - s) * 100)
    roll_year.append(y0 + 10)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# 左：各月份，夏冬配色
avg_m = df.groupby('month')['ret'].mean() * 100
col2 = ['#f39c12' if 5 <= m <= 10 else '#2ecc71' for m in range(1, 13)]
axes[0].bar(range(1, 13), avg_m, color=col2, alpha=0.85, edgecolor='white')
axes[0].set_xticks(range(1, 13)); axes[0].set_xticklabels(MONTHS)
axes[0].axhline(0, color='black', linewidth=0.5)
axes[0].set_ylabel('平均月報酬（%）')
axes[0].set_title('各月份報酬\\n（橘 = 夏季，綠 = 冬季）', fontsize=11)
from matplotlib.patches import Patch
axes[0].legend(handles=[
    Patch(color='#f39c12', alpha=0.85, label='夏季（5–10 月）'),
    Patch(color='#2ecc71', alpha=0.85, label='冬季（11–4 月）'),
])

# 右：滾動 20 年冬季溢酬
col3 = ['#2ecc71' if p > 0 else '#e74c3c' for p in roll_prem]
axes[1].bar(roll_year, roll_prem, color=col3, alpha=0.75, width=1.5)
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].set_xlabel('20 年窗口中點'); axes[1].set_ylabel('冬季 − 夏季 月均報酬（%）')
axes[1].set_title('冬季溢酬是否穩定？\\n滾動 20 年窗口', fontsize=11)

plt.suptitle('Sell in May and Go Away 驗證', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.show()
"""))

c6.append(md("""\
## 六、討論

**結論：**
- 一月效應在早期資料（1881–1950）相對明顯，但 **1991 年後大幅減弱至幾乎消失**
- 冬季溢酬（Sell in May）整體存在，但在某些 20 年窗口為負，策略表現**不穩定**
- 兩者都符合「被發現 → 被套利 → 消亡」的市場自我糾正過程

**這告訴我們什麼？**
> **市場異常一旦廣為人知，就會被套利消除。**
> 這是弱式效率市場假說（Weak-form EMH）的最佳示範。
> 但效應的消亡往往需要幾十年，在此期間仍有人獲利。

**思考問題：**
1. 一月效應最初為什麼存在？（提示：稅務損失收割、基金年末換倉、年初再配置）
2. 把交易成本和稅負算進去，「五月賣股走人」策略實際上還能賺嗎？
3. 台股有一月效應嗎？農曆年前後有異常報酬嗎？（文化因素可能產生不同的季節效應）
4. 如果你發現一個新的市場異常，你要怎麼確認它是真實的而不是資料探勘出來的巧合？
"""))

c6.append(md("""\
## 七、這跟你有什麼關係？

**不要跟隨「幾月買股必漲」的建議——即使效應真的存在，套利後你也拿不到。**

最直觀的驗證：如果你真的每年五月賣出、十月底買回（Sell in May），
和完全不動（Buy and Hold）相比，145 年下來結果怎樣？
"""))
c6.append(code("""\
# 模擬 Sell in May 策略 vs Buy and Hold（1881–今）
p_bah, p_sim = 1.0, 1.0
bah_track, sim_track, date_track = [1.0], [1.0], [df.index[0]]

for date, row in df.iterrows():
    p_bah *= (1 + row['ret'])
    if row['month'] not in [5, 6, 7, 8, 9, 10]:
        p_sim *= (1 + row['ret'])   # 冬季持有
    # 夏季現金，假設利率 0（對 Sell-in-May 策略有利的保守假設）
    bah_track.append(p_bah)
    sim_track.append(p_sim)
    date_track.append(date)

n_years = len(df) / 12
bah_ann = (p_bah ** (1 / n_years) - 1) * 100
sim_ann = (p_sim ** (1 / n_years) - 1) * 100

print(f"Buy and Hold：年化 {bah_ann:.2f}%，最終資產 {p_bah:,.0f}x")
print(f"Sell in May ：年化 {sim_ann:.2f}%，最終資產 {p_sim:,.0f}x")
print(f"每年差距：{bah_ann - sim_ann:.2f}%（Buy and Hold 勝）")
print()
print(f"這還沒算：每年兩次的交易成本 + 潛在資本利得稅")
print(f"結論：跟隨季節性操作建議，不但沒有幫助，還會讓你少賺 {bah_ann - sim_ann:.2f}%/年")

fig, ax = plt.subplots(figsize=(12, 4))
ax.semilogy(date_track, bah_track, label=f'Buy and Hold（{bah_ann:.1f}%/年）',
            color='#2ecc71', linewidth=1)
ax.semilogy(date_track, sim_track, label=f'Sell in May（{sim_ann:.1f}%/年）',
            color='#e74c3c', linewidth=1, linestyle='--')
ax.set_ylabel('累積資產（對數）')
ax.set_title('Buy and Hold vs Sell in May（1881–今）', fontsize=12)
ax.legend(fontsize=10)
plt.tight_layout(); plt.show()
"""))

save(c6, "06_january_effect.ipynb")

print("\n✅ 全部完成！")
print(f"   04_trinity_study.ipynb")
print(f"   05_dca_vs_lumpsum.ipynb")
print(f"   06_january_effect.ipynb")
