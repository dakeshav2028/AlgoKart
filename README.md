## AlgoKart Chat Bot



## Create a virtual environment:
python -m venv venv


## Activate your virtual environment

```bash
venv\Scripts\activate
```

## Create a requirement.txt file and install it

```bash
pip install -r requirements.txt
```
## Create a .env file for keeping your environment variable.
GROQ_API_KEY=your_api_key_here
ASTRA_DB_TOKEN=your_token_here
HUGGINGFACE_TOKEN=your_token_here


## Use setup.py for installing your local package.

- <either mention -e . inside your requirements.txt Or run python setup.py install >

## Run the Streamlit App

```bash
streamlit run app.py
```
