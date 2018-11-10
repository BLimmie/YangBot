from trigger_class import Trigger, compile_phrases

# Phrases that trigger YangBot.
triggers = [
    Trigger(
        pattern=compile_phrases(["dank"]),
        response="I sure hope you're talking about dank memes and not that dank green!"
    ),
    Trigger(
        pattern=compile_phrases(["blaze"]),
        response="I sure hope you're talking about the pizza!"
    ),
    Trigger(
        pattern=compile_phrases(["alcohol", "vodka", "wine", "beer", "drunk", "whiskey", "beers"]),
        response="Reminder that underage drinking is prohibited at UCSB.",
        gauchito_only=True
    ),
    Trigger(
        pattern=compile_phrases(["mj", "420", "weed", "kush", "marijuana"]),
        response="Despite the passing of Prop 64, marijuana usage is prohibited at UCSB except for university-approved "
                 "research."
    ),
    Trigger(
        pattern=compile_phrases(["adderall", "adderal", "addy"]),
        response="If you need to study, go to the UCSB Library. Most people focus the best on the 8th floor."
    ),
    Trigger(
        pattern=compile_phrases(["drug", "acid", "lsd", "shrooms", "xanax", "coke", "cocaine"]),
        response="Substance abuse is prohibited at UCSB"
    ),
    Trigger(
        pattern=compile_phrases(["fire"]),
        response="If you need to study, go to the UCSB Library. Most people focus the best on the 8th floor."
    ),
    Trigger(
        pattern=compile_phrases(["party"]),
        response="Go back to studying",
        gauchito_only=True
    )
]
