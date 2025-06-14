from dotenv import load_dotenv
import asyncio
import os
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, CommandStart
from db import add_order, get_rate
from logging_config import logger
from test_file import generate
import tempfile
import io
import docx
import fitz  # PyMuPDF
import models
from config_beforeOS import conn


router = Router()
photo_ids = []
# load_dotenv()

import kb
import text

# Определяем машину состояний для генерации
class GenerateProcess(StatesGroup):
    waiting_file = State()
    waiting_answer = State()
    

@router.message(CommandStart())
async def start_handler(msg: Message):
    user_id = msg.from_user.id
    user = models.User(user_id)
    await user.start(conn)
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.buttons_menu)

# надо вызвать после выбора языка
# @router.message(Command('start_2'))
# async def start_handler(msg: Message):
#     await msg.answer(text.greet_1.format(name=msg.from_user.full_name), reply_markup=kb.menu4444)

@router.message(Command('menu'))
@router.message(F.text == "Menu")
async def copy_link(msg: Message):
    await msg.reply("You are in the main menu", reply_markup=kb.buttons_menu)

@router.message(Command('add_services'))
@router.message(F.text == "Add services")
async def instruction(msg: Message):
    await msg.answer(text.service_text, reply_markup=kb.services_menu)


@router.message(Command('generate'))
@router.message(F.text == "Generate")
async def instruction(msg: Message, state: FSMContext):
    await msg.answer(text.generate_text, reply_markup=kb.buttons_menu)
    await state.set_state(GenerateProcess.waiting_file)


@router.message(GenerateProcess.waiting_file)
async def process1_generate(msg: Message, state: FSMContext):
    text_input = None

    # Если это обычное текстовое сообщение
    if msg.text:
        text_input = msg.text


    # Если это документ (например, .txt, .docx, .pdf)
    elif msg.document:
        file = await msg.bot.get_file(msg.document.file_id)
        file_path = file.file_path
        file_data = await msg.bot.download_file(file_path)

        try:
            text_input = await file_to_text(msg.bot, msg.document.file_id)
        except Exception as e:
            await msg.answer(
                "Не удалось обработать документ. Убедитесь, что формат поддерживается и файл не повреждён.")
            logger.error(f"Ошибка обработки файла: {e}")
            return


    # Если это изображение, предполагаем что нужно OCR (опционально)
    elif msg.photo:
        await msg.answer("Изображения пока не поддерживаются. Отправьте текст или документ.")
        return

    # Если не удалось извлечь текст
    if not text_input:
        await msg.answer("Не удалось определить тип сообщения. Пожалуйста, отправьте текст или документ.")
        return

    # Подаем текст в функцию
    try:
        await msg.answer("Please wait, the meeting protocol is being generated!")
        # txt, time = asyncio.run(generate(text_input))
        txt, time = await generate(text_input)
        txt = str(txt).replace(r'\n', '\n').replace('```', '')
        time = str(txt).replace(r'\n', '\n').replace('```', '')
        logger.info(f"Результат генерации: {txt}, {time} ({type(txt)})")
        await msg.answer(str(txt), reply_markup=kb.buttons_menu)
        await state.clear()
    except ValueError as e:
        await msg.answer("Ошибка при обработке текста. Убедитесь, что вы отправили корректную информацию.")
        logger.error(f"Error ValueError: {e}")


# Функция парсинга DOCX из файла
def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

# Функция парсинга PDF из файла
def extract_text_from_pdf(file_path: str) -> str:
    text = []
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text.append(page.get_text())
    return '\n'.join(text)


async def file_to_text(bot: Bot, file_id: str) -> str:
    """
    Конвертирует файл в текст (PDF, DOCX, TXT)
    """
    file = await bot.get_file(file_id)
    ext = os.path.splitext(file.file_path)[1].lower()

    if ext not in ('.pdf', '.docx', '.txt'):
        raise ValueError("Неподдерживаемый формат файла")

    # Временный путь
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, os.path.basename(file.file_path))

    # Скачиваем файл
    await bot.download_file(file.file_path, tmp_path)

    try:
        if ext == '.pdf':
            return extract_text_from_pdf(tmp_path)
        elif ext == '.docx':
            return extract_text_from_docx(tmp_path)
        else:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                return f.read()
    finally:
        os.remove(tmp_path)

