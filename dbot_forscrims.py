import discord
from discord import message
from discord.ext import tasks
import re
import os
from dotenv import load_dotenv
import psycopg2

#.envファイル読み込み
load_dotenv()
 
TOKEN = os.environ['TOKEN']
 
client = discord.Client()

BOSYUCHANNEL_ID = int(os.environ['BOSYUCHANNEL_ID'])

tier = {"アイアン":1, "ブロンズ":2, "シルバー":3, "ゴールド":4, "プラチナ":5, "ダイヤモンド":6, "マスター":7, "グランドマスター":8, "チャレンジャー":9}

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conc.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS database(
         user_id INTEGER,
         user_name STRING,
         created_datetime TEXT,
         teamname TEXT,
         date_and_time,
         tier_average INTEGER,
         matche TEXT,
         comments TEXT)''')


@client.event
async def on_ready():
   print('ログインしました')
 
@client.event
async def on_message(message):
   if message.content.startswith('!post'):
      print('!post detected')
      return await post_add(message)

   if message.content.startswith('!delete'):
      print('!delete detected')
      return await post_delete(message)
   
   if message.content.startswith('!update'):
      print('!update detected')
      return await post_update(message)

   if message.content.startswith('!mylist'):
      print('!mylist detected')
      return await post_mylist(message)
   
   if message.content.startswith('!search'):
      return await search_by_tier(message)

   # if message.content.startswith('!list'):
   #    print('!list detected')
   #    return await post_list(message)

   # if message.content.startswith('!refresh'):
   #    print('!refresh detected')
   #    return await post_refresh(message)
 
   # if message.content.startswith("!delall"):
   #    return await delete_allposts(message)


async def post_add(message):
   post_message = re.match(r'^!post (.+),(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),(\d),(.+),(.+)$',message.content)
   post_message = post_message.groups()
   if post_message:
      c.execute('insert into database values(?, ?, ?, ?, ?, ?, ?, ?)',
                  [message.author.id, message.author.name, message.created_at, post_message[0], post_message[1], post_message[2], post_message[3], post_message[4]])
      # on conflict (user_id,teamname) do update set created_datatime'
      post_rowid = c.lastrowid 
      con.commit()
      embed=discord.Embed(title="Success!", description="投稿IDは`"+str(post_rowid)+"`です", color=0x00ff01)
      return await message.channel.send(embed=embed)
   else:
      embed=discord.Embed(title="Error!", description="引数の数が間違っている可能性があります", color=0xff0000)
      return await message.channel.send(embed=embed)

async def post_delete(message):
   post_message = re.findall(r'^!delete +([0-9]+)$',message.content)
   if post_message:
      post_nakami = c.execute('SELECT * FROM database WHERE user_id=? and rowid=?',
                             [message.author.id, post_message[0]]).fetchone() 
      if post_nakami:
         c.execute('DELETE FROM database WHERE user_id=? and rowid=?',
              [message.author.id, post_message[0]])
         con.commit()
         embed=discord.Embed(title="Success!", description=
                             "登録日時:`"+post_nakami[2]+"`に登録された`"+post_message[0]+"`の投稿を削除しました", color=0x00ff01)
         return await message.channel.send(embed=embed)
      else :
         embed=discord.Embed(title="Error!", description=
                             "`"+post_message[0]+"`は登録されていません。また削除は登録したユーザーのみ可能です", color=0xff0000)
         return await message.channel.send(embed=embed)
   else:
      embed=discord.Embed(title="Error!", description="形式が違います`!delete [post_ID]`", color=0xff0000)
      return await message.channel.send(embed=embed)

# async def post_update(message):
   post_message = re.findall(r'^!update (\d+) (.+),(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),(\d),(.+),(.+)$',message.content)
   if post_message:
      print(type(post_message))
      print(post_message)
      post_nakami = c.execute('SELECT * FROM database WHERE user_id=? and rowid=?',[message.author.id, post_message[0][0]]).fetchone() 

      if post_nakami:
         c.execute('UPDATE database SET teamname=?,date_and_time=?,tier_average=?,matches=?,comments=? WHERE user_id=? and rowid=?',[post_message[0][1],post_message[0][2],post_message[0][3],post_message[0][4],post_message[0][5],message.author.id, post_message[0][0]])
         con.commit()
         embed=discord.Embed(title="Success!", description=post_message[0][0]+"の投稿を更新しました", color=0x00ff01)
         return await message.channel.send(embed=embed)
      else:
         embed=discord.Embed(title="Error!", description="`"+post_message[0][0]+"`は登録されていません。また更新は登録したユーザーのみ可能です", color=0xff0000)
         return await message.channel.send(embed=embed)
   else:
      embed=discord.Embed(title="Error!", description="形式が違います`!update [post_ID]`", color=0xff0000)
      return await message.channel.send(embed=embed)

async def post_update(message):
   post_message = re.match(r'^!update (\d+) (.+),(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),(\d),(.+),(.+)$',message.content)
   post_message = post_message.groups()
   if post_message:
      # print(type(post_message))
      # print(post_message)
      post_nakami = c.execute('SELECT * FROM database WHERE user_id=? and rowid=?',[message.author.id, post_message[0]]).fetchone() 

      if post_nakami:
         c.execute('''UPDATE database SET
                  teamname=?,
                  date_and_time=?,
                  tier_average=?,
                  matches=?,
                  comments=?
                  WHERE user_id=? and rowid=?'''
                  ,[post_message[1],post_message[2],post_message[3],post_message[4],post_message[5],message.author.id, post_message[0]])
         con.commit()
         embed=discord.Embed(title="Success!", description=post_message[0]+"の投稿を更新しました", color=0x00ff01)
         return await message.channel.send(embed=embed)
      else:
         embed=discord.Embed(title="Error!", description="`"+post_message[0]+"`は登録されていません。また更新は登録したユーザーのみ可能です", color=0xff0000)
         return await message.channel.send(embed=embed)
   else:
      embed=discord.Embed(title="Error!", description="形式が違います`!update [post_ID]`", color=0xff0000)
      return await message.channel.send(embed=embed)

async def post_list():
   mypost = c.execute('''SELECT user_id, teamname, strftime("%m月%d日 %H時%M分",date_and_time), tier_average, matches, comments, database.rowid, tier
                     FROM database join tier_list using(tier_average) 
                     order by database.rowid asc limit 10''').fetchall()
   channel = client.get_channel(BOSYUCHANNEL_ID)
   if mypost:
      for i in range(len(mypost)):
         embed=discord.Embed(title="対戦募集", color=0x668cff)
         embed.add_field(name="チーム名", value=mypost[i][1], inline=False)
         embed.add_field(name="対戦開始日時", value=mypost[i][2], inline=True)
         embed.add_field(name="平均レート", value=mypost[i][7], inline=True)
         embed.add_field(name="試合数", value=mypost[i][4], inline=True)
         embed.add_field(name="コメント", value=mypost[i][5], inline=False)
         embed.add_field(name="連絡先", value="<@"+str(mypost[i][0])+">", inline=False)
         embed.set_footer(text="ID: "+str(mypost[i][6]))

         await channel.send(embed=embed)
      
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(mypost)):
         embed1.add_field(name=str(i+1), value=
         "`チーム名`: "+mypost[i][1]+"\n"+
         " `対戦開始日時`: "+mypost[i][2]+
         " `平均レート`: "+mypost[i][7]+"\n"+
         " `試合数`: "+mypost[i][4]+
         " `コメント`: "+mypost[i][5]+"\n"+
         " `連絡先`: "+"<@"+str(mypost[i][0])+">"
         , inline=False)
      await channel.send(embed=embed1)

   else:
      embed=discord.Embed(title="Error!", description="登録が見つかりませんでした", color=0xff0000)
      return await channel.send(embed=embed)
   print("post_list Done")

async def edit_list():
   # mypost = c.execute('SELECT user_id, teamname, date_and_time, tier_average, matches, comments, rowid FROM database WHERE user_id =?',[message.author.id]).fetchall()
   mypost = c.execute('''SELECT user_id, teamname, strftime("%m月%d日 %H時%M分",date_and_time), tier_average, matches, comments, database.rowid, tier
                     FROM database join tier_list using(tier_average)
                     order by database.rowid asc limit 20''').fetchall()
   channel = client.get_channel(854600745550741554)
   # メッセージの取得
   edit_message = await channel.fetch_message(854610120680275988)
   if mypost:      
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(mypost)):
         embed1.add_field(name=str(i+1), value=
         f'`チーム名:` {mypost[i][1]}\n`対戦開始日時:` {mypost[i][2]}`平均レート:` {mypost[i][7]}\n'
         f'`試合数:` {mypost[i][4]}`コメント:` {mypost[i][5]}\n'
         f'`連絡先:` <@{mypost[i][0]}>`post_ID:` {mypost[i][6]}'
         , inline=False)
      await edit_message.edit(content=None, embed=embed1)

   else:
      embed=discord.Embed(title="Error!", description="登録が見つかりませんでした", color=0xff0000)
      return await channel.send(embed=embed)
   print("edit_list Done")


async def post_mylist(message):
   # mypost = c.execute('SELECT user_id, teamname, date_and_time, tier_average, matches, comments, rowid FROM database WHERE user_id =?',[message.author.id]).fetchall()
   mypost = c.execute('''SELECT user_id, teamname, strftime("%m月%d日 %H時%M分",date_and_time), tier_average, matches, comments, database.rowid, tier 
                     FROM database join tier_list using(tier_average)
                     WHERE user_id =?
                     order by date_and_time asc limit 10''',[message.author.id]).fetchall()

   if mypost:
      # for i in range(len(mypost)):
      #    embed=discord.Embed(title=f"対戦募集{i+1}", color=0x668cff)
      #    embed.add_field(name="チーム名", value=mypost[i][1], inline=False)
      #    embed.add_field(name="対戦開始日時", value=mypost[i][2], inline=True)
      #    embed.add_field(name="平均レート", value=mypost[i][7], inline=True)
      #    embed.add_field(name="試合数", value=mypost[i][4], inline=True)
      #    embed.add_field(name="コメント", value=mypost[i][5], inline=False)
      #    embed.add_field(name="連絡先", value="<@"+str(mypost[i][0])+">", inline=False)
      #    embed.set_footer(text="ID: "+str(mypost[i][6]))

      #    await message.channel.send(embed=embed)
      
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(mypost)):
         embed1.add_field(name=str(i+1)+".", value=
         f'`チーム名`: {mypost[i][1]}\n`対戦開始日時`: {mypost[i][2]}`平均レート`: {mypost[i][7]}\n'
         f'`試合数`: {mypost[i][4]}`コメント`: {mypost[i][5]}\n'
         f'`連絡先`: <@{mypost[i][0]}>`post_ID`:{mypost[i][6]}'
         , inline=False)
      await message.channel.send(embed=embed1)

   else:
      embed=discord.Embed(title="Error!", description="登録が見つかりませんでした", color=0xff0000)
      return await message.channel.send(embed=embed)

async def search_by_tier(message):
   msg1 = re.findall(r'^!search ([^ 　]+)$',message.content)
   msg2 = re.findall(r'^!search (\d) +(\d)$',message.content)
   msg3 = re.findall(r'^!search ([^ 　]+) +([^ 　]+)$',message.content)
   if msg1:
      result = c.execute('''SELECT user_id, teamname, strftime("%m月%d日 %H時%M分",date_and_time), tier_average, matches, comments, database.rowid, tier 
               FROM database join tier_list using(tier_average)
               WHERE (tier_average =? or tier =?)order by date_and_time asc limit 20'''
               ,[msg1[0],msg1[0]]).fetchall()
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(result)):
         embed1.add_field(name=str(i+1)+".", value=
         f'`チーム名`: {result[i][1]}\n`対戦開始日時`: {result[i][2]}`平均レート`: {result[i][7]}\n'
         f'`試合数`: {result[i][4]}`コメント`: {result[i][5]}\n'
         f'`連絡先`: <@{result[i][0]}>`post_ID`:{result[i][6]}'
         , inline=False)
      await message.channel.send(embed=embed1)
   if msg2:
      print(msg2[0][0],msg2[0][1])
      result = c.execute('''SELECT user_id, teamname, strftime("%m月%d日 %H時%M分",date_and_time), tier_average, matches, comments, database.rowid, tier 
               FROM database join tier_list using(tier_average)
               WHERE (tier_average BETWEEN ? AND ?)order by date_and_time asc limit 20'''
               ,[msg2[0][0],msg2[0][1]]).fetchall()
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(result)):
         embed1.add_field(name=str(i+1)+".", value=
         f'`チーム名`: {result[i][1]}\n`対戦開始日時`: {result[i][2]}`平均レート`: {result[i][7]}\n'
         f'`試合数`: {result[i][4]}`コメント`: {result[i][5]}\n'
         f'`連絡先`: <@{result[i][0]}>`post_ID`:{result[i][6]}'
         , inline=False)
      await message.channel.send(embed=embed1)
   if msg3:
      msg3_1 = str(msg3[0][0])
      msg3_2 = str(msg3[0][1])
      msg3_1 = tier[msg3_1]
      msg3_2 = tier[msg3_2]
      print(msg3_1,msg3_2)
      result = c.execute('''SELECT user_id, teamname, strftime("%m月%d日 %H時%M分",date_and_time), tier_average, matches, comments, database.rowid, tier 
               FROM database join tier_list using(tier_average)
               WHERE (tier_average BETWEEN ? AND ?) order by date_and_time asc limit 20'''
               ,[msg3_1,msg3_2]).fetchall()
      embed1=discord.Embed(title="対戦募集一覧", color=0x668cff)
      for i in range(len(result)):
         embed1.add_field(name=str(i+1)+".", value=
         f'`チーム名`: {result[i][1]}\n`対戦開始日時`: {result[i][2]}`平均レート`: {result[i][7]}\n'
         f'`試合数`: {result[i][4]}`コメント`: {result[i][5]}\n'
         f'`連絡先`: <@{result[i][0]}>`post_ID`:{result[i][6]}'
         , inline=False)
      await message.channel.send(embed=embed1)


#今日-1日のレコードより古いレコードを削除　一定間隔で実行するか、各コマンドが呼ばれたときに一緒に実行するか検討
async def post_refresh():
   c.execute('DELETE from database WHERE date_and_time <= datetime("now", "-1 day", "localtime")')
   con.commit()
   print('deleted old records')

#指定チャンネルの全メッセージを削除
async def delete_allposts():
   channel = client.get_channel(BOSYUCHANNEL_ID)
   await channel.purge()
   print("delete_allposts Done")

@tasks.loop(seconds=60)
async def update_posts():
   #削除パート
   await delete_allposts()
   #投稿パート
   await post_list()
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
