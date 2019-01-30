from typing import List, Callable
import re


class Trigger:
    def __init__(self, predicate: Callable[[str], bool], response: str, gauchito_only=False):
        self.predicate = predicate
        self.response = response
        self.gauchito_only = gauchito_only

    def check(self, message: str):
        return self.predicate(message)


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


def match_phrases(phrases: List[str]):
    """
    Compiles multiple phrases into a single predicate function that returns True if the input contain any of the
    phrases surrounded by word boundaries.
    """
    # escape regex metacharacters and ignore repeated whitespace in multi-word phrases
    phrases = [re.escape(phrase).replace(r"\ ", r"\s+") for phrase in phrases]

    pattern = re.compile(r"\b(?:{})\b".format("|".join(phrases)))

    def matches_phrases(message: str) -> bool:
        return pattern.search(message) is not None

    # for tests, make the source pattern available on the function
    matches_phrases._source = pattern

    return matches_phrases
