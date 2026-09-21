# Brazilian E-Commerce (Olist) - Sales & Customer Analytics EDA

**Author:** Jimmy Le-Nguyen  
**GitHub:** [github.com/jimmyle9080](https://github.com/jimmyle9080)

---

## Overview

An end-to-end analytics pipeline built on the **Brazilian E-Commerce Public Dataset by Olist** - one of the most comprehensive real-world e-commerce datasets publicly available. The dataset spans **99,441 real orders across 9 relational tables** from 2016 to 2018, covering customers, sellers, products, payments, reviews, and logistics across all of Brazil.

---

## Why This Project Matters

This project shows:

- Ability to work with **multi-table relational data** (not just flat CSVs)
- **SQL joins and aggregations** across 9 normalized tables
- **Business-driven feature engineering** from raw transactional data
- **Customer segmentation** using spend-based tiering
- **Operational KPI monitoring** including delivery SLAs and satisfaction scores
- **Power BI integration** through structured CSV exports

---

## Key Business Findings

| Finding | Detail | Significance |
|---|---|---|
| Total revenue | $16,008,872 across 99,441 orders | Baseline for YoY growth tracking |
| Avg order value | $160.99 | Benchmark for upsell and basket size analysis |
| Top revenue state | SP (São Paulo) at $5,770,266 | 36% of all revenue from one state |
| Top revenue category | Health & Beauty at $1,258,681 | Consumer goods dominate over electronics |
| Most used payment | Credit card - 76,132 orders | Installment-based purchasing is dominant |
| Avg review score | 4.16 / 5.0 | Strong baseline customer satisfaction |
| 5-star review rate | 59.2% of all orders | Majority of customers highly satisfied |
| Late delivery rate | 6.8% (6,534 orders) | Meaningful operational improvement opportunity |
| Avg delivery time | 12.1 days | Significant vs same-day expectations in developed markets |

---

## Dataset

- **Source:** [Kaggle - Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **99,441 orders** | **9 relational tables** | **2016-2018**
- Licensed under CC BY-NC-SA 4.0

### Required Files
Place all 9 CSV files in the `data/` folder before running:
```
data/
├── olist_orders_dataset.csv
├── olist_customers_dataset.csv
├── olist_order_items_dataset.csv
├── olist_order_payments_dataset.csv
├── olist_order_reviews_dataset.csv
├── olist_products_dataset.csv
├── olist_sellers_dataset.csv
├── olist_sellers_dataset.csv
└── product_category_name_translation.csv
```
> Note: `olist_geolocation_dataset.csv` is excluded from this repo due to file size. It is not used in the analysis and can be downloaded separately from Kaggle if needed for mapping extensions.

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Navigate into the project folder
cd olist_project

# 3. Run everything (or open in VS Code and press play on main.py)
python3 main.py
```

Output folders are created automatically on first run. The Jupyter notebook `olist_analytics.ipynb` is also available for an interactive cell-by-cell walkthrough.

---

## Project Structure

```
olist_project/
├── data/                        # 9 Kaggle CSV files
├── outputs/
│   ├── charts/                  # 6 professional visualizations
│   └── exports/                 # Power BI-ready CSV exports
├── olist_analytics.ipynb        # Jupyter notebook version
├── main.py                      # Single entry point - run this
├── requirements.txt
└── README.md
```

---

## How the Data is Structured

The dataset uses a normalized relational schema - orders, customers, products, payments, and reviews are each in separate tables joined by keys. This is how real production databases are structured at companies like Amazon, Stripe, and PayPal.

```
olist_orders  ──── olist_customers      (customer_id)
     │
     ├────────── olist_order_items      (order_id)  ── olist_products
     │                                                       │
     │                                          product_category_translation
     ├────────── olist_order_payments   (order_id)
     ├────────── olist_order_reviews    (order_id)
     └────────── olist_sellers          (seller_id)
```

The pipeline joins all tables into a single master order-level dataset before analysis, rollup payments and reviews to one row per order, and translates Portuguese product categories to English.

---

## Outputs

### Charts (outputs/charts/)
| File | Description |
|---|---|
| 1_revenue_trends.png | Monthly revenue and order volume 2017-2018 |
| 2_category_analysis.png | Top 10 product categories by revenue and avg price |
| 3_payment_analysis.png | Payment type distribution and avg order value |
| 4_satisfaction_delivery.png | Review score distribution and delivery time by state |
| 5_revenue_by_state.png | Revenue and customer satisfaction by Brazilian state |
| 6_order_timing.png | Hourly and day-of-week order patterns |

### Power BI Exports (outputs/exports/)
| File | Description |
|---|---|
| orders_master.csv | Full joined dataset - all 99,441 orders with all features |
| customer_segments.csv | Customer segmentation by lifetime spend tier |
| monthly_revenue.csv | Monthly revenue and order volume trends |
| revenue_by_state.csv | State-level revenue and satisfaction analysis |
| top_categories.csv | Top product categories by revenue and avg price |
| payment_type_analysis.csv | Payment method breakdown and avg order values |
| delivery_performance.csv | Delivery KPIs and late rate by state |
| review_score_distribution.csv | Customer satisfaction breakdown with delivery correlation |
| hourly_orders.csv | Order timing patterns by hour and day of week |

---

## Chart Insights

### Revenue & Order Volume Trends (2017-2018)
![Revenue Trends](outputs/charts/1_revenue_trends.png)

- Monthly revenue and order volume plotted side by side for 2017 vs 2018
- Revenue grew significantly year over year across almost every month
- November shows a clear spike in both years driven by Black Friday
- The 2018 line consistently sits above 2017, confirming strong and sustained platform growth

---

### Product Category Performance
![Category Analysis](outputs/charts/2_category_analysis.png)

- Top 10 categories ranked by total revenue (left) and average item price (right)
- Health & Beauty leads in total revenue, followed by Watches & Gifts and Bed/Bath/Table
- The avg price chart reveals a different pattern -- computers and furniture have high prices but lower order volumes, meaning fewer but higher-value transactions
- High revenue does not always mean high price per item, and high price does not always mean high total revenue

---

### Payment Behavior Analysis
![Payment Analysis](outputs/charts/3_payment_analysis.png)

- Order volume and average order value broken down by payment type
- Credit card dominates with 76,132 orders
- Boleto (a Brazilian bank slip where customers pay at a bank or ATM) is the second most common, unique to the Brazilian market
- Voucher orders have the lowest average order value, suggesting they are used for smaller promotional purchases
- Debit card usage is minimal compared to credit, indicating customers prefer installment-based credit purchasing

---

### Customer Satisfaction & Delivery Performance
![Satisfaction and Delivery](outputs/charts/4_satisfaction_delivery.png)

- Left: distribution of review scores from 1 to 5 across all delivered orders
- Right: top 10 Brazilian states by average delivery time in days
- 59.2% of orders receive a 5-star review with an overall average of 4.16/5.0
- The 1-star bucket is the second largest category, suggesting customers either love or hate the experience with little middle ground
- States further from Sao Paulo's distribution infrastructure experience significantly longer delivery times
- Longer delivery times correlate directly with lower review scores, confirming delivery speed as a key satisfaction driver

---

### Revenue and Customer Satisfaction by State
![Revenue by State](outputs/charts/5_revenue_by_state.png)

- Total revenue per Brazilian state (bars) overlaid with average review score (line) for the top 12 states
- Sao Paulo (SP) generates $5.77M, nearly 3x more than Rio de Janeiro (RJ) in second place
- The steep revenue dropoff shows how concentrated demand is in SP
- RJ has one of the lowest satisfaction scores despite being the second highest revenue state, pointing to a fulfillment or delivery quality issue in that market
- High revenue and high satisfaction do not always go together -- this chart makes that gap visible

---

### Order Timing Patterns
![Order Timing](outputs/charts/6_order_timing.png)

- Order volume by hour of day (left) and day of week (right)
- Orders peak in the early afternoon between 1pm and 4pm
- Monday is the highest volume day, suggesting customers browse over the weekend and convert on Monday
- Weekdays significantly outperform weekends across all days
- The hourly pattern is consistent, indicating predictable demand windows throughout the day

---

## Customer Segmentation

Customers are segmented by total lifetime spend into four tiers:

| Segment | Spend Range | Behavior |
|---|---|---|
| Budget | $0 - $100 | Single or low-value purchases, price-sensitive |
| Mid-tier | $100 - $300 | Repeat purchasers, moderate basket size |
| Premium | $300 - $1,000 | High engagement, category-diverse shoppers |
| VIP | $1,000+ | Highest lifetime value, retention priority |

**Why this matters:**
- Customer segmentation by lifetime value is a foundational technique in CRM and retention strategy
- Understanding which customers are in which tier and what drives movement between tiers helps identify where to focus retention efforts
- Budget customers represent volume, VIP customers represent disproportionate revenue -- treating them the same way is a missed opportunity

---

## Technical Approach

### Multi-Table SQL Joins
The core analytical challenge of this dataset is working with 9 normalized relational tables. The pipeline:
1. Loads all 9 CSVs into an in-memory SQLite database
2. Aggregates payments to one row per order (sum of payment value, mode of payment type)
3. Aggregates items to one row per order (count, total price, total freight)
4. Aggregates reviews to one row per order (mean score)
5. Joins everything through the orders table as the central fact table
6. Translates Portuguese category names to English via a lookup join

### Feature Engineering
- `delivery_days` - actual days between purchase timestamp and delivery
- `delivery_delta` - actual vs estimated delivery (positive = late)
- `delivered_late` - binary flag for SLA breach
- `purchase_hour`, `purchase_dow`, `purchase_month` - time-based behavioral features
- `customer_segment` - spend-tier segmentation (Budget / Mid-tier / Premium / VIP)

### SQL Analysis Queries
Six core SQL queries drive the analysis:
- **Monthly revenue** - YoY growth tracking with order volume
- **Revenue by state** - geographic revenue concentration and satisfaction correlation
- **Top categories** - product mix by revenue and average price
- **Payment type analysis** - payment method behavior and order value
- **Delivery performance** - SLA breach rate and average delivery time by state
- **Review score distribution** - satisfaction breakdown with delivery correlation

---

## Skills Demonstrated

- **Python** - Pandas, NumPy, Matplotlib, Seaborn, multi-table merging, datetime parsing
- **SQL** - SQLite with multi-table joins, window functions, GROUP BY aggregations, CASE logic
- **Data Modeling** - Working with normalized relational schema across 9 tables
- **EDA** - Revenue trends, geographic analysis, customer behavior, satisfaction analysis
- **Feature Engineering** - Time-based features, SLA calculations, spend-tier segmentation
- **Business Storytelling** - Translating transactional data into actionable business insights
- **Power BI Integration** - Structured CSV exports for live dashboard connection

---

## License

Dataset licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).  
Code: MIT License.
