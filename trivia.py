import random

import jellyfish

from trivia_questions import trivia_list

TIMEOUT = 5 * 60

correct_answer_format = "Correct! The answer is %s"
incorrect_answer_format = "Wrong. The answer is %s"


async def trivia_question(client, channel, prev=None):
    trivia_id = get_random_trivia_question_id(prev)
    await client.send_message(channel, trivia_list[trivia_id][0])
    answer = await client.wait_for_message(
        timeout=TIMEOUT,
        channel=channel,
        check=(
            lambda msg: (msg.content == '$stoptrivia'
                         or
                         jellyfish.damerau_levenshtein_distance(
                             msg.content, trivia_list[trivia_id][1]) <= 1
                         )
        )
    )
    if answer is None:
        await client.send_message(channel, incorrect_answer_format % trivia_list[trivia_id][1])
        await trivia_question(client, channel, prev=trivia_id)
    elif answer.content == '$stoptrivia':
        await client.send_message(channel, "Stopping trivia")
    else:
        await client.send_message(channel, correct_answer_format % trivia_list[trivia_id][1])
        await trivia_question(client, channel, prev=trivia_id)


def get_random_trivia_question_id(prev):
    while (True):
        id = random.choice(list(trivia_list.keys()))
        if prev is None or id != prev:
            return id
