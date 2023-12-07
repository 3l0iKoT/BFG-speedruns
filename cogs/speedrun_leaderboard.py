import disnake, os, requests, json, sqlite3, asyncio
from disnake.ext import commands
from disnake.ui import Select, View
from disnake import Embed
from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect('top speedruns.db')
cursor = conn.cursor()

url = os.getenv('SPEEDRUN_URL')

async def TopDescriptionEmbed(lvl):
    # Вернёт массив из следующих столбиков [top1, top2, top3, top4, top5, top6, top7, top8, top9, top10]
    tops = cursor.execute(f'SELECT top1, top2, top3, top4, top5, top6, top7, top8, top9, top10 FROM speedruns WHERE lvl = {lvl}').fetchone()
    description = ''
    for i in range(10):
        time = str(json.loads(tops[i])['Time']).split(".")
        ms = time[1] + '0' * (4 - len(time[1]))
        s = '0' * (len(str(int(time[0]) % 60)) == 1) + str(int(time[0]) % 60)
        m = '0' * (len(str(int(time[0]) // 60)) == 1) + str(int(time[0]) // 60)
        description += f"{i+1}) **__{m}:{s}:{ms}__** {json.loads(tops[i])['Name']} ||{json.loads(tops[i])['PlayerID']}||\n"
    embed = Embed(
        title = f'Топ спидранеров на Level {lvl}',
        description = description,
        color = disnake.Colour.random()
    )
    return embed

async def AllTopDescriptionEmbed():
    embed = Embed(title='Топ спидранеров', color=disnake.Colour.random())
    for i in range(6):
        tops = cursor.execute(f'SELECT top1, top2, top3 FROM speedruns WHERE lvl = {i}').fetchone()
        times = ["00:00:0", "00:00:0", "00:00:0"]
        for j in range(3):
            time = str(json.loads(tops[j])['Time']).split(".")
            ms = time[1] + '0' * (4 - len(time[1]))
            s = '0' * (len(str(int(time[0]) % 60)) == 1) + str(int(time[0]) % 60)
            m = '0' * (len(str(int(time[0]) // 60)) == 1) + str(int(time[0]) // 60)
            times[j] = f"{m}:{s}:{ms}"
        embed.add_field(
            name=f"**Level {i}**",
            value=f"{json.loads(tops[0])['Name']}\n:first_place:**__{times[0]}__**\n{json.loads(tops[1])['Name']}\n:second_place:**__{times[1]}__**\n{json.loads(tops[2])['Name']}\n:third_place:**__{times[2]}__**",
            inline=True
        )
    return embed

async def LoadingData(ctx):
    last_run = cursor.execute('SELECT cur FROM run').fetchone()[0]
    response_data = requests.post(url, data={"SpeedrunID":f"{last_run}"}).text
    if (response_data == ""):
        await ctx.send("Новых забегов не обнаружено")
        return
    while (response_data != ""):
        data = json.loads(response_data)
        for i in range(len(data)):
            load_pl = data[i]
            load_plstr = str(load_pl).replace("'", '"', -1)
            can_sort = True
            first_pos = 10
            second_pos = 10
            for j in range(10):
                save_pl = json.loads(cursor.execute(f'SELECT top{j + 1} FROM speedruns WHERE lvl = {last_run % 6}').fetchone()[0])
                if (load_pl['PlayerID'] == save_pl['PlayerID']) and (load_pl['Time'] >= save_pl['Time']):
                    can_sort = False
                    break
                if (load_pl['PlayerID'] == save_pl['PlayerID']) and (load_pl['Time'] < save_pl['Time']):
                    second_pos = j + 1
                    break
            if can_sort:
                for j in range(10):
                    save_pl = json.loads(cursor.execute(f'SELECT top{j + 1} FROM speedruns WHERE lvl = {last_run % 6}').fetchone()[0])
                    if (load_pl['Time'] < save_pl['Time']):
                        first_pos = j + 1
                        break
                for j in range(second_pos - 1, first_pos - 1, -1):
                    save_plstr = cursor.execute(f'SELECT top{j} FROM speedruns WHERE lvl = {last_run % 6}').fetchone()[0]
                    # ОБНОВЛЯЮ значение элемента, таблицы "speedruns" столбика "top(какой-то)", где lvl = (какому-то числу), на данные о спидранере
                    cursor.execute(f"UPDATE speedruns SET top{j + 1} = '{save_plstr}' WHERE lvl = {last_run % 6}")
                save_pl = json.loads(cursor.execute(f'SELECT top{first_pos} FROM speedruns WHERE lvl = {last_run % 6}').fetchone()[0])
                if (first_pos <= second_pos) and (load_pl['Time'] < save_pl['Time']):
                    cursor.execute(f"UPDATE speedruns SET top{first_pos} = '{load_plstr}' WHERE lvl = {last_run % 6}")

        print(f"Спидран #{last_run} проверен")
        await ctx.send(f"Спидран #{last_run} проверен")
        last_run += 1
        cursor.execute(f"UPDATE run SET cur = {last_run}") # Не использую WHERE так как в таблице "run" всего один элемент
        conn.commit()
        response_data = requests.post(url, data={"SpeedrunID":f"{last_run}"}).text
        await asyncio.sleep(1)
    await ctx.send("Загрузил")

class speedrun_leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['top'])
    async def топ(self, ctx):
        view = SelectView()
        await ctx.send(embed = await AllTopDescriptionEmbed(), view = view)

    @commands.slash_command(name='top', description='Show the top speedrunners')
    async def top(self, ctx: disnake.ApplicationCommandInteraction):
        view = SelectView()
        await ctx.send(embed = await AllTopDescriptionEmbed(), view = view)

    @commands.command(aliases=['download'])
    async def загрузи(self, ctx):
        if not (ctx.author.id == 695684705328169060): await ctx.send("хер те")
        await LoadingData(ctx)

def setup(bot):
    bot.add_cog(speedrun_leaderboard(bot))

class SelectView(View):
    @disnake.ui.select(
        placeholder = "Выбрать вид топа",
        options = [
            disnake.SelectOption(label="Все карты", value="-"),
            disnake.SelectOption(label="Level 0", value="0"),
            disnake.SelectOption(label="Level 1", value="1"),
            disnake.SelectOption(label="Level 2", value="2"),
            disnake.SelectOption(label="Level 3", value="3"),
            disnake.SelectOption(label="Level 4", value="4"),
            disnake.SelectOption(label="Level 5", value="5"),
        ]
    )

    async def select_callback(self, select, interaction):
        select.disabled = True
        if select.values[0] == "-":
            await interaction.response.edit_message(embed=await AllTopDescriptionEmbed())
        if select.values[0] == "0":
            await interaction.response.edit_message(embed=await TopDescriptionEmbed(0))
        if select.values[0] == "1":
            await interaction.response.edit_message(embed=await TopDescriptionEmbed(1))
        if select.values[0] == "2":
            await interaction.response.edit_message(embed=await TopDescriptionEmbed(2))
        if select.values[0] == "3":
            await interaction.response.edit_message(embed=await TopDescriptionEmbed(3))
        if select.values[0] == "4":
            await interaction.response.edit_message(embed=await TopDescriptionEmbed(4))
        if select.values[0] == "5":
            await interaction.response.edit_message(embed=await TopDescriptionEmbed(5))