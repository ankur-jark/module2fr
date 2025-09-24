FROM python:3.11-slim

WORKDIR /app

# Install dependencies (service + shared)
COPY user-profile-service/requirements.txt ./requirements.txt
COPY shared/requirements.txt ./shared-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r shared-requirements.txt

# Copy shared modules from parent context
COPY shared /app/shared

# Copy service code
COPY user-profile-service/. .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]