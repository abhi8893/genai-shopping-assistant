#!/usr/bin/env python3

import argparse
import logging
import os
import sys

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text as sql_text

# NOTE: Crafted by a Human, Refactored by an AI.
# NOTE: Sometimes, not so good an idea.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def create_product_hierarchy(df_prod_raw):
    df_hier_prep = (
        df_prod_raw[["category", "subcategory"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .rename(
            columns={"category": "category_name", "subcategory": "subcategory_name"}
        )
    )
    df_hier_prep["category_id"] = (
        df_hier_prep["category_name"].astype("category").cat.codes + 1
    )
    df_hier_prep["subcategory_id"] = (
        df_hier_prep["subcategory_name"].astype("category").cat.codes + 1
    )
    df_hier_prep["category_slug"] = (
        df_hier_prep["category_name"].str.lower().str.replace(" ", "-")
    )
    df_hier_prep["subcategory_slug"] = (
        df_hier_prep["subcategory_name"].str.lower().str.replace(" ", "-")
    )
    df_hier_prep["id"] = range(1, len(df_hier_prep) + 1)
    return df_hier_prep


def prepare_products_data(df_prod_raw, df_hier_prep):
    df_prod_prep = df_prod_raw.copy()
    df_prod_prep.rename(
        columns={"category": "category_name", "subcategory": "subcategory_name"},
        inplace=True,
    )
    df_prod_prep["category_slug"] = (
        df_prod_prep["category_name"].str.lower().str.replace(" ", "-")
    )
    df_prod_prep["subcategory_slug"] = (
        df_prod_prep["subcategory_name"].str.lower().str.replace(" ", "-")
    )
    df_prod_prep = pd.merge(
        df_prod_prep,
        df_hier_prep[
            ["category_slug", "subcategory_slug", "category_id", "subcategory_id"]
        ],
        on=["category_slug", "subcategory_slug"],
        how="left",
        validate="many_to_one",
    )
    df_prod_prep["slug"] = df_prod_prep["name"].str.lower().str.replace(" ", "-")
    df_prod_prep["id"] = range(1, len(df_prod_prep) + 1)
    cols_to_keep = [
        "id",
        "name",
        "slug",
        "description",
        "category_id",
        "subcategory_id",
        "price",
    ]
    return df_prod_prep[cols_to_keep]


def initialize_database(engine):
    with engine.connect() as conn:
        sql_script = """
        DELETE FROM product;
        DELETE FROM product_hierarchy;
        """
        execute_sql_script(conn, sql_script)

        check_seq_sql = """
        SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence';
        """
        result = conn.execute(sql_text(check_seq_sql)).fetchone()
        if result:
            seq_reset_sql = """
            DELETE FROM sqlite_sequence WHERE name IN ('product', 'product_hierarchy');
            """
            execute_sql_script(conn, seq_reset_sql)


def execute_sql_script(conn, sql_script):
    for statement in sql_script.split(";"):
        try:
            conn.execute(sql_text(statement))
            conn.commit()
        except Exception as e:
            logger.error("Error executing SQL: %s", statement)
            logger.error("Error details: %s", str(e))
            conn.rollback()
            raise


def load_product_data(data_file, data_dir):
    if data_dir:
        data_fpath = os.path.join(data_dir, data_file)
    else:
        data_fpath = data_file
    df = pd.read_csv(data_fpath)
    return df


def ingest_product_data(db_url, data_file, data_dir, reset_db=False, log_level="INFO"):
    logger.setLevel(log_level)

    engine = create_engine(db_url)
    if reset_db:
        logger.info("Resetting database...")
        initialize_database(engine)
    df_raw = load_product_data(data_file, data_dir)
    df_hier = create_product_hierarchy(df_raw)
    df_products = prepare_products_data(df_raw, df_hier)

    with engine.connect() as conn:
        df_hier.to_sql("product_hierarchy", con=conn, if_exists="append", index=False)
        df_products.to_sql("product", con=conn, if_exists="append", index=False)
    logger.info("Product data ingestion completed successfully!")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-url", type=str, default="sqlite:///ecom.db")
    parser.add_argument("--data-file", type=str)
    parser.add_argument("--data-dir", type=str, default=None)
    parser.add_argument("--reset-db", action="store_true")
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(ingest_product_data(**vars(parse_arguments())))
