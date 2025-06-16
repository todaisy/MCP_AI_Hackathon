import logging  # библиотека для сохранения логов ошибок в файл
from dotenv import load_dotenv
import os
load_dotenv()


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.getenv('LOG_FILE')),
            logging.StreamHandler()
        ]
    )


logger = logging.getLogger(__name__)
