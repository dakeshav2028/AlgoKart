import pandas as pd
from langchain_core.documents import Document

def data_converter():

    product_data = pd.read_csv(r"C:\notes of course\Flipkart\data\flipkart_product_review.csv")

    data = product_data[["product_name", "Review"]]

    product_list = []

    ## Itrate over the rows of the DataFrame

    for index, row in data.iterrows():
        object = {
            "product_name": row["product_name"],
            "review": row["Review"]
        }

    ## Append the object to the product list
    product_list.append(object)
    docs = []
    for entry in product_list:
        metadata = {"product_name": entry['product_name']}
        doc = Document(page_content= entry['review'], metadata= metadata)
        docs.append(doc)    
    return docs



