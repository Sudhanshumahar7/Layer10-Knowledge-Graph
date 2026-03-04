# --- Stage 1: Build Frontend ---
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# Set production URL to empty for relative calls
ENV REACT_APP_API_URL=""
RUN npm run build

# --- Stage 2: Final Image ---
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies if any (none needed for basic fastapi/networkx)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend and root requirements
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend code, data, and built frontend
COPY backend/ ./backend/
COPY data/ ./data/
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Expose port (Hugging Face uses 7860)
EXPOSE 7860

# Run with uvicorn on all interfaces
# Note: We run from root so BASE_DIR in main.py works correctly
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
