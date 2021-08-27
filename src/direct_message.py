from src.tools.botfunction import BotFunction
import discord
from discord.utils import get
import psycopg2
import random
import string
import smtplib
from src.modules.db_helper import member_exists, connection_error, refresh_member_in_db

class direct_message(BotFunction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message, *args, **kwargs):
        raise NotImplementedError

class introduction(direct_message):
    """
    Introduction DM Message
    DM Message to Try Again for Gaucho or Prospective Role
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    async def action(self, message):
        # FIX: CHANNEL ID
        if (message.channel.id == 876950801795391518 and message.content[0] == '1') or 'try again' in message.content.lower():
            await message.author.send('Current Students: Please respond to this message with your UCSB email \nProspective Students: Please respond with "Prospective"')

class email(direct_message):
    """
    Send Email Verification Code
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message, *args, **kwargs):
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)) and ('@ucsb.edu' or 'prospective' in message.content.lower()):
                conn = self.bot.conn
                cur = conn.cursor()
                random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not member_exists(conn, message.author.id, True):
                    if "'" in message.author.display_name: 
                        # Helps to insert display names containing apostrophes
                        cur.execute(f"""INSERT INTO {'test'} VALUES ('{message.author.id}','{message.author.display_name.replace("'", "''")}', '{''}', 
                                    '{message.content}', '{random_code}')""")
                    else: 
                        cur.execute(f"""INSERT INTO {'test'} VALUES ('{message.author.id}','{message.author.display_name}', '{''}', 
                                    '{message.content}', '{random_code}')""")
                    conn.commit()

                    # Send Email
                    gmail_user = 'yangbot.ucsb@gmail.com'
                    gmail_password = 'YangBot1234'

                    sent_from = gmail_user
                    to = message.content    # new member's email
                    subject = f'UCSB Discord Verification'
                    body = f'\n Hello UCSB Discord User, \n\n Copy and paste this code to verify this email address: \n\n {random_code} \n\n Best,\n UCSB Discord'

                    email_text = """\
                    From: %s
                    To: %s
                    Subject: %s

                    %s
                    """ % (sent_from, ", ".join(to), subject, body)

                    try:
                        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                        smtp_server.ehlo()
                        smtp_server.login(gmail_user, gmail_password)
                        smtp_server.sendmail(sent_from, to, email_text)
                        smtp_server.close()
                        print ("Email sent successfully!")
                        await message.author.send('Check your email for a Verification Code. Type that code here:')
                    except Exception as ex:
                        print('@ucsb Error')
                        print ("Something went wrong….", ex)

class wrong_email(direct_message):
    """
    Send Try Again for Email Verification Code Message
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message, *args, **kwargs):
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)) and ('@ucsb.edu' or 'prospective' not in message.content.lower()):
            await message.author.send('Sorry, you were not approved. If you think this was a mistake, please try again. Type "Try Again" to retry for approval.')

class role(direct_message):
    """
    Add Gaucho or Prospective Role
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message, *args, **kwargs):
        conn = self.bot.conn
        client = self.bot.client
        
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            try:
                # gets member info from server
                # FIX: GUILD ID
                # guild = client.get_guild(bot.config["server_id"])
                guild = client.get_guild(857393796621795353) # ME Server ID
                cur = conn.cursor()
                for user in guild.members:
                    if user == message.author:
                        m = user
                cur.execute(f"SELECT * FROM {'test'} where id = '{m.id}'")
                member = cur.fetchone()

                # test["code"] in message
                if member[4] in message.content.upper(): 
                    # Gaucho role for UCSB students
                    if '@ucsb.edu' in member[3]: # checks test["email"]
                        member_role = get(m.guild.roles, name='Gaucho')
                        await m.add_roles(member_role)
                        await m.send('Gaucho role added')
                    # Prospective role for other
                    else:                        
                        member_role = get(m.guild.roles, name='Prospective')
                        await m.add_roles(member_role)
                        await m.send('Prospective role added')
                    refresh_member_in_db(conn, member, self.bot.roles, True)

            except Exception as e:
                print('role error')
                print ("Something went wrong….", e)
                connection_error(e, conn)