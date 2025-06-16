import datetime
import json
from yandex_neural_api.client import YandexNeuralAPIClient
from dotenv import load_dotenv
import os
load_dotenv()

token = os.getenv('TOKEN')
folder = os.getenv('FOLDER')
client = YandexNeuralAPIClient(token, folder)


async def generate(txt: str, time=datetime.datetime.now()) -> tuple:
    is_diolog = int(await client.generate_text_async(
        f"""Определи - является ли следующий текст(выделенный <>) диалогом <{txt}>, если является, то верни 1, иначе - 0."""
    ))

    if is_diolog:
        # Суммаризация
        gen_txt = await client.generate_text_async(f'''
        Дан следующий текст: "{txt}".
        Твоя задача: По смыслу определить обсуждаемые в нем темы и вопросы,
        Придумать заголовки для всех обсуждаемых тем и вопросов, 
        и в качестве ответа вернуть красткий пересказ диалога в формате:
        1.Заголовок обсуждения(важно - он не должен содержать слова "Тема","Заголовок" и т.п.) - просто напиши заголовок и все. 2.Краткий персказ обсуждения этой темы, без потери смысла.
        3.Итог обсуждения, (если прийти к конкретному итогу не удалось - то напиши, из-за чего)
        Повтори 1, 2 и 3-тий пункт для каждой найденой темы. После напиши краткий итог диалога(если прийти к конкретному итогу не удалось - то напиши, из-за чего).(Важно, что если текст - не на русском языке, то ответ так же должен быть на английском, слов на русском быть не должно)
        ''')

        # Даты
        gen_date = await client.generate_text_async(f'''
        Если в тексте: "{txt}" обсуждались какие-либо даты (назывались конкретные числа в которые должны произойти те, или иные события(возможно без информации о месяце или годе происходящего)), то напиши их в формате JSON файла
        со следующими полями: {{"all_dates" :[{{"name": "", "date": "", "assignee": "","description": ""}}, ...]}}. В поле name 
        должно содержаться название мероприятия планируемого в эту дату(если оно не называлось прямо - придумай такое, которое максимально точно описывает обсуждаемое событие)
        а в поле 'date' - дата в формате YYYY-MM-DD(без каких либо слов, или специальных символов - так как выглядят данные формата date-time в json) (если год или месяц не обсуждались, то брать из {time.date()}). Если для одного и того же события выбирались разные даты, то добавь в json запись для каждого варианта.
        В поле 'assignee' должен быть указан ответственный за выполнение данной задачи(тот, кто должен будет её выполнить, или сказал, что её выполнит) субъект(им может быть как и конкретный человек, так и названая организация), если ответственные лица не назывались, в поле assignee верни пустую строку.
        В поле 'description' - должно быть краткое описание поставленой задачи - то что необходимо выполнить, 
        Важно, что бы в кажом объекте возврощаемого JSON-а присутствовали все описаные поля(даже какие то из них будут пустые)
        (Важно, что если большая часть слов в тексте - не на русском языке, то названия всех событий должны быть на английском языке, на русском слов быть не должно, иначе - все названия должны быть на русском) 
        Иначе, если даты в тексте не обсуждались - верни {{"all_dates" :[]}}
        ''')

    else:
        gen_txt = 'Извините, из приведенных данных нельзя вынести ничего полезного:('
        gen_date = '{"all_dates": []}'

    # Парсинг JSON
    try:
        dates_json = json.loads(gen_date)
        if not isinstance(dates_json, dict) or "all_dates" not in dates_json:
            dates_json = {"all_dates": []}
    except Exception:
        dates_json = {"all_dates": []}

    # Финальная сборка
    return (
        gen_txt.strip().replace(r'\n', '\n').replace('*', ''),
        gen_date.strip().replace(r'\n', '\n').replace('*', '').replace('```', '')
    )


# MCP-compatible tool call
async def handle_tool_call_async(tool_call_json: str) -> str:
    tool_call_json.replace('```', '').replace('*', '')
    try:
        tool_call = json.loads(tool_call_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Некорректный JSON"}, ensure_ascii=False)

    tool_name = tool_call.get("tool_call")
    args = tool_call.get("arguments", {})
    transcript = args.get("transcript", "")

    if not transcript.strip():
        return json.dumps({"error": "Поле 'transcript' отсутствует или пустое"}, ensure_ascii=False)

    if tool_name in ("summarize_meeting", "extract_tasks"):
        try:
            summary_text, dates_json_str = await generate(transcript)
            dates_json = json.loads(dates_json_str)
        except Exception as e:
            return json.dumps({"error": f"Ошибка при обработке: {str(e)}"}, ensure_ascii=False)

        return json.dumps({
            "summary": summary_text,
            "dates": dates_json
        }, ensure_ascii=False)

    return json.dumps({"error": f"Неизвестный инструмент: {tool_name}"}, ensure_ascii=False)
