#!/usr/bin/env python3
import argparse
import logging
import os
import sys

# Add the project root to sys.path to allow absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from domains.users.models import UserDB  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Create an administrator user in the e-commerce database."
    )
    parser.add_argument(
        "--db-url",
        type=str,
        required=True,
        help="Database connection URL (e.g. sqlite:///ecom_backend.db)",
    )
    args = parser.parse_args()

    logger.info("=== Create Admin User ===")

    # Gracefully handle non-interactive environments (e.g. EOFError)
    try:
        first_name = input("First Name [Admin]: ").strip() or "Admin"
    except EOFError:
        first_name = "Admin"

    try:
        last_name = input("Last Name [User]: ").strip() or "User"
    except EOFError:
        last_name = "User"

    engine = create_engine(args.db_url)
    Session = sessionmaker(bind=engine)  # noqa: N806
    session = Session()

    try:
        admin_user = UserDB(
            first_name=first_name,
            last_name=last_name,
            role="admin",  # Admin role
        )
        session.add(admin_user)
        session.commit()
        logger.info(
            "Successfully created admin user: %s %s (ID: %s)",
            first_name,
            last_name,
            admin_user.id,
        )
    except Exception as e:
        session.rollback()
        logger.error("Error creating admin user: %s", e)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
