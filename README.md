## Crypto OHLC charts
Discord bot that generates crypto OHLC charts (Open, High, Low, Closing), using plotly and coingecko.

![](https://github.com/TivenTux/crypto-ohlc-charts/blob/main/demo.gif)

## Environment Variables

**discord_token** - your discord bot token (https://discord.com/developers/applications) <br>
**chart_bg_color** - Chart background color (options: black, white). Default black. <br>
**target_currency** - Set the currency for the charts. Default USD <br> 
**bot_keyword** - Keyword which the bot will respond to. Default '!c'<br>
**notification_auto_delete** - How many seconds to auto delete the error messages. Default 15<br>

__Message Content Intent will need to be enabled on Bot options under Privileged Gateway Intents on [discord developers panel](https://discord.com/developers/applications) in order for the command message & keyword to work.__

You can specify these environment variables when starting the container using the `-e` command-line option as documented
[here](https://docs.docker.com/engine/reference/run/#env-environment-variables):
```bash
docker run -e "discord_token=yyy"
```


## Building the container

After cloning this repository, you can run
```bash
docker build -t crypto-ohlc-charts .
```

## Running the container

```bash
docker run -d -e "discord_token=yyy" crypto-ohlc-charts

```
