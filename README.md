# Layer10 · Organizational Knowledge Graph

A modern, full-stack system designed to capture, deduplicate, and visualize organizational memory (entities, decisions, and relationships) from GitHub project history.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+** (for backend & pipeline)
- **Node.js 18+ & npm** (for frontend)
- **Gemini API Key** (for running the extraction pipeline)

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
GITHUB_TOKEN=your_github_token
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run the Backend (FastAPI)
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
API available at: `http://localhost:8000`

### 4. Run the Frontend (React)
```powershell
cd frontend
npm install
npm start
```
UI available at: `http://localhost:3000`

---

## 🏗️ Architecture Overview

The system is split into four distinct phases, migrating from raw GitHub data to an interactive knowledge graph.

### 1. Ingestion (`pipeline/ingest.py`)
Fetches closed GitHub issues and comments into a unified `data/corpus.json`.

### 2. Extraction (`pipeline/extract.py` + `pipeline/ontology.py`)
Uses structured semantic analysis to extract entities (`Person`, `Decision`, `Topic`, `Artifact`) and relationships with verbatim textual evidence.

### 3. Graph Construction (`pipeline/build_graph.py`)
Builds a directed **NetworkX** graph. Implements **ID Normalization** to deduplicate entities across batches (e.g., merging "@john_doe" and "John Doe").

### 4. Visualization (FastAPI + React)
- **Backend API**: A FastAPI server that performs graph filtering, metrics calculation, and serves PyVis HTML.
- **Frontend UI**: A professional React dashboard (dark theme) featuring a live Knowledge Graph, interactive Analytics charts, and a Node Explorer for evidence traversal.

---

## 📄 Ontology & Relationship Contract

| Entity Type | Description |
|---|---|
| `Person` | Team members or contributors mentioned in discussions. |
| `Topic` | Abstract concepts, requirements, or design patterns. |
| `Artifact` | Code artifacts, URLs, documentation, or specific versions. |
| `Decision` | Resolved choices, rejections, or terminal states of a discussion. |

Every relationship in the graph is **grounded**. In the Node Explorer, you can view the exact **quote** and **source URL** that justifies every edge, ensuring verifiable data lineage.

---

## 🛠️ Project Structure

```
Layer10/
├── 📂 backend/           # FastAPI server & graph service logic
├── 📂 frontend/          # React UI (CRA) & API integration layer
├── 📂 pipeline/          # Data generation & extraction scripts
├── 📂 data/              # Persistent stores (corpus, extractions, final graph)
└── README.md             # This document
```

---
