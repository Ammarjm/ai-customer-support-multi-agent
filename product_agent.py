import re
import pandas as pd

from llm.local_llm import generate_text
from tools.product_tool import (
    search_product,
    recommend_products
)


PRODUCTS_PATH = "data/products.csv"

products = pd.read_csv(PRODUCTS_PATH)


# Detect Specific Product

def detect_product(question):

    question_lower = question.lower()

    # Product ID such as P001
    product_id_match = re.search(
        r"\bP\d{3}\b",
        question,
        re.IGNORECASE
    )

    if product_id_match:
        return product_id_match.group().upper()

    # Product name
    product_names = sorted(
        products["product_name"].astype(str).tolist(),
        key=len,
        reverse=True
    )

    for product_name in product_names:

        if product_name.lower() in question_lower:
            return product_name

    return None


# Detect Product Category

def detect_category(question):

    question = question.lower()

    categories = {
        "Laptop": [
            "laptop",
            "notebook"
        ],

        "Smartphone": [
            "smartphone",
            "phone",
            "mobile"
        ],

        "Audio": [
            "audio",
            "headphone",
            "headphones",
            "earbuds",
            "earbud",
            "speaker",
            "headset"
        ],

        "Accessories": [
            "accessory",
            "accessories",
            "mouse",
            "keyboard",
            "charger",
            "power bank",
            "webcam",
            "stand",
            "hub",
            "ssd"
        ],

        "Monitor": [
            "monitor",
            "display",
            "screen"
        ]
    }

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in question:
                return category

    return None


# Extract Maximum Price

def extract_max_price(question):

    question = question.lower()

    patterns = [
        r"(?:under|below|less than|up to|max|maximum)\s*\$?\s*(\d+(?:\.\d+)?)",
        r"(?:budget(?:\s+of|\s+is)?\s*)\$?\s*(\d+(?:\.\d+)?)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            question
        )

        if match:
            return float(
                match.group(1)
            )

    return None


# Extract Minimum Rating

def extract_min_rating(question):

    question = question.lower()

    patterns = [
        r"(?:rating|rated)\s*(?:at least|above|over|minimum|min)?\s*([0-5](?:\.\d+)?)",

        r"(?:at least|above|over|minimum|min)\s*([0-5](?:\.\d+)?)\s*(?:rating|stars?)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            question
        )

        if match:

            rating = float(
                match.group(1)
            )

            if 0 <= rating <= 5:
                return rating

    return None


# Extract Specifications

def extract_specifications(question):

    question = question.lower()

    possible_specs = {
        "8gb ram": [
            "8gb ram",
            "8 gb ram"
        ],

        "16gb ram": [
            "16gb ram",
            "16 gb ram"
        ],

        "32gb ram": [
            "32gb ram",
            "32 gb ram"
        ],

        "256gb ssd": [
            "256gb ssd",
            "256 gb ssd"
        ],

        "512gb ssd": [
            "512gb ssd",
            "512 gb ssd"
        ],

        "1tb ssd": [
            "1tb ssd",
            "1 tb ssd"
        ],

        "lightweight": [
            "lightweight",
            "light weight"
        ],

        "gaming": [
            "gaming"
        ],

        "4k": [
            "4k"
        ],

        "qhd": [
            "qhd"
        ],

        "1080p": [
            "1080p"
        ],

        "full hd": [
            "full hd"
        ],

        "wireless": [
            "wireless"
        ],

        "bluetooth": [
            "bluetooth"
        ],

        "usb-c": [
            "usb-c",
            "usb c"
        ],
        "earbuds": [
    "earbuds",
    "earbud"
    ],

    "headphones": [
    "headphones",
    "headphone"
    ],

    "speaker": [
    "speaker",
    "speakers"
    ],
    "student": [
    "student",
    "students"
    ]
    }

    detected = []

    for specification, aliases in possible_specs.items():

        for alias in aliases:

            if alias in question:

                detected.append(
                    specification
                )

                break

    return ", ".join(detected)


# Detect Recommendation Question

def is_recommendation_question(question):

    question = question.lower()

    keywords = [
    "recommend",
    "recommendation",
    "suggest",
    "best",
    "good for",
    "suitable for",
    "looking for",
    "i need",
    "i want",
    "budget",
    "under",
    "below",
    "less than"
    ]

    return any(
        keyword in question
        for keyword in keywords
    )


# Answer Specific Product Question

def answer_product_question(
    question,
    product
):

    product_data = search_product.invoke(
        {
            "query": product
        }
    )

    if product_data.startswith(
        "No product was found"
    ):
        return product_data

    prompt = f"""
You are the Product Agent for TechStore.

Answer the customer's question using ONLY
the product information below.

Do not invent information.

Product Information:
{product_data}

Customer Question:
{question}

Answer:
"""

    return generate_text(
        prompt,
        max_new_tokens=150
    )


# Recommend Products

def answer_recommendation(question):

    # Extract customer requirements
    category = detect_category(question)

    max_price = extract_max_price(question)

    min_rating = extract_min_rating(question)

    specifications = extract_specifications(question)

    # Search products using the Product Tool
    product_data = recommend_products.invoke(
        {
            "category": category or "",
            "max_price": max_price,
            "min_rating": min_rating,
            "specifications": specifications,
            "limit": 3
        }
    )

    # No matching products
    if product_data.startswith(
        "No products match"
    ):
        return product_data

    # Build customer requirements summary
    requirements = []

    if category:
        requirements.append(
            f"category: {category}"
        )

    if max_price is not None:
        requirements.append(
            f"price up to ${max_price:g}"
        )

    if min_rating is not None:
        requirements.append(
            f"rating of at least {min_rating:g}"
        )

    if specifications:
        requirements.append(
            f"specifications: {specifications}"
        )

    # Create intro
    if requirements:

        requirements_text = ", ".join(
            requirements
        )

        intro = (
            "Based on your requirements "
            f"({requirements_text}), "
            "I recommend the following products:"
        )

    else:

        intro = (
            "I recommend the following products:"
        )

    # Return REAL product data directly
    return (
        f"{intro}\n\n"
        f"{product_data}"
    )


# General Product Question

def answer_general_product_question(question):

    category = detect_category(
        question
    )

    product_data = recommend_products.invoke(
        {
            "category": category or "",
            "max_price": None,
            "min_rating": None,
            "specifications": "",
            "limit": 5
        }
    )

    prompt = f"""
You are the Product Agent for TechStore.

Answer the customer's question using ONLY
the available product data below.

Do not invent information.

Product Data:

{product_data}

Customer Question:
{question}

Answer:
"""

    return generate_text(
        prompt,
        max_new_tokens=180
    )


# Main Product Agent

def product_agent(question):

    product = detect_product(
        question
    )

    # Specific product question
    if product:

        return answer_product_question(
            question,
            product
        )

    # Recommendation question
    if is_recommendation_question(
        question
    ):

        return answer_recommendation(
            question
        )

    # General product question
    return answer_general_product_question(
        question
    )