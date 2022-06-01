# wordle_tg_bot

## Возможности

- `/start`: запуск и перезапуск бота
- `/help`: помощь по командам
- `/weather`: погода в Брянске
- `/file <имя_файла>`: получить файл, отправленный заранее
- `/dev`: информация о разработчике
- `/cat`: случайные фото кошек из Интернета
- `/dog`: случайные фото собак из Интернета
- `/yes_or_no`: получить ответ да/нет с GIF-анимацией
- `/wordle`: игра Wordle

## Запуск бота

1. Установить Python: [ссылка для скачивания](https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe)
2. Перейти в папку с проектом в консоли с помощью `cd`
3. Установить зависимости: `python -m pip install -r requirements.txt`
4. Запустить бота: `python app.py`

## Дерево файлов

- [`📂 files`](files/) — каталог для сохранения файлов
  - [`helloworld.txt`](files/helloworld.txt) — первый тестовый файл
  - [`test.txt`](files/test.txt) — второй тестовый файл
- [`📂 game`](game/) — пакет для работы с игрой wordle
  - [`📂 assets`](game/assets/) — пакет для работы с игрой wordle
    - [`contains.png`](game/assets/contains.png) — блок для буквы, содержащейся в слове
    - [`correct.png`](game/assets/correct.png) — блок для буквы, содержащейся в слове на нужном месте
    - [`font.ttf`](game/assets/font.ttf) — шрифт Circe, начертание ExtraBold
    - [`full_correct.png`](game/assets/full_correct.png) — рамка для угаданного слова
    - [`game.png`](game/assets/game.png) — игровое поле
    - [`words.txt`](game/assets/words.txt) — база слов
    - [`wrong.png`](game/assets/wrong.png) — блок для буквы, не содержащейся в слове
  - [`init.py`](game/__init__.py) — файл инициализации пакета для внешнего доступа к функциям
  - [`manager.py`](game/manager.py) — основной файл менеджера отрисовки игрового поля
  - [`models.py`](game/models.py) — вспомогательный файл с представлениями моделей для игры
- [`app.py`](app.py) — главный файл бота со всей логикой
- [`requirements.txt`](requirements.txt) — файл с зависимостями для установки
