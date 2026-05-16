"""
data_converter.py
-----------------
Loads Amazon Reviews 2023 data via direct Parquet files on Hugging Face
(avoids the deprecated loading script that newer `datasets` versions reject).

Parquet URLs follow this pattern:
  reviews : hf://datasets/McAuley-Lab/Amazon-Reviews-2023/raw/review_categories/<Cat>.jsonl
  metadata: hf://datasets/McAuley-Lab/Amazon-Reviews-2023/raw/meta_categories/<Cat>.jsonl

We use pd.read_parquet with the huggingface hub parquet API instead.
"""

import pandas as pd
from langchain_core.documents import Document

# ── configurable ──────────────────────────────────────────────────────────────
CATEGORY    = "Electronics"
MAX_REVIEWS = 5000
MIN_LEN     = 30
# ─────────────────────────────────────────────────────────────────────────────

# Direct parquet URLs — no loading script needed
REVIEW_URL = (
    "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023"
    "/resolve/main/raw/review_categories/{category}.jsonl"
)
META_URL = (
    "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023"
    "/resolve/main/raw/meta_categories/{category}.jsonl"
)

# Parquet API (converted files — fast, no script needed)
REVIEW_PARQUET = (
    "hf://datasets/McAuley-Lab/Amazon-Reviews-2023/"
    "raw/review_categories/{category}.jsonl"
)


def _load_reviews(category: str, max_rows: int) -> pd.DataFrame:
    """Load reviews using datasets library with parquet config (no script)."""
    print(f"[_load_reviews] Connecting to Hugging Face for {category} reviews...")
    from datasets import load_dataset
    # Use the parquet-converted split — avoids the loading script
    ds = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023",
        f"raw_review_{category}",
        split="full",
        streaming=True,
        trust_remote_code=False,
    )
    rows = []
    for item in ds:
        if len(rows) >= max_rows:
            break
        text = (item.get("text") or "").strip()
        if len(text) < MIN_LEN:
            continue
        rows.append({
            "asin":      item.get("parent_asin", ""),
            "user_id":   item.get("user_id", ""),
            "rating":    float(item.get("rating", 0)),
            "title":     item.get("title", ""),
            "text":      text,
            "timestamp": item.get("timestamp", 0),
        })
    return pd.DataFrame(rows)


def _load_meta(category: str) -> pd.DataFrame:
    """Load product metadata using datasets library with parquet config."""
    print(f"[_load_meta] Connecting to Hugging Face for {category} metadata...")
    from datasets import load_dataset
    ds = load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023",
        f"raw_meta_{category}",
        split="full",
        streaming=True,
        trust_remote_code=False,
    )
    rows = []
    for item in ds:
        features    = item.get("features") or []
        description = item.get("description") or []
        rows.append({
            "asin":          item.get("parent_asin", ""),
            "product_title": item.get("title", ""),
            "avg_rating":    float(item.get("average_rating") or 0),
            "rating_number": int(item.get("rating_number") or 0),
            "price":         item.get("price", ""),
            "description":   " ".join(description) if description else "",
            "features":      " | ".join(features)  if features    else "",
        })
    return pd.DataFrame(rows)


def data_converter(category: str = CATEGORY, max_reviews: int = MAX_REVIEWS):
    """Returns LangChain Documents for vector store ingestion."""
    print(f"[data_converter] Loading reviews ({category}) ...")
    reviews_df = _load_reviews(category, max_reviews)

    print(f"[data_converter] Loading metadata ({category}) ...")
    meta_df = _load_meta(category)

    meta_lookup = {row["asin"]: row for _, row in meta_df.iterrows()}

    docs = []
    for _, row in reviews_df.iterrows():
        asin  = row["asin"]
        meta  = meta_lookup.get(asin, {})

        product_title = meta.get("product_title") or asin
        features      = meta.get("features", "")
        description   = meta.get("description", "")
        avg_rating    = meta.get("avg_rating", row["rating"])
        rating_number = meta.get("rating_number", 1)
        price         = meta.get("price", "N/A")

        page_content = (
            f"Product: {product_title}\n"
            f"Features: {features}\n"
            f"Description: {description}\n"
            f"Review title: {row['title']}\n"
            f"Review: {row['text']}\n"
            f"Rating: {row['rating']}/5"
        )

        docs.append(Document(
            page_content=page_content,
            metadata={
                "asin":          asin,
                "product_name":  product_title,
                "rating":        row["rating"],
                "avg_rating":    avg_rating,
                "rating_number": rating_number,
                "price":         price,
                "user_id":       row["user_id"],
                "category":      category,
            }
        ))

    print(f"[data_converter] Created {len(docs)} documents.")
    return docs


def get_top_products(category: str = CATEGORY, n: int = 5) -> str:
    """Formatted top-N products by avg rating × review count."""
    try:
        meta_df = _load_meta(category)
        top = (
            meta_df[meta_df["rating_number"] > 0]
            .sort_values(["avg_rating", "rating_number"], ascending=False)
            .drop_duplicates("asin")
            .head(n)
        )
        lines = []
        for _, row in top.iterrows():
            price_str = f" | Price: {row['price']}" if row["price"] else ""
            asin = row['asin']
            lines.append(
                f"- {row['product_title']}"
                f" | Avg rating: {row['avg_rating']:.1f}/5"
                f" | Reviews: {int(row['rating_number'])}"
                f"{price_str}"
                f" | Link: https://www.amazon.in"
            )
        return "\n".join(lines) if lines else "No top products data available."
    except Exception as e:
        print(f"[get_top_products] Warning: {e}")
        return "Top products data temporarily unavailable."
