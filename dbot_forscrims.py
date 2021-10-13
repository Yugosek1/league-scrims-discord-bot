import discord
from discord import message
from discord.ext import tasks
import re
import os
import psycopg2
from datetime import datetime, timedelta, timezone

TOKEN = os.environ['TOKEN']
BOSYUCHANNEL_ID = int(os.environ['BOSYUCHANNEL_ID'])
tier = {"アイアン":1, "ブロンズ":2, "シルバー":3, "ゴールド":4, "プラチナ":5, "ダイヤモンド":6, "マスター":7, "グランドマスター":8, "チャレンジャー":9}
JST = timezone(timedelta(hours=+9), 'JST')
 
client = discord.Client()

def get_connection():
    dsn = os.environ.get('DATABASE_URL')
    return psycopg2.connect(dsn)

conn = get_connection()
conn.autocommit=True
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS database(
            id SERIAL NOT NULL,
            user_id BIGINT,
            user_name VARCHAR(32),
            created_datetime TIMESTAMP,
            teamname TEXT,
            date_and_time TIMESTAMP,
            tier_average INTEGER,
            matches TEXT,
            comments TEXT)''')
conn.commit()


@client.event
async def on_ready():
   print('ログインしました')
 
@client.event
async def on_message(message):
   if message.content.startswith('!post'):
      return await post_add(message)

   if message.content.startswith('!delete'):
      return await post_delete(message)
   
   if message.content.startswith('!update'):
      return await post_update(message)

   if message.content.startswith('!mylist'):
      return await post_mylist(message)
   
   if message.content.startswith('!search'):
      return await search_by_tier(message)


async def post_add(message):
   post_message = re.findall(r'^!post (.+),(\d{4}-\d{2}-\d{2} \d{2}:\d{2}),(\d),(.+),(.+)$',message.content)
   if post_message:
      cur.execute('insert into database(user_id, user_name, created_datetime, teamname, date_and_time, tier_average , matches, comments)values(%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                  [message.author.id, message.author.name, message.created_at, post_message[0][0], post_message[0][1], post_message[0][2], post_message[0][3], post_message[0][4]])
      id_of_new_row = cur.fetchone()[0]
      conn.commit()
      print(id_of_new_row)
      embed=discord.Embed(title="Success!", description="投稿IDは`"+str(id_of_new_row)+"`です", color=0x00ff01)
      return await message.channel.send(embed=embed)
   else:
      embed=discord.Embed(title="Error!", description="引数の数が間違っている可能性があります", color=0xff0000)
      return await message.channel.send(embed=embed)

async def post_delete(message):
   post_message = re.findall(r'^!delete +([0-9]+)$',message.content)
   if post_message:
      cur.execute('SELECT * FROM database WHERE user_id= %s and id= %s',[message.author.id, post_message[0]])
      post_nakami = cur.fetchone()
      print(post_nakami)
      print(post_message[0])
      if post_nakami:
         cur.execute('DELETE FROM database WHERE user_id=%s and id=%s',[message.author.id, post_message[0]])
         conn.commit()
         embed=discord.Embed(title="Success!", description=
                             "登録日時:`"+post_nakami[3].strftime('%m月%d日 %H時%M分')+"`に登録された`"+post_message[0]+"`の投稿を削除しました", color=0x00ff01)
         return await message.channel.send(embed=embed)
      else :
         embed=discord.Embed(title="Error!", description=
                             "`"+post_message[0]+"`は登録されていません。また削除は登録したユーザーのみ可能です", color=0xff0000)
         return await message.channel.send(embed=embed)
   else:
      embed=discord.Embed(title="Error!", description="形式が違います`!delete [post_ID]`", color=0xff0000)
      return await message.channel.send(embed=embed)


async def post_update(message):
   post_message = re.findall(r'^!update (\d+) (.+),(\d{4}-\d{2}-\d{2} \d{2}:\d{2}),(\d),(.+),(.+)$',message.content)
   if post_message:
      cur.execute('SELECT * FROM database WHERE user_id=%s and id=%s',[message.author.id, post_message[0][0]])
      post_nakami = cur.fetchone()
      if post_nakami:
         cur.execute('''UPDATE database SET
                  teamname=%s,
                  date_and_time=%s,
                  tier_average=%s,
                  matches=%s,
                  comments=%s
                  WHERE user_id=%s and id=%s'''
                  ,[post_message[0][1],post_message[0][2],post_message[0][3],post_message[0][4],post_message[0][5],message.author.id, post_message[0][0]])
         conn.commit()
         embed=discord.Embed(title="Success!", description="`"+post_message[0][0]+"`の投稿を更新しました", color=0x00ff01)
         return await message.channel.send(embed=embed)
      else:
         embed=discord.Embed(title="Error!", description="`"+post_message[0][0]+"`は登録されていません。また更新は登録したユーザーのみ可能です", color=0xff0000)
         return await message.channel.send(embed=embed)
   else:
      embed=discord.Embed(title="Error!", description="形式が違います`!update [post_ID]`", color=0xff0000)
      return await message.channel.send(embed=embed)

async def edit_list():
   cur.execute('''SELECT user_id, teamname, date_trunc('minute',date_and_time), tier_average, matches, comments, id, tier
                     FROM database join tier_list using(tier_average)
                     order by id asc limit 20''')
   mypost = cur.fetchall()
   channel = client.get_channel(BOSYUCHANNEL_ID)
   # メッセージの取得:常に更新するメッセージの固有ID(ex. 854610120680275988)
   edit_message = await channel.fetch_message(854610120680275988)
   if mypost:      
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(mypost)):
         embed1.add_field(name=str(i+1), value=
         f'''`チーム名:` {mypost[i][1]}\n`対戦開始日時:` {mypost[i][2].strftime('%m月%d日 %H時%M分')}`平均レート:` {mypost[i][7]}\n'''
         f'''`試合数:` {mypost[i][4]}`コメント:` {mypost[i][5]}\n'''
         f'''`連絡先:` <@{mypost[i][0]}>`投稿ID:` {mypost[i][6]}'''
         , inline=False)
         embed1.set_footer(text=f"last updated on : {datetime.now(JST).strftime('%Y-%m-%d %H:%M')}",
                          icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
      await edit_message.edit(content=None, embed=embed1)

   else:
      channel = client.get_channel(BOSYUCHANNEL_ID)
   # メッセージの取得:常に更新するメッセージの固有ID(ex. 854610120680275988)
      edit_message = await channel.fetch_message(854610120680275988)
      embed=discord.Embed(title="Error!", description="登録が見つかりませんでした", color=0xff0000)
      return await edit_message.edit(content=None, embed=embed)
   print("edit_list Done")

async def post_mylist(message):
   cur.execute('''SELECT user_id, teamname, date_trunc('minute',date_and_time), tier_average, matches, comments, id, tier 
                     FROM database join tier_list using(tier_average)
                     WHERE user_id =%s
                     order by date_and_time asc limit 20''',[message.author.id])
   mypost = cur.fetchall()

   if mypost:
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(mypost)):
         embed1.add_field(name=str(i+1)+".", value=
         f'''`チーム名`: {mypost[i][1]}\n`対戦開始日時`: {mypost[i][2].strftime('%m月%d日 %H時%M分')}`平均レート`: {mypost[i][7]}\n'''
         f'''`試合数`: {mypost[i][4]}`コメント`: {mypost[i][5]}\n'''
         f'''`連絡先`: <@{mypost[i][0]}>`投稿ID`: {mypost[i][6]}'''
         , inline=False)
      await message.channel.send(embed=embed1)

   else:
      embed=discord.Embed(title="Error!", description="登録が見つかりませんでした", color=0xff0000)
      return await message.channel.send(embed=embed)


async def search_by_tier(message):
   # !search 1
   msg1 = re.findall(r'^!search ([\d+][^ 　]+)$',message.content)
   # !search ゴールド
   msg2 = re.findall(r'^!search ([\D+][^ 　]+)$',message.content)
   # !search 1 4
   msg3 = re.findall(r'^!search (\d) +(\d)$',message.content)
   # !search アイアン プラチナ
   msg4 = re.findall(r'^!search ([\D 　]+) +([\D 　]+)$',message.content)
   if msg1:
      cur.execute('''SELECT user_id, teamname, date_trunc('minute',date_and_time), tier_average, matches, comments, id, tier 
                  FROM database join tier_list using(tier_average) WHERE (tier_average =%s or tier =%s)
                  order by date_and_time asc limit 20''',[msg1[0],msg1[0]])
      result = cur.fetchall()
      if result:
         embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
         for i in range(len(result)):
            embed1.add_field(name=str(i+1)+".", value=
            f'''`チーム名`: {result[i][1]}\n`対戦開始日時`: {result[i][2].strftime('%m月%d日 %H時%M分')}`平均レート`: {result[i][7]}\n'''
            f'''`試合数`: {result[i][4]}`コメント`: {result[i][5]}\n'''
            f'''`連絡先`: <@{result[i][0]}>`投稿ID`:{result[i][6]}'''
            , inline=False)
         await message.channel.send(embed=embed1)
      else:
         embed=discord.Embed(title="Error!", description="登録が見つかりませんでした", color=0xff0000)
         return await message.channel.send(embed=embed)

   if msg2:
      print(msg2[0])
      cur.execute('''SELECT user_id, teamname, date_trunc('minute',date_and_time), tier_average, matches, comments, id, tier 
                  FROM database join tier_list using(tier_average) WHERE (tier =%s)
                  order by date_and_time asc limit 20''',[msg2[0],])
      result = cur.fetchall()
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(result)):
         embed1.add_field(name=str(i+1)+".", value=
         f'''`チーム名`: {result[i][1]}\n`対戦開始日時`: {result[i][2].strftime('%m月%d日 %H時%M分')}`平均レート`: {result[i][7]}\n'''
         f'''`試合数`: {result[i][4]}`コメント`: {result[i][5]}\n'''
         f'''`連絡先`: <@{result[i][0]}>`投稿ID`:{result[i][6]}'''
         , inline=False)
      await message.channel.send(embed=embed1)
   if msg3:
      print(msg3[0][0])
      print(msg3[0][1])
      cur.execute('''SELECT user_id, teamname, date_trunc('minute',date_and_time), tier_average, matches, comments, id, tier 
                  FROM database join tier_list using(tier_average) WHERE (tier_average BETWEEN %s AND %s)
                  order by date_and_time asc limit 20''',
                  [msg3[0][0],msg3[0][1]])
      result = cur.fetchall()
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(result)):
         embed1.add_field(name=str(i+1)+".", value=
         f'''`チーム名`: {result[i][1]}\n`対戦開始日時`: {result[i][2].strftime('%m月%d日 %H時%M分')}`平均レート`: {result[i][7]}\n'''
         f'''`試合数`: {result[i][4]}`コメント`: {result[i][5]}\n'''
         f'''`連絡先`: <@{result[i][0]}>`投稿ID`:{result[i][6]}'''
         , inline=False)
      await message.channel.send(embed=embed1)
   if msg4:
      msg4_1 = str(msg4[0][0])
      msg4_2 = str(msg4[0][1])
      msg4_1 = tier[msg4_1]
      msg4_2 = tier[msg4_2]
      print(msg4_1,msg4_2)
      cur.execute('''SELECT user_id, teamname, date_trunc('minute',date_and_time), tier_average, matches, comments, id, tier 
                  FROM database join tier_list using(tier_average)
                  WHERE (tier_average BETWEEN %s AND %s) order by date_and_time asc limit 20''',[msg4_1,msg4_2])
      result = cur.fetchall()
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(result)):
         embed1.add_field(name=str(i+1)+".", value=
         f'''`チーム名`: {result[i][1]}\n`対戦開始日時`: {result[i][2].strftime('%m月%d日 %H時%M分')}`平均レート`: {result[i][7]}\n'''
         f'''`試合数`: {result[i][4]}`コメント`: {result[i][5]}\n'''
         f'''`連絡先`: <@{result[i][0]}>`投稿ID`:{result[i][6]}'''
         , inline=False)
      await message.channel.send(embed=embed1)


#今日-1日のレコードより古いレコードを削除　一定間隔で実行するか、各コマンドが呼ばれたときに一緒に実行するか検討
async def post_refresh():
   cur.execute("DELETE from database WHERE date_and_time <= CURRENT_TIMESTAMP - interval '1 day';")
   conn.commit()
   print('post_refresh Done')


@tasks.loop(seconds=60)
async def update_posts():
   #editパート
   await edit_list()
   #refreshパート
   await post_refresh()
   
@update_posts.before_loop
async def before_update_posts():
    # botがログインするまで(on_readyが発火するまで）待機します
    await client.wait_until_ready()

update_posts.start()

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
