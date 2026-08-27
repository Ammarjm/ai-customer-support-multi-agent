import re

from llm.local_llm import generate_text

from agents.customer_support_agent import (
    customer_support_agent
)

from agents.product_agent import (
    product_agent
)


# Detect obvious Customer Support questions

def detect_customer_support(question):

    question_lower = question.lower()

    support_keywords = [
        "return",
        "refund",
        "shipping",
        "shipment",
        "warranty",
        "payment",
        "company",
        "policy",
        "policies",
        "order",
        "order status",
        "track order",
        "tracking",
        "shipped",
        "delivered"
    ]

    # Order ID such as O0001
    order_id = re.search(
        r"\bO\d+\b",
        question,
        re.IGNORECASE
    )

    if order_id:
        return True

    return any(
        keyword in question_lower
        for keyword in support_keywords
    )


# Detect obvious Product questions

def detect_product_question(question):

    question_lower = question.lower()

    product_keywords = [
        "product",
        "products",
        "laptop",
        "monitor",
        "phone",
        "smartphone",
        "headphones",
        "headphone",
        "earbuds",
        "earbud",
        "speaker",
        "keyboard",
        "mouse",
        "charger",
        "accessories",
        "recommend",
        "recommendation",
        "suggest",
        "best",
        "price",
        "rating",
        "specifications",
        "specs",
        "ram",
        "ssd",
        "4k",
        "wireless"
    ]

    # Product ID such as P001
    product_id = re.search(
        r"\bP\d{3}\b",
        question,
        re.IGNORECASE
    )

    if product_id:
        return True

    return any(
        keyword in question_lower
        for keyword in product_keywords
    )


# Use LLM to classify unclear questions

def classify_with_llm(question):

    prompt = f"""
You are the Routing Agent for TechStore.

Your job is to classify the customer's question.

There are only two possible agents:

CUSTOMER_SUPPORT
Use this agent for:
- company information
- company policies
- returns
- refunds
- shipping
- warranty
- payment
- order status
- order information
- order tracking

PRODUCT
Use this agent for:
- product information
- product specifications
- product prices
- available products
- product search
- product recommendations
- customer requirements
- budget
- ratings

Customer Question:
{question}

Return ONLY one label:

CUSTOMER_SUPPORT

or

PRODUCT

Label:
"""

    result = generate_text(
        prompt,
        max_new_tokens=10
    )

    result = result.strip().upper()

    if "CUSTOMER_SUPPORT" in result:
        return "customer_support"

    if "PRODUCT" in result:
        return "product"

    return None


# Decide which agent should handle the question

def route_question(question):

    # Strong indication of order/support question
    if detect_customer_support(question):
        return "customer_support"

    # Strong indication of product question
    if detect_product_question(question):
        return "product"

    # Use LLM for unclear questions
    llm_route = classify_with_llm(
        question
    )

    if llm_route:
        return llm_route

    # Safe default
    return "customer_support"


# Routing Agent

def routing_agent(question):

    route = route_question(
        question
    )

    if route == "product":

        answer = product_agent(
            question
        )

        return {
            "agent": "Product Agent",
            "answer": answer
        }

    answer = customer_support_agent(
        question
    )

    return {
        "agent": "Customer Support Agent",
        "answer": answer
    }