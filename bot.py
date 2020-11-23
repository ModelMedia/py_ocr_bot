import os
from dotenv import load_dotenv
from telethon import TelegramClient, events, errors
from ocr import ocr_space_file, ocr_space_url, ocr_response_data

import log_srv

load_dotenv()
logger = log_srv.get_logger(__name__)
# logger.warning()

BOT_TOKEN = os.getenv('BOT_TOKEN')
APP_API_ID = os.getenv('APP_API_ID')
APP_API_HASH = os.getenv('APP_API_HASH')

bot = TelegramClient('bot', APP_API_ID, APP_API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message wnen the command /start is issued"""
    try:
        await event.respond(
            """Hi! I am bot for OCR on pictures and pdf files.\nSend me image/pdf file with text.\nI will process the file. And if the OCR service finds the text there, \nthen you will get the result of its work.
            """)
        logger.info('event.respond on /start')
    except Exception as inst_exception:
        logger.warning(inst_exception)
    # else:
        # raise events.StopPropagation


# @bot.on(events.UserUpdate)
# async def uploading_handler(event):
#     """userUpdate"""
#     # If someone is uploading, say something
#     client = event.client
#     print('event.client: ', client)
#     if event.uploading:
#         if event.photo:
#             # await client.send_message(event.user_id, 'What are you sending?')
#             await event.respond(event.user_id, 'What photo are you sending?')
#         else:
#             await event.respond(event.user_id, 'I receive only photo or pdf!')


@bot.on(events.NewMessage)
async def rec_file(event):
    """receive file from user
       allowed only mime_type: application/pdf, image/png, image/jpeg,
       image/gif, image/bmp, image/tiff.
        The maximum length for a message is 35,000 bytes or 4,096 characters
    """
    logger.info('event.NewMessage')
    print(event)
    e_msg = event.message
    if e_msg.document:
        print('document.mime_type:', e_msg.document.mime_type)
    if e_msg.file:
        f = e_msg.file
        print('file.name:', f.name)
    # cur_dir = os.getcwd()
    # path = await e_msg.download_media(file='\downloads')
    path_file = await e_msg.download_media()
    logger.info('File saved to: ' + str(path_file))

    # proccessing the file by servise ocr api
    resp_ocr = ocr_space_file(path_file)
    data_ocr = ocr_response_data(resp_ocr)
    logger.info('result ocr - ocr_code: ' + str(data_ocr['ocr_code']))
    logger.info('result ocr - parsed_text: \n' + str(data_ocr['parsed_text']))
    try:
        os.remove(path_file)
        logger.info('File remove ' + str(path_file))
    except Exception as os_remove_exception:
        logger.warning(os_remove_exception)

    pars_text = data_ocr['parsed_text']

    #reply by parsed text
    logger.info('reply by parsed text')
    await event.reply('parsed text:\n' + pars_text)


def main():
    """
    Start the bot
    """
    bot.run_until_disconnected()

if __name__ == "__main__":
    main()
