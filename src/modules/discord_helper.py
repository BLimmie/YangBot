from discord import Embed, Member, Role
from typing import List

async def add_roles(member: Member, roles: List[Role]):
    """
    Give a member roles

    args:
    member = member object
    roles = list of role objects to give
    """
    await member.add_roles(*roles)


async def change_nickname(member: Member, name: str):
    """
    Change a member's nickname

    args:
    member = member object
    name (string) = nickname to give member
    """
    await member.edit(nick=name)

async def kick_member(member: Member):
    """
    Kicks a member

    args:
    member = member object
    """
    await member.kick()


async def try_send(member: Member, message):
    try:
        await member.send(message)
    except:
        print("Unable to send PM")

def generate_embed(embed_dict: dict) -> Embed:
    '''
    Creates an Embed object using the given dictionary. The dictionary has no required values, and every key is optional (may be absent or assigned to `None`).\n
    Note the following type requirements for each key. See the official Embed documentation for more info.
    ```python
    str: title, description, url, image, thumbnail
    int: color
    dict: author, footer
    List[dict]: fields
    datetime: timestamp
    ```
    '''
    # safe_keys refers to what you can pass in Embed's initializer directly, unsafe_keys refers to the attributes that may only be modified via methods.
    safe_keys = {}
    unsafe_keys = {}
    for key, value in embed_dict.items():
        match key:
            case 'author' | 'fields' | 'footer' | 'image' | 'thumbnail':
                unsafe_keys[key] = value
            case _:
                safe_keys[key] = value

    embed = Embed(**safe_keys)
    for key, value in unsafe_keys.items():
        match key:
            case 'author' if isinstance(value, dict):
                embed.set_author(
                    name=value['name'],
                    url=value.get('url'),
                    icon_url=value.get('icon_url')
                )
            case 'fields' if isinstance(value, List):
                for item in value:
                    embed.add_field(
                        name=item['name'],
                        value=item['value'],
                        inline=item.get('inline')
                    )
            case 'footer' if isinstance(value, dict):
                embed.set_footer(
                    text=value.get('text'),
                    icon_url=value.get('icon_url')
                )
            case 'image':
                embed.set_image(url=value)
            case 'thumbnail':
                embed.set_thumbnail(url=value)
            case _:
                pass
                #print('Unknown Embed key given', key, 'with value', value)

    return embed
