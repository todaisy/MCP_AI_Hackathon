from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# для версии с выбором языков
button_choose_ru = KeyboardButton(text='Русский', callback_data="ru_btn")
button_choose_en = KeyboardButton(text='English', callback_data="en_btn")
buttons_lang = [[button_choose_ru, button_choose_en]]
menu_lang = ReplyKeyboardMarkup(keyboard=buttons_lang, resize_keyboard=True)

# кнопка в главное меню
main_menu = KeyboardButton(text='Menu', callback_data="menu_btn")

# меню выбора подключения сервисов и начала генерации протокола встречи
btn_services = KeyboardButton(text='Add services', callback_data="serv_btn")
btn_start = KeyboardButton(text='Generate', callback_data="start_btn")
buttons = [[btn_services, btn_start]]
buttons_menu = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# меню подключения сервисов для вывода
btn_calendar = KeyboardButton(text='Add calendar', callback_data="calendar_btn")
btn_docs = KeyboardButton(text='Add docs', callback_data="docs_btn")
btn_sheets = KeyboardButton(text='Add sheets', callback_data="sheets_btn")
add_services = [[btn_calendar, btn_docs], [main_menu]]
services_menu = ReplyKeyboardMarkup(keyboard=add_services, resize_keyboard=True)
