FROM python:3.11-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone https://github.com/sebszczec/gpw-stock-monitor.git .

RUN pip install --no-cache-dir yfinance rich

ENTRYPOINT ["python", "run.py"]
