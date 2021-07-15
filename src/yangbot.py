import traceback
from commands_refactor import command_on_message
from auto_on_message_refactor import auto_on_message


class YangBot():
    def __init__(self, bot, conn, config):
        """
        Initialization of all data
        """
        self.debug = False
        self.bot = bot
        self.conn = conn
        self.config = config
        self.roles = {
        "Fitness Peeps": 526130516324515842,
        "IV Dining": 508531374224048135,
        "Lib Sessions": 518908406057402388,
        "Dining Peeps": 494572009590882304,
        "Contributed": 499745117746364417,
        "Gaucho": 338230169875775499,
        "Visitor": 499744895532007434,
        "Prospective": 515666723563896833,
        "Gauchito": 458155146950475787,
        "Faculty": 481244587373887488,
        "Friendo": 338236189738008576,
        "Contributors": 366139942507905024,
        "Server Legacy": 462526711607721994,
        "Yangbot Interns": 507431677954490370,
        "Yangbot Devs": 498616292455219210,
        "Demimod": 495835874257534987,
        "Admins": 322140419448242176,
        "Club Officers": 270730327469719553,
        "2021": 557352577814233158,
        "2023": 557347165547003951,
        "Timeout": 557351724566708274,
        "Muted": 500037399494262825
        }
        self.command_on_message_list = {}
        self.auto_on_message_list = {}
        
        for action in command_on_message.__subclasses__():
            action.bot = bot
            action.conn = conn
            action.config = config
            action.guildRoles = self.roles
            self.command_on_message_list[action.__name__] = action()
    
        for action in auto_on_message.__subclasses__():
            action.bot = bot
            action.conn = conn
            action.guildRoles = self.roles
            self.auto_on_message_list[action.__name__] = action()

    async def run_command_on_message(self, message):
        command = message.content.split()[0][1:]
        if command in self.command_on_message_list:
            return await self.command_on_message_list[command].proc(message, message.created_at, message.author)
            
    async def run_auto_on_message(self, message):
        if message is not None:
            for key, func in self.auto_on_message_list.items():
                try:
                    return await func.proc(message,message.created_at,message.author)
                except Exception:
                    traceback.print_exc()
                    assert False
                    
