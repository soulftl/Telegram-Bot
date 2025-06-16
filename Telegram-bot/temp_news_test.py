import logging
from news import get_news_by_category
import sys

# Configure logging to output to a file and console
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("temp_news_debug.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting script to fetch 'administration' news...")
    try:
        admin_news = get_news_by_category("administration")
        if admin_news:
            logger.info(f"Found {len(admin_news)} administration news articles.")
            for i, news_item in enumerate(admin_news[:5]): # Print first 5 for brevity
                logger.info(f"--- News Item {i+1} ---")
                logger.info(f"Title: {news_item.get('title')}")
                logger.info(f"Link: {news_item.get('link')}")
                logger.info(f"Date: {news_item.get('date')}")
                logger.info(f"Description: {news_item.get('description', '')[:100]}...") # Truncate description
        else:
            logger.info("No administration news articles found.")
    except Exception as e:
        logger.error(f"An error occurred during news fetching: {e}", exc_info=True) 