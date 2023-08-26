FROM python:3.11

WORKDIR /crypto-ohlc-charts

COPY requirements.txt .
COPY ./src .

RUN pip install -r requirements.txt

CMD ["python", "./crypto_ohlc_charts.py"]










