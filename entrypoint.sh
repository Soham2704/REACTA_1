#!/bin/bash
set -e

echo "--- Starting Entrypoint Script ---"

# Cloud Run filesystem is read-only except for /tmp (which is a RAM disk).
# We need to copy our embedded database and set cache paths to /tmp.

# 1. Setup ChromaDB in /tmp
echo "Setting up ChromaDB in /tmp..."
export CHROMADB_PERSIST_DIRECTORY="/tmp/rules_chroma_db"
if [ -d "rules_chroma_db" ]; then
    echo "Copying existing rules_chroma_db to /tmp..."
    cp -R rules_chroma_db /tmp/
else
    echo "No existing rules_chroma_db found. Creating empty /tmp directory."
    mkdir -p /tmp/rules_chroma_db
fi

# 2. Setup Cache Re-direction (HuggingFace, Torch, etc.)
echo "Configuring cache paths to /tmp..."
export TRANSFORMERS_CACHE="/tmp/transformers"
export SENTENCE_TRANSFORMERS_HOME="/tmp/sentence_transformers"
export TORCH_HOME="/tmp/torch"
export HF_HOME="/tmp/huggingface"
export MPLCONFIGDIR="/tmp/matplotlib"

# Create these directories just in case
mkdir -p $TRANSFORMERS_CACHE
mkdir -p $SENTENCE_TRANSFORMERS_HOME
mkdir -p $TORCH_HOME
mkdir -p $HF_HOME

# 3. Start the Application
echo "Starting Uvicorn..."
# Execute the passed command (CMD) or default
# We use exec so uvicorn receives signals
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
