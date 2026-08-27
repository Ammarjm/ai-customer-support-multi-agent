import re
import pandas as pd

from langchain.tools import tool


PRODUCTS_PATH = "data/products.csv"


def load_products():
    return pd.read_csv(PRODUCTS_PATH)


def format_product(product):
    return (
        f"Product ID: {product['product_id']}\n"
        f"Name: {product['product_name']}\n"
        f"Category: {product['category']}\n"
        f"Price: ${product['price']}\n"
        f"Stock: {product['stock']}\n"
        f"Rating: {product['rating']}\n"
        f"Description: {product['description']}"
    )


@tool
def search_product(query: str) -> str:
    """
    Search for a product using product ID, name,
    category, or description.
    """

    products = load_products()

    query = query.strip().lower()

    searchable_text = (
        products["product_id"].astype(str)
        + " "
        + products["product_name"].astype(str)
        + " "
        + products["category"].astype(str)
        + " "
        + products["description"].astype(str)
    ).str.lower()

    matches = products[
        searchable_text.str.contains(
            re.escape(query),
            regex=True,
            na=False
        )
    ]

    if matches.empty:
        return f"No product was found matching '{query}'."

    matches = matches.sort_values(
        by=["rating", "price"],
        ascending=[False, True]
    )

    results = []

    for _, product in matches.head(5).iterrows():
        results.append(
            format_product(product)
        )

    return "\n\n---\n\n".join(results)


@tool
def recommend_products(
    category: str = "",
    max_price: float | None = None,
    min_rating: float | None = None,
    specifications: str = "",
    limit: int = 3
) -> str:
    """
    Recommend products based on category,
    maximum price, minimum rating and specifications.
    """

    products = load_products()

    results = products.copy()

    # Only products available in stock
    results = results[
        results["stock"] > 0
    ]

    # Filter category
    if category:
        results = results[
            results["category"]
            .str.lower()
            .eq(category.lower())
        ]

    # Filter maximum price
    if max_price is not None:
        results = results[
            results["price"] <= max_price
        ]

    # Filter minimum rating
    if min_rating is not None:
        results = results[
            results["rating"] >= min_rating
        ]

    # Filter specifications
    if specifications:

        specs = [
            spec.strip().lower()
            for spec in specifications.split(",")
            if spec.strip()
        ]

        for spec in specs:

            searchable_text = (
                results["product_name"].astype(str)
                + " "
                + results["description"].astype(str)
            ).str.lower()

            results = results[
                searchable_text.str.contains(
                    re.escape(spec),
                    regex=True,
                    na=False
                )
            ]

    if results.empty:
        return "No products match the requested requirements."

    # Best rating first
    # If rating is equal, cheaper product first
    results = results.sort_values(
        by=["rating", "price"],
        ascending=[False, True]
    )

    limit = max(
        1,
        min(int(limit), 5)
    )

    results = results.head(limit)

    output = []

    for _, product in results.iterrows():
        output.append(
            format_product(product)
        )

    return "\n\n---\n\n".join(output)