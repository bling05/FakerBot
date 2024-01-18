import discord
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random

TOKEN = ''
NUMBER_OF_POSTS = 3
COMMENTS_PER_POST = 3

with open("champions.txt", "r") as file:
    champs = file.read().split()

ranks = ['iron', 'bronze', 'silver', 'gold', 'gold_plus', 'platinum', 'platinum_plus', 'emerald', 'emerald_plus', 'diamond', 'd2_plus', 'master', 'master_plus', 'grandmaster', 'challenger']

rune_dict = {
    8005: "Press the Attack", 8008: "Lethal Tempo", 8021: "Fleet Footwork", 8010: "Conquerer",
    8112: "Electrocute", 8124: "Predator", 8128: "Dark Harvest", 9923: "Hail of Blades",
    8214: "Summon Aery", 8229: "Arcane Comet", 8230: "Phase Rush",
    8437: "Grasp of the Undying", 8439: "Aftershock", 8465: "Guardian",
    8351: "Glacial Augment", 8360: "Unsealed Spellbook", 8369: "First Strike",
    9101: "Overheal", 9111: "Triumph", 8009: "Prescence of Mind",
    8126: "Cheap Shot", 8139: "Taste of Blood", 8143: "Sudden Impact",
    8224: "Nullifying Orb", 8226: "Manaflow Band", 8275: "Nimbus Cloak",
    8446: "Demolish", 8463: "Font of Life", 8401: "Shield Bash",
    8306: "Hextech Flashtraption", 8304: "Magical Footwear", 8313: "Perfect Timing",
    9104: "Legend: Alacrity", 9105: "Legend: Tenacity", 9103: "Legend: Bloodline",
    8136: "Zombie Ward", 8120: "Ghost Poro", 8138: "Eyeball Collection",
    8210: "Transcendence", 8234: "Celerity", 8233: "Absolute Focus",
    8429: "Conditioning", 8444: "Second Wind", 8473: "Bone Plating",
    8321: "Future's Market", 8316: "Minion Dematerializer", 8345: "Biscuit Delivery",
    8014: "Coup de Grace", 8017: "Cut Down", 8299: "Last Stand",
    8135: "Treasure Hunter", 8134: "Ingenius Hunter", 8105: "Relentless Hunter", 8106: "Ultimate Hunter",
    8237: "Scorch", 8232: "Water Walking", 8236: "Gathering Storm",
    8451: "Overgrowth", 8453: "Revitalize", 8242: "Unflinching",
    8347: "Cosmic Insight", 8410: "Approach Velocity", 8352: "Time Warp Tonic",
    5008: "Adaptive Force", 5005: "Attack Speed", 5007: "Ability Haste"
}

intents = discord.Intents.all()
intents.members = True
client = discord.Client(command_prefix=',', intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="'!matchup and !build'"))

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        await message.channel.send(random.choice(chatter))
        return

    if message.content.lower().split()[0] == '!build':
        if len(message.content.split()) != 4:
            await message.reply('Format: "!build <Your Champion Name> <Enemy Champion Name> <Rank>"\nEx: !build drmundo aatrox gold (gold+, platinum+, diamond+, master+, all are also available as ranks!)')
            return
        c1 = message.content.lower().split()[1].replace('.','').replace("'","")
        c2 = message.content.lower().split()[2].replace('.','').replace("'","")
        rank = message.content.lower().split()[3].replace('diamond+','d2_plus').replace('+','_plus')

        if c1 not in champs or c2 not in champs or rank not in ranks:
            await message.reply('Please check that your spelling was correct!')
            return

        build_url = f'https://lolalytics.com/lol/{c1}/vs/{c2}/build/?tier={rank}&patch=30'
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(build_url)
        time.sleep(5)
        soup = bs(driver.page_source, "html.parser")

        img_elements = soup.find_all('img', {'class': 'Spell_spell32br__jxm+J'})
        sums = [img.get('alt') for img in img_elements]
        print(sums)

        starters_ct = 0
        for div in soup.find('div', {'class': 'SummaryStarting_starting__oqr6S'}):
            print(div)
            starters_ct += 1

        img_elements = soup.find_all('img', {'class': 'Item_item32br__kEZk9'})
        initial_list = [img.get('alt') for img in img_elements]
        items = []
        for i in initial_list:
            if i not in items and i != None:
                items.append(i.replace("Sanguine Blade", "Hullbreaker"))

        overall = []
        overall_div = soup.find('div', {'class': 'ChampionVsStats_stats__7sEQ-'})
        for div in overall_div:
            innerdiv = div.find('div')
            overall.append(innerdiv.text)

        starter_items = items[:starters_ct]
        core_items = items[starters_ct:starters_ct+3]
        additional_items = items[starters_ct+3:]
        print(starter_items)
        print(core_items)
        print(additional_items)

        unfiltered_runes = []
        div_elements = soup.find_all('div', {'class': 'RuneSet_rune__GvPL6'})
        for div in div_elements:
            for div2 in div.find_all('div'):
                imgs = div2.find_all('img')
                for img in imgs:
                    if 'RuneImage_grey__4hY4L' not in img.get('class'):
                        if int(img.get('alt')) in rune_dict:
                            unfiltered_runes.append(rune_dict[int(img.get('alt'))])

        div_elements2 = soup.find('div', {'class': 'RuneSet_mod__Z2F8m'}).find('div')
        img_div = div_elements2.find_all('img')
        for img in img_div:
            if 'RuneImage_grey__4hY4L' not in img.get('class'):
                unfiltered_runes.append(rune_dict[int(img.get('alt'))])

        runes = []
        [runes.append(rune) for rune in unfiltered_runes if rune not in runes]

        user = message.author
        build = discord.Embed(title=f"Build Info for {c1.capitalize()} vs {c2.capitalize()}, {rank.capitalize().replace('_plus','+')}", url=build_url)
        build.set_author(name=f"Recommended build and items taken from LoLalytics.com", icon_url=user.avatar.url)
        build.add_field(name="Recommended summoner spells:", value=f"{sums[0]} and {sums[1]}", inline=True)
        build.add_field(name="Recommended starter items:", value=", ".join(starter_items), inline=False)
        build.add_field(name="Core items:", value=", ".join(core_items), inline=False)
        build.add_field(name="Additional items:", value=", ".join(additional_items), inline=False)
        build.add_field(name="Recommended runes", value=", ".join(runes), inline=False)
        build.add_field(name="Winrate/Games Analyzed", value=", ".join(overall) + " games", inline=False)
        build.set_footer(text="Created by antiskid")

        await message.reply(embed=build)

    if message.content.lower().split()[0] == '!matchup':

        if len(message.content.split()) != 3:
            await message.reply('Format: "!matchup <Your Champion Name> <Enemy Champion Name>". Please type two-word names as one word.')
            return
        try:
            c1 = message.content.lower().split()[1].replace('.','').replace("'","")
            c2 = message.content.lower().split()[2].replace('.','').replace("'","")
            if c1 not in champs or c2 not in champs:
                await message.reply('Please check that your spelling was correct!')
                return

        except Exception as e:
            await message.reply('Format: "!matchup <Your Champion Name> <Enemy Champion Name>")')
            print(e)
            return

        try:
            urls = []
            titles = {}
            query = f"{c1} vs {c2} reddit"
            page = requests.get(f"https://www.google.com/search?q={query}&num={NUMBER_OF_POSTS}")
            soup = bs(page.content, "html.parser")
            links = soup.findAll("a")
            for link in links :
                link_href = link.get('href')
                if "url?q=" in link_href and not "webcache" in link_href:
                    url = link.get('href').split("?q=")[1].split("&sa=U")[0]
                    urls.append(url)
                    titles[url] = (link.text.split('Redditwww.reddit.com')[0][:-3])

            for url in urls:

                response = requests.get(url + ".json", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
                json = response.json()

                # Extract the post data
                post = json[0]['data']['children'][0]['data']

                # Filter out posts containing media
                if "media_embed" in post and "content" in post["media_embed"]:
                    continue
                elif "post_hint" in post and post["post_hint"].startswith("rich:"):
                    continue
                elif post["is_reddit_media_domain"] == True:
                    continue
                else:
                    print(url)

                embed = discord.Embed(title=titles[url], url=url)
                user = message.author
                embed.set_author(name=f"Matchup info for {c1.capitalize()} vs {c2.capitalize()}, as requested by {user.display_name}", icon_url=user.avatar.url)
                embed.set_footer(text="Created by antiskid")

                msg_block = "\n".join(comment["data"]["body"] for comment in json[1]["data"]["children"][:COMMENTS_PER_POST]).replace(" -&gt;", "\n- ")

                # Split and send messages if msg_block exceeds 1000 characters
                while msg_block:
                    chunk, msg_block = msg_block[:1000], msg_block[1000:]
                    if not embed.fields:  # Check if fields list is empty (first chunk)
                        embed.add_field(name=url, value=chunk)
                    else:
                        embed.add_field(name="\u200B", value=chunk, inline=False)

                await message.reply(embed=embed)

        except Exception as e:
            print('No more posts!')

        moba_url = f'https://mobalytics.gg/lol/champions/{c2}/counters'
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(moba_url)
        time.sleep(5)
        soup = bs(driver.page_source, "html.parser")

        tips = []
        for p in soup.find_all('p', class_='m-p0i13t'):
            for span in p.find_all('span', class_='m-omerw7'):
                span.replace_with(span.text)
            tips.append(p.get_text())

        laning_tips = tips[:3]
        strategy_tips = tips[3:6]
        spikes_tips = tips[6:]

        embed2 = discord.Embed(title=f"General matchup tips vs {c2.capitalize()}", url=moba_url)
        embed2.set_author(name=f"Tips taken from mobalytics.gg", icon_url=user.avatar.url)
        embed2.add_field(name=f"Laning against {c2.capitalize()}", value="\n\n".join(laning_tips), inline=False)
        embed2.add_field(name="", value="\n", inline=False)
        embed2.add_field(name=f"Strategy vs {c2.capitalize()}", value="\n\n".join(strategy_tips), inline=False)
        embed2.add_field(name="", value="\n", inline=False)
        embed2.add_field(name=f"{c2.capitalize()}'s power spikes", value="\n\n".join(spikes_tips), inline=False)
        embed2.set_footer(text="Created by antiskid")

        await message.reply(embed=embed2)

client.run(TOKEN)
