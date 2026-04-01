from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os
from flipkart.data_converter import data_converter
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
ASTRA_DB_API_ENDPOINT=os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN=os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_KEYSPACE=os.getenv("ASTRA_DB_KEYSPACE")
HF_TOKEN = os.getenv("HF_TOKEN")


GROQ_API_KEY=os.getenv("GROQ_API_KEY")
ASTRA_DB_API_ENDPOINT=os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN=os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_KEYSPACE=os.getenv("ASTRA_DB_KEYSPACE")
HF_TOKEN = os.getenv("HF_TOKEN")

embeddings = HuggingFaceEndpointEmbeddings(
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_TOKEN"),
    repo_id="BAAI/bge-base-en-v1.5"
)

def data_ingestion(status):

    vstore = AstraDBVectorStore(
        embedding=embeddings,
        collection_name = "flipkart",
        api_endpoint = ASTRA_DB_API_ENDPOINT,
        token = ASTRA_DB_APPLICATION_TOKEN,
        namespace = ASTRA_DB_KEYSPACE 
    )

    storage = status

    if storage == None:
        docs = data_converter()
        insert_ids = vstore.add_documents(docs)
    
    else:
        return vstore
    return vstore, insert_ids

if __name__ == "__main__":

    vstore, insert_ids = data_ingestion(None)
    print(f"\n Inserted {len(insert_ids)} documents.")
    results = vstore.similarity_search("Can you tell me the low budget sound basshead?")
    for res in results:
        print(f"\n {res.page_content} [{res.metadata}]")





