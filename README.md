# ⚡ FlowForge — Operations Automation Command Center

FlowForge is a portfolio-grade Python application that turns messy inbound business requests into structured, prioritized, and routed work. It combines an interactive dashboard, a REST API, persistent SQLite storage, deterministic classification, entity extraction, priority scoring, routing recommendations, export tools, automated tests, Docker support, and CI.

> **Portfolio project:** This is a self-directed software project using fictional data. It is designed to demonstrate backend development, workflow automation, API design, data processing, and practical product engineering.

## Why this project exists

Operations teams often receive work through email, forms, chat, and APIs. The raw requests are inconsistent and hard to triage. FlowForge standardizes each request into a structured record, scores urgency, recommends an owner and next action, and stores an auditable history.

## Features

- **Interactive command-center dashboard** built with Streamlit
- **REST API** built with FastAPI
- **Request classification** across billing, sales, support, operations, account, and general queues
- **Priority scoring** from 0–100 with P0/P1/P2/P3 labels
- **Entity extraction** for emails, phone numbers, monetary values, and reference IDs
- **Sentiment signal** for positive / neutral / negative requests
- **Suggested owner and next action** for every request
- **SQLite persistence and audit trail**
- **CSV export** of the active work queue
- **Dockerfile** for portable deployment
- **Automated unit tests**
- **GitHub Actions CI**
- **Fictional demo data** for immediate testing

## Architecture

```text
Inbound request
   ↓
Normalization + field extraction
   ↓
Category classification
   ↓
Priority scoring
   ↓
Routing recommendation
   ↓
SQLite audit trail
   ↙             ↘
Streamlit UI    FastAPI REST API
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed_demo.py
streamlit run streamlit_app.py
```

Open the local Streamlit URL shown in your terminal.

## Run the API

```bash
uvicorn api:app --reload
```

Then visit `/docs` on the local server for interactive API documentation.

### Example API payload

```json
{
  "source": "email",
  "subject": "Checkout outage",
  "text": "URGENT: checkout is down and all orders are blocked."
}
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Docker

```bash
docker build -t flowforge .
docker run -p 8501:8501 flowforge
```

## What this demonstrates

This project demonstrates practical Python engineering across backend APIs, workflow automation, business rules, data extraction, persistent storage, dashboard development, testing, CI, containerization, and product-oriented software design.
