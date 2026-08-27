import pandas as pd
from langchain.tools import tool


ORDERS_PATH = "data/orders.csv"


def load_orders():
    return pd.read_csv(
        ORDERS_PATH,
        dtype={
            "order_id": str,
            "customer_id": str,
            "product_id": str
        }
    )


def clean_value(value):
    if pd.isna(value):
        return "Not available"

    return str(value)


@tool
def search_order(order_id: str) -> str:
    """
    Search for a TechStore order using its order ID.
    Use this tool when the customer asks about order status
    or order information.
    """

    orders = load_orders()

    order_id = order_id.strip().upper()

    result = orders[
        orders["order_id"].str.upper() == order_id
    ]

    if result.empty:
        return f"No order was found with order ID {order_id}."

    order = result.iloc[0]

    return (
        f"Order ID: {clean_value(order['order_id'])}\n"
        f"Customer ID: {clean_value(order['customer_id'])}\n"
        f"Product ID: {clean_value(order['product_id'])}\n"
        f"Quantity: {clean_value(order['quantity'])}\n"
        f"Status: {clean_value(order['status'])}\n"
        f"Order Date: {clean_value(order['order_date'])}\n"
        f"Delivery Date: {clean_value(order['delivery_date'])}\n"
        f"Total Amount: ${clean_value(order['total_amount'])}"
    )