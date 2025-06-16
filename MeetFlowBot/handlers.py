from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile
from dotenv import load_dotenv

import kb
import models
import text
from config_beforeOS import conn
from logging_config import logger
from neiro import handle_tool_call_async
from functions import get_dates, file_to_text, text_to_docx, text_to_pdf
import datetime
import json

router = Router()
load_dotenv()


# Определяем машину состояний для генерации
class GenerateProcess(StatesGroup):
    waiting_file = State()
    waiting_answer = State()
    generated_text = State()


@router.message(CommandStart())
async def start_handler(msg: Message):
    user_id = msg.from_user.id
    user = models.User(user_id)
    await user.start(conn)
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.buttons_menu)

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
async def process_generate(msg: Message, state: FSMContext):
    text_input = None
    time_input = datetime.datetime.now()

    # Если это обычное текстовое сообщение
    if msg.text:
        text_input = msg.text

    # Если это документ (например, .txt, .docx, .pdf)
    elif msg.document:
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

    msd_input_id = msg.message_id
    # Подаем текст в функцию
    try:
        await msg.answer("Пожалуйста, ожидайте, протокол встречи формируется!")
        text_input = str(text_input).replace(r'\n', r'\\n')
        data = {
            "tool_call": "summarize_meeting",
            "arguments": {
                "transcript": text_input
            }
        }

        json_string = json.dumps(data, ensure_ascii=False)
        result = await handle_tool_call_async(json_string)
        result_data = json.loads(result)
        txt = result_data['summary']
        dates_list = result_data['dates']['all_dates']
        logger.info(f"Результат генерации: {txt}, {dates_list} ({type(txt)})")
        await msg.answer(txt, reply_markup=kb.buttons_menu)
        text_time = get_dates(dates_list)
        if text_time:
            await msg.answer(text_time, reply_markup=kb.buttons_menu)

        user_id = msg.from_user.id
        user = models.Handlers(user_id=user_id, id_mess_input=msd_input_id, time_input=time_input, id_mess_output=msd_input_id+2)
        await user.do_request(conn)

        await msg.answer("Хотите получить сгенерированный протокол в другом формате?", reply_markup=kb.format_menu)
        if text_time:
            await state.update_data(generated_text=txt + '\n\n\nОбсуждаемые даты:\n' + text_time)
        else:
            await state.update_data(generated_text=txt)
    except ValueError as e:
        await msg.answer("Ошибка при обработке текста. Убедитесь, что вы отправили корректную информацию.")
        logger.error(f"Error ValueError: {e}")



@router.callback_query(F.data.in_(['format_word', 'format_pdf', 'format_no']))
async def process_format_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("generated_text")

    if not text:
        await callback.message.answer("Текст для экспорта не найден. Пожалуйста, начните сначала.")
        await state.clear()
        await callback.answer()
        return

    if callback.data == 'format_word':
        try:
            path = text_to_docx(text)
            file = FSInputFile(path)
            await callback.message.answer_document(file, caption="Вот ваш протокол в формате Word")
        except Exception as e:
            logger.error(f"Ошибка при создании DOCX: {e}")
            await callback.message.answer("Ошибка при создании Word-файла.")
    elif callback.data == 'format_pdf':
        try:
            path = text_to_pdf(text)
            file = FSInputFile(path)
            await callback.message.answer_document(file, caption="Вот ваш протокол в формате PDF")
        except Exception as e:
            logger.error(f"Ошибка при создании PDF: {e}")
            await callback.message.answer("Ошибка при создании PDF-файла.")
    elif callback.data == 'format_no':
        await callback.message.answer("Окей, завершаем обработку.", reply_markup=kb.buttons_menu)

    await state.clear()
    await callback.answer()
