import discord
import sqlite3
import re
import os
from dotenv import load_dotenv
from pprint import pprint

#.envファイル読み込み
load_dotenv()
 
TOKEN = os.environ['TOKEN']
 
client = discord.Client()

BOSYUCHANNEL_ID = os.environ['BOSYUCHANNEL_ID']
 
con = sqlite3.connect('db2.db')
c = con.cursor()
c.execute(
   'CREATE TABLE IF NOT EXISTS database(user_id INTEGER, user_name STRING, created_datetime TEXT, teamname, date_and_time , tier_average INTEGER, matches, comments )'
)
c.execute(
   'CREATE UNIQUE INDEX IF NOT EXISTS unq_idx_1 ON database (user_id,teamname)')
   
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

   if message.content.startswith('!show'):
      print('!show detected')
      return await post_show(message)

   if message.content.startswith('!mylist'):
      print('!mylist detected')
      return await post_mylist(message)

   if message.content.startswith('!list'):
      print('!list detected')
      return await post_list(message)

   if message.content.startswith('!refresh'):
      print('!refresh detected')
      return await post_refresh(message)

async def post_add(message):
   post_message = message.content.lstrip('!post')
   post_message = post_message.lstrip()
   post_message = post_message.split(',')
   if len(post_message)==5:
      c.execute('insert into database values(?, ?, ?, ?, ?, ?, ?, ?)',
                  [message.author.id, message.author.name, message.created_at, post_message[0], post_message[1], post_message[2], post_message[3], post_message[4]])
      # on conflict (user_id,teamname) do update set created_datatime'
      post_rowid = c.lastrowid 
      con.commit()
      embed=discord.Embed(title="Success!", description="投稿IDは`"+str(post_rowid)+"`です", color=0x00ff01)
      return await message.channel.send(embed=embed)
      # return await message.channel.send('登録完了 登録番号(ROWID):'+str(post_rowid)+'(削除用)')
   else:
      embed=discord.Embed(title="Error!", description="引数の数が間違っている可能性があります", color=0xff0000)
      return await message.channel.send(embed=embed)

async def post_delete(message):
   post_message = re.findall('^!delete +([0-9]+)$',message.content)
   if post_message:
      post_nakami = c.execute('SELECT * FROM database WHERE user_id=? and rowid=?',
                             [message.author.id, post_message[0]]).fetchone() 
      if post_nakami:
         c.execute('DELETE FROM database WHERE user_id=? and rowid=?',
              [message.author.id, post_message[0]])
         con.commit()
         embed=discord.Embed(title="Success!", description="登録日時:`"+post_nakami[2]+"`に登録された`"+post_message[0]+"`の投稿を削除しました", color=0x00ff01)
         return await message.channel.send(embed=embed)
         # return await message.channel.send('登録日時: '+post_nakami[2]+'に登録された'+post_message[0]+'の投稿を削除しました')
      else :
         embed=discord.Embed(title="Error!", description="`"+post_message[0]+"`は登録されていません。また削除は登録したユーザーのみ可能です", color=0xff0000)
         return await message.channel.send(embed=embed)
         # return await message.channel.send(post_message[0]+'は登録されていません。また削除は登録したユーザーのみ可能です')
   else:
      embed=discord.Embed(title="Error!", description="形式が違います`!delete [登録番号]`", color=0xff0000)
      return await message.channel.send(embed=embed)
      # return await message.channel.send('形式が違います""!delete [登録番号]""')      

async def post_mylist(message):
   # mypost = c.execute('SELECT user_id, teamname, date_and_time, tier_average, matches, comments, rowid FROM database WHERE user_id =?',[message.author.id]).fetchall()
   mypost = c.execute('SELECT user_id, teamname, date_and_time, tier_average, matches, comments, database.rowid, tier FROM database join tier_list using(tier_average) WHERE user_id =? order by database.rowid asc limit 10',[message.author.id]).fetchall()

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

         await message.channel.send(embed=embed)
   else:
      embed=discord.Embed(title="Error!", description="登録が見つかりませんでした", color=0xff0000)
      return await message.channel.send(embed=embed)

#今日-1日のレコードより古いレコードを削除　scheduleモジュールを使って一定間隔で実行するか、各コマンドが呼ばれたときに一緒に実行するか検討
async def post_refresh(message):
   c.execute('DELETE from database WHERE date_and_time <= datetime("now", "-1 day", "localtime")')
 
# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
