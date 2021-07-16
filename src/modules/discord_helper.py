async def add_roles(member, roles):
    """
    Give a member roles

    args:
    member = member object
    roles = list of role objects to give
    """
    await member.add_roles(*roles)


async def change_nickname(member, name):
    """
    Change a member's nickname

    args:
    member = member object
    name (string) = nickname to give member
    """
    await member.edit(nick=name)

async def kick_member(member):
    """
    Kicks a member

    args:
    member = member object
    """
    await member.kick()


async def try_send(member, message):
    try:
        await member.send(message)
    except:
        print("Unable to send PM")
