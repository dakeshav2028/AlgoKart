# Deploying AlgoKart to Render

This guide will walk you through deploying your AlgoKart chatbot to the cloud using [Render](https://render.com/).

## Prerequisites
1.  **GitHub Account**: Your project must be pushed to a GitHub repository.
2.  **Render Account**: Sign up for a free account at Render.com.

## Step 1: Connect your Repository
1.  Log in to the **Render Dashboard**.
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub account and select your `AlgoKart` repository.

## Step 2: Configure Web Service
Fill in the following details:
- **Name**: `algokart-chatbot` (or your preferred name)
- **Region**: Select the one closest to you (e.g., Singapore or US East).
- **Branch**: `main` (or yours)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Step 3: Set Environment Variables
This is the **most important step**. Click on the **Advanced** button or the **Environment** tab and add the following keys from your `.env` file:

| Key | Description |
| :--- | :--- |
| `GROQ_API_KEY` | Your Groq API key |
| `HF_TOKEN` | Your Hugging Face token |
| `ASTRA_DB_API_ENDPOINT` | From your Datastax Astra dashboard |
| `ASTRA_DB_APPLICATION_TOKEN` | From your Datastax Astra dashboard |
| `ASTRA_DB_KEYSPACE` | Usually `default_keyspace` |
| `PYTHON_VERSION` | `3.11.9` (Crucial for LangChain stability) |

## Step 4: Deploy
Click **Create Web Service**. Render will now:
1.  Download your code.
2.  Install all dependencies from `requirements.txt`.
3.  Start the app using Streamlit.

## Troubleshooting
- **Build Fails**: Check the logs for missing dependencies.
- **Port Error**: Don't worry about the port; Render sets the `$PORT` automatically, and we've updated `app.py` to handle it!
- **Model Errors**: Ensure your `GROQ_API_KEY` is correct and has access to the model defined in `retrieval_generation.py`.

---
*Happy Deploying!* 🚀
