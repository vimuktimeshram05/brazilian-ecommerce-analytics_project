"""
Brazilian E-Commerce (Olist) - Sales & Customer Analytics EDA
Author: Jimmy Le-Nguyen
GitHub: https://github.com/jimmyle9080

Dataset: Brazilian E-Commerce Public Dataset by Olist (Kaggle)
99,441 orders | 9 relational tables | 2016-2018

How to run:
    1. pip install -r requirements.txt
    2. Navigate into the project folder: cd olist_project
    3. Run main.py (or press the play button in VS Code)

Outputs:
    - outputs/charts/  : 6 professional visualizations
    - outputs/exports/ : Power BI-ready CSV exports
"""

from pathlib import Path
Path("outputs/charts").mkdir(parents=True, exist_ok=True)
Path("outputs/exports").mkdir(parents=True, exist_ok=True)

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Colors ─────────────────────────────────────────────────────────────────────
PRIMARY_COLOR = "#2A9D8F"
ACCENT_COLOR  = "#E76F51"
BLUE_COLOR    = "#457B9D"
WARN_COLOR    = "#E9C46A"
BG_COLOR      = "#F8F9FA"

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'figure.facecolor': BG_COLOR,
    'axes.facecolor': 'white',
    'axes.spines.top': False,
    'axes.spines.right': False
})

# ── Step 1: Load & Join ────────────────────────────────────────────────────────
print("=" * 60)
print("  BRAZILIAN E-COMMERCE (OLIST) - ANALYTICS EDA")
print("  Author: Jimmy Le-Nguyen")
print("=" * 60)

print("\n[1/6] Loading and joining datasets...")

orders    = pd.read_csv("data/olist_orders_dataset.csv")
customers = pd.read_csv("data/olist_customers_dataset.csv")
items     = pd.read_csv("data/olist_order_items_dataset.csv")
payments  = pd.read_csv("data/olist_order_payments_dataset.csv")
reviews   = pd.read_csv("data/olist_order_reviews_dataset.csv")
products  = pd.read_csv("data/olist_products_dataset.csv")
sellers   = pd.read_csv("data/olist_sellers_dataset.csv")
cat_trans = pd.read_csv("data/product_category_name_translation.csv")

# Parse timestamps
for col in ['order_purchase_timestamp','order_approved_at',
            'order_delivered_customer_date','order_estimated_delivery_date']:
    orders[col] = pd.to_datetime(orders[col], errors='coerce')

# Feature engineering
orders['purchase_year']       = orders['order_purchase_timestamp'].dt.year
orders['purchase_month']      = orders['order_purchase_timestamp'].dt.month
orders['purchase_month_name'] = orders['order_purchase_timestamp'].dt.strftime('%b')
orders['purchase_dow']        = orders['order_purchase_timestamp'].dt.day_name()
orders['purchase_hour']       = orders['order_purchase_timestamp'].dt.hour
orders['delivery_days']       = (orders['order_delivered_customer_date'] -
                                   orders['order_purchase_timestamp']).dt.days
orders['delivery_delta']      = (orders['order_delivered_customer_date'] -
                                   orders['order_estimated_delivery_date']).dt.days
orders['delivered_late']      = (orders['delivery_delta'] > 0).astype(int)

# Rollup payments, items, reviews to one row per order
pay_agg = payments.groupby('order_id').agg(
    total_payment=('payment_value', 'sum'),
    payment_installments=('payment_installments', 'max'),
    payment_type=('payment_type', lambda x: x.mode()[0])
).reset_index()

items_agg = items.groupby('order_id').agg(
    total_items=('order_item_id', 'count'),
    total_price=('price', 'sum'),
    total_freight=('freight_value', 'sum')
).reset_index()

rev_agg = reviews.groupby('order_id').agg(
    review_score=('review_score', 'mean')
).reset_index()

products = products.merge(cat_trans, on='product_category_name', how='left')

# Build master table
master = (orders
    .merge(customers[['customer_id','customer_state','customer_city']], on='customer_id', how='left')
    .merge(pay_agg,   on='order_id', how='left')
    .merge(items_agg, on='order_id', how='left')
    .merge(rev_agg,   on='order_id', how='left')
)

delivered     = master[master['order_status'] == 'delivered'].copy()
total_revenue = pay_agg['total_payment'].sum()
avg_order     = pay_agg['total_payment'].mean()
late_rate     = delivered['delivered_late'].mean() * 100

print(f"   Total orders       : {len(master):,}")
print(f"   Delivered orders   : {len(delivered):,}")
print(f"   Total revenue      : ${total_revenue:,.0f}")
print(f"   Avg order value    : ${avg_order:.2f}")
print(f"   Late delivery rate : {late_rate:.1f}%")
print(f"   Unique customers   : {master['customer_id'].nunique():,}")
print(f"   Unique sellers     : {items['seller_id'].nunique():,}")
print(f"   Unique products    : {items['product_id'].nunique():,}")

# ── Step 2: SQL Analysis ───────────────────────────────────────────────────────
print("\n[2/6] Running SQL analysis...")
conn = sqlite3.connect(":memory:")
master.to_sql("orders_master", conn, if_exists="replace", index=False)
items.to_sql("order_items",    conn, if_exists="replace", index=False)
products.to_sql("products",    conn, if_exists="replace", index=False)
pay_agg.to_sql("payments",     conn, if_exists="replace", index=False)

queries = {
    "monthly_revenue": """
        SELECT purchase_year, purchase_month, purchase_month_name,
               COUNT(*) AS order_count,
               ROUND(SUM(total_payment), 2) AS total_revenue,
               ROUND(AVG(total_payment), 2) AS avg_order_value
        FROM orders_master
        WHERE order_status = 'delivered'
          AND purchase_year IN (2017, 2018)
        GROUP BY purchase_year, purchase_month, purchase_month_name
        ORDER BY purchase_year, purchase_month
    """,
    "revenue_by_state": """
        SELECT customer_state,
               COUNT(*) AS order_count,
               ROUND(SUM(total_payment), 2) AS total_revenue,
               ROUND(AVG(total_payment), 2) AS avg_order_value,
               ROUND(AVG(review_score), 2) AS avg_review_score
        FROM orders_master
        WHERE order_status = 'delivered'
        GROUP BY customer_state
        ORDER BY total_revenue DESC
        LIMIT 15
    """,
    "top_categories": """
        SELECT p.product_category_name_english AS category,
               COUNT(DISTINCT oi.order_id) AS order_count,
               ROUND(SUM(oi.price), 2) AS total_revenue,
               ROUND(AVG(oi.price), 2) AS avg_price,
               ROUND(SUM(oi.freight_value), 2) AS total_freight
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE p.product_category_name_english IS NOT NULL
        GROUP BY category
        ORDER BY total_revenue DESC
        LIMIT 15
    """,
    "payment_type_analysis": """
        SELECT payment_type,
               COUNT(*) AS order_count,
               ROUND(SUM(total_payment), 2) AS total_revenue,
               ROUND(AVG(total_payment), 2) AS avg_order_value,
               ROUND(AVG(payment_installments), 1) AS avg_installments
        FROM payments
        GROUP BY payment_type
        ORDER BY total_revenue DESC
    """,
    "delivery_performance": """
        SELECT customer_state,
               COUNT(*) AS delivered_orders,
               ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
               SUM(delivered_late) AS late_deliveries,
               ROUND(SUM(delivered_late)*100.0/COUNT(*), 1) AS late_rate_pct,
               ROUND(AVG(review_score), 2) AS avg_review_score
        FROM orders_master
        WHERE order_status = 'delivered'
          AND delivery_days IS NOT NULL
        GROUP BY customer_state
        ORDER BY late_rate_pct DESC
        LIMIT 15
    """,
    "review_score_distribution": """
        SELECT CAST(review_score AS INT) AS review_score,
               COUNT(*) AS order_count,
               ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(), 1) AS pct,
               ROUND(AVG(total_payment), 2) AS avg_order_value,
               ROUND(AVG(delivery_days), 1) AS avg_delivery_days
        FROM orders_master
        WHERE order_status = 'delivered'
          AND review_score IS NOT NULL
        GROUP BY CAST(review_score AS INT)
        ORDER BY review_score
    """,
    "hourly_orders": """
        SELECT purchase_hour,
               COUNT(*) AS order_count,
               ROUND(AVG(total_payment), 2) AS avg_order_value
        FROM orders_master
        WHERE order_status = 'delivered'
        GROUP BY purchase_hour
        ORDER BY purchase_hour
    """,
    "summary_stats": """
        SELECT
            COUNT(*) AS total_orders,
            COUNT(DISTINCT customer_id) AS unique_customers,
            ROUND(SUM(total_payment), 2) AS total_revenue,
            ROUND(AVG(total_payment), 2) AS avg_order_value,
            ROUND(AVG(review_score), 2) AS avg_review_score,
            ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
            SUM(delivered_late) AS late_deliveries,
            ROUND(SUM(delivered_late)*100.0/COUNT(*), 1) AS late_rate_pct
        FROM orders_master
        WHERE order_status = 'delivered'
          AND delivery_days IS NOT NULL
    """
}

results = {}
for name, query in queries.items():
    results[name] = pd.read_sql_query(query, conn)
    results[name].to_csv(f"outputs/exports/{name}.csv", index=False)

conn.close()

stats     = results["summary_stats"].iloc[0]
top_cats  = results["top_categories"]
state_rev = results["revenue_by_state"]
pay_data  = results["payment_type_analysis"]

print(f"   Avg review score     : {stats['avg_review_score']:.2f} / 5.0")
print(f"   Avg delivery days    : {stats['avg_delivery_days']} days")
print(f"   Late deliveries      : {int(stats['late_deliveries']):,} ({stats['late_rate_pct']}%)")
print(f"   Top revenue category : {top_cats.iloc[0]['category']} (${top_cats.iloc[0]['total_revenue']:,.0f})")
print(f"   Top revenue state    : {state_rev.iloc[0]['customer_state']} (${state_rev.iloc[0]['total_revenue']:,.0f})")

# Customer segmentation
customer_spend = (master[master['order_status']=='delivered']
                  .groupby('customer_id')
                  .agg(total_orders=('order_id','count'),
                       total_spend=('total_payment','sum'),
                       avg_review=('review_score','mean'),
                       customer_state=('customer_state','first'))
                  .reset_index())
customer_spend['segment'] = pd.cut(customer_spend['total_spend'],
                                     bins=[0,100,300,1000,100000],
                                     labels=['Budget','Mid-tier','Premium','VIP'])
customer_spend.to_csv("outputs/exports/customer_segments.csv", index=False)
master.to_csv("outputs/exports/orders_master.csv", index=False)

# ── Step 3: Visualizations ─────────────────────────────────────────────────────
print("\n[3/6] Generating visualizations...")

# Chart 1: Monthly Revenue Trend
fig, axes = plt.subplots(2, 1, figsize=(14, 8))
fig.suptitle('Revenue & Order Volume Trends (2017-2018)', fontsize=14, fontweight='bold')

monthly = results["monthly_revenue"]
m17 = monthly[monthly['purchase_year'] == 2017]
m18 = monthly[monthly['purchase_year'] == 2018]

axes[0].plot(m17['purchase_month'], m17['total_revenue'], marker='o',
              color=BLUE_COLOR, linewidth=2, label='2017', markersize=5)
axes[0].plot(m18['purchase_month'], m18['total_revenue'], marker='o',
              color=ACCENT_COLOR, linewidth=2, label='2018', markersize=5)
axes[0].set_ylabel('Total Revenue ($)')
axes[0].set_title('Monthly Revenue by Year')
axes[0].legend()
axes[0].set_xticks(range(1, 13))
axes[0].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun',
                           'Jul','Aug','Sep','Oct','Nov','Dec'])

axes[1].bar(m17['purchase_month'] - 0.2, m17['order_count'],
             width=0.4, color=BLUE_COLOR, alpha=0.8, label='2017')
axes[1].bar(m18['purchase_month'] + 0.2, m18['order_count'],
             width=0.4, color=ACCENT_COLOR, alpha=0.8, label='2018')
axes[1].set_ylabel('Order Count')
axes[1].set_title('Monthly Order Volume by Year')
axes[1].legend()
axes[1].set_xticks(range(1, 13))
axes[1].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun',
                           'Jul','Aug','Sep','Oct','Nov','Dec'])

plt.tight_layout()
plt.savefig("outputs/charts/1_revenue_trends.png", dpi=150, bbox_inches='tight')
plt.close()

# Chart 2: Top Product Categories
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Product Category Performance', fontsize=14, fontweight='bold')

cat10 = top_cats.head(10)
axes[0].barh(cat10['category'], cat10['total_revenue'],
              color=PRIMARY_COLOR, alpha=0.85, edgecolor='white')
axes[0].set_xlabel('Total Revenue ($)')
axes[0].set_title('Top 10 Categories by Revenue')
axes[0].invert_yaxis()

axes[1].barh(cat10['category'], cat10['avg_price'],
              color=ACCENT_COLOR, alpha=0.85, edgecolor='white')
axes[1].set_xlabel('Avg Item Price ($)')
axes[1].set_title('Top 10 Categories by Avg Price')
axes[1].invert_yaxis()

plt.tight_layout()
plt.savefig("outputs/charts/2_category_analysis.png", dpi=150, bbox_inches='tight')
plt.close()

# Chart 3: Payment Analysis
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Payment Behavior Analysis', fontsize=14, fontweight='bold')

colors_pay = [PRIMARY_COLOR, ACCENT_COLOR, WARN_COLOR, BLUE_COLOR]
axes[0].bar(pay_data['payment_type'], pay_data['order_count'],
             color=colors_pay[:len(pay_data)], edgecolor='white')
axes[0].set_xlabel('Payment Type')
axes[0].set_ylabel('Order Count')
axes[0].set_title('Orders by Payment Type')
for i, v in enumerate(pay_data['order_count']):
    axes[0].text(i, v + 100, f'{v:,}', ha='center', fontsize=9, fontweight='bold')

axes[1].bar(pay_data['payment_type'], pay_data['avg_order_value'],
             color=colors_pay[:len(pay_data)], edgecolor='white')
axes[1].set_xlabel('Payment Type')
axes[1].set_ylabel('Avg Order Value ($)')
axes[1].set_title('Avg Order Value by Payment Type')
for i, v in enumerate(pay_data['avg_order_value']):
    axes[1].text(i, v + 1, f'${v:.0f}', ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig("outputs/charts/3_payment_analysis.png", dpi=150, bbox_inches='tight')
plt.close()

# Chart 4: Review Scores & Delivery
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Customer Satisfaction & Delivery Performance', fontsize=14, fontweight='bold')

rev_data   = results["review_score_distribution"]
del_data   = results["delivery_performance"]
rev_colors = ['#E63946','#E76F51','#E9C46A','#2A9D8F','#457B9D']

bars = axes[0].bar(rev_data['review_score'].astype(str),
                    rev_data['order_count'], color=rev_colors, edgecolor='white')
axes[0].set_xlabel('Review Score (1=Low, 5=High)')
axes[0].set_ylabel('Order Count')
axes[0].set_title('Review Score Distribution')
for bar, (_, row) in zip(bars, rev_data.iterrows()):
    axes[0].text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 200,
                 f'{row["pct"]}%', ha='center', fontsize=9, fontweight='bold')

axes[1].barh(del_data.head(10)['customer_state'],
              del_data.head(10)['avg_delivery_days'],
              color=ACCENT_COLOR, alpha=0.8, edgecolor='white')
axes[1].set_xlabel('Avg Delivery Days')
axes[1].set_title('Top 10 States by Avg Delivery Time')
axes[1].invert_yaxis()

plt.tight_layout()
plt.savefig("outputs/charts/4_satisfaction_delivery.png", dpi=150, bbox_inches='tight')
plt.close()

# Chart 5: Revenue by State
fig, ax = plt.subplots(figsize=(14, 6))
state12 = state_rev.head(12)
ax2 = ax.twinx()
ax.bar(state12['customer_state'], state12['total_revenue'],
        color=PRIMARY_COLOR, alpha=0.8, edgecolor='white', label='Total Revenue')
ax2.plot(state12['customer_state'], state12['avg_review_score'],
          color=ACCENT_COLOR, marker='o', linewidth=2, markersize=6,
          label='Avg Review Score')
ax.set_xlabel('Customer State')
ax.set_ylabel('Total Revenue ($)', color=PRIMARY_COLOR)
ax2.set_ylabel('Avg Review Score', color=ACCENT_COLOR)
ax2.set_ylim(3, 5)
ax.set_title('Revenue and Customer Satisfaction by State (Top 12)',
              fontsize=13, fontweight='bold')
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
plt.tight_layout()
plt.savefig("outputs/charts/5_revenue_by_state.png", dpi=150, bbox_inches='tight')
plt.close()

# Chart 6: Order Timing
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Order Timing Patterns', fontsize=14, fontweight='bold')

hourly = results["hourly_orders"]
axes[0].bar(hourly['purchase_hour'], hourly['order_count'],
             color=PRIMARY_COLOR, alpha=0.8, edgecolor='white')
axes[0].set_xlabel('Hour of Day')
axes[0].set_ylabel('Order Count')
axes[0].set_title('Orders by Hour of Day')
axes[0].set_xticks(range(0, 24))

dow_order  = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
dow_counts = (master[master['order_status']=='delivered']
              ['purchase_dow'].value_counts()
              .reindex(dow_order, fill_value=0))
axes[1].bar(range(7), dow_counts.values,
             color=[PRIMARY_COLOR if d not in ['Saturday','Sunday'] else WARN_COLOR
                    for d in dow_order], edgecolor='white')
axes[1].set_xticks(range(7))
axes[1].set_xticklabels(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
axes[1].set_ylabel('Order Count')
axes[1].set_title('Orders by Day of Week')
weekday_p = mpatches.Patch(color=PRIMARY_COLOR, label='Weekday')
weekend_p = mpatches.Patch(color=WARN_COLOR,    label='Weekend')
axes[1].legend(handles=[weekday_p, weekend_p])

plt.tight_layout()
plt.savefig("outputs/charts/6_order_timing.png", dpi=150, bbox_inches='tight')
plt.close()

# ── Step 4: Summary ────────────────────────────────────────────────────────────
print("\n[4/6] Exports saved to outputs/exports/")
print("\n[5/6] Charts saved to outputs/charts/")
print("\n[6/6] Done!")
print(f"\n   CHARTS  -> outputs/charts/")
print(f"   EXPORTS -> outputs/exports/")
print(f"\n   Total orders         : {len(master):,}")
print(f"   Total revenue        : ${total_revenue:,.0f}")
print(f"   Avg order value      : ${avg_order:.2f}")
print(f"   Avg review score     : {stats['avg_review_score']:.2f} / 5.0")
print(f"   Late delivery rate   : {stats['late_rate_pct']}%")
print(f"   Top revenue category : {top_cats.iloc[0]['category']}")
print(f"   Top revenue state    : {state_rev.iloc[0]['customer_state']}")
print("\n" + "=" * 60)
print("  Connect outputs/exports/ to Power BI for live dashboard")
print("=" * 60)
