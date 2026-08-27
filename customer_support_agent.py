import re

from rag.rag_system import retrieve_documents
from tools.order_tool import search_order
from llm.local_llm import generate_text


# Detect Order ID

def extract_order_id(question):

    pattern = r"\bO\d+\b"

    match = re.search(
        pattern,
        question,
        re.IGNORECASE
    )

    if match:
        return match.group().upper()

    return None


# Detect Order Questions

def is_order_question(question):

    order_keywords = [
        "order",
        "order status",
        "delivery status",
        "my order",
        "track",
        "tracking",
        "shipped",
        "delivered"
    ]

    question_lower = question.lower()

    return any(
        keyword in question_lower
        for keyword in order_keywords
    )


# Generate LLM Answer
# --------------------------------------------------

def generate_answer(
    question,
    context
):

    prompt = f"""
You are the Customer Support Agent for TechStore.

Answer the customer's question using ONLY the
information provided in the context.

Do not invent information.

If the required information is not available,
say that you do not have enough information.

Keep the answer clear, concise, and helpful.

Context:
{context}

Customer Question:
{question}

Answer:
"""

    return generate_text(
        prompt,
        max_new_tokens=150
    )


# Answer Company and Policy Questions Using RAG

def answer_with_rag(question):

    documents = retrieve_documents(
        question,
        k=2
    )

    if not documents:

        return (
            "I could not find relevant "
            "company information."
        )

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    return generate_answer(
        question,
        context
    )


# Answer Order Questions

def answer_order_question(question):

    order_id = extract_order_id(
        question
    )

    if not order_id:

        return (
            "Please provide your order ID "
            "so I can check your order."
        )

    order_information = search_order.invoke(
        {
            "order_id": order_id
        }
    )

    # Handle order not found directly
    if order_information.startswith(
        "No order was found"
    ):

        return order_information

    return generate_answer(
        question,
        order_information
    )


# Customer Support Agent

def customer_support_agent(question):

    if is_order_question(question):

        return answer_order_question(
            question
        )

    return answer_with_rag(
        question
    )