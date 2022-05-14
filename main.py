import json
import os
import sys

import discord
from discord.errors import LoginFailure
from seebuoy import ndbc

from helpers import c_to_f, m_to_f, mps_to_kts
from exceptions import InvalidBuoyId, NoTokenError

# Creates token file if it doesnt exist
if os.path.exists("token.txt") != True:

    with open("token.txt", "w") as file:
        pass

with open("token.txt", "r") as file:
    TOKEN = file.read()

    print(f"TOKEN: {TOKEN}")

    if TOKEN == "":
        raise NoTokenError("\n\nYou did not supply a token in the token.txt file.\nInstructions for making a bot can be found here: https://discordpy.readthedocs.io/en/stable/discord.html")

# The last buoy that the user searched
with open("last_search.json", "r") as file:
    last_search = json.load(file)

bot = discord.Bot()

@bot.event
async def on_ready():
    print("Ready!")

def get_buoy(number):

    # Retrieve latest reading from buoy
    all_data = ndbc.real_time(number)

    # If the data returns None, it means there wasnt a buoy with that ID
    if type(all_data) == type(None):

        raise InvalidBuoyId(f"No buoy with ID {number}")

    data = all_data.iloc[0] # .iloc[0] retrieves the first row of the dataframe

    # We will return the buoy data in a dict
    data_dict = {}

    # Convert all measurements to imperial
    data_dict["wind_speed"] = mps_to_kts(
        data["wspd"]
    )

    data_dict["gust_speed"] = mps_to_kts(
        data["gst"]
    )

    data_dict["air_temp"] = c_to_f(
        data["atmp"]
    )

    data_dict["water_temp"] = c_to_f(
        data["wtmp"]
    )

    data_dict["wave_height"] = m_to_f(
        data["wvht"]
    )

    return data_dict

@bot.slash_command(description="Return data from specified buoy", guild_ids=[730614557600383066])
async def buoy(ctx, buoy_id = None):

    print("pog")

    author_id = str(ctx.author.id) # We need this to be a string for json

    # If they dont supply an id, we will use their previous search
    if buoy_id is None:

        # If we cant find their previous search, we tell them to enter it
        if author_id not in last_search:
            await ctx.respond("❌ **Please enter a buoy ID number!**")

            return

        buoy_id = last_search[author_id]

        print(type(buoy_id))

        print(f"DIJAIODJUIWJ WIDJ IWDJ: {buoy_id}")

    # Save this number to last search file
    last_search[author_id] = buoy_id

    with open("last_search.json", "w") as file:
        json.dump(last_search, file)

    try:
        data = get_buoy(buoy_id)

    except InvalidBuoyId:

        await ctx.respond("❌ Invalid buoy ID!")

        return

    message = f"""
__**Buoy {buoy_id}**__

⛵   **Wind:** {data["wind_speed"]} kts
💨   **Gust:** {data["gust_speed"]} kts
🌡️   **Air Temp:** {data["air_temp"]} F
♨   **Water Temp:** {data["water_temp"]} F
🌊   **Wave:** {data["wave_height"]} ft
"""

    await ctx.respond(message)

bot.run(TOKEN)
