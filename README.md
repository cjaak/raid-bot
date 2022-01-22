# raid-bot

An intuitive way to manage Raids as an online community using a simple discord-bot.


## Installation

Create a .env file containing your bot token

```
BOT_TOKEN = "your-token"
```


### Requirements

The raid-bot required discord.py oder pycord 2.0 or higher

````commandline
pip install -r requirements.txt
````

## Usage

### Getting started
In order to start the bot use:

````commandline
python raid_bot/main.py 
````

### Usage in Discord

Due to the design of slash commands help for each parameter will be displayed alongside each option:

![Example: Raid-Command](demo-screenshots/slashcommand-usage.png)

Setting the time can be done by typing date and time e.g `22.01.2022 22:00` or `01/22/2022 9pm`.
It is also possible to specify the date by using the next day and a time e.g. `Friday 8pm`.
When there's only the time specified the event will be scheduled for this day.

![Example: Raid](demo-screenshots/example-raid.png)


