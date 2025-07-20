import psycopg2
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("hostname", "localhost"),
        dbname=os.getenv("dbname", "pagila"),
        user=os.getenv("user_name", "postgres"),
        password=os.getenv("password", ""),
        port=5432
    )

def run_query(query):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        return columns, rows
    except Exception as e:
        print("❌ SQL Execution Error:", e)
        raise

def get_text_columns(schema=None, table=None):
    """Return all text/varchar columns in the database or filtered by schema/table."""
    query = """
        SELECT table_schema, table_name, column_name
        FROM information_schema.columns
        WHERE data_type IN ('text', 'character varying', 'character')
        AND table_schema NOT IN ('information_schema', 'pg_catalog')
    """
    if schema:
        query += f" AND table_schema = '{schema}'"
    if table:
        query += f" AND table_name = '{table}'"

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print("❌ Failed to fetch text columns:", e)
        return []

def get_primary_key_column(schema, table):
    """Returns the primary key column of a table if available, otherwise None."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = %s
              AND tc.table_name = %s;
        """
        cur.execute(query, (schema, table))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"❌ Failed to get primary key for {schema}.{table}:", e)
        return None

def fix_encoding_for_column(schema, table, column, id_column="id", corruption_regex=None):
    """
    Fix encoding issues in a single column.
    If corruption_regex is provided, it will filter values using it.
    """
    fixed_count = 0
    try:
        conn = get_connection()
        cur = conn.cursor()

        full_table = f'"{schema}"."{table}"'
        corruption_clause = f"WHERE {column} ~ '{corruption_regex}'" if corruption_regex else ""

        query = f"""
            SELECT {id_column}, {column}
            FROM {full_table}
            {corruption_clause};
        """

        cur.execute(query)
        rows = cur.fetchall()

        for row_id, bad_value in rows:
            if not isinstance(bad_value, str):
                continue
            try:
                fixed_value = bad_value.encode('latin1').decode('utf-8')
                if fixed_value != bad_value:
                    cur.execute(
                        f"UPDATE {full_table} SET {column} = %s WHERE {id_column} = %s",
                        (fixed_value, row_id)
                    )
                    fixed_count += 1
            except UnicodeDecodeError:
                continue 

        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Fixed {fixed_count} entries in {schema}.{table}.{column}")
    except Exception as e:
        print(f"❌ Error processing {schema}.{table}.{column}:", e)

def fix_all_encoding_issues(corruption_regex="Ã|â€™|â€“|â€œ|â€|Ãƒ"):
    """
    Run fix_encoding_for_column on all text/varchar/char columns in all tables.
    `corruption_regex` can be changed or set to None for full scan.
    """
    columns_info = get_text_columns()
    for schema, table, column in columns_info:
        id_column = get_primary_key_column(schema, table)
        if id_column:
            fix_encoding_for_column(schema, table, column, id_column, corruption_regex)
        else:
            print(f"Skipping {schema}.{table} - no suitable primary key found.")

