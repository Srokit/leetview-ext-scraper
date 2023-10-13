"""
OpenAI API for use to get hints for problems with the problem description
and one of the problem solutions.
"""

import os

import openai

OPENAI_KEY = os.environ.get("OPENAI_KEY")
if OPENAI_KEY is None:
    raise Exception("OPENAI_KEY environment variable not set.")

def request_hint(problem_description, problem_solution):
    """
    Request a hint from the OpenAI API.
    """

    openai.api_key = OPENAI_KEY

    system_message_content = """
You are an interviewer for a software engineering position. You are interviewing a candidate. The candidate is working on the following problem:

{}

The solution to the problem is:

{}

Give the candidate a small hint that will help them solve the problem.
Do not give the candidate the full solution.
    """.format(problem_description, problem_solution)

    limit_response_message = "Limit the response to 1 short sentence."

    user_asking_message = "I am stuck can I please have a hint?"

    chat_completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": system_message_content,
            },
            {
                "role": "system",
                "content": limit_response_message,
            },
            {
                "role": "user",
                "content": user_asking_message,
            },
        ],
    )

    # first_response = chat_completion.choices[0].message.content

    # get_rid_of_first_part_of_hint_message = "Remove first the part of this message where the interviewer explains that it will give a hint :\n{}".format(first_response)

    # chat_completion = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": get_rid_of_first_part_of_hint_message,
    #         },
    #     ],
    # )

    response = chat_completion.choices[0].message.content
    return response

