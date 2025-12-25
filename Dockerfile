# ==========================================
# Phase 1: Build the Frontend (React/Vite)
# ==========================================
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend dependency files first (better caching)
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the production assets (Vite defaults to 'dist' folder)
RUN npm run build


# ==========================================
# Phase 2: Setup the Backend (Python/FastAPI)
# ==========================================
FROM python:3.11-slim AS backend-runner

WORKDIR /app

# Install system dependencies if needed (e.g., for some python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install system dependencies
# - tesseract-ocr: for pytesseract
# - libgl1-mesa-glx: for opencv (if used by dependencies)
# - libgomp1: for some torch/numpy optimizations
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend codebase
COPY . .

# Copy the BUILT frontend assets from Phase 1 into a 'static' directory
COPY --from=frontend-builder /app/frontend/dist ./static

# Copy entrypoint script
COPY entrypoint.sh .
# Install dos2unix to fix Windows line endings (CRLF) -> Linux (LF)
RUN apt-get update && apt-get install -y dos2unix && dos2unix entrypoint.sh && chmod +x entrypoint.sh && rm -rf /var/lib/apt/lists/*

# Expose port (Cloud Run sets $PORT environment variable, default is 8080)
ENV PORT=8080
EXPOSE 8080

# Command to run the application using entrypoint script
CMD ["./entrypoint.sh"]
