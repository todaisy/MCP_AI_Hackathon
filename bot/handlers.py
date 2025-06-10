from dotenv import load_dotenv
import os
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, CommandStart
from db import add_order, get_rate
from logging_config import logger
# from config import ADMIN_ID


router = Router()
photo_ids = []
# load_dotenv()

import kb
import text


@router.message(CommandStart())
async def start_handler(msg: Message):
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
async def instruction(msg: Message):
    await msg.answer(text.generate_text, reply_markup=kb.buttons_menu)


