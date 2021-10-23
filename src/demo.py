import psycopg2

pg_connection = {
    "dbname": "ecommerce",
    "user": "ecommerce_user",
    "password": "password",
    "host": "postgres_db",
    "port": 5432
}

conn = psycopg2.connect(**pg_connection)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a query
cur.execute("SELECT * FROM select * from pg_database")

# Retrieve query results
records = cur.fetchall()
print(records)
