from typing import List, Pattern
import re


class Trigger:
    def __init__(self, pattern: Pattern, response: str, gauchito_only=False):
        self.pattern = pattern
        self.response = response
        self.gauchito_only = gauchito_only

    def check(self, message: str):
        return self.pattern.search(message) is not None


def find_response(triggers: List[Trigger], message: str, is_gauchito: bool):
    """
    Returns the first matching trigger in a list of triggers given the message contents and whether or not the author
    is a gauchito.

    Returns None if the message matches none of the triggers
    """
    for trigger in triggers:
        if trigger.gauchito_only and not is_gauchito:
            continue
        if trigger.check(message):
            return trigger.response
    return None


def compile_phrases(phrases: List[str]):
    """
    Compiles multiple phrases into a single regex that matches any of the input phrases surrounded by word boundaries.
    """
    # escape regex metacharacters and ignore repeated whitespace in multi-word phrases
    phrases = [re.escape(phrase).replace(r"\ ", r"\s+") for phrase in phrases]

    return re.compile(r"\b(?:{})\b".format("|".join(phrases)))
