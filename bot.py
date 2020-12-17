import os
from dotenv import load_dotenv
from telethon import TelegramClient, events, errors, Button
from ocr import ocr_space_file, ocr_space_url, ocr_response_data

import log_srv
from settings import get_default_settings
from utills import set_lang, settings_msg, settings_buttons_inline, language_buttons_inline, menu_button_inline
from file_srv import str_to_file, check_dir, is_file_valid

load_dotenv()
logger = log_srv.get_logger(__name__)
# logger.warning()

BOT_TOKEN = os.getenv('1441556191:AAE7UgTUJB2vpToDpGWCPh-KKzjc1Taep8g')
APP_API_ID = os.getenv('2474270')
APP_API_HASH = os.getenv('d6c0a53a212d5cd76afd69a48a9d80f8')

srv_settings = get_default_settings()
logger.info('default srv_settings: ' + str(srv_settings))

list_lang_btn_inline = language_buttons_inline()


bot = TelegramClient('bot', APP_API_ID, APP_API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage(pattern='/start|/settings'))
async def start(event):
    """Send a message wnen the command /start is issued"""

    try:
        await event.respond(settings_msg(srv_settings), buttons=settings_buttons_inline())

        logger.info('event.respond on /start')
    except Exception as inst_exception:
        logger.warning(inst_exception)


@bot.on(events.NewMessage)
async def rec_file(event):
    """receive file from user
       allowed only mime_type: application/pdf, image/png, image/jpeg,
       image/gif, image/bmp, image/tiff.
        The maximum length for a message is 35,000 bytes or 4,096 characters
    """
    # allowed_file_types = ['application/pdf', 'image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/tiff']

    logger.info('event.NewMessage')
    print(event)

    event_msg = event.message
    # msg_id = event_msg.id
    # logger.info('msg_id: ' + str(msg_id))
    # chat = await event.get_chat()
    # logger.info('event.chat: ' + str(chat))
    # sender = await event.get_sender()
    # logger.info('event.sender: ' + str(sender))
    # logger.info('event.chat_id: ' + str(event.chat_id))
    # logger.info('event.sender_id: ' + str(event.sender_id))
    # user_id = event_msg.peer_id
    # logger.info('user_id: ' + str(user_id))
    # logger.info('event_client: ' + str(event.client))

    if event_msg.document:
        logger.info('document.mime_type: ' + event_msg.document.mime_type)

    # try:
    #     b=allowed_file_types.index(event_msg.document.mime_type)
    # except ValueError:
    #     logger.warning(ValueError)
        if not is_file_valid(event_msg):

            await event.reply('Sorry, this file type cannot be processed\nOnly these types of files can be processed: PDF, PNG, JPG(JPEG), BMP, TIF(TIFF), GIF.\nOther limits:\nFile size limit - 1 MB. PDF page limit - 3\nLimit requests to API service - 500 calls/DAY.')

        else:
            await event.reply('Please, wait. Just one moment ....')

            if event_msg.file:
                user_file = event_msg.file
                # logger.info('file.mime_type: ' + user_file.mime_type)
                # logger.info('file.name: ' + user_file.name)
                # logger.info('file.size: ' + str(user_file.size)) #size in bytes of this file.

            check_dir('tmp')

            user_file = await event_msg.download_media(file='tmp/' + user_file.name)
            logger.info('File saved to: ' + str(user_file))

            # proccessing the file by servise ocr api
            resp_ocr = ocr_space_file(user_file, language=srv_settings['lang']['code'], isTable=srv_settings['isTable']['code'])
            data_ocr = ocr_response_data(resp_ocr)
            logger.info('result ocr - ocr_code: ' + str(data_ocr['ocr_code']))
            # logger.info('result ocr - parsed_text: \n' + str(data_ocr['parsed_text']))

            #remove user's file
            try:
                os.remove(user_file)
                logger.info('File remove ' + str(user_file))
            except Exception as os_remove_exception:
                logger.warning(os_remove_exception)

            if data_ocr['ocr_exit_code'] != 1:
                logger.info('error result ocr code: {!s}'.format(data_ocr['ocr_code']))
                await event.reply('Ooops! Something went wrong:\n{!s}'.format(data_ocr['ocr_code']))
            else:
                pars_text = data_ocr['parsed_text']
                logger.info('Length of parsed text {!s} items'.format(len(pars_text)))
                # logger.info('parsed text:\n {}'.format(pars_text))
                #reply by parsed text
                if srv_settings['result']['code'] == 'file':

                    str_to_file(pars_text)
                    logger.info('reply by text file')

                    await event.respond(file='tmp/ocr_text.txt', message='Parsing result in this file')
                    os.remove('tmp/ocr_text.txt')
                elif srv_settings['result']['code'] == 'message':
                    logger.info('reply by message with parsed text')
                    await event.reply('Parsed text:\n' + pars_text)


@bot.on(events.CallbackQuery)
async def handle_callback_query(event: events.CallbackQuery.Event):

    logger.info('event.stringify: ' + str(event))
    # msg_id = event.original_update.msg_id
    # user_id = event.original_update.user_id
    cb_data = event.original_update.data
    logger.info('event cb_data: ' + str(cb_data))

    if 'check_limits' in str(cb_data):
        # logger.info('query cb cb_data: ' + str(cb_data))
        limits_msg = settings_msg(srv_settings, limits=True)
        # logger.info('query cb limits_msg: ' + limits_msg)
        await event.edit(limits_msg, buttons=menu_button_inline())
    if 'back_main_menu' in str(cb_data):
        msg = settings_msg(srv_settings)
        # logger.info('query cb msg: ' + msg)
        await event.edit(msg, buttons=settings_buttons_inline())
    elif 'set_lang' in str(cb_data):

        update_msg = settings_msg(srv_settings, lang=True)
        # logger.info('query cb update_msg: ' + update_msg)
        await event.edit(update_msg, buttons=list_lang_btn_inline)

    elif 'langcode_' in str(cb_data):

        lang_code = str(cb_data)[-4:-1]
        logger.info('query cb lang_code: ' + lang_code)

        srv_settings['lang']['code'] = lang_code
        srv_settings['lang']['desc'] = set_lang[lang_code]

        logger.info('query cb settings: ' + str(srv_settings))
        update_msg = settings_msg(srv_settings,  lang=True)
        # logger.info('query cb update_msg: ' + update_msg)
        await event.edit(update_msg, buttons=list_lang_btn_inline)

    elif 'table' in str(cb_data):
        srv_settings['isTable']['code'] = True
        srv_settings['isTable']['desc'] = 'table'
        srv_settings['update'] = True
        update_msg = settings_msg(srv_settings)
        # logger.info('query cb update_msg: ' + update_msg)
        await event.edit(update_msg, buttons=settings_buttons_inline(format_txt='plain'))

    elif 'plain' in str(cb_data):
        srv_settings['isTable']['code'] = False
        srv_settings['isTable']['desc'] = 'plain'
        srv_settings['update'] = True
        update_msg = settings_msg(srv_settings)
        # logger.info('query cb update_msg: ' + update_msg)
        await event.edit(update_msg, buttons=settings_buttons_inline(format_txt='table'))

    elif 'file' in str(cb_data):
        srv_settings['result']['code'] = 'file'
        srv_settings['result']['desc'] = 'file'
        srv_settings['update'] = True
        update_msg = settings_msg(srv_settings)
        # logger.info('query cb update_msg: ' + update_msg)
        await event.edit(update_msg, buttons=settings_buttons_inline(result='message'))

    elif 'message' in str(cb_data):
        srv_settings['result']['code'] = 'message'
        srv_settings['result']['desc'] = 'message'
        srv_settings['update'] = True
        update_msg = settings_msg(srv_settings)
        # logger.info('query cb update_msg: ' + update_msg)
        await event.edit(update_msg, buttons=settings_buttons_inline(result='file'))
    logger.info('query cb settings after: ' + str(srv_settings))


@bot.on(events.Raw)
async def handler(update):
    # Print all incoming updates
    # logger.info('update.stringify: ' + update.stringify())
    pass


def main():
    """
    Start the bot
    """
    bot.run_until_disconnected()


if __name__ == "__main__":
    main()
