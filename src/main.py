import schedule
import time
from datetime import datetime
from pathlib import Path
from loguru import logger
from typing import List, Dict, Any

from config import (
    EMAIL_CONFIG,
    NOTIFICATION_CONFIG,
    OUTPUT_DIR,
    ATTACHMENTS_DIR,
    LOG_DIR,
    DB_CONNECTION_STRING
)
from email_processor import EmailProcessor
from storage import Storage
from notification import Notifier

# Configure logging
log_file = LOG_DIR / f"scraper_{datetime.now().strftime('%Y%m%d')}.log"
logger.add(log_file, rotation="500 MB", level="INFO")

def process_emails() -> None:
    """Main function to process emails"""
    try:
        # Initialize components
        email_processor = EmailProcessor({
            **EMAIL_CONFIG,
            'attachments_dir': ATTACHMENTS_DIR
        })
        storage = Storage({
            'output_dir': OUTPUT_DIR,
            'db_connection_string': DB_CONNECTION_STRING
        })
        notifier = Notifier(NOTIFICATION_CONFIG)

        # Process emails
        emails = email_processor.get_emails()
        if not emails:
            logger.info("No new emails to process")
            return

        # Save to different formats
        storage.save_to_csv(emails)
        storage.save_to_excel(emails)
        storage.save_to_db(emails)

        # Send notification
        notifier.send_summary(emails)

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        if NOTIFICATION_CONFIG['enabled']:
            Notifier(NOTIFICATION_CONFIG).send_notification(
                "Email Scraper Error",
                f"Error occurred: {str(e)}"
            )

def main():
    """Entry point with scheduling"""
    logger.info("Starting Email Scraper")

    # Schedule the job
    schedule.every(10).minutes.do(process_emails)

    # Run immediately on start
    process_emails()

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()