import os
import csv
import psycopg2
from psycopg2 import sql
import randomize_db as rddb  # Twój moduł generujący CSV

def generate_structure(db_name: str, password: str,
                       generate_csv=True):


    # Connect to PostgreSQL server to create database

    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password=password
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Check if database exists

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    if cur.fetchone():
        print(f"Database '{db_name}' already exists.\n")
        cur.close()
        conn.close()
        return 0

    cur.execute(
        sql.SQL("CREATE DATABASE {} OWNER {}").format(
            sql.Identifier(db_name),
            sql.Identifier('postgres')
        )
    )
    print(f"Database '{db_name}' created.\n")
    cur.close()
    conn.close()

    # CSV generation with random data
    
    if generate_csv:
        os.makedirs("tables", exist_ok=True)
        rddb.generate_csv_files(addresses_count=50, shops_count=10,
                                clients_count=100, exporters_count=5,
                                total_components=100)


    # Connect to the newly created database and create structure

    conn = psycopg2.connect(
        host="localhost",
        database=db_name,
        user="postgres",
        password=password
    )
    conn.autocommit = True
    cur = conn.cursor()

    sql_file_path = "database/database_skeleton.sql"
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    for stmt in sql_content.split(";"):
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)

    print(f"Structure of database '{db_name}' created.\n")

    
    # Data import from CSV files
    fk_safe_order = [
        "addresses",
        "exporters",
        "components",
        "shops",
        "clients",
        "cpus",
        "gpus",
        "rams",
        "psus",
        "disks",
        "motherboards",
        "exporter_offers",
        "imports",
        "sales"
    ]

    for table_name in fk_safe_order:
        file_path = os.path.join("tables", f"{table_name}.csv")
        if not os.path.exists(file_path):
            continue

        with open(file_path, newline='', encoding="utf-8-sig") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # nagłówki
            headers = [h.strip('"') for h in headers]  # strip quotes from headers

            for row in reader:
                placeholders = ','.join(['%s'] * len(row))
                insert_stmt = sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                    sql.Identifier(table_name),
                    sql.SQL(',').join(map(sql.Identifier, headers)),
                    sql.SQL(placeholders)
                )
                cur.execute(insert_stmt, row)

    print(f"Data imported from CSV files in 'tables'.")
    cur.close()
    conn.close()
    return 1

generate_structure("my_database", "milosz", generate_csv=True)
