# demand_shortage_features.csv

## Overview
This dataset provides a monthly aggregated summary of inventory and demand per SKU.
It is designed to support demand forecasting and shortage detection in a supply chain context.
Each row represents a unique combination of SKU_Code, year, and month.

## Purpose
- Feed a demand forecasting model (target: mfg_units_sold_total).
- Detect stockout risk and urgent shortages at the SKU level.
- Provide actionable triggers for an AI agent to make replenishment decisions.

## Source
Derived from the raw file `model_full.csv` (supply chain operational data),
aggregated by SKU_Code, year, and month.

## Granularity
- Level: SKU x Month
- Rows: one per (SKU, year, month)
- Time span: depends on the source data

## Columns

| Column | Type | Description |
|---|---|---|
| SKU_Code | int | Unique product identifier |
| year | int | Year of the record |
| month | int | Month of the record (1-12) |
| year_month | string | Combined label in YYYY-MM format |
| mfg_units_sold_total | float | Total units sold for the SKU in the month |
| mfg_units_sold_mean | float | Average daily units sold for the SKU in the month |
| mfg_avg_inventory | float | Average inventory level (standardized) |
| mfg_below_rop_rate | float | Proportion of days inventory was below the Reorder Point (0-1) |
| mfg_avg_lead_time | float | Average supplier lead time in days |
| mfg_avg_days_cover | float | Average days of coverage (inventory / average demand) |
| mfg_promo_rate | float | Proportion of days with an active promotion (0-1) |
| mfg_avg_forecast | float | Average demand forecast (standardized) |
| mfg_avg_inv_vs_rop | float | Average gap between inventory level and Reorder Point |
| stockout_risk_flag | int (0/1) | 1 if mfg_below_rop_rate > 0.5 (high stockout risk) |
| urgent_shortage_flag | int (0/1) | 1 if mfg_avg_days_cover < mfg_avg_lead_time (imminent stockout) |

## Derived Flags
- stockout_risk_flag: indicates the SKU spent more than 50% of the month below its Reorder Point.
- urgent_shortage_flag: indicates the current coverage is shorter than the supplier lead time,
  meaning inventory will run out before the next shipment arrives.

## Notes & Caveats
- mfg_avg_inventory, mfg_avg_forecast, and mfg_avg_inv_vs_rop are standardized (mean ~0, std ~1).
  They are not in raw units.
- mfg_units_sold_total and mfg_units_sold_mean are in raw units and are suitable as regression targets.
- The dataset is time-series oriented. When modeling, use TimeSeriesSplit (not random KFold)
  to avoid data leakage.
- Some SKUs may have missing months if no records existed for that period.

## Suggested Use Cases
1. Demand Forecasting - predict mfg_units_sold_total.
2. Shortage Detection - flag SKUs where urgent_shortage_flag = 1.
3. Reorder Policy Optimization - compare mfg_avg_days_cover with mfg_avg_lead_time.
4. Agent Triggers - feed flags to an AI agent for automated replenishment.

## Example Row
SKU_Code,year,month,year_month,mfg_units_sold_total,mfg_units_sold_mean,mfg_avg_inventory,mfg_below_rop_rate,mfg_avg_lead_time,mfg_avg_days_cover,mfg_promo_rate,mfg_avg_forecast,mfg_avg_inv_vs_rop,stockout_risk_flag,urgent_shortage_flag
10,2017,9,2017-09,1520,50.6,0.42,0.61,5.2,3.1,0.12,0.38,-0.21,1,1

## Related Files
- market_signals.csv - market-level signals per category x month.
- model_full.csv - raw operational data (source).