import psycopg
from db_config import DB_CONFIG

try:
    with psycopg.connect(**DB_CONFIG) as conn:
        print("PostgreSQL connection successful!")

        with conn.cursor() as cur:
            cur.execute("SELECT current_database();")
            result = cur.fetchone()

            print("Connected Database:", result[0])

except psycopg.Error as e:
    print("Database connection failed:", e)