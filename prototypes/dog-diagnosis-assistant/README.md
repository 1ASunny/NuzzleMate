# Dog Diagnosis Assistant Prototype

This folder contains an early canine-focused prototype for **NuzzleMate**.

It includes:

- A Streamlit demo app for dog health Q&A.
- Optional RAGFlow integration.
- FastAPI inference server examples for Qwen2, GLM-4, and Yi LoRA models.
- Utility scripts for PDF splitting, RAGFlow upload, and SSH tunneling.

> This is a historical prototype and research demo. It is not a production-ready veterinary diagnosis system.

## Safety Boundary

The assistant is designed for educational and assisted-triage scenarios only. It should not replace professional veterinary diagnosis, treatment, or prescription decisions.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Environment Variables

Sensitive values such as API keys and SSH passwords should be stored in `.env` or GitHub Secrets, never hard-coded in source files.

See `.env.example` for required variables.

## Data

Original datasets are intentionally excluded from this clean package. See `data/README.md`.

## Suggested Location in NuzzleMate

```text
prototypes/dog-diagnosis-assistant/
```
