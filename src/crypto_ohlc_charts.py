import asyncio
import subprocess
import datetime
import time
import os
from random import randrange
from os import environ
from plotly import graph_objs
import discord
from PIL import ImageOps, Image
from pycoingecko import CoinGeckoAPI

#configuration options
if environ.get('discord_token') is not None:
    discord_token = os.environ['discord_token']
else:
    discord_token = ''
if environ.get('chart_bg_color') is not None:
    chart_bg_color = os.environ['chart_bg_color']
else:
    chart_bg_color = 'black'
if environ.get('target_currency') is not None:
    target_currency = os.environ['target_currency']
else:
    target_currency = 'usd' #valid currencies here: https://api.coingecko.com/api/v3/simple/supported_vs_currencies
if environ.get('bot_keyword') is not None:
    bot_keyword = os.environ['bot_keyword']
else:
    bot_keyword = '!c'
if environ.get('notification_auto_delete') is not None:
    notification_auto_delete = os.environ['notification_auto_delete']
else:
    notification_auto_delete = 15 #in seconds

#initialize things
chart_dir = './tmp/'
cg = CoinGeckoAPI()
go = graph_objs
all_coins_list = cg.get_coins_list()
valid_coingecko_currencies = cg.get_supported_vs_currencies()
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(prefix='', intents=intents)

def get_change(previous, current):
    '''
    Takes 2 numbers, returns their difference in percentage.
    '''
    if current == previous:
        return 0
    try:
        roso = (abs(current - previous) / previous) * 100.0
        rosod = "%.3f" % roso
        if float(current) < float(previous):
            rosod = -abs(rosod)
        return rosod
    except ZeroDivisionError:
        return 0

async def notification_handler(channel, msgtype, msgname, msgvalue):
    '''
    Notifies user on errors.
    '''
    embed=discord.Embed(title=msgtype, colour=0xffa500)
    embed.add_field(name=msgname, value=msgvalue, inline=False)
    msg = await channel.send(embed=embed)
    await asyncio.sleep(int(notification_auto_delete))
    await msg.delete()
    return

def remove_chart_file(file):
    '''
    Takes filepath, deletes file.
    '''
    print('deleting chart file ' + file)
    try:
        command1 = subprocess.run(f'rm {file}', capture_output=True, text=True, shell=True, check=False).stdout
        print(command1)
    except Exception as e:
        print(e)
        return 0
    return 1

def get_coingecko(ticker, currency):
    '''
    Takes crypto ticker, currency, returns OHLC data and ticker in uppercase.
    '''
    x = 0
    tickerid = ''
    while x < len(all_coins_list):
        if ticker.lower() == str(all_coins_list[x]['symbol'].lower()):
            tickerid = str(all_coins_list[x]['id'])
            print(tickerid)
            break
        x += 1
    try:
        ohlcdata = cg.get_coin_ohlc_by_id(tickerid, currency.lower(), 14)
    except Exception as e:
        print(e)
        return 0
    return ohlcdata, ticker.upper()

def validate_currency(currency):
    '''
    Checks if the currency is valid for coingecko.
    Takes currency, returns 1 if valid.
    '''
    if currency.lower() in valid_coingecko_currencies:
        return 1
    return 0

@client.event
async def on_ready():
    '''
    On discord client ready, this executes
    '''
    print('Logged in as', client.user.name)

@client.event
async def on_message(message):
    '''
    Processes messages. Needs message_content intent enabled on discord bot management.
    '''
    rmsg = message.content
    rmsg2 = rmsg.upper()
    channel = message.channel
    author = message.author.id
    alerthandled = 'init'
    epoch_time = int(time.time())
    userid = author

    if message.author == client.user:
        return

    if rmsg2.startswith(bot_keyword.upper()):
        #no legit request is that long
        check_currency = validate_currency(target_currency)
        if len(rmsg) > 12:
            return
        async with message.channel.typing():
            inputed = message.content[3:]
            params = inputed.split()
            num_params = len(params)
            tick = str(params[0])
            ticker = tick.upper()
            result = 'ok'
            chartcolor = chart_bg_color
            if num_params > 0:
                start_index = 1
#                timespan = str(params[1]).upper()
                for i in range(start_index, len(params)):
                    indicator = params[i].upper()
                    if indicator == 'WHITE':
                        print('chartcolor white')
                        chartcolor = 'white'
                    if indicator == 'BLACK':
                        print('chartcolor black')
                        chartcolor = 'black'

            if ticker == 'XBT':
                ticker = 'BTC'
            if check_currency != 1:
                print('Default set currency is not valid for coingecko. Using USD instead.')
                default_currency = 'usd'
            else:
                default_currency = target_currency
            if result != 'stock':
                try:
                    jsondata, tickerfinal = get_coingecko(ticker, default_currency)
                    result = 'crypto'

                except Exception as e:
                    print(e, ' cant find ticker, sending notification.')
                    result = 'nan'
                    alerthandled = 'yes'
                    await message.add_reaction('⚠')
                    fieldname = "**" + ticker + "** " + "ticker not found."
                    asyncio.ensure_future(notification_handler(channel, " ", fieldname, 'Please try again.'))

            if result == 'crypto':
                chart_name = "c_" + ticker + '_' + str(userid)[-2:] + str(randrange(884)) + str(message.channel.id)[-3:] + str(epoch_time)[-4:] +  ".png"
                chart_name2 = chart_name.replace('/','')
                chart_filepath = chart_dir + chart_name2

                i = 0
                ohlc_date = []
                ohlc_open = []
                ohlc_high = []
                ohlc_low = []
                ohlc_close = []
                while i < len(jsondata):
                    data_open = jsondata[i][1]
                    data_high = jsondata[i][2]
                    data_low = jsondata[i][3]
                    data_close = jsondata[i][4]
                    epochconverted = datetime.datetime.fromtimestamp(jsondata[i][0]/1000).strftime('%Y-%m-%d %H:%M:%S')
                    ohlc_date.append(epochconverted)
                    #print(jsondata[i])
                    if 'e' in str(data_open):
                        data_open = str("%.17f" % jsondata[i][1]).rstrip('0').rstrip('.')
                        #print(data_open)
                        ohlc_open.append(data_open)
                    else:
                        ohlc_open.append(jsondata[i][1])
                    if 'e' in str(data_high):
                        data_high = str("%.17f" % jsondata[i][2]).rstrip('0').rstrip('.')
                        ohlc_high.append(data_high)
                    else:
                        ohlc_high.append(jsondata[i][2])
                    if 'e' in str(data_low):
                        data_low = str("%.17f" % jsondata[i][3]).rstrip('0').rstrip('.')
                        ohlc_low.append(data_low)
                    else:
                        ohlc_low.append(jsondata[i][3])
                    if 'e' in str(data_close):
                        data_close = str("%.17f" % jsondata[i][4]).rstrip('0').rstrip('.')
                        ohlc_close.append(data_close)
                    else:
                        ohlc_close.append(jsondata[i][4])
                    i += 1
                #print(ohlc_open)
                fig = go.Figure(data=go.Candlestick(x=ohlc_date,
                                open=ohlc_open,
                                high=ohlc_high,
                                low=ohlc_low,
                                close=ohlc_close))
                fig.update_yaxes(anchor='free')
                fig.update(layout_xaxis_rangeslider_visible=False)
                fig.update_xaxes(ticks="outside", tickwidth=2, ticklen=7)
                fig.update_layout(yaxis = dict(exponentformat = 'none'))
                y_axis_title = tickerfinal + ' / ' + str(default_currency.upper())
                if chartcolor == 'black':
                    fig.update_layout(font_size=16, font_family="Arial", font_color="white", title_font_size=20, title_font_family="Arial", title_font_color="white")
                    fig.update_layout(paper_bgcolor='rgb(0,0,0)', plot_bgcolor='rgb(0,0,0)', xaxis= dict(showgrid=False), yaxis= dict(showgrid=False))
                if chartcolor == 'white':
                    fig.update_layout(font_size=16, font_family="Arial", font_color="black", title_font_size=20, title_font_family="Arial", title_font_color="black")
                    fig.update_layout(paper_bgcolor='rgb(255,255,255)', plot_bgcolor='rgb(255,255,255)', xaxis= dict(showgrid=False), yaxis= dict(showgrid=False))
                fig.update_yaxes(title_text=y_axis_title, position=0, ticks="outside", tickwidth=2, ticklen=10)
                fig.write_image(chart_filepath)
                img = Image.open(chart_filepath)
                border = (0, 90, 50, 45) # left, top, right, bottom
                dimg = ImageOps.crop(img, border)
                dimg.save(chart_filepath)

        if alerthandled == 'yes':
            print('sent alert already, pass')
        else:
            await channel.send('', file=discord.File(chart_filepath))
            print(remove_chart_file(chart_filepath))
        return

def Main():
    '''
    Starts discord loop
    '''
    client.run(discord_token)

if __name__ == "__main__":
    Main()
