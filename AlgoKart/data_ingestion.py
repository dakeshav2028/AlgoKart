from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from AlgoKart.data_converter import data_converter
from dotenv import load_dotenv
import os

load_dotenv()

ASTRA_DB_API_ENDPOINT      = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_KEYSPACE          = os.getenv("ASTRA_DB_KEYSPACE")

embeddings = HuggingFaceEndpointEmbeddings(
    huggingfacehub_api_token=os.getenv("HF_TOKEN"),
    repo_id="BAAI/bge-base-en-v1.5",
)


def data_ingestion(status=None, category="Electronics", max_reviews=5000):
    """
    status=None  → ingest fresh documents into AstraDB (run once)
    status="done" → connect to existing collection (normal app startup)
    """
    # autodetect_collection=True skips the create_collection call on startup
    # which was causing the timeout when the collection already exists
    vstore = AstraDBVectorStore(
        embedding=embeddings,
        collection_name="flipkart",
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_APPLICATION_TOKEN,
        namespace=ASTRA_DB_KEYSPACE,
        autodetect_collection=True,     # ← fixes the timeout on startup
    )

    if status is None:
        print(f"[data_ingestion] Ingesting {category} reviews ...")
        docs = data_converter(category=category, max_reviews=max_reviews)
        insert_ids = vstore.add_documents(docs)
        print(f"[data_ingestion] Inserted {len(insert_ids)} documents.")
        return vstore, insert_ids

    return vstore


if __name__ == "__main__":
    vstore, ids = data_ingestion(status=None)
    print(f"Inserted {len(ids)} documents.")
