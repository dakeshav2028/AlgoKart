# Algokart Setup Guide

## 1. Python version
Use Python 3.11 or 3.12. Do NOT use 3.13 (langchain incompatibility).

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2. Fresh install (important — wipe old env first if upgrading)

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

If you previously had langchain 1.x installed, wipe the venv and reinstall:
```powershell
deactivate
Remove-Item -Recurse -Force venv
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. .env file

```
GROQ_API_KEY=...
ASTRA_DB_API_ENDPOINT=...
ASTRA_DB_APPLICATION_TOKEN=...
ASTRA_DB_KEYSPACE=default_keyspace
HUGGINGFACE_TOKEN=...
```

## 4. First-time ingestion (run ONCE to load Amazon data into AstraDB)

```powershell
python -m flipkart.data_ingestion
```

## 5. Run the app

```powershell
python app.py
```
