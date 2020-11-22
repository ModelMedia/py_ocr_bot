import os
import requests
import log_srv

from dotenv import load_dotenv

load_dotenv()

logger = log_srv.get_logger(__name__)
OCR_API = os.getenv('OCR_API')

url_api = 'https://api.ocr.space/parse/image'


def ocr_space_file(filename, overlay=False, language='eng', ocrengine=1):
    """ OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :param ocrengine: OCR API offers two different
                    OCR engine: 1 or 2.
                    Defaults to 1.
    :return: Result in JSON format.
    """

    payload = {'isOverlayRequired': overlay,
               'apikey': OCR_API,
               'language': language,
               'OCREngine': ocrengine,
               }

    """
    payload = {'isOverlayRequired': overlay,
               'language': language,
               'OCREngine': ocrengine,
               }
    files = [
            ('file',('ru1.png', open('E:/temp/ru1.png', 'rb'),'image/png'))
            ]
    headers = {
              'apikey': OCR_API
            }
    """
    try:
        with open(filename, 'rb') as f:
            r = requests.post('https://api.ocr.space/parse/image', files={filename: f}, data=payload,)
        # r = requests.request("POST", url_api, headers=headers, data=payload, files=files)
        logger.info('filename: ' + filename)
        logger.info('response.status_code: ' + str(r.status_code))
        r.raise_for_status()
    except requests.exceptions.HTTPError as res_HTTPError:
        #print('res_HTTPError: ' + str(res_HTTPError))
        logger.warning('res_HTTPError: ' + str(res_HTTPError))
    except requests.exceptions.ConnectionError as res_ConnectionError:
        logger.warning('res_ConnectionError: ' + str(res_ConnectionError))
    finally:
        return r.content.decode()


def ocr_space_url(url, overlay=False,  language='eng', ocrengine=1):
    """ OCR.space API request with remote file.
        Python3.5 - not tested on 2.7
    :param url: Image url.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :param ocrengine: OCR API offers two different
                    OCR engine: 1 or 2.
                    Defaults to 1.
    :return: Result in JSON format.
    """

    payload = {'url': url,
               'isOverlayRequired': overlay,
               'apikey': OCR_API,
               'language': language,
               'OCREngine': ocrengine,
               }
    r = requests.post(url_api, data=payload)
    return r.content.decode()


if __name__ == "__main__":
    # print(ocr_space_file(filename='E:/temp/ru1.png', language='rus'))
    print(ocr_space_url(url='http://dl.a9t9.com/ocrbenchmark/eng.png'))