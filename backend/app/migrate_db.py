"""Safe SQLite schema migration helper for PayPilot AI."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "paypilot.db")
ROOT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "paypilot.db")

target_db = DB_PATH if os.path.exists(DB_PATH) else ROOT_DB_PATH


def migrate():
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    # 1. Merchants table columns
    merchant_cols = [
        ("website_url", "TEXT"),
        ("logo_icon", "TEXT DEFAULT '🏬'"),
        ("rating", "REAL DEFAULT 4.5"),
    ]
    for col_name, col_type in merchant_cols:
        try:
            cursor.execute(f"ALTER TABLE merchants ADD COLUMN {col_name} {col_type};")
            print(f"Added column merchants.{col_name}")
        except sqlite3.OperationalError:
            pass  # Already exists

    # 2. Products table columns
    product_cols = [
        ("original_price_paise", "INTEGER"),
        ("subcategory", "TEXT"),
        ("brand", "TEXT"),
        ("image_url", "TEXT"),
        ("product_url", "TEXT"),
        ("provider_code", "TEXT DEFAULT 'internal'"),
        ("provider_name", "TEXT DEFAULT 'PayPilot Catalog'"),
        ("data_source_type", "TEXT DEFAULT 'DEMO'"),
        ("rating", "REAL DEFAULT 4.5"),
        ("rating_count", "INTEGER DEFAULT 120"),
        ("specifications", "TEXT"),
        ("supports_integrated_checkout", "INTEGER DEFAULT 1"),
        ("updated_at", "TEXT"),
    ]
    for col_name, col_type in product_cols:
        try:
            cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type};")
            print(f"Added column products.{col_name}")
        except sqlite3.OperationalError:
            pass  # Already exists

    conn.commit()
    conn.close()
    print("Schema migration completed.")


if __name__ == "__main__":
    migrate()
