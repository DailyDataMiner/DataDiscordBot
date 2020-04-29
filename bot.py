import os
import json
import operator
import collections

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

## Appends a new record to the JSON
def addJSON(data, message):

    name = message[0]
    hour = int(message[1])

    data.update({name:hour})

    with open('stats.json', 'w') as jsonFile:
        json.dump(data, jsonFile)

    return 200

## Checks if user already exists in JSON
def checkJSON(data, name):

    try:
        ## No error occurs if it exists
        data[name]
        return 300
    except KeyError:
        return 200

## Gets JSON data
def getJSON():
    f = open('stats.json',)
    return json.load(f)

## Update stats json file
def updateJSON(message):

    with open('stats.json', 'r') as jsonFile:
        data = json.load(jsonFile)

    name = message[0]
    hour = int(message[1])

    try:
        data[name] = hour
    except KeyError:
        return 400

    with open('stats.json', 'w') as jsonFile:
        json.dump(data, jsonFile)

    return 200

## Checks to ensure the value requested is an int
def checkValue(value):
    try:
        int(value)
        return 200
    except ValueError:
        return 300

## Removes the callsign and leaves the remainder
def removeAddStart(message):
    ## Removes the callsign
    edit = message[4:]
    ## Removes trailing and leading whitespace
    stripped = edit.strip()

    ## Returns split string
    return stripped.split(',')

## Removes the callsign and leaves the remainder
def removeUpdateStart(message):
    ## Removes the callsign
    edit = message[7:]
    ## Removes trailing and leading whitespace
    stripped = edit.strip()

    ## Returns split string
    return stripped.split(',')

@client.event
async def on_message(message):

    ## Will respond to whatever channel the message was in
    textchannel = message.channel
    channel = client.get_channel(textchannel.id)

    ## Returns the latest stats for people on Animal crossing
    if message.content.startswith('!stats'):

        ## Figure out how to do the ... instead of this
        await channel.send('Getting list of current statistics on playtime')

        data = getJSON()

        ## Sorts it from most to least hours 
        itemize_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        sorted_data = collections.OrderedDict(itemize_data)

        list_str = ''

        ## Used for handling first and last person
        count = 1
        max_len = len(sorted_data)

        ## Iterates through sorted tuple and creates the message to be sent
        for (k, v) in sorted_data.items():
            tmp = ''
            if count == 1:
                tmp = str(count) + '. ' + k + ' has ' + str(v) + ' hours in Animal Crossing and has too many hours!\n'
            elif count == max_len:
                tmp = str(count) + '. ' + k + ' has ' + str(v) + ' hours in Animal Crossing and is dead last!\n'
            else:
                tmp = str(count) + '. ' + k + ' has ' + str(v) + ' hours in Animal Crossing!\n'
            
            list_str = list_str + tmp
            count += 1

        await channel.send(list_str)

    if message.content.startswith('!update'):

        ## Gets the part of the request that isn't the callsign
        request = removeUpdateStart(message.content)

        if checkValue(request[1]) != 200:
            await channel.send('Value is not a number!!!')
        else:
            ## Sends request to update JSON file
            status = updateJSON(request)
            if status == 200:
                await channel.send('Stats have been updated!')
            elif status == 300:
                await channel.send('User could not be found! Please add the user first.')

    if message.content.startswith('!add'):

        data = getJSON()

        request = removeAddStart(message.content)

        if checkValue(request[1]) != 200:
            await channel.send('Value is not a number!!!')
        else:
            if checkJSON(data, request[0]) != 200:
                await channel.send('User already exists!')
            else:
                status = addJSON(data, request)
                await channel.send('User has been inserted into the stats page!')

client.run(TOKEN)