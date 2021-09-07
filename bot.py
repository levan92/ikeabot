import os 
import logging

import validators

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from utils.watcher import get_stock
from utils.db_utils import UserLinksDB
from utils.msgs import help_msg
from utils.emojis import EMO

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ADDING_LINKS, REMOVING_LINKS = range(2)

user_links_db = UserLinksDB()

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f"Hi I'm iKea {EMO['robot']}")

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(help_msg)

def view_links(update, context):
    ''' Display user links '''
    chat_id = update.message.chat.id
    links = user_links_db.get(chat_id)
    if links:
        update.message.reply_text("I'm looking out for these links for you")
        for i, l in enumerate(links):
            update.message.reply_text(f"{i+1}) {l.link}")
        update.message.reply_text(f"/stock to perform a stock take on your list {EMO['smile']}")
        update.message.reply_text(f"/add or /remove to edit list")
    else:
        update.message.reply_text("Nothing to look out for. Please /add.")

def start_add_links(update, context):
    '''Start convo to add ikea links'''
    update.message.reply_text('Please give me links to add to the watchlist, and send /done to stop adding links')
    update.message.reply_text('Currently we have:')
    chat_id = update.message.chat.id
    try:
        links = [ l.link for l in user_links_db.get(chat_id) ]
        context.user_data['links'] = links
        for i, link in enumerate(links):
            update.message.reply_text(f"{i+1}) {link}")
    except Exception as e:
        context.user_data['links'] = []
    return ADDING_LINKS

def add_link(update, context):
    '''Add ikea link'''
    links = []
    for link in update.message.text.split('\n'):
        link = link.strip()
        if validators.url(link):
            logger.info(f'Adding {link}')
            links.append(link)
        else:
            msg = f'Invalid link format: {link}'
            logger.warn(msg)
    context.user_data['links'].extend(links)
    context.user_data['links'] = list(set(context.user_data['links']))
    update.message.reply_text(f"go on.. let me know when you are /done.")
    return ADDING_LINKS

def start_remove_links(update, context):
    '''Start convo to remove ikea links'''
    msg = 'Here are the current links, please let me know which to remove (you can give me either the number or the actual link), and send /done to stop removing links'
    logger.info(msg)
    update.message.reply_text(msg)
    chat_id = update.message.chat.id
    links = [l.link for l in user_links_db.get(chat_id)]
    for i, link in enumerate(links):
        update.message.reply_text(f"{i+1}) {link}")
    context.user_data['links'] = links
    context.user_data['to_removes'] = []
    return REMOVING_LINKS

def remove_link(update, context):
    '''Remove ikea link'''
    links = context.user_data['links']
    to_removes = context.user_data['to_removes']
    for text in update.message.text.split():
        text = text.strip()
        selected = None
        try:
            ind = int(text) - 1
            if ind <= len(links):
                selected = links[ind]
        except Exception as e:
            # gave a string/url
            if text in links:
                selected = text
        if selected:
            to_removes.append(selected)
            update.message.reply_text(f'Removing {selected}.')
    update.message.reply_text(f"go on.. let me know when you are /done.")
    return REMOVING_LINKS

def end_edit_links(update, context):
    chat_id = update.message.chat.id
    links = context.user_data.get('links')
    to_removes = context.user_data.get('to_removes', [])
    for select in set(to_removes):
        if select in links:
            links.remove(select)
    if links:
        update.message.reply_text(f"Will look out for these now:")
        for i, link in enumerate(links):
            update.message.reply_text(f"{i+1}) {link}")
        logger.info(links)
        user_links_db.replace(chat_id, links)
        update.message.reply_text(f"/stock to perform a stock take on your list {EMO['smile']}")
    else:
        msg = "No links received! /add again?"
        logger.info(msg)
        update.message.reply_text(msg)
    return ConversationHandler.END

def report_stock(update, context):
    chat_id = update.message.chat.id
    links = [ l.link for l in user_links_db.get(chat_id) ]

    if links:
        update.message.reply_text('Hold on, checking with IKEA..')
        for i, link in enumerate(links):
            name, success = get_stock(link)
            if success is None:
                msg = f'{i+1}) {name}: {EMO["warn"]} Unable to get info, sorry check yourself {link}'
            elif success:
                msg = f'{i+1}) {name}: {EMO["tick"]} Available! Get it here: {link}'
            else:
                msg = f'{i+1}) {name}: {EMO["cross"]} Nuu out of stock :('
            update.message.reply_text(msg, disable_web_page_preview=True)
    else:
        update.message.reply_text('You have nothing on the list, please /add to it!')

def clear(update, context):
    '''Clear everything from list and db'''

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token = os.environ.get('TELE_TOKEN')
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stock", report_stock))
    dp.add_handler(CommandHandler("list", view_links))
    dp.add_handler(CommandHandler("help", help))

    convo_handler = ConversationHandler(
        entry_points=[CommandHandler('add', start_add_links), CommandHandler('remove', start_remove_links)],
        states={
            ADDING_LINKS: [CommandHandler('done', end_edit_links), MessageHandler(Filters.text, add_link)],
            REMOVING_LINKS: [CommandHandler('done', end_edit_links), MessageHandler(Filters.text, remove_link)]
        },
        fallbacks=[],
    )
    dp.add_handler(convo_handler)

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, help))


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
