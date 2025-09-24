FROM python:3.11-slim

WORKDIR /app

# Install dependencies (service + shared)
COPY api-gateway/requirements.txt ./requirements.txt
COPY shared/requirements.txt ./shared-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r shared-requirements.txt

# Copy shared modules (available within parent build context)
COPY shared /app/shared

# Copy service code
COPY api-gateway/. .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]