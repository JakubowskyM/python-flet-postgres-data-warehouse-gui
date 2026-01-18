import os
import csv
import psycopg2
from psycopg2 import sql
import randomize_db as rddb

def generate_structure(db_name: str, password: str,
                       generate_csv: bool, create_db: bool):
    """
    Function operates in two modes:
    1. Creating a new database (create_db=True, generate_csv=True)
       - checks connection to the server
       - generates CSV files
       - creates the database
       - creates structure and imports data
       - returns 1 if success, 0 if error
    2. Login to existing database (create_db=False, generate_csv=False)
       - checks connection to existing database
       - returns psycopg2 connection object if OK, 0 if error
    """

    if not create_db and not generate_csv:
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    database=db_name,
                    user="postgres",
                    password=password
                )
                conn.autocommit = True
                print(type(conn))
                print(f"Połączono z istniejącą bazą '{db_name}'.")
                return conn
            except Exception as e:
                return 0
                

    elif create_db and generate_csv:

            os.makedirs("tables", exist_ok=True)
            rddb.generate_csv_files(
                addresses_count=50, shops_count=10,
                clients_count=100, exporters_count=5,
                total_components=100
            )
            print("Pliki CSV wygenerowane.")


            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user="postgres",
                password=password
            )
            conn.autocommit = True
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cur.fetchone():
                print(f"Baza '{db_name}' już istnieje.")
                cur.close()
                conn.close()
                return 0

            cur.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(db_name),
                    sql.Identifier("postgres")
                )
            )
            print(f"Baza '{db_name}' utworzona.")
            cur.close()
            conn.close()

            conn = psycopg2.connect(
                host="localhost",
                database=db_name,
                user="postgres",
                password=password
            )
            conn.autocommit = True
            cur = conn.cursor()

            sql_file_path = "database/database_skeleton.sql"
            try:
                with open(sql_file_path, "r", encoding="utf-8") as f:
                    sql_content = f.read()
            except UnicodeDecodeError:
                print("Błąd odczytu pliku SQL – sprawdź kodowanie pliku.")
                cur.close()
                conn.close()
                return 0

            for stmt in sql_content.split(";"):
                stmt = stmt.strip()
                if stmt:
                    cur.execute(stmt)
            print(f"Struktura bazy '{db_name}' utworzona.")

            fk_safe_order = [
                "addresses","exporters","components","shops","clients",
                "cpus","gpus","rams","psus","disks","motherboards",
                "exporter_offers","imports","sales"
            ]
            for table_name in fk_safe_order:
                file_path = os.path.join("tables", f"{table_name}.csv")
                if not os.path.exists(file_path):
                    continue
                with open(file_path, newline='', encoding="utf-8-sig") as csvfile:
                    reader = csv.reader(csvfile)
                    headers = next(reader)
                    headers = [h.strip('"') for h in headers]
                    for row in reader:
                        placeholders = ','.join(['%s'] * len(row))
                        insert_stmt = sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                            sql.Identifier(table_name),
                            sql.SQL(',').join(map(sql.Identifier, headers)),
                            sql.SQL(placeholders)
                        )
                        cur.execute(insert_stmt, row)
            print("Import CSV zakończony.")

            cur.close()
            conn.close()
            return 1
