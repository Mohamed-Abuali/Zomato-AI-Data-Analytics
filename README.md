# Zomato AI Data Analytics Platform

> An end-to-end, production-style analytics engineering project demonstrating modern data warehousing, dimensional modeling, workflow orchestration, and LLM-powered enrichment on food-delivery data.

[![dbt](https://img.shields.io/badge/dbt-1.12-FF694A?logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Snowflake](https://img.shields.io/badge/Snowflake-Data%20Warehouse-29B5E8?logo=snowflake&logoColor=white)](https://www.snowflake.com/)
[![Airflow](https://img.shields.io/badge/Apache%20Airflow-Orchestration-017CEE?logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-LLM%20Enrichment-412991?logo=openai&logoColor=white)](https://openai.com/)

---

## Executive Summary

This portfolio project simulates the analytics platform of a food-delivery marketplace (Zomato-style). It ingests raw transactional data into **Snowflake**, transforms it through a layered dbt project into an **analytics-ready star schema**, orchestrates end-to-end batch workflows with **Apache Airflow (Dockerized)**, and augments unstructured customer reviews with **LLM-powered sentiment and topic enrichment**.

The project is designed to showcase the skills of a modern **Analytics / Data Engineer**:
- Warehouse-first ELT design
- Dimensional modeling (Kimball star schema)
- Data quality testing & documentation with dbt
- Workflow orchestration with Airflow
- Secure programmatic auth (Snowflake **key-pair authentication**)
- Practical GenAI integration (OpenAI, structured JSON outputs)
- Reproducible dev environment (venv, Docker Compose)

---

## Key Highlights (for Reviewers)

- **Layered dbt project** with 7 staging views and 10 mart models (dims, facts, business marts).
- **Star schema** with conformed dimensions (`dim_customer`, `dim_restaurants`, `dim_food`, `dim_date`) and grain-explicit facts (`fct_orders`, `fact_order_items`).
- **Business marts** delivering KPIs: daily city revenue, delivery SLA performance, and restaurant scorecards.
- **Data contracts & tests** declared in `_sources.yml`, `_staging.yml`, `_marts.yml` (uniqueness, not-null, referential integrity).
- **Airflow DAG** (`zomato_batch.py`) orchestrating the ingest → dbt run → dbt test → AI enrichment flow.
- **LLM enrichment pipeline** (`enrich_reviews.py`) classifying reviews with `gpt-4o-mini` and persisting structured outputs to `ZOMATO.AI.REVIEW_ENRICHED`.
- **Secure connectivity** via Snowflake RSA key-pair authentication (no passwords, MFA-safe).

---

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│   Raw CSV / Source  │ ──▶ │  Snowflake — RAW    │ ──▶ │  dbt Staging (views) │
│  (orders, reviews…) │     │       schema        │     │      staging.*       │
└─────────────────────┘     └─────────────────────┘     └──────────┬───────────┘
                                                                   │
                                                                   ▼
┌──────────────────────────────────────┐          ┌────────────────────────────┐
│  AI Enrichment (OpenAI gpt-4o-mini)  │◀────────│   dbt Marts (tables)       │
│  ZOMATO.AI.REVIEW_ENRICHED           │          │  dim_*, fct_*, mart_*      │
└──────────────────────────────────────┘          └──────────────┬─────────────┘
                                                                 │
                                                                 ▼
                                                    ┌─────────────────────────┐
                                                    │  BI / Analytics / ML    │
                                                    └─────────────────────────┘

                    Orchestrated by Apache Airflow (Docker Compose)
```

---

## Tech Stack

| Layer                  | Technology                                          |
| ---------------------- | --------------------------------------------------- |
| **Data Warehouse**     | Snowflake                                           |
| **Transformation**     | dbt-core, dbt-snowflake                             |
| **Orchestration**      | Apache Airflow (Docker Compose)                     |
| **AI / LLM**           | OpenAI (`gpt-4o-mini`), structured JSON responses   |
| **Language**           | Python 3.10+, SQL, Jinja                            |
| **Auth**               | Snowflake key-pair (RSA) authentication             |
| **Environment Config** | `python-dotenv`                                     |
| **Version Control**    | Git / GitHub                                        |

---

## Repository Layout

```
zomato_ai_data_analytics_project/
├── zomato/                            # dbt project root
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/                   # Source-aligned views (RAW → staging)
│   │   │   ├── _sources.yml           # Source table declarations
│   │   │   ├── _staging.yml           # Column-level tests & docs
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_order_items.sql
│   │   │   ├── stg_users.sql
│   │   │   ├── stg_reviews.sql
│   │   │   ├── stg_restaurants.sql
│   │   │   ├── stg_food.sql
│   │   │   └── stg_men.sql            # menu staging
│   │   └── marts/                     # Dimensional models & business marts
│   │       ├── _marts.yml
│   │       ├── dim_customer.sql
│   │       ├── dim_restaurants.sql
│   │       ├── dim_food.sql
│   │       ├── dim_date.sql
│   │       ├── fct_orders.sql
│   │       ├── fact_order_items.sql
│   │       ├── mart_daily_city_revenune.sql
│   │       ├── mart_delivery_sla.sql
│   │       └── mart_restaurant_performance.sql
│   ├── ai/
│   │   ├── enrich_reviews.py          # LLM sentiment / topic classifier
│   │   └── text_to_sql.py             # Text-to-SQL prototype
│   ├── airflow/
│   │   ├── dags/zomato_batch.py       # End-to-end batch DAG
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── seeds/                         # Static reference data
│   ├── snapshots/                     # SCD tracking
│   ├── macros/                        # Reusable Jinja/SQL macros
│   ├── analyses/                      # Ad-hoc queries
│   └── tests/                         # Custom data tests
├── generate_rsa_key.py                # Snowflake key-pair generator utility
├── .gitignore
└── README.md
```

---

## Data Model

### Sources (`ZOMATO.RAW`)
`restaurant`, `orders`, `order_items`, `users`, `reviews`, `menu`, `food`

### Staging Layer — views in `staging` schema
Renames, casts, and lightly cleans source columns. One staging model per source table (1-to-1).

### Marts Layer — tables in `mart` schema

**Dimensions**
| Model              | Grain             | Purpose                            |
| ------------------ | ----------------- | ---------------------------------- |
| `dim_customer`     | one row / user    | Customer attributes                |
| `dim_restaurants`  | one row / restaurant | Restaurant metadata             |
| `dim_food`         | one row / food item | Food catalog                     |
| `dim_date`         | one row / calendar day | Time-intelligence dimension  |

**Facts**
| Model              | Grain                    | Purpose                       |
| ------------------ | ------------------------ | ----------------------------- |
| `fct_orders`       | one row / order          | Header-level order fact       |
| `fact_order_items` | one row / order-item     | Line-item revenue fact        |

**Business Marts**
| Model                          | Business Question                                 |
| ------------------------------ | ------------------------------------------------- |
| `mart_daily_city_revenue`      | Revenue trend by city and date                    |
| `mart_delivery_sla`            | SLA breach rate & avg delivery time by restaurant |
| `mart_restaurant_performance`  | Restaurant scorecards (orders, revenue, ratings)  |

---

## Data Quality

Tests are declared alongside models and executed via `dbt test`:
- **Uniqueness** on all primary keys
- **Not-null** constraints on business-critical columns
- **Referential integrity** between facts and dimensions (`relationships` tests)
- **Accepted values** for enum-style columns (e.g., order status, sentiment label)

---

## AI-Powered Review Enrichment

The `zomato/ai/enrich_reviews.py` pipeline:

1. Reads new reviews from `ZOMATO.RAW.REVIEWS` (that aren't already enriched).
2. Sends each review to OpenAI `gpt-4o-mini` with a strict JSON-schema system prompt.
3. Extracts four structured signals:
   - `sentiment_label` (positive / negative / neutral)
   - `sentiment_score` (float, -1.0 → 1.0)
   - `topic` (delivery, food, service, pricing, etc.)
   - `key_issue` (≤ 6-word summary of the customer pain point)
4. Persists results to `ZOMATO.AI.REVIEW_ENRICHED`, feeding downstream marts and BI.

These enriched fields power qualitative KPIs — e.g., "top 5 customer complaints by city last week."

---

## Getting Started

### Prerequisites

- Python 3.10+
- Snowflake account (with a database named `ZOMATO`)
- Docker & Docker Compose (for the Airflow stack)
- OpenAI API key (for the enrichment pipeline)

### 1. Clone & install

```bash
git clone https://github.com/Mohamed-Abuali/Zomato-AI-Data-Analytics.git
cd Zomato-AI-Data-Analytics

python -m venv venv
.\venv\Scripts\activate           # Windows
# source venv/bin/activate        # macOS / Linux

pip install dbt-snowflake snowflake-connector-python openai python-dotenv cryptography
```

### 2. Configure Snowflake key-pair authentication (MFA-safe)

```bash
python generate_rsa_key.py
```

Then in Snowflake, register the printed public key:
```sql
ALTER USER <YOUR_USER> SET RSA_PUBLIC_KEY='<paste_key_here>';
```

### 3. Create your `.env` file

```env
SNOWFLAKE_ACCOUNT=<account_locator>
SNOWFLAKE_USER=<user>
SNOWFLAKE_PRIVATE_KEY_PATH=./rsa_key.p8
SNOWFLAKE_WAREHOUSE=<warehouse>
SNOWFLAKE_DATABASE=ZOMATO
SNOWFLAKE_SCHEMA=RAW

OPENAI_API_KEY=sk-...
```

### 4. Configure your dbt profile (`~/.dbt/profiles.yml`)

```yaml
zomato:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <account_locator>
      user: <user>
      private_key_path: <absolute_path_to_rsa_key.p8>
      role: <role>
      database: ZOMATO
      warehouse: <warehouse>
      schema: dev
      threads: 4
```

### 5. Run the dbt pipeline

```bash
cd zomato
dbt debug             # verify connectivity
dbt run               # build all staging + marts
dbt test              # execute data quality tests
dbt docs generate && dbt docs serve
```

### 6. Run the AI enrichment

```bash
cd zomato/ai
python enrich_reviews.py
```

### 7. (Optional) Launch Airflow

```bash
cd zomato/airflow
docker compose up -d
```
Airflow UI → [http://localhost:8080](http://localhost:8080)

---

## Skills Demonstrated

- **Analytics Engineering** — Kimball-style dimensional modeling, layered ELT design, dbt best practices
- **Data Engineering** — Snowflake performance & security, key-pair auth, batch orchestration
- **Software Engineering** — clean Python, environment isolation, secrets handling, IaC via Docker Compose
- **AI / GenAI Integration** — production-shaped LLM calls with structured JSON outputs and idempotent writes
- **Communication** — self-documenting dbt project, tested data contracts, clear README

---

## Roadmap

- [ ] Add **Great Expectations** integration for external DQ checks
- [ ] Replace CSV ingestion with **Snowpipe** / **Fivetran**
- [ ] Add **exposures** for downstream BI dashboards
- [ ] Deploy Airflow to **AWS MWAA** or **Astronomer**
- [ ] Swap OpenAI for a **local Ollama** LLM for cost-free enrichment
- [ ] Build a **Streamlit** dashboard on top of the marts

---

## Author

**Mohamed Abuali** — Analytics / Data Engineer

- GitHub: [@Mohamed-Abuali](https://github.com/Mohamed-Abuali)
- Project: [Zomato-AI-Data-Analytics](https://github.com/Mohamed-Abuali/Zomato-AI-Data-Analytics)

Open to opportunities in **Data Engineering**, **Analytics Engineering**, and **AI/Data Platform** roles.

---

## License

Released under the MIT License for educational and portfolio purposes.
