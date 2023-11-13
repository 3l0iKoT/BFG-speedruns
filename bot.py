import disnake, os, sqlite3
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect('top speedruns.db')
cursor = conn.cursor()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

@bot.event
async def on_ready():
    cursor.execute('''CREATE TABLE IF NOT EXISTS speedruns (lvl INTEGER, top1 TEXT, top2 TEXT, top3 TEXT, top4 TEXT, top5 TEXT, top6 TEXT, top7 TEXT, top8 TEXT, top9 TEXT, top10 TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS run (cur INTEGER)''')
    if cursor.execute('SELECT cur FROM run').fetchone() is None:
        cursor.execute('INSERT INTO run (cur) VALUES (?)', ('3'))
    for i in range(6):
        if cursor.execute(f'SELECT top1 FROM speedruns WHERE lvl = {i}').fetchone() is None:
            null_pl = '{"id": 0, "PlayerID": 0, "Name":"None", "Time": 5999.9999}'
            cursor.execute('INSERT INTO speedruns (lvl, top1, top2, top3, top4, top5, top6, top7, top8, top9, top10) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (f'{i}', null_pl, null_pl, null_pl, null_pl, null_pl, null_pl, null_pl, null_pl, null_pl, null_pl))
    conn.commit()
    print("Бот запущен!")

for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

bot.run(TOKEN)