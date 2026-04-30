from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_groq import ChatGroq
from AlgoKart.data_ingestion import data_ingestion
from AlgoKart.data_converter import get_top_products

from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)  # Ensure this model is available in your Groq account

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def generation(vstore, category=None):
    search_kwargs = {"k": 5}
    if category:
        search_kwargs["filter"] = {"category": category}
    retriever = vstore.as_retriever(search_kwargs=search_kwargs)

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Given a chat history and the latest user question which might reference "
         "context in the chat history, formulate a standalone question which can be "
         "understood without the chat history. Do NOT answer the question, just "
         "reformulate it if needed and otherwise return it as is."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt
    )

    PRODUCT_BOT_TEMPLATE = """
You are Algokart, a friendly and knowledgeable ecommerce assistant.
You recommend products based on three signals:
  1. Customer reviews — what real buyers say (quality, pros, cons)
  2. Top-selling products — highly rated with many positive reviews
  3. User purchase history — products the user previously bought or viewed

INSTRUCTIONS:
- Greetings (hi/hello/hey): respond warmly, introduce yourself, skip product context.
- Product questions: use all three signals above.
- Mention avg rating when available. Be honest about low-rated products.
- Personalize using purchase history if provided.
- Keep answers concise and friendly.
- IMPORTANT: Always provide a clickable markdown link to the product using the provided Amazon Link (e.g. [Product Name](https://www.amazon.com/dp/ASIN)) whenever you mention or recommend a product.

TOP SELLING PRODUCTS:
{top_products}

USER PURCHASE HISTORY:
{purchase_history}

RETRIEVED CONTEXT:
{context}

QUESTION: {input}

YOUR ANSWER:
"""

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", PRODUCT_BOT_TEMPLATE),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    document_prompt = PromptTemplate(
        input_variables=["page_content", "asin"],
        template="{page_content}\nASIN: {asin}\nLink: https://www.amazon.com/dp/{asin}"
    )
    question_answer_chain = create_stuff_documents_chain(
        model, qa_prompt, document_prompt=document_prompt
    )
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
