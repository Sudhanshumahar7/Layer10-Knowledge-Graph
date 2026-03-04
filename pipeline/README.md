# Data Pipeline Scripts

These scripts handle the transformation of raw GitHub data into a structured Knowledge Graph.

## 🚀 Order of Execution

Run these from the project root:

1. **Ingest Phase**: 
   ```bash
   python pipeline/ingest.py
   ```
   *Fetches issues from GitHub API into `data/corpus.json`.*

2. **Extraction Phase**:
   ```bash
   python pipeline/extract.py
   ```
   *Uses semantic processing to identify entities and claims. Outputs to `data/graph_extractions.json`.*

3. **Graph Build Phase**:
   ```bash
   python pipeline/build_graph.py
   ```
   *Deduplicates entities and constructs the final NetworkX graph in `data/knowledge_graph.json`.*

## 📂 File Summary

- **`ingest.py`**: Connector for GitHub REST API.
- **`extract.py`**: Extraction engine for semantic analysis.
- **`ontology.py`**: Pydantic models for structured data extraction.
- **`build_graph.py`**: Logic for entity resolution and graph serialization.

## 🔑 Requirements
Requires `GITHUB_TOKEN` and `GEMINI_API_KEY` in the root `.env` file.
