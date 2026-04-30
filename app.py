import streamlit as st
from AlgoKart.retrieval_generation import generation
from AlgoKart.data_ingestion import data_ingestion
from AlgoKart.data_converter import get_top_products

st.set_page_config(page_title="AlgoKart Assistant", page_icon="🛍️")

# Available categories from Amazon dataset
AVAILABLE_CATEGORIES = [
    "All_Beauty", "Amazon_Fashion", "Appliances", "Arts_Crafts_and_Sewing", "Automotive",
    "Books", "CDs_and_Vinyl", "Cell_Phones_and_Accessories", "Clothing_Shoes_and_Jewelry",
    "Collectibles_and_Fine_Art", "Computers", "Digital_Music", "Electronics", "Gift_Cards",
    "Grocery_and_Gourmet_Food", "Handmade_Products", "Health_and_Household",
    "Health_and_Personal_Care", "Home_and_Kitchen", "Industrial_and_Scientific",
    "Kindle_Store", "Magazine_Subscriptions", "Movies_and_TV", "Musical_Instruments",
    "Office_Products", "Patio_Lawn_and_Garden", "Pet_Supplies", "Software",
    "Sports_and_Outdoors", "Tools_and_Home_Improvement", "Toys_and_Games",
    "Video_Games", "Unknown"
]

# Initialize models and data
@st.cache_resource
def load_backend(category="Electronics"):
    print(f"[app.py] Initializing vstore and RAG chain for {category}...")
    vstore = data_ingestion("done", category=category)
    chain = generation(vstore, category=category)
    
    print(f"[app.py] Fetching top products for {category}...")
    top_products = get_top_products(category=category, n=5)
    return chain, top_products

# Add logo if it exists
import os
logo_path = os.path.join("frontend", "logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)

selected_category = st.sidebar.selectbox("Select Category", AVAILABLE_CATEGORIES, index=AVAILABLE_CATEGORIES.index("Electronics"))

chain, TOP_PRODUCTS = load_backend(selected_category)

st.title("🛍️ AlgoKart Shopping Assistant")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = "default"

if "purchase_history" not in st.session_state:
    st.session_state.purchase_history = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What are you looking for today?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    greetings = {
        "hi", "hello", "hey", "hii", "helo",
        "good morning", "good evening", "good afternoon",
        "sup", "yo", "howdy",
    }
    
    if prompt.lower() in greetings:
        response = (
            "Hello! 👋 I'm Algokart, your smart shopping assistant. "
            "I can help you with product recommendations based on customer reviews, "
            "top-rated products, and your purchase history. What are you looking for today?"
        )
    else:
        # Build purchase history string from session
        purchase_history = st.session_state.purchase_history
        if purchase_history:
            history_str = "Previously purchased or viewed by this user:\n" + "\n".join(
                f"- {item}" for item in purchase_history
            )
        else:
            history_str = "No previous purchase history available for this user."

        try:
            with st.spinner("Thinking..."):
                response = chain.invoke(
                    {
                        "input": prompt,
                        "top_products": TOP_PRODUCTS,
                        "purchase_history": history_str,
                    },
                    config={"configurable": {"session_id": st.session_state.session_id}},
                )["answer"]
        except Exception as e:
            response = f"An error occurred: {e}"
            
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar for additional settings
with st.sidebar:
    st.header("Settings")
    st.write("Session ID:", st.session_state.session_id)
    
    new_purchase = st.text_input("Add to Purchase History:")
    if st.button("Add"):
        if new_purchase:
            st.session_state.purchase_history.append(new_purchase)
            st.success(f"Added {new_purchase}")
            st.rerun()
    
    if st.session_state.purchase_history:
        st.write("Current Purchase History:")
        for item in st.session_state.purchase_history:
            st.write(f"- {item}")
        if st.button("Clear History"):
            st.session_state.purchase_history = []
            st.rerun()
