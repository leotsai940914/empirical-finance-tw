"""
學術研究 Notebooks 產生器
三個基於公開學術資料的研究型 Notebook：
  01_shiller_cape.ipynb   — Shiller CAPE 與長期市場報酬
  02_fama_french.ipynb    — Fama-French 因子模型
  03_damodaran.ipynb      — Damodaran 產業估值分析
執行：python3 create_research_notebooks.py
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
# Notebook 1：Shiller CAPE
# ══════════════════════════════════════════════════════════════════════════════
c1 = []

c1.append(md("""
# 01 | Shiller CAPE 與長期市場報酬
**資料來源：Robert Shiller（耶魯大學）— 2013 年諾貝爾經濟學獎得主**

> **核心問題：股市現在貴不貴？怎麼用資料判斷？**
>
> 本 Notebook 使用 Shiller 的 150 年歷史資料，驗證一個簡單但強大的發現：
> **當股市估值（CAPE）偏高時，未來 10 年的實質報酬率往往偏低。**
"""))

c1.append(md("## ⚙️ Step 0：安裝套件"))
c1.append(code("""\
%pip install xlrd openpyxl
print("✅ 完成")
"""))

c1.append(md("## 匯入套件"))
c1.append(code(f"""\
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

c1.append(md("""\
## 一、什麼是 CAPE？

### 普通 P/E 的問題
企業盈餘（EPS）隨景氣循環大幅波動：
- 景氣好 → EPS 高 → P/E 看起來低（「很便宜！」→ 其實在高點）
- 景氣差 → EPS 崩潰 → P/E 突然很高（「好貴！」→ 其實在低點）

用普通 P/E 判斷時機，容易得出錯誤結論。

### CAPE 的解法（Cyclically Adjusted P/E）
> **CAPE = 股價 ÷ 過去 10 年平均實質盈餘（剔除通膨）**

用 10 年平均平滑掉景氣循環的雜訊，讓估值更有參考意義。

| | 普通 P/E | CAPE |
|--|---------|------|
| 盈餘基準 | 當年 EPS | 過去 10 年平均實質 EPS |
| 景氣敏感度 | 高（容易誤導） | 低（更穩定） |
| 預測能力 | 差 | 對未來 10 年報酬有顯著預測力 |
| 歷史均值 | 約 15–16 倍 | 約 16–17 倍 |
"""))

c1.append(md("## 二、載入 Shiller 資料"))
c1.append(code("""\
import os

LOCAL = "data/shiller_data.csv"

if os.path.exists(LOCAL):
    df = pd.read_csv(LOCAL, parse_dates=['date'], index_col='date')
    print(f"✅ 從本機載入（{len(df)} 筆）")
else:
    print("⏳ 從網路下載 Shiller 資料...")
    url = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
    raw = pd.read_excel(url, sheet_name="Data", skiprows=7, header=0)

    # 過濾有效資料列
    raw = raw[pd.to_numeric(raw.iloc[:, 0], errors='coerce').notna()].copy()
    raw = raw[raw.iloc[:, 0].astype(float) > 1800].copy()

    # 解析十進位日期：1871.01 = 1月，1871.10 = 10月
    dec = raw.iloc[:, 0].astype(float)
    year  = dec.apply(lambda x: int(x))
    month = dec.apply(lambda x: max(1, int(round((x % 1) * 100))))

    df = pd.DataFrame({
        'date'       : pd.to_datetime({'year': year, 'month': month, 'day': 1}),
        'price'      : pd.to_numeric(raw.iloc[:, 1],  errors='coerce'),
        'dividend'   : pd.to_numeric(raw.iloc[:, 2],  errors='coerce'),
        'earnings'   : pd.to_numeric(raw.iloc[:, 3],  errors='coerce'),
        'cpi'        : pd.to_numeric(raw.iloc[:, 4],  errors='coerce'),
        'long_rate'  : pd.to_numeric(raw.iloc[:, 6],  errors='coerce'),
        'real_price' : pd.to_numeric(raw.iloc[:, 7],  errors='coerce'),
        'cape'       : pd.to_numeric(raw.iloc[:, 12], errors='coerce'),
    }).dropna(subset=['date', 'price', 'cape'])

    df = df.set_index('date').sort_index()
    df.to_csv(LOCAL)
    print(f"✅ 下載完成，已快取到 {LOCAL}（{len(df)} 筆）")

df.tail(3)
"""))

c1.append(code("""\
print(f"資料期間：{df.index[0].strftime('%Y-%m')} 至 {df.index[-1].strftime('%Y-%m')}")
print(f"總月數　：{len(df)} 個月（約 {len(df)//12} 年）")
print(f"CAPE 歷史均值  ：{df['cape'].mean():.1f} 倍")
print(f"CAPE 歷史中位數：{df['cape'].median():.1f} 倍")
print(f"CAPE 最高點：{df['cape'].max():.1f} 倍（{df['cape'].idxmax().strftime('%Y-%m')}）")
print(f"CAPE 最低點：{df['cape'].min():.1f} 倍（{df['cape'].idxmin().strftime('%Y-%m')}）")
"""))

c1.append(md("## 三、S&P 500 — 150 年走勢"))
c1.append(code("""\
fig, ax = plt.subplots(figsize=(14, 5))
ax.semilogy(df.index, df['real_price'], color='steelblue', linewidth=0.7)

events = {
    '1929\\n大崩盤': ('1929-09', 2.5),
    '1966\\n高峰':   ('1966-02', 2.8),
    '2000\\n科技泡沫':('2000-08', 2.5),
    '2008\\n金融海嘯':('2007-10', 2.5),
}
for label, (date_str, mult) in events.items():
    date = pd.to_datetime(date_str)
    y = df['real_price'].asof(date)
    ax.annotate(label, xy=(date, y), xytext=(date, y * mult),
                arrowprops=dict(arrowstyle='->', color='red', lw=1),
                fontsize=8, ha='center', color='darkred')

ax.set_title('S&P 500 實質價格走勢（1871–今，對數尺度）', fontsize=13)
ax.set_ylabel('實質價格指數（對數）')
ax.set_xlabel('年份')
plt.tight_layout()
plt.show()
"""))

c1.append(md("## 四、CAPE 歷史走勢"))
c1.append(code("""\
cape_mean = df['cape'].mean()

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df.index, df['cape'], color='darkorange', linewidth=0.7, label='CAPE')
ax.axhline(cape_mean, color='gray', linestyle='--', linewidth=1.2,
           label=f'歷史均值 ({cape_mean:.1f}x)')
ax.axhline(25, color='red', linestyle=':', linewidth=1, alpha=0.6, label='警戒線 (25x)')

ax.fill_between(df.index, cape_mean, df['cape'],
                where=(df['cape'] > cape_mean), alpha=0.12, color='red', label='高於均值（偏貴）')
ax.fill_between(df.index, df['cape'], cape_mean,
                where=(df['cape'] < cape_mean), alpha=0.12, color='green', label='低於均值（偏便宜）')

peaks = {'1929\\n(31x)': '1929-09', '2000\\n(44x)': '1999-12', '2022\\n(38x)': '2021-10'}
for label, d in peaks.items():
    date = pd.to_datetime(d)
    y = df['cape'].asof(date)
    ax.annotate(label, xy=(date, y), xytext=(date, y + 4),
                fontsize=8, ha='center', color='darkred',
                arrowprops=dict(arrowstyle='->', color='darkred', lw=0.8))

ax.set_title('Shiller CAPE 歷史走勢（1881–今）', fontsize=13)
ax.set_ylabel('CAPE（倍）')
ax.legend(loc='upper left', fontsize=8)
plt.tight_layout()
plt.show()
"""))

c1.append(md("""\
## 五、核心驗證：CAPE 能預測未來報酬嗎？

**假說：CAPE 越高，未來 10 年實質報酬越低。**

我們把每個月的 CAPE 值，對應到「該月買入、持有 10 年的年化實質報酬率」，
用散點圖直接驗證兩者的關係。
"""))
c1.append(code("""\
# 計算未來 10 年年化實質報酬率（120 個月後）
df['real_price_10y'] = df['real_price'].shift(-120)
df['return_10y'] = (df['real_price_10y'] / df['real_price']) ** (1/10) - 1

test = df.dropna(subset=['cape', 'return_10y']).copy()

fig, ax = plt.subplots(figsize=(9, 6))
sc = ax.scatter(test['cape'], test['return_10y'] * 100,
                c=test.index.year, cmap='plasma', alpha=0.35, s=8)
plt.colorbar(sc, ax=ax, label='年份')

# 趨勢線
z = np.polyfit(test['cape'], test['return_10y'] * 100, 1)
p = np.poly1d(z)
xr = np.linspace(test['cape'].min(), test['cape'].max(), 200)
ax.plot(xr, p(xr), 'r-', linewidth=2, label='趨勢線')

corr = test['cape'].corr(test['return_10y'])
ax.set_title(f'CAPE vs 未來 10 年實質年化報酬率\\n（相關係數 = {corr:.2f}）', fontsize=13)
ax.set_xlabel('當時的 CAPE（倍）')
ax.set_ylabel('未來 10 年實質年化報酬率（%）')
ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
ax.legend()
plt.tight_layout()
plt.show()
"""))

c1.append(code("""\
# 按 CAPE 五分位數分組，看各組的平均未來報酬
test['cape_group'] = pd.qcut(test['cape'], q=5,
    labels=['最低 20%\\n（最便宜）', '次低 20%', '中間 20%', '次高 20%', '最高 20%\\n（最貴）'])

summary = test.groupby('cape_group', observed=True)['return_10y'].agg(['mean', 'std']) * 100
summary.columns = ['平均年化報酬 (%)', '標準差 (%)']
print("CAPE 分位數 vs 未來 10 年年化實質報酬：")
print(summary.round(2).to_string())
"""))

c1.append(md("""\
## 六、討論

**結論：CAPE 與未來 10 年報酬呈顯著負相關（相關係數約 -0.6 至 -0.7）。**

這不是在說「CAPE 高，明天就會崩」，而是：
> 「以目前價格買進，未來 10 年的期望年化報酬率比長期均值低。」

**思考問題：**
1. 目前 CAPE 約 30+ 倍。歷史上僅 1929、2000 年前後曾達到此水位。之後分別發生了什麼？
2. 分組統計裡，「最便宜 20%」和「最貴 20%」的報酬差距有多大？這在投資實務上意味著什麼？
3. 低 CAPE ≠ 立刻上漲。有沒有 CAPE 低但接下來十年報酬仍然不好的時期？為什麼？
4. 台股的 CAPE 歷史均值和美股相同嗎？如果不同，為什麼？
"""))

c1.append(md("""\
## 七、這跟你有什麼關係？

**CAPE 是估值溫度計，不是擇時工具。**

你剛才建立的散點圖回歸線，可以直接用來推算：
「以目前估值買入，未來 10 年的期望報酬大概是多少？」

這不能告訴你「明年漲不漲」，但可以幫你校準長期報酬預期，
避免在高點把 All-in 的獲利預期設得不切實際。
"""))
c1.append(code("""\
# p 是上方散點圖建立的回歸線，直接代入現在的 CAPE
current_cape  = df['cape'].iloc[-1]
predicted_10y = p(current_cape)

print(f"目前 S&P 500 CAPE：{current_cape:.1f} 倍（歷史均值 {df['cape'].mean():.1f} 倍）")
print(f"根據 145 年歷史回歸，預測未來 10 年實質年化報酬：約 {predicted_10y:.1f}%")
print()

# 各估值水位的預測
print(f"{'CAPE':>8} | {'預期10年報酬':>12}")
print("-" * 25)
for cape_val in [15, 20, 25, 30, 35, 40, round(current_cape)]:
    ret = p(cape_val)
    marker = " ← 目前" if abs(cape_val - current_cape) < 2 else ""
    print(f"{cape_val:>8.0f} | {ret:>+11.1f}%{marker}")

print()
print("重點：CAPE 在 30 倍以上時，過去 145 年的期望報酬多數落在 0–4%")
print("這不是說『不要投資』，而是：")
print("  → 降低期望值，把計畫報酬率從 7% 調成 4–5%")
print("  → 不要在高估值時一次 All-in，分批更能降低序列風險")
print("  → 費用控制和持續投資比擇時更重要")
"""))

save(c1, "01_shiller_cape.ipynb")


# ══════════════════════════════════════════════════════════════════════════════
# Notebook 2：Fama-French 因子模型
# ══════════════════════════════════════════════════════════════════════════════
c2 = []

c2.append(md("""\
# 02 | Fama-French 因子模型
**資料來源：Kenneth French Data Library（達特茅斯大學）**
**理論來源：Eugene Fama & Kenneth French — Fama 2013 年諾貝爾經濟學獎得主**

> **核心問題：什麼因素決定股票的長期報酬？CAPM 說的「市場風險」夠嗎？**
>
> 本 Notebook 使用 1926 年至今的美股月資料，
> 驗證規模效應、價值效應、動能效應是否真實存在於數據中。
"""))

c2.append(md("## ⚙️ Step 0：安裝套件"))
c2.append(code("""\
%pip install pandas-datareader
print("✅ 完成")
"""))

c2.append(md("## 匯入套件"))
c2.append(code(f"""\
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

c2.append(md("""\
## 一、從 CAPM 到 Fama-French 三因子模型

### CAPM（1964，夏普、林特納）
> 超額報酬 = β × 市場超額報酬

CAPM 認為唯一重要的風險是「市場風險（β）」。
但實證研究發現，很多股票的報酬無法被 β 解釋——存在「異常報酬」。

### Fama-French 三因子（1992）
> 超額報酬 = β₁ × **Mkt-RF** + β₂ × **SMB** + β₃ × **HML**

新增兩個因子：

| 因子 | 全名 | 概念 |
|------|------|------|
| **Mkt-RF** | Market Risk Premium | 市場超額報酬（同 CAPM 的 β） |
| **SMB** | Small Minus Big | 小型股 − 大型股報酬差 |
| **HML** | High Minus Low | 高帳面市值比 − 低帳面市值比（價值股 − 成長股）|

### 後來又加入動能因子（Carhart 1997）
| 因子 | 全名 | 概念 |
|------|------|------|
| **Mom** | Momentum | 過去 12 個月贏家 − 輸家 |

這四個因子加在一起，能解釋大多數主動基金的報酬。
"""))

c2.append(md("## 二、載入 Fama-French 資料"))
c2.append(code("""\
import os
import pandas_datareader.data as web

LOCAL_FF3 = "data/ff3_factors.csv"
LOCAL_MOM = "data/ff_momentum.csv"

if os.path.exists(LOCAL_FF3) and os.path.exists(LOCAL_MOM):
    ff3 = pd.read_csv(LOCAL_FF3, index_col=0, parse_dates=True)
    mom = pd.read_csv(LOCAL_MOM, index_col=0, parse_dates=True)
    print(f"✅ 從本機載入")
else:
    print("⏳ 從 Kenneth French 資料庫下載...")
    ff3 = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start='1926-07')[0]
    mom = web.DataReader('F-F_Momentum_Factor',       'famafrench', start='1926-07')[0]
    ff3.index = pd.to_datetime(ff3.index.to_timestamp())
    mom.index = pd.to_datetime(mom.index.to_timestamp())
    ff3.to_csv(LOCAL_FF3)
    mom.to_csv(LOCAL_MOM)
    print(f"✅ 下載完成，已快取")

# 合併，轉換為小數報酬率
factors = ff3.join(mom, how='inner') / 100
factors.columns = ['Mkt-RF', 'SMB', 'HML', 'RF', 'Mom']
factors = factors.dropna()

print(f"\\n資料期間：{factors.index[0].strftime('%Y-%m')} 至 {factors.index[-1].strftime('%Y-%m')}")
print(f"總月數：{len(factors)}")
print("\\n各因子月報酬統計（%）：")
print((factors[['Mkt-RF','SMB','HML','Mom']] * 100).describe().round(2).to_string())
"""))

c2.append(md("## 三、各因子累積報酬（1926–今）"))
c2.append(code("""\
cumret = (1 + factors[['Mkt-RF','SMB','HML','Mom']]).cumprod()

fig, axes = plt.subplots(2, 1, figsize=(13, 10))

# 對數尺度：看長期複利效果
axes[0].semilogy(cumret.index, cumret['Mkt-RF'], label='市場超額報酬 (Mkt-RF)', linewidth=1)
axes[0].semilogy(cumret.index, cumret['SMB'],    label='規模因子 (SMB)',         linewidth=1)
axes[0].semilogy(cumret.index, cumret['HML'],    label='價值因子 (HML)',         linewidth=1)
axes[0].semilogy(cumret.index, cumret['Mom'],    label='動能因子 (Mom)',         linewidth=1)
axes[0].set_title('四大因子累積報酬（對數尺度，1 美元投入）', fontsize=12)
axes[0].set_ylabel('累積報酬（對數）')
axes[0].legend()
axes[0].axhline(1, color='black', linewidth=0.5, linestyle='--')

# 線性尺度：看各因子相對規模
axes[1].plot(cumret.index, cumret[['SMB','HML','Mom']])
axes[1].set_title('SMB / HML / Mom 累積報酬（線性尺度）', fontsize=12)
axes[1].set_ylabel('累積報酬')
axes[1].legend(['規模因子 (SMB)', '價值因子 (HML)', '動能因子 (Mom)'])
axes[1].axhline(1, color='black', linewidth=0.5, linestyle='--')

plt.tight_layout()
plt.show()
"""))

c2.append(md("""\
## 四、規模效應驗證（Size Premium）

**命題：小型股的長期報酬優於大型股（SMB > 0）**

Fama & French 發現，市值小的公司股票長期報酬系統性地高於大型公司。
原因有兩種解讀：
- **風險補償說**：小公司流動性差、倒閉風險高，投資人需要更高報酬補償
- **行為金融說**：市場對小型股關注少，容易被低估
"""))
c2.append(code("""\
# 計算滾動 10 年年化 SMB 溢酬
rolling_smb = (factors['SMB'] + 1).rolling(120).apply(np.prod, raw=True) ** (1/10) - 1

fig, axes = plt.subplots(2, 1, figsize=(13, 8))

# 累積報酬
axes[0].plot(cumret.index, cumret['SMB'], color='royalblue', linewidth=1)
axes[0].axhline(1, color='black', linewidth=0.5, linestyle='--')
axes[0].fill_between(cumret.index, 1, cumret['SMB'],
                     where=(cumret['SMB'] > 1), alpha=0.2, color='green', label='小型股領先')
axes[0].fill_between(cumret.index, cumret['SMB'], 1,
                     where=(cumret['SMB'] < 1), alpha=0.2, color='red', label='大型股領先')
axes[0].set_title('規模因子（SMB）累積報酬', fontsize=12)
axes[0].legend()

# 滾動 10 年溢酬
axes[1].bar(rolling_smb.dropna().index, rolling_smb.dropna() * 100,
            color=rolling_smb.dropna().apply(lambda x: 'steelblue' if x > 0 else 'salmon'),
            width=20, alpha=0.7)
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].set_title('SMB 滾動 10 年年化溢酬（%）', fontsize=12)
axes[1].set_ylabel('年化溢酬（%）')

plt.tight_layout()
plt.show()

smb_ann = (cumret['SMB'].iloc[-1]) ** (1/len(factors) * 12) - 1
print(f"SMB 全期年化溢酬：{smb_ann*100:.2f}%")
print(f"SMB 為正（小型股領先）的月份比例：{(factors['SMB']>0).mean()*100:.1f}%")
"""))

c2.append(md("""\
## 五、價值效應驗證（Value Premium）

**命題：高帳面市值比（便宜股、價值股）長期報酬優於低帳面市值比（成長股）（HML > 0）**

這挑戰了「好公司 = 好投資」的直覺：
即使是平庸的公司，如果夠便宜，長期報酬可能更好。

> **注意**：2010 年後科技股（低帳面市值比的成長股）強勢崛起，
> 導致價值溢酬近年明顯縮水，這是學術界正在激烈討論的議題。
"""))
c2.append(code("""\
rolling_hml = (factors['HML'] + 1).rolling(120).apply(np.prod, raw=True) ** (1/10) - 1

fig, axes = plt.subplots(2, 1, figsize=(13, 8))

axes[0].plot(cumret.index, cumret['HML'], color='forestgreen', linewidth=1)
axes[0].axhline(1, color='black', linewidth=0.5, linestyle='--')
axes[0].fill_between(cumret.index, 1, cumret['HML'],
                     where=(cumret['HML'] > 1), alpha=0.2, color='green', label='價值股領先')
axes[0].fill_between(cumret.index, cumret['HML'], 1,
                     where=(cumret['HML'] < 1), alpha=0.2, color='red', label='成長股領先')

# 標記 2007 年後的成長股時代
axes[0].axvspan(pd.Timestamp('2007-01'), cumret.index[-1], alpha=0.07, color='orange', label='成長股強勢期')
axes[0].set_title('價值因子（HML）累積報酬', fontsize=12)
axes[0].legend(fontsize=8)

axes[1].bar(rolling_hml.dropna().index, rolling_hml.dropna() * 100,
            color=rolling_hml.dropna().apply(lambda x: 'forestgreen' if x > 0 else 'salmon'),
            width=20, alpha=0.7)
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].set_title('HML 滾動 10 年年化溢酬（%）', fontsize=12)
axes[1].set_ylabel('年化溢酬（%）')

plt.tight_layout()
plt.show()

hml_ann = (cumret['HML'].iloc[-1]) ** (1/len(factors) * 12) - 1
print(f"HML 全期年化溢酬：{hml_ann*100:.2f}%")
recent = factors.loc['2010':, 'HML']
print(f"2010 年後 HML 月均報酬：{recent.mean()*100:.3f}%（{'正' if recent.mean()>0 else '負'}溢酬）")
"""))

c2.append(md("""\
## 六、動能效應驗證（Momentum）

**命題：過去 12 個月報酬排名高的股票，接下來 1 個月繼續領先（Mom > 0）**

動能效應是行為金融學的核心發現，和「均值回歸」直接矛盾：
- **均值回歸**說：漲多的會跌回來
- **動能效應**說：漲多的短期還會繼續漲

兩個都是真的——只是時間尺度不同（動能：1–12 個月；均值回歸：3–5 年）。

> **風險**：動能因子有「崩潰」特性——在市場急速反轉時會短暫大虧損（稱為 Momentum Crash）。
"""))
c2.append(code("""\
rolling_mom = (factors['Mom'] + 1).rolling(120).apply(np.prod, raw=True) ** (1/10) - 1

fig, axes = plt.subplots(2, 1, figsize=(13, 8))

axes[0].plot(cumret.index, cumret['Mom'], color='darkorange', linewidth=1)
axes[0].axhline(1, color='black', linewidth=0.5, linestyle='--')
axes[0].fill_between(cumret.index, 1, cumret['Mom'],
                     where=(cumret['Mom'] > 1), alpha=0.2, color='green', label='動能策略獲利')
axes[0].fill_between(cumret.index, cumret['Mom'], 1,
                     where=(cumret['Mom'] < 1), alpha=0.2, color='red', label='動能策略虧損')

# 標記動能崩潰（Momentum Crash）
crashes = {'1932\\n崩潰': '1932-08', '2009\\n崩潰': '2009-03'}
for label, d in crashes.items():
    date = pd.to_datetime(d)
    y = cumret['Mom'].asof(date)
    axes[0].annotate(label, xy=(date, y), xytext=(date, y * 1.5),
                     fontsize=8, ha='center', color='darkred',
                     arrowprops=dict(arrowstyle='->', color='darkred', lw=0.8))

axes[0].set_title('動能因子（Mom）累積報酬', fontsize=12)
axes[0].legend(fontsize=8)

axes[1].bar(rolling_mom.dropna().index, rolling_mom.dropna() * 100,
            color=rolling_mom.dropna().apply(lambda x: 'darkorange' if x > 0 else 'salmon'),
            width=20, alpha=0.7)
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].set_title('Mom 滾動 10 年年化溢酬（%）', fontsize=12)
axes[1].set_ylabel('年化溢酬（%）')

plt.tight_layout()
plt.show()
"""))

c2.append(md("## 七、四因子相關性"))
c2.append(code("""\
import matplotlib.colors as mcolors

corr = factors[['Mkt-RF','SMB','HML','Mom']].corr()

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
plt.colorbar(im, ax=ax)

labels = ['市場 (Mkt-RF)', '規模 (SMB)', '價值 (HML)', '動能 (Mom)']
ax.set_xticks(range(4)); ax.set_yticks(range(4))
ax.set_xticklabels(labels, fontsize=9)
ax.set_yticklabels(labels, fontsize=9)

for i in range(4):
    for j in range(4):
        ax.text(j, i, f'{corr.iloc[i,j]:.2f}', ha='center', va='center',
                fontsize=11, color='white' if abs(corr.iloc[i,j]) > 0.5 else 'black')

ax.set_title('四因子相關係數矩陣', fontsize=12)
plt.tight_layout()
plt.show()

print("\\n觀察：")
print(f"• Mkt-RF 與 SMB 相關性：{corr.loc['Mkt-RF','SMB']:.2f}")
print(f"• SMB 與 HML 相關性：{corr.loc['SMB','HML']:.2f}")
print(f"• HML 與 Mom 相關性：{corr.loc['HML','Mom']:.2f}（通常為負！）")
"""))

c2.append(md("""\
## 八、討論

**結論：三個因子溢酬（規模、價值、動能）在長達近百年的美股資料中確實存在。**

**思考問題：**
1. 如果這些溢酬是公開的學術研究結論，為什麼沒有被套利消失？
2. 價值溢酬在 2010 年後大幅萎縮。是因子失效了，還是只是暫時的週期？
3. 動能和均值回歸同時成立，差別只在時間尺度。你要怎麼用這個知識設計策略？
4. Fama-French 模型能解釋台股嗎？台股的小型股效應是否更明顯？
"""))

c2.append(md("""\
## 九、這跟你有什麼關係？

**因子溢酬存在，但費用會把它吃掉。**

這個研究最大的個人投資含義不是「去買小型價值股」，而是：

> 市場風險溢酬（Mkt-RF）是最穩定的因子，年化約 8%。
> 你只需要買一支費用率 0.1% 的全市場 ETF，就能拿到幾乎全部的市場溢酬。
> 主動選股試圖多拿 SMB/HML，但大多數人的交易成本和錯誤決策比這些溢酬還貴。
"""))
c2.append(code("""\
mkt_premium = factors['Mkt-RF'].mean() * 12 * 100   # 年化市場溢酬

products = [
    ("全市場 ETF（VOO/VT）",          0.03),
    ("台灣 0050 ETF",                  0.43),
    ("主動型基金（市場平均）",          1.50),
    ("高費用主動基金",                  2.50),
]

print(f"市場因子歷史年化溢酬：{mkt_premium:.1f}%")
print()
print(f"{'投資工具':^24} | {'年費用率':>8} | {'實際拿到':>10} | {'溢酬保留率':>10}")
print("-" * 60)
for name, fee in products:
    net  = mkt_premium - fee
    pct  = net / mkt_premium * 100
    print(f"  {name:^24} | {fee:>7.2f}% | {net:>9.1f}% | {pct:>9.0f}%")

print()
print("結論：選股能力要能持續超越市場 1.5% 以上，才有理由買主動型基金")
print("學術研究顯示，能長期做到這件事的主動基金，不到 10%")
print("對一般投資人而言，'不要輸給市場' 比 '打敗市場' 容易得多")
"""))

save(c2, "02_fama_french.ipynb")


# ══════════════════════════════════════════════════════════════════════════════
# Notebook 3：Damodaran 產業估值分析
# ══════════════════════════════════════════════════════════════════════════════
c3 = []

c3.append(md("""\
# 03 | Damodaran 產業估值分析
**資料來源：Aswath Damodaran（NYU Stern 商學院）— 估值領域最知名的學者**

> **核心問題：本益比 30 倍，是貴還是便宜？**
>
> 答案：要看跟誰比。本 Notebook 使用 Damodaran 整理的美股各產業估值資料，
> 建立「不同產業應該有不同估值基準」的分析框架。
"""))

c3.append(md("## ⚙️ Step 0：安裝套件"))
c3.append(code("""\
%pip install openpyxl xlrd
print("✅ 完成")
"""))

c3.append(md("## 匯入套件"))
c3.append(code(f"""\
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

c3.append(md("""\
## 一、為什麼估值要和同業比？

### Gordon Growth Model（股利折現模型）
> **合理 P/E = 配息率 ÷ （必要報酬率 − 成長率）**

這個公式說明了決定 P/E 倍數的三個關鍵：

| 變數 | 效果 | 例子 |
|------|------|------|
| **成長率 ↑** | P/E 應該更高 | 科技股高成長 → 高 P/E 合理 |
| **必要報酬率（風險）↑** | P/E 應該更低 | 能源股風險高 → P/E 較低 |
| **配息率 ↑** | P/E 應該更高 | 公用事業穩定配息 → 較高 P/E |

**結論：不同產業天生就應該有不同的 P/E 基準，用同一把尺比較是錯誤的。**
"""))

c3.append(md("## 二、載入 Damodaran 資料"))
c3.append(code("""\
import os

LOCAL = "data/damodaran_pe.csv"

if os.path.exists(LOCAL):
    df = pd.read_csv(LOCAL)
    print(f"✅ 從本機載入（{len(df)} 個產業）")
else:
    print("⏳ 從 NYU Damodaran 網站下載...")
    url = "https://pages.stern.nyu.edu/~adamodar/pc/datasets/pedata.xls"

    # Damodaran 檔案有 7 行 metadata，第 8 行才是欄位標題
    try:
        raw = pd.read_excel(url, sheet_name='Industry Averages', skiprows=7, header=0)
    except Exception:
        raw = pd.read_excel(url, sheet_name='Industry Averages', skiprows=7, header=0, engine='xlrd')

    # 欄位位置（固定，不隨年份異動）：
    # 0=Industry Name, 1=N firms, 2=Loss%, 3=Current PE, 4=Trailing PE,
    # 5=Forward PE, 6=MktCap/NI(all), 7=MktCap/NI(profitable), 8=Growth 5y, 9=PEG
    df = pd.DataFrame()
    df['industry']  = raw.iloc[:, 0].astype(str).str.strip()
    df['n_firms']   = pd.to_numeric(raw.iloc[:, 1], errors='coerce')
    df['pe']        = pd.to_numeric(raw.iloc[:, 3], errors='coerce')  # Current PE
    df['pe_adj']    = pd.to_numeric(raw.iloc[:, 7], errors='coerce')  # Mkt Cap/NI (profitable firms)
    df['growth_5y'] = pd.to_numeric(raw.iloc[:, 8], errors='coerce') * 100  # Expected 5yr growth → %
    df['peg']       = pd.to_numeric(raw.iloc[:, 9], errors='coerce')  # PEG Ratio

    # 過濾無效資料
    df = df[df['industry'].str.len() > 2].copy()
    df = df[df['n_firms'].notna() & (df['n_firms'] > 5)].copy()
    df = df.dropna(subset=['pe_adj'])
    df = df[df['pe_adj'] > 0].copy()       # 移除負 P/E
    df = df[df['pe_adj'] < 500].copy()     # 移除異常高值

    df.to_csv(LOCAL, index=False)
    print(f"✅ 下載完成，已快取（{len(df)} 個產業）")

print(f"\\n有效產業數：{len(df)}")
df.sort_values('pe_adj', ascending=False).head(10)
"""))

c3.append(md("## 三、各產業 P/E 分布"))
c3.append(code("""\
# 排序，取前後各 20 個產業，讓圖不要太擁擠
df_sorted = df.sort_values('pe_adj', ascending=True).reset_index(drop=True)

n_show = min(40, len(df_sorted))
df_plot = pd.concat([
    df_sorted.head(n_show // 2),
    df_sorted.tail(n_show // 2)
]).drop_duplicates()

colors = ['#e74c3c' if pe > df_sorted['pe_adj'].median() else '#2ecc71'
          for pe in df_plot['pe_adj']]

fig, ax = plt.subplots(figsize=(11, max(10, len(df_plot) * 0.32)))
bars = ax.barh(range(len(df_plot)), df_plot['pe_adj'], color=colors, alpha=0.8, edgecolor='white')
ax.set_yticks(range(len(df_plot)))
ax.set_yticklabels(df_plot['industry'], fontsize=8)
ax.axvline(df_sorted['pe_adj'].median(), color='black', linestyle='--', linewidth=1.2,
           label=f"中位數 ({df_sorted['pe_adj'].median():.1f}x)")
ax.set_xlabel('P/E（倍，排除虧損公司後調整）')
ax.set_title('美股各產業本益比（Damodaran）', fontsize=13)
ax.legend()
plt.tight_layout()
plt.show()

print(f"所有產業 P/E 中位數：{df['pe_adj'].median():.1f} 倍")
print(f"所有產業 P/E 均值：{df['pe_adj'].mean():.1f} 倍")
"""))

c3.append(md("## 四、最貴 vs 最便宜的產業"))
c3.append(code("""\
top10 = df.nlargest(10, 'pe_adj')[['industry','pe_adj','n_firms']].reset_index(drop=True)
bot10 = df.nsmallest(10, 'pe_adj')[['industry','pe_adj','n_firms']].reset_index(drop=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].barh(range(10), top10['pe_adj'][::-1], color='#e74c3c', alpha=0.8)
axes[0].set_yticks(range(10))
axes[0].set_yticklabels(top10['industry'][::-1], fontsize=9)
axes[0].set_xlabel('P/E（倍）')
axes[0].set_title('P/E 最高（最貴）10 個產業', fontsize=11)
for i, v in enumerate(top10['pe_adj'][::-1]):
    axes[0].text(v + 0.5, i, f'{v:.0f}x', va='center', fontsize=9)

axes[1].barh(range(10), bot10['pe_adj'], color='#2ecc71', alpha=0.8)
axes[1].set_yticks(range(10))
axes[1].set_yticklabels(bot10['industry'], fontsize=9)
axes[1].set_xlabel('P/E（倍）')
axes[1].set_title('P/E 最低（最便宜）10 個產業', fontsize=11)
for i, v in enumerate(bot10['pe_adj']):
    axes[1].text(v + 0.1, i, f'{v:.0f}x', va='center', fontsize=9)

plt.tight_layout()
plt.show()
"""))

c3.append(md("""\
## 五、是什麼決定了估值倍數？

**驗證：成長率越高的產業，P/E 是否真的越高？**

如果 Gordon Model 是對的，預期成長率高的產業應該獲得更高的 P/E 倍數。
"""))
c3.append(code("""\
valid = df.dropna(subset=['pe_adj', 'growth_5y']).copy()
valid = valid[(valid['growth_5y'] > -50) & (valid['growth_5y'] < 100)]

fig, ax = plt.subplots(figsize=(9, 6))
sc = ax.scatter(valid['growth_5y'], valid['pe_adj'],
                s=valid['n_firms'].clip(5, 500) / 5,
                alpha=0.5, color='steelblue', edgecolors='none')

# 趨勢線
z = np.polyfit(valid['growth_5y'], valid['pe_adj'], 1)
p = np.poly1d(z)
xr = np.linspace(valid['growth_5y'].min(), valid['growth_5y'].max(), 100)
ax.plot(xr, p(xr), 'r-', linewidth=2, label='趨勢線')

corr = valid['growth_5y'].corr(valid['pe_adj'])
ax.set_title(f'預期成長率 vs P/E\\n（相關係數 = {corr:.2f}，點的大小 = 公司數）', fontsize=12)
ax.set_xlabel('預期 5 年盈餘成長率（%）')
ax.set_ylabel('P/E（倍）')
ax.legend()
plt.tight_layout()
plt.show()

print(f"成長率 vs P/E 相關係數：{corr:.2f}")
"""))

c3.append(md("## 六、PEG 比率 — 把成長率納入估值"))
c3.append(code("""\
# PEG = P/E ÷ 成長率，理論上 PEG < 1 代表被低估
valid_peg = df.dropna(subset=['peg']).copy()
valid_peg = valid_peg[(valid_peg['peg'] > 0) & (valid_peg['peg'] < 10)]
valid_peg = valid_peg.sort_values('peg')

fig, ax = plt.subplots(figsize=(11, max(8, len(valid_peg) * 0.18)))
colors_peg = ['#2ecc71' if peg < 1.5 else '#e67e22' if peg < 3 else '#e74c3c'
              for peg in valid_peg['peg']]
ax.barh(range(len(valid_peg)), valid_peg['peg'], color=colors_peg, alpha=0.8)
ax.set_yticks(range(len(valid_peg)))
ax.set_yticklabels(valid_peg['industry'], fontsize=7)
ax.axvline(1.5, color='orange', linestyle='--', linewidth=1, label='PEG = 1.5（合理基準）')
ax.set_xlabel('PEG 比率')
ax.set_title('美股各產業 PEG 比率（綠 < 1.5 < 橙 < 3 < 紅）', fontsize=11)
ax.legend()
plt.tight_layout()
plt.show()
"""))

c3.append(md("""\
## 七、討論

**結論：估值必須在同業框架下比較，不同產業有天然不同的 P/E 基準。**

**思考問題：**
1. 軟體業的 P/E 通常遠高於銀行業。根據 Gordon Model，這合理嗎？原因是什麼？
2. PEG < 1 的產業是「真的便宜」還是「成長預期太低」？
3. 台積電的 P/E 應該跟哪些公司比？台灣半導體業的合理估值倍數是多少？
4. 熊市時估值會均值回歸（往均值靠攏）。哪些產業在熊市中 P/E 壓縮幅度最大？

**延伸應用：**
- 把 FinMind 的台股財報資料和這個框架結合，建立台股版的產業估值基準
- 每年 Damodaran 會更新資料，可以比較今年和去年的估值變化
"""))

c3.append(md("""\
## 八、這跟你有什麼關係？

**下次看到一支股票的 P/E，先問：「它跟誰比？」**

你剛才下載的 Damodaran 資料，就是你的估值基準表。
台灣學生最常討論的股票（台積電、聯發科、輝達）都在半導體產業——
讓我們直接查出這個產業的 P/E 基準是多少。
"""))
c3.append(code("""\
# 查詢你感興趣的產業 P/E 基準
keywords = ['Semiconductor', 'Software', 'Bank', 'Pharma', 'Retail', 'Auto']

print("Damodaran 產業 P/E 基準（可用來對照個股估值）：")
print()
print(f"{'產業':^34} | {'公司數':>6} | {'現值P/E':>9} | {'預期成長':>8} | {'PEG':>6}")
print("-" * 72)
for kw in keywords:
    matches = df[df['industry'].str.contains(kw, case=False, na=False)]
    for _, row in matches.head(2).iterrows():
        g_str = f"{row['growth_5y']:.1f}%" if pd.notna(row['growth_5y']) else "N/A"
        p_str = f"{row['peg']:.2f}"        if pd.notna(row['peg'])        else "N/A"
        print(f"  {row['industry']:^34} | {int(row['n_firms']):>6} | {row['pe_adj']:>9.1f}x | {g_str:>8} | {p_str:>6}")

print()
print("如何用這個表分析台積電（TSM）？")
print("  1. 找 Semiconductors 的產業 P/E → 這是「合理基準」")
print("  2. 台積電 P/E 高於基準 → 市場給予溢價，需要更高成長預期支撐")
print("  3. 台積電 P/E 低於基準 → 相對同業便宜，但要確認沒有基本面問題")
print()
semi = df[df['industry'].str.contains('Semiconductor', case=False, na=False)]
if not semi.empty:
    median_pe = semi['pe_adj'].median()
    print(f"目前半導體產業中位 P/E：{median_pe:.1f} 倍")
    print(f"→ 你持有或關注的半導體股，P/E 高於 {median_pe:.0f} 倍代表市場已給予溢價")
"""))

save(c3, "03_damodaran.ipynb")

print("\n✅ 全部完成！")
print(f"   資料夾：{BASE}")
