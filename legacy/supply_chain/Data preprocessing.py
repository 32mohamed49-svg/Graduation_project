import pandas as pd, numpy as np
import sys, os, json
from sklearn.preprocessing import StandardScaler

df = pd.read_csv(r"C:\Users\Yathrip\Downloads\supply_chain_dataset1.csv")

print(df.head(10))

print(f"\nDataset contains {df.shape[0]} rows and {df.shape[1]} columns.")

df.info()

df.describe()

df.drop_duplicates(inplace=True)

print(df.isnull().sum())

null_percentages = df.isnull().mean() * 100

print("null_percentages")
print(null_percentages)

SRC = sys.argv[1] if len(sys.argv) > 1 else "supply_chain_dataset1.csv"
OUT = (sys.argv[2] if len(sys.argv) > 2 else "output").rstrip("/\\") + "/"
os.makedirs(OUT, exist_ok=True)
KEY = ["SKU_ID", "Warehouse_ID"]
TARGET = "Units_Sold"
rep = []
log = lambda s: (print(s), rep.append(s))


df = pd.read_csv(SRC, parse_dates=["Date"])
log(f"Raw shape: {df.shape}")
log(f"Missing values: {int(df.isna().sum().sum())} | duplicate rows: {df.duplicated().sum()} | duplicate (SKU,WH,Date): {df.duplicated(KEY+['Date']).sum()}")
for c in df.select_dtypes(include=["object", "string"]):
    df[c] = df[c].str.strip()
df = df.drop_duplicates()

neg = int((df.select_dtypes("number") < 0).sum().sum())
bad_price = int((df.Unit_Price <= df.Unit_Cost).sum())
log(f"Negative values: {neg} | price<=cost: {bad_price}")

const = [c for c in df.columns if df[c].nunique() == 1]
df = df.drop(columns=const)
log(f"Dropped constant columns: {const}")

full = pd.date_range(df.Date.min(), df.Date.max())
miss_days = full.difference(df.Date.unique())
log(f"Missing calendar days in range: {[str(d.date()) for d in miss_days]}")

df = df.sort_values(KEY + ["Date"]).reset_index(drop=True)
g = df.groupby(KEY, observed=True)


df["Month"] = df.Date.dt.month
df["DayOfWeek"] = df.Date.dt.dayofweek
df["WeekOfYear"] = df.Date.dt.isocalendar().week.astype(int)
df["IsWeekend"] = (df.DayOfWeek >= 5).astype(int)
df["IsMonthEnd"] = df.Date.dt.is_month_end.astype(int)
df["Month_sin"], df["Month_cos"] = np.sin(2*np.pi*df.Month/12), np.cos(2*np.pi*df.Month/12)
df["DOW_sin"], df["DOW_cos"] = np.sin(2*np.pi*df.DayOfWeek/7), np.cos(2*np.pi*df.DayOfWeek/7)

df["Unit_Margin"] = df.Unit_Price - df.Unit_Cost
df["Margin_Pct"] = df.Unit_Margin / df.Unit_Price
df["Inventory_vs_ROP"] = df.Inventory_Level - df.Reorder_Point
df["Below_ROP"] = (df.Inventory_Level <= df.Reorder_Point).astype(int)
df["Order_Placed"] = (df.Order_Quantity > 0).astype(int)
df["Order_Quantity_log"] = np.log1p(df.Order_Quantity)

for l in [1, 7, 14]:
    df[f"Sold_lag{l}"] = g[TARGET].shift(l)
for w in [7, 14, 30]:
    df[f"Sold_roll{w}_mean"] = g[TARGET].transform(lambda s: s.shift(1).rolling(w).mean())
df["Sold_roll7_std"] = g[TARGET].transform(lambda s: s.shift(1).rolling(7).std())
df["Forecast_lag1_err"] = g.apply(lambda x: (x[TARGET] - x.Demand_Forecast).shift(1), include_groups=False).reset_index(level=[0,1], drop=True)
df["Days_of_Cover"] = df.Inventory_Level / df.Sold_roll7_mean.clip(lower=1)   # uses past sales only


for c in ["Units_Sold", "Inventory_Level", "Demand_Forecast"]:
    q1, q3 = df[c].quantile([.25, .75]); i = q3 - q1
    m = (df[c] < q1-1.5*i) | (df[c] > q3+1.5*i)
    df[f"{c}_Outlier"] = m.astype(int)
    log(f"IQR outliers in {c}: {int(m.sum())} ({m.mean():.2%}) -> flagged, kept")

df.to_csv(OUT + "supply_chain_clean_full.csv", index=False)
log(f"Full clean file: {df.shape}")


WARM = 30
m = df.groupby(KEY, observed=True).cumcount() >= WARM
md = df[m].dropna().copy()
log(f"Dropped {len(df)-len(md)} warm-up rows (first {WARM} days per SKU-WH) -> {md.shape}")

md["SKU_Code"] = md.SKU_ID.str.extract(r"(\d+)").astype(int)
md = pd.get_dummies(md, columns=["Warehouse_ID", "Region", "Supplier_ID"], dtype=int)

ud = np.array(sorted(md.Date.unique()))
c1, c2 = ud[int(len(ud)*.70)], ud[int(len(ud)*.85)]
tr, va, te = md[md.Date < c1], md[(md.Date >= c1) & (md.Date < c2)], md[md.Date >= c2]
log(f"Time split | train < {str(c1)[:10]}: {len(tr)} | val < {str(c2)[:10]}: {len(va)} | test: {len(te)}")

clip_cols = ["Inventory_Level", "Inventory_vs_ROP", "Days_of_Cover", "Demand_Forecast"]
for c in clip_cols:
    lo, hi = tr[c].quantile([.005, .995])
    for d in (tr, va, te): d[c] = d[c].clip(lo, hi)

scale_cols = ["Inventory_Level", "Supplier_Lead_Time_Days", "Reorder_Point", "Unit_Cost", "Unit_Price",
              "Unit_Margin", "Margin_Pct", "Demand_Forecast", "Inventory_vs_ROP", "Order_Quantity_log",
              "Days_of_Cover", "Sold_lag1", "Sold_lag7", "Sold_lag14", "Sold_roll7_mean", "Sold_roll14_mean",
              "Sold_roll30_mean", "Sold_roll7_std", "Forecast_lag1_err", "WeekOfYear"]
sc = StandardScaler().fit(tr[scale_cols])
for d in (tr, va, te):
    d[scale_cols] = sc.transform(d[scale_cols])
json.dump({"cols": scale_cols, "mean": sc.mean_.tolist(), "scale": sc.scale_.tolist()},
          open(OUT + "scaler_params.json", "w"), indent=1)

drop = ["SKU_ID", "Order_Quantity", "Month", "DayOfWeek", "Units_Sold_Outlier"]
for n, d in [("train", tr), ("val", va), ("test", te)]:
    d.drop(columns=drop).to_csv(OUT + f"model_{n}.csv", index=False)
log(f"Model columns: {tr.drop(columns=drop).shape[1]} (target = {TARGET}, unscaled; Date kept for reference - drop before fitting)")
open(OUT + "cleaning_report.txt", "w").write("\n".join(rep))



folder = r"C:\Users\Yathrip\Downloads\output"

tr = pd.read_csv(folder + r"\model_train.csv"); tr["Split"] = "train"
va = pd.read_csv(folder + r"\model_val.csv");   va["Split"] = "val"
te = pd.read_csv(folder + r"\model_test.csv");  te["Split"] = "test"

full = pd.concat([tr, va, te], ignore_index=True)
full.to_csv(folder + r"\model_full.csv", index=False)
print(full.shape)   