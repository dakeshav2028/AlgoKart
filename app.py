from flask import Flask, render_template, request, session
from AlgoKart.retrieval_generation import generation
from AlgoKart.data_ingestion import data_ingestion
from AlgoKart.data_converter import get_top_products
import os

print("[app.py] Initializing vstore and RAG chain...")
vstore = data_ingestion("done")
chain = generation(vstore)

print("[app.py] Fetching top products...")
TOP_PRODUCTS = get_top_products(n=5)
print(f"[app.py] Ready. Top products loaded:\n{TOP_PRODUCTS}")

app = Flask(__name__, template_folder='frontend', static_folder='frontend', static_url_path='')
app.secret_key = os.urandom(24)   # needed for Flask session


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/get", methods=["POST", "GET"])
def chat():
    if request.method == "POST":
        user_input = request.form["msg"].strip()

        # Handle greetings before invoking the RAG chain
        greetings = {
            "hi", "hello", "hey", "hii", "helo",
            "good morning", "good evening", "good afternoon",
            "sup", "yo", "howdy",
        }
        if user_input.lower() in greetings:
            return (
                "Hello! 👋 I'm Algokart, your smart shopping assistant. "
                "I can help you with product recommendations based on customer reviews, "
                "top-rated products, and your purchase history. What are you looking for today?"
            )

        # Build purchase history string from session
        purchase_history = session.get("purchase_history", [])
        if purchase_history:
            history_str = "Previously purchased or viewed by this user:\n" + "\n".join(
                f"- {item}" for item in purchase_history
            )
        else:
            history_str = "No previous purchase history available for this user."

        result = chain.invoke(
            {
                "input": user_input,
                "top_products": TOP_PRODUCTS,
                "purchase_history": history_str,
            },
            config={"configurable": {"session_id": session.get("session_id", "default")}},
        )["answer"]

        return str(result)


@app.route("/set_history", methods=["POST"])
def set_history():
    """
    Endpoint to set a user's purchase history for the session.
    POST JSON: { "session_id": "user123", "purchases": ["Product A", "Product B"] }
    Call this when the user logs in or from your user DB.
    """
    data = request.get_json()
    session["session_id"] = data.get("session_id", "default")
    session["purchase_history"] = data.get("purchases", [])
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
