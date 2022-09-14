from dataclasses import dataclass, KW_ONLY

@dataclass
class help_text:
    '''
    A container for displaying the help text for a command.\n
    It is expected that every class will implement a `helptxt` classmethod and have it return a `help_text` object.
    '''
    name: str
    desc: str
    _: KW_ONLY
    mod_only: bool = False

    def field_dict(self, show_mod_commands: bool) -> dict | None:
        '''
        Returns a field-dictionary for the help text. If this command is mod_only and mod commands shouldn't be displayed, then the field-dict for INVALID_CMD is returned instead.
        '''
        return INVALID_CMD.field_dict(True) if self.mod_only and not show_mod_commands else {
            "name": self.name,
            "value": self.desc
        }

INVALID_CMD = help_text("Command unavailable", "This command is either restricted or doesn't exist.")
