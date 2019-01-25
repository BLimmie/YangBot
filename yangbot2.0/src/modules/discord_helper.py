import discord

async def add_roles(member, roles):
    await member.add_roles(*roles)

async def change_nickname(member, name):
    await member.edit(nick=name)