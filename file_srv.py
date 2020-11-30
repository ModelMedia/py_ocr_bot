import os
import log_srv

logger = log_srv.get_logger(__name__)


def str_to_file(ocr_value):
    """
    open new file,
    write the ocr result to it
    and return it
    """
    logger.info('str_to_file')

    try:
        with open('ocr_result/ocr_text.txt', 'tw', encoding='utf-8') as f:
            f.write(ocr_value)

        if os.path.isfile('ocr_result/ocr_text.txt'):
            logger.info('ocr result file exist: ocr_result/ocr_text.txt')

        return 'ocr_result/ocr_text.txt'

    except Exception as file_exception:
        logger.warning(file_exception)


