import os
import psycopg2

connection = psycopg2.connect(
    host="localhost",
    database="ziina_payments_reconciliation",
    user="postgres",
    password=os.environ["DB_PASSWORD"]
)

cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM product_ledger;")

count = cursor.fetchone()[0]

print(f"Database connection successful. Product ledger rows: {count}")

cursor.close()
connection.close()