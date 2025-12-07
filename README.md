# 🏙️ Multi-Agent AI Compliance System

An advanced AI-powered system for automated zoning code analysis and building compliance checking (DCPR 2034, UDCPR), featuring Multi-Agent Orchestration, RAG (Retrieval Augmented Generation), and Reinforcement Learning (RL) for ongoing optimization.

## 🚀 Key Features

*   **Multi-Agent Architecture**:
    *   **Orchestrator**: Manages the workflow.
    *   **RAG Agent**: Retrieves specific regulations from PDFs (`chroma_client.py`).
    *   **Rule Engine**: Deterministic calculation of FSI, open spaces, and envelopes.
    *   **RL Agent**: Learns optimal policy decisions based on user feedback (`stable-baselines3`).
*   **Advanced OCR & Ingestion**: Uses **Tesseract OCR** to handle scanned regulatory PDFs and vectorizes them into ChromaDB.
*   **Detailed Feasibility Analysis**:
    *   **Inputs**: Plot Size, Road Width, Zoning (Residential/Commercial/etc.), Proposed Use, Height.
    *   **Advanced Constraints**: ASR Rates (Premium Calculation), Plot Deductions (Road Widening), and more.
*   **Interactive Feedback Loop**: Users can upvote/downvote reports. Data is logged in full detail (`inputs` + `outputs`) to retrain the RL agent.
*   **3D Visualization**: Generates a simple `.stl` geometry file of the allowable building envelope.

## 🛠️ Installation

### Prerequisites
*   **Python 3.10+**
*   **Tesseract OCR**: Must be installed on your system.
    *   *Windows*: [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Add to PATH or `C:\Program Files\Tesseract-OCR`)
*   **Google Gemini API Key**: Required for the LLM analysis.

### Setup Steps
1.  **Clone the Repository**:
    ```bash
    git clone <repo-url>
    cd multi-agent-compliance-system
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    *   Open `.env` and paste your API Key:
        ```ini
        GEMINI_API_KEY=your_actual_key_here
        ```

4.  **Ingest Regulations (First Run Only)**:
    *   Place your regulatory PDF (e.g., `DCPR_2034.pdf`) in the `io/` folder.
    *   Run the ingestion script:
        ```bash
        py ingest_pdf.py
        ```
    *   *Note: This processes the PDF, extracts text via OCR, and saves embeddings to `rules_chroma_db`.*

## 🏃‍♂️ Usage

**One-Click Start (Windows):**
Double-click **`start_system.bat`**
*   This script automatically starts the FastAPI Backend (`main.py`) and the Streamlit Frontend (`app.py`).

**Manual Start:**
1.  **Backend**: `uvicorn main:app --reload`
2.  **Frontend**: `streamlit run app.py`

### using the Dashboard
1.  **Select a Case Study**: Choose a pre-defined case (e.g., `case_study_mumbai_detailed.json`) or create a new one in `inputs/case_studies/`.
2.  **Adjust Parameters**: Use the sidebar to tweak Plot Size, Road Width, Zoning, ASR Rate, etc.
3.  **Run Analysis**: Click "Run Full Pipeline".
4.  **View Report**: Read the detailed AI analysis, citations, and calculations.
5.  **Give Feedback**: Click Thumbs Up/Down. This data is saved to `io/feedback.jsonl` to make the AI smarter.

## 📂 Project Structure

*   `main.py`: FastAPI Backend (API Endpoints).
*   `main_pipeline.py`: Core logic (Orchestrator, LLM calls, Context assembly).
*   `app.py`: Streamlit Frontend (UI).
*   `mcp_client.py` & `chroma_client.py`: Data handling, RAG retrieval, and logging.
*   `ingest_pdf.py`: OCR and Vector ingestion engine.
*   `extract_rules_ai.py`: Logic for parsing specific rules from text.
*   `inputs/`: Case study JSON files.
*   `io/`: Storage for PDFs, feedback logs, and generated reports.
*   `outputs/`: Generated 3D models (`.stl`) and JSON reports.

## 🧠 Reinforcement Learning (RL)
The system uses PPO (Proximal Policy Optimization) to learn from user feedback.
*   **State**: `[Plot Size, Location, Road Width]`
*   **Action**: Policy decisions (Strict vs Liberal interpretation).
*   **Reward**: Derived from User Feedback (Upvote = +1, Downvote = -1).
*   *Training script located in `rl_env/`.*

## 📄 License
MIT License