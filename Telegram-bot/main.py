import logging
from handlers import bot, logger

def main():
    """Main function to run the bot."""
    try:
        logger.info("Starting bot...")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
