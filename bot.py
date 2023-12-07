import disnake, os, sqlite3
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect('top speedruns.db') # Подключаемся к базе данных (Если файла нету, он создаться сам)
cursor = conn.cursor() # Создаём курсор (С помощью него мы можем управлять таблицей)
TOKEN = os.getenv('DISCORD_TOKEN')

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

@bot.event
async def on_ready():
    # Создаём таблицу если его не существует, в скобках столбики (имя ТИП, имя ТИП)
    # Типы: TEXT, INTEGER, REAL, BLOB, ANY, NUMERIC  (Сам использовал только TEXT и INTEGER, про остальные не знаю)
    cursor.execute('''CREATE TABLE IF NOT EXISTS speedruns
    (
        lvl INTEGER, 
        top1 TEXT,
        top2 TEXT,
        top3 TEXT,
        top4 TEXT,
        top5 TEXT,
        top6 TEXT,
        top7 TEXT,
        top8 TEXT,
        top9 TEXT,
        top10 TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS run (cur INTEGER)''') # Создал новую таблицу что бы сохранять одно значение 0_0
    # В одном .db файле можно хранить хоть сколько таблиц
    # Вписывать столбики можно в строчку и столбиком, но обязательно через запятую

    if cursor.execute('SELECT cur FROM run').fetchone() is None: # Выбираю один элемент (.fetchone()) из столбика "cur" таблицы "run" и проверяю пустой ли он
        cursor.execute('INSERT INTO run (cur) VALUES (?)', ('3')) # Добавляю НОВУЮ СТРОЧКУ в таблицу "run", "(cur, ...)" столбики в которые я введу значения
    for i in range(6):
        if cursor.execute(f'SELECT top1 FROM speedruns WHERE lvl = {i}').fetchone() is None: # Почти тоже самое что и в 36 строчке, но ищу элемент тех строчек у которых lvl = i
        # В строчке 36 не использую WHERE так как в таблице "run" всего один элемент
            null_pl = '{"id": 0, "PlayerID": 0, "Name":"None", "Time": 5999.9999}'
            cursor.execute('INSERT INTO speedruns (lvl, top1, top2, top3, top4, top5, top6, top7, top8, top9, top10) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (f'{i}', null_pl, null_pl, null_pl, null_pl, null_pl, null_pl, null_pl, null_pl, null_pl, null_pl))
    conn.commit() # После всех изменений сохраняем их, если это не сделать, то он сохранит только в временный файл,
    # и тогда при выборе элемента, он выберет не изменённый элемент
    print("Бот запущен!")

for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

# Остальной код в папке cogs

bot.run(TOKEN)