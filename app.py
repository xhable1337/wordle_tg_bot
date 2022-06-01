import asyncio
from datetime import datetime
import logging
from random import choice
import requests
from string import ascii_letters

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup

from game import WordleManager

# Токен из @BotFather
token = '5393671799:AAHegR2MM6TQTk8N5ck6pd9PdDIuTFDHvrs'

# Создание объекта бота
bot = Bot(token=token, parse_mode='HTML')

# Создание диспетчера для взаимодействия с запросами от Telegram
dp = Dispatcher(bot, storage=MemoryStorage())

# Создание логгера для вывода системных сообщений в консоль
logger = logging.getLogger('@main')

# Глобальная переменная для хранения общего слова дня
correct_word = "empty"

# Список админов
admins = [
    124361528
]


class UserState(StatesGroup):
    """Класс для работы с состояниями пользователей."""
    first_name = State()
    last_name = State()
    age = State()

    word_input = State()


async def set_commands(bot: Bot):
    # Создаём список команд
    commands: list[BotCommand] = [
        BotCommand("start", "Перезапуск бота"),
        BotCommand("help", "Помощь"),
        BotCommand("weather", "Погода в Брянске"),
        BotCommand("file", "Получить файл (/file имя_файла)"),
        BotCommand("dev", "Информация о разработчике"),
        BotCommand("cat", "Случайный котик из Интернета"),
        BotCommand("dog", "Случайный пёсик из Интернета"),
        BotCommand("yes_or_no", "Получить ответ да/нет"),
        BotCommand("wordle", "Открыть игру"),
    ]

    # Устанавливаем список команд
    await bot.set_my_commands(commands)


@dp.message_handler(commands=['cancel'], state='*')
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено.")


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    # Формируем текст и оставляем место для имени в приветствии
    text = (
        "👋 Привет, {}!\n"
        "Мои возможности перечислены в кнопке меню слева от поля чата. "
        "Также можно воспользоваться командой /help."
    )

    # Получаем данные из состояния
    data = await state.get_data()

    # Если пользователь не указывал данные, запрашиваем их
    if (data.get('first_name', ""), data.get('last_name', "")) == ("", ""):
        # Устанавливаем для приветствия данные из Telegram
        name = message.from_user.full_name

        # Добавляем приглашение познакомиться
        text += f"\n\nДавай познакомимся! Как тебя зовут? "
        text += "(если не хочешь делиться информацией: /cancel)"

        # Устанавливаем состояние ожидания имени от пользователя
        await UserState.first_name.set()
    # Если данные уже есть, поприветствуем пользователя по имени и фамилии
    else:
        name = ' '.join(
            [data.get('first_name'), data.get('last_name')]
        )

    await message.answer(text.format(name))


@dp.message_handler(state=UserState.first_name)
async def got_first_name(message: types.Message, state: FSMContext):
    # Получаем имя из сообщения и пишем её с заглавной буквы
    first_name = message.text.capitalize()

    # Добавляем имя к состоянию
    await state.update_data({'first_name': first_name})

    # Запрашиваем фамилию пользователя
    await message.answer(
        f"Хорошо, {first_name}, а поделишься своей фамилией?"
        "\n\nОтмена: /cancel"
    )

    # Переключаем состояние
    await UserState.next()


@dp.message_handler(state=UserState.last_name)
async def got_last_name(message: types.Message, state: FSMContext):
    # Получаем данные о состоянии пользователя
    data = await state.get_data()

    # Получаем имя из состояния
    first_name = data.get('first_name')

    # Получаем фамилию из сообщения и пишем её с заглавной буквы
    last_name = message.text.capitalize()

    # Добавляем фамилию к состоянию
    await state.update_data({'last_name': last_name})

    # Запрашиваем возраст пользователя
    await message.answer(
        f"{first_name} {last_name}. Как хорошо звучит! Сколько тебе лет?"
        "\n\nОтмена: /cancel"
    )

    # Переключаем состояние
    await UserState.next()


@dp.message_handler(state=UserState.age)
async def got_age(message: types.Message, state: FSMContext):
    # Если возраст не является числом, не принимаем его
    if not message.text.isdigit():
        return await message.answer(
            "Не думаю, что отправленный тобой текст — твой возраст. Попробуй ещё раз."
            "\n\nОтмена: /cancel"
        )

    # Получаем возраст из сообщения и приводим к целочисленному типу
    age = int(message.text)

    # Если возраст слишком маленький или большой, не принимаем его
    if not 12 <= age <= 99:
        return await message.answer(
            "Полагаю, ты указал неверный возраст. Попробуй ещё раз."
            "\n\nОтмена: /cancel"
        )

    # Получаем данные о состоянии пользователя
    data = await state.get_data()

    # Получаем имя и фамилию из состояния
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    # Добавляем возраст к состоянию
    await state.update_data({'age': age})

    # Выбор правильного варианта (год/года/лет)
    if str(age)[-1] == '1':
        age_text = 'год'
    elif str(age)[-1] in '234':
        age_text = 'года'
    else:
        age_text = 'лет'

    # Отвечаем на сообщение
    await message.answer(
        f"Вот, что я о тебе узнал:\n\n"

        f"<b>Имя:</b> {first_name}\n"
        f"<b>Фамилия:</b> {last_name}\n"
        f"<b>Возраст:</b> {age} {age_text}\n\n"

        f"Теперь ты можешь пользоваться всеми функциями.\n"
        f"Напоминаю: их можно найти в кнопке «Меню» или по команде /help."
    )

    # Завершаем состояние сбора информации о пользователе
    await state.reset_state(with_data=False)


@dp.message_handler(commands=['help'], state='*')
async def help(message: types.Message):
    # Получаем список команд, представленных в боте
    commands = await bot.get_my_commands()

    # Формируем новый список команд вида «команда - описание»
    commands_list = [f"/{cmd.command} — {cmd.description}" for cmd in commands]

    # Создаём str, где каждая команда представлена с новой строки
    commands_text = '\n'.join(commands_list)

    # Формируем текст сообщения
    text = "<b><u>Мои команды:</u></b>\n\n" + commands_text
    text += "\n\nЕсли вы отправите мне файл, я надёжно его сохраню в своей папке и дам команду, чтобы снова его получить."

    await message.answer(text)


@dp.message_handler(Text(contains="погод", ignore_case=True))
@dp.message_handler(commands=['weather'], state='*')
async def weather(message: types.Message):
    # OpenWeatherMap API URL
    api_url = 'http://api.openweathermap.org/data/2.5/weather'

    # Параметры для запроса
    # id - город, appid - API токен
    params = {
        'id': 571476,
        'appid': 'e9c3a204b56b981c281dad540173c4c3',
        'lang': 'ru',
        'units': 'metric'
    }

    # Выполнение запроса и получение его в JSON
    response = requests.get(api_url, params).json()

    # ! Парсинг JSON
    # Получение описания погоды (ясно, облачно и т.п.)
    weather = str(response['weather'][0]['description'])

    # Получение температуры воздуха
    temp = int(response['main']['temp'])

    # Получение влажности воздуха
    humidity = response['main']['humidity']

    # Получение времени рассвета и заката из UNIX Timestamp
    sunrise = datetime.fromtimestamp(
        response['sys']['sunrise']).strftime('%H:%M')
    sunset = datetime.fromtimestamp(
        response['sys']['sunset']).strftime('%H:%M')

    # Формировка клавиатуры для самостоятельного просмотра погоды
    kb = Markup(row_width=1).add(
        Button(text='Gismeteo',
               url='https://www.gismeteo.ru/weather-bryansk-4258/'),
        Button(text='Яндекс.Погода',
               url='https://yandex.ru/pogoda/bryansk'),
        Button(text='Google Погода',
               url='https://www.google.com/search?q=Погода+в+Брянске')
    )

    # Формировка текста сообщения
    text = (
        f'☁️ <b>Текущая погода в Брянске:</b> <i>{weather}, {temp}°C</i>\n'
        f'💧 <b>Влажность:</b> <i>{humidity}%</i>\n'
        f'🌞 <b>Рассвет:</b> <code>{sunrise}</code>\n'
        f'🌝 <b>Закат:</b> <code>{sunset}</code>'
    )

    await message.answer(text, reply_markup=kb)


@dp.message_handler(commands=['file'], state='*')
async def file(message: types.Message):
    # Получаем аргументы
    args = message.get_args()

    # Если пользователь не указал файл, ответим ему информацией
    if args == '':
        return await message.answer(
            'ℹ <b>Использование команды:</b> <code>/file имя_файла</code>'
        )

    # Если пользователь указал больше одного файла, ответим ему информацией
    if len(args.split()) != 1:
        return await message.answer(
            'ℹ <b>Использование команды:</b> <code>/file имя_файла</code>'
        )

    # Если пользователь передал в команду имя одного файла, пробуем найти его
    try:
        with open(f'./files/{args}', 'rb') as file:
            # Отправляем найденный файл пользователю
            await message.answer_chat_action(types.ChatActions.UPLOAD_DOCUMENT)
            await message.answer_document(
                file,
                caption=f"✅ Вот запрошенный вами файл <code>{args}</code>."
            )
    except FileNotFoundError:
        # Если файл не найден (open() выдал ошибку), сообщим об этом
        return await message.answer(
            f'❌ <b>Запрошенный файл</b> <code>{args}</code> <b>не найден.</b>'
        )


@dp.message_handler(content_types=['document'], state='*')
async def upload_document(message: types.Message):
    name = message.document.file_name
    await message.document.download(destination_file=f'./files/{name}')
    await message.answer(
        'Файл успешно скачан в папку бота!\n'
        f'Для загрузки можно использовать команду <code>/file {name}</code>'
    )


@dp.message_handler(commands=['dev'], state='*')
async def dev(message: types.Message):
    # Создаём кнопку для перехода на страницу VK
    keyboard = Markup().add(Button('Страница VK', 'https://vk.com/kostia.erokhin'))
    await message.answer('👨‍💻')
    await message.answer(
        text="<b>Разработчик:</b> Ерохин Константин",
        reply_markup=keyboard)


@dp.message_handler(commands=['cat'], state='*')
async def cat(message: types.Message):
    # Уведомляем пользователя, что идёт загрузка фото
    await message.answer_chat_action(types.ChatActions.UPLOAD_PHOTO)

    # Получаем URL файла от API
    file_url: str = requests.get('https://aws.random.cat/meow').json()['file']

    # Отправляем файл с подписью
    await message.answer_photo(photo=file_url, caption="Смотри, какой красивый котик 😻")


@dp.message_handler(commands=['dog'], state='*')
async def dog(message: types.Message):
    # Получаем URL файла от API
    file_url: str = requests.get('https://random.dog/woof.json').json()['url']

    # Создаём подпись
    caption = "Взгляни на этого красивого пёсика 🐶"

    # Если полученный файл - гифка
    if file_url.lower().endswith('.gif'):
        # Уведомляем пользователя, что идёт загрузка видео
        await message.answer_chat_action(types.ChatActions.UPLOAD_VIDEO)

        # Отправляем файл
        await message.answer_animation(animation=file_url, caption=caption)

    # Если полученный файл - видео
    elif file_url.lower().endswith('.webm') or file_url.lower().endswith('.mp4'):
        # Уведомляем пользователя, что идёт загрузка видео
        await message.answer_chat_action(types.ChatActions.UPLOAD_VIDEO)

        # Отправляем файл
        await message.answer_video(video=file_url, caption=caption)

    # Если полученный файл - не видео или гифка, то есть фото
    else:
        # Уведомляем пользователя, что идёт загрузка фото
        await message.answer_chat_action(types.ChatActions.UPLOAD_PHOTO)

        # Отправляем файл
        await message.answer_photo(photo=file_url, caption=caption)


@dp.message_handler(commands=['yes_or_no'], state='*')
async def yes_or_no(message: types.Message):
    await message.answer_chat_action(types.ChatActions.UPLOAD_VIDEO)

    # Получаем response от API
    response = requests.get('https://yesno.wtf/api').json()

    # Получаем URL файла из response от API
    file_url: str = response['image']

    # Словарь для перевода ответа да/нет/возможно из response от API
    ru_answers = {
        'yes': 'да',
        'no': 'нет',
        'maybe': 'возможно'
    }

    # Получаем ответ на русском языке
    answer = ru_answers[response['answer']]

    # Отправляем гифку
    await message.answer_animation(animation=file_url, caption=f"Ответ: {answer}")


@dp.message_handler(commands=['wordle'], state='*')
async def wordle(message: types.Message, state: FSMContext):
    with WordleManager(correct_word) as manager:
        data = await state.get_data()
        words = data.get('words', [])

        manager.bulk_draw_words(words)

        text = (
            "== <u>Wordle</u> ==\n\n"
            f"⚖️ <b>Осталось попыток:</b> {6 - len(words)}\n"
            f"⌛ Ожидаю от тебя слово... Если уже не хочешь играть: /cancel"
        )

        await message.answer_photo(types.InputFile(manager.image_bytes), text)
        await UserState.word_input.set()


def until_next_word():
    now = datetime.today()
    tomorrow = datetime(now.year, now.month, now.day)
    d = tomorrow - now
    mm, ss = divmod(d.seconds, 60)
    hh, mm = divmod(mm, 60)

    delta = ":".join(map(str, [hh, mm, ss]))
    return delta


@dp.message_handler(state=UserState.word_input)
async def wordle_got_word(message: types.Message, state: FSMContext):
    text = ""

    if len(message.text) != 5 or not message.text.isalpha():
        return await message.answer("Слово должно состоять из 5 русских букв. Повтори попытку (или /cancel).")

    for letter in message.text:
        if letter in ascii_letters:
            return await message.answer("Слово должно состоять из 5 русских букв. Повтори попытку (или /cancel).")

    with WordleManager(correct_word) as manager:
        data = await state.get_data()
        words = data.get('words', [])
        words.append(message.text.lower())
        await state.update_data({'words': words})

        manager.bulk_draw_words(words)

        if manager.is_finished:
            await state.update_data({'wordle_available': False})

            delta = until_next_word()

            text = (
                "== <u>Wordle</u> ==\n\n"
                f"🏆 Ты успешно угадал слово {correct_word}!\n"
                f"ℹ️ Количество попыток: {len(words)} / 6\n"
                f"⏭️ Следующее слово будет доступно через {delta} (либо по админ-команде /new_word)."
            )
            await state.reset_state(with_data=False)
        else:
            if len(words) == 6:
                delta = until_next_word()
                text = (
                    "== <u>Wordle</u> ==\n\n"
                    f"📝 <b>Слово <u>{message.text}</u> принято. Взгляни на игровое поле.</b>\n\n"
                    f"⚖️ <b>Осталось попыток:</b> {6 - len(words)}\n"
                    f"🚫 К сожалению, ты не угадал слово {correct_word}.\n"
                    f"⏭️ Следующее слово будет доступно через {delta} (либо по админ-команде /new_word)."
                )
                await state.reset_state(with_data=False)
            else:
                text = (
                    "== <u>Wordle</u> ==\n\n"
                    f"📝 <b>Слово <u>{message.text}</u> принято. Взгляни на игровое поле.</b>\n\n"
                    f"⚖️ <b>Осталось попыток:</b> {6 - len(words)}\n"
                    f"⌛ Ожидаю от тебя слово... Если уже не хочешь играть: /cancel"
                )

        return await message.answer_photo(types.InputFile(manager.image_bytes), text)


@dp.message_handler(IDFilter(admins), commands=['new_word'], state='*')
async def new_word(message: types.Message, state: FSMContext):
    load_word()
    await message.answer(
        f"Новое слово сгенерировано. Вот оно: <tg-spoiler>{correct_word}</tg-spoiler>.\n"
        "Можете воспользоваться командой /wordle для игры.")
    logger.info(f'Новое слово: {correct_word}')


def load_word():
    with open('./game/assets/words.txt', 'r', encoding='UTF-8') as file:
        global correct_word
        words = file.read().splitlines()
        correct_word = choice(words)


async def main():
    # Запуск логирования
    logging.basicConfig(
        level=logging.INFO,
        datefmt='%d.%m.%Y | %H:%M:%S',
        format="[%(asctime)s] %(levelname)s: %(name)s - %(message)s",
    )

    # Вывод в консоль информации о запуске бота
    bot_obj = await bot.get_me()
    logger.info(f"Запуск бота {bot_obj.full_name} (@{bot_obj.username})...")

    # Установка команд
    await set_commands(bot)

    # Рандомный выбор слова дня
    load_word()
    logger.info(f'Слово дня: {correct_word}')

    # Пропуск апдейтов и запуск long-polling
    try:
        await dp.skip_updates()
        await dp.start_polling()
    # После завершения работы бота закрываем соединение с хранилищем FSM
    finally:
        logger.error('Terminating bot...')
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()
        logger.error('Goodbye!')


if __name__ == "__main__":
    asyncio.run(main())
