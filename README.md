# Resume Judge AI Agent

An automated resume evaluation system using AI Agents to analyze and score candidates against a Job Description.

## Key Features

1. **Hybrid OCR:** Direct text extraction from PDFs or OCR (EasyOCR) for scanned images.
2. **AI Agent Workflow:** Uses a Reviewer and Auditor (QC) node-based graph for high-accuracy evaluations.
3. **Thai Language Support:** Analysis and summaries are provided in Thai.

## Prerequisites

1. **Python 3.10+**
2. **OpenAI API Key:** Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```
3. **Project Prep:**
   - Place your resume PDF files in the `resumes/` folder.
   - Edit `job_description.txt` with your desired job requirements.

## How to Use

### Option 1: Using `uv` (Recommended)

1. **Create & Sync Environment:**
   ```powershell
   uv sync
   ```
2. **Run the Evaluation:**
   ```powershell
   uv run main.py
   ```

### Option 2: Using standard Python & pip

1. **Create Virtual Environment:**
   ```powershell
   python -m venv .venv
   ```
2. **Activate Environment:**
   - Windows: `.\.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
3. **Install Dependencies:**
   ```powershell
   pip install -e .
   ```
4. **Run the Evaluation:**
   ```powershell
   python main.py
   ```

## Key File Structure

- `main.py`: Orchestrator script (OCR -> Judge).
- `OCR.py`: Text extraction and OCR logic.
- `judge.py`: The AI Agent logic (Reviewer & Auditor).
- `ocr_results.csv`: Raw extracted text from resumes.
- `judge_results.csv`: **Final evaluation results (Score + Analysis)**.
- `job_description.txt`: Input file for job requirements.

## Viewing Results

Open **`judge_results.csv`** in Excel:

- **Score:** 0-10 rating.
- **Evaluation:** Detailed strengths and weaknesses in Thai.

## Privacy & Configuration

The default model is `gpt-4o-mini`. While this requires an internet connection to OpenAI, your resume data is only processed for the evaluation.

### 100% Offline Usage (Ollama)

If you require maximum data privacy and want to run the system **100% offline**, you can switch to **Ollama**:

1. Install [Ollama](https://ollama.com/).
2. Pull a local model: `ollama pull llama3.2`.
3. In `judge.py`, switch `ChatOpenAI` to `ChatOllama`.
4. Run using: `uv run main.py`.

_Note: For complete offline OCR, ensure you have run the program at least once with an internet connection to download the initial EasyOCR model files._
