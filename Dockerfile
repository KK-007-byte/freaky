FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE <port-we-find>
CMD ["python", "ML project/Stocks_upgrade.py"]
