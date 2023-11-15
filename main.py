import wikipedia
import datetime
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import python_weather
import requests
from requests import HTTPError
import random

# Настройки бота
answer_locale = "ru"                                                    # Язык ответов Wikipedia и Forecast
bot_version = "1.1"                                                     # Версия бота
api_id = 00000000                                                       # Ключ Telegram API
api_hash = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"                           # Хэш Telegram API
app = Client("my_account", api_id=api_id, api_hash=api_hash)

wikipedia.set_lang(answer_locale)

@app.on_message(filters.command("catgif", "m."))
async def send_random_cat_gif(client, message):
    url = "https://lolhie3.github.io/catgifdb/catgifdb.gfyset"
    response = requests.get(url)
    if response.status_code == 200:
        gifs = response.text.split('\n')
        random_gif = random.choice(gifs)
        await message.reply_animation(random_gif)
    else:
        await message.reply('❌ БД недоступна.')

@app.on_message(filters.command("typewriter", "m.") & filters.me)
async def animtext_command(_, message):
    input_text = message.text.split("m.typewriter ", maxsplit=1)[1]
    temp_text = input_text
    edited_text = ""
    typing_symbol = "_"

    while edited_text != input_text:
        try:
            await message.edit(edited_text + typing_symbol)
            time.sleep(0.1)
            edited_text = edited_text + temp_text[0]
            temp_text = temp_text[1:]
            await message.edit(edited_text)
            time.sleep(0.1)
        except FloodWait:
            print("Flood overflow! Wait...")

autoscr = filters.chat([])


@app.on_message(autoscr)
def auto_read(_, message: Message):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    app.read_chat_history(message.chat.id)
    print(f"[{current_time}] Прочитано сообщение в {message.chat.id}")
    message.continue_propagation()


@app.on_message(filters.command("autoscroll", "m.") & filters.me)
def add_keep(_, message: Message):
    if message.chat.id in autoscr:
        autoscr.remove(message.chat.id)
        message.edit("✅ **Авточтение выключено.**")
    else:
        autoscr.add(message.chat.id)
        message.edit("✅ **Авточтение включено.**")

@app.on_message(filters.command("eval", "m."))
def eval_command(client, message):
    command = message.text.split(" ", 1)[1]
    if command.startswith(("exit", "dir", "import", "def", "message", "delete", "remove", "erase", "os")):
        message.reply("❌ Некорректное выражение/код!")
    else:
        try:
            result = eval(command)
            message.reply(f"{command} = {result}")
        except Exception as e:
            message.reply(f"❌ Произошла ошибка: {str(e)}")

@app.on_message(filters.command("wiki", "m."))
def search_command(client, message):
    query = message.text.split(' ', 1)[1]
    page_py = wikipedia.page(title=query)
    response = "**Найдено (Wikipedia):**\n\n" + page_py.content[:1024]
    message.reply(response)

@app.on_message(filters.command("forecast", "m."))
async def forecast_command(client, message):
    query = message.text.split(' ', 1)[1]
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    if query:
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await client.get(query, locale=answer_locale)
            await message.reply(f"Погодная сводка для **{query}** на момент **{current_time} (UTC+4)** \n\n🌡️ Температура: {weather.current.temperature}°C\n🥶️ Ощущается: {weather.current.feels_like}°C\n🌧 Влажность: {weather.current.humidity}%\n💨 Ветер: {weather.current.wind_speed} км/ч\n👀 Видимость: {weather.current.visibility} км")
            for forecast in weather.forecasts:
                print(forecast)
                for hourly in forecast.hourly:
                    print(f' --> {hourly!r}')
    else:
        message.reply("Использование: m.forecast <город>")

@app.on_message(filters.command("help", "m."))
def help_command(client, message):
    start_time = time.time()
    message.delete()
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 1)
    message.reply(f"🤖 **MimeBot версии {bot_version}**\n\nКоманды для всех:\n`m.wiki <название>` - поиск статьи на Википедии\n`m.eval <выражение>` - выражения и выполнение кода\n`m.forecast <город>` - показать погоду\n`m.catgif` - гифка с котиком (не работает в большинстве случаев)\n\nКоманды для юзера:\n`m.typewriter <текст>` - анимировать текст\n`m.autoscroll` - вкл/выкл авточтение чатов (сбрасывается при выходе)\n\n**Пинг: {ping_time} ms**")

app.run()
