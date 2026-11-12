
import psycopg
import pandas as pd
from db_config import DB_CONFIG


def get_sales_data():
    query = """
        SELECT
            order_id,
            order_date,
            product,
            category,
            region,
            quantity,
            unit_price,
            quantity * unit_price AS revenue
        FROM sales
        ORDER BY order_date;
    """

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            records = cur.fetchall()

            columns = [desc.name for desc in cur.description]

    return pd.DataFrame(records, columns=columns)


def add_sale(order_date, product, category, region, quantity, unit_price):
    query = """
        INSERT INTO sales (
            order_date,
            product,
            category,
            region,
            quantity,
            unit_price
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING order_id;
    """

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    order_date,
                    product,
                    category,
                    region,
                    quantity,
                    unit_price
                )
            )
            new_id = cur.fetchone()[0]

    return new_id


def update_sale(order_id, order_date, product, category,
                region, quantity, unit_price):

    query = """
        UPDATE sales
        SET order_date = %s,
            product = %s,
            category = %s,
            region = %s,
            quantity = %s,
            unit_price = %s
        WHERE order_id = %s
        RETURNING order_id;
    """

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    order_date,
                    product,
                    category,
                    region,
                    quantity,
                    unit_price,
                    order_id
                )
            )

            result = cur.fetchone()

    return result[0] if result else None


def delete_sale(order_id):

    query = """
        DELETE FROM sales
        WHERE order_id = %s
        RETURNING order_id;
    """

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (order_id,))
            result = cur.fetchone()

    return result[0] if result else None
