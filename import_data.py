
import pandas as pd
import psycopg
from decimal import Decimal
from db_config import DB_CONFIG

CSV_FILE = "Sales_data.csv"

try:
    # Read CSV dataset
    df = pd.read_csv(CSV_FILE)

    # Validate required columns
    required_columns = [
        "OrderDate", "Product", "Category",
        "Region", "Quantity", "UnitPrice"
    ]

    if not all(column in df.columns for column in required_columns):
        raise ValueError("CSV file is missing required columns.")

    if df.empty:
        raise ValueError("CSV file contains no records.")

    # Check missing values
    if df[required_columns].isnull().any().any():
        raise ValueError("CSV contains missing values.")

    # Convert data types
    df["OrderDate"] = pd.to_datetime(
        df["OrderDate"], errors="raise"
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="raise"
    )

    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"], errors="raise"
    )

    if (df["Quantity"] <= 0).any():
        raise ValueError("Quantity must be greater than zero.")

    if (df["Quantity"] % 1 != 0).any():
        raise ValueError("Quantity must contain whole numbers.")

    if (df["UnitPrice"] < 0).any():
        raise ValueError("UnitPrice cannot be negative.")

    # Connect to PostgreSQL
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:

            # Prevent accidental duplicate imports
            cur.execute("SELECT COUNT(*) FROM sales")
            existing_records = cur.fetchone()[0]

            if existing_records > 0:
                raise ValueError(
                    "Sales table already contains records. "
                    "Import cancelled to prevent duplicates."
                )

            # Insert records
            insert_query = """
                INSERT INTO sales (
                    order_date,
                    product,
                    category,
                    region,
                    quantity,
                    unit_price
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            records = [
                (
                    row.OrderDate.date(),
                    row.Product,
                    row.Category,
                    row.Region,
                    int(row.Quantity),
                    Decimal(str(row.UnitPrice))
                )
                for row in df.itertuples(index=False)
            ]

            cur.executemany(insert_query, records)

    print("\nCSV data imported successfully!")
    print("Total records imported:", len(df))

except FileNotFoundError:
    print("Error: sales_data.csv file not found.")

except (ValueError, TypeError) as e:
    print("Data validation error:", e)

except psycopg.Error as e:
    print("Database error:", e)
