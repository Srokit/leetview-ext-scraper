"""
OpenAI API for use to get hints for problems with the problem description
and one of the problem solutions.
"""

import os
import errno
import signal
import functools
import time

import openai

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator

NUM_CHOICES = 4

CURR_MODEL_CHOICE = "gpt-3.5-turbo"
# Uncomment for gpt-4 when not rate limited
# CURR_MODEL_CHOICE = "gpt-4"

OPENAI_KEY = os.environ.get("OPENAI_KEY")
if OPENAI_KEY is None:
    raise Exception("OPENAI_KEY environment variable not set.")

def request_hints(problem_description, problem_solution):
    """
    Request a list of hints from the OpenAI API.
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

    @timeout(4)
    def run_completion():
        # Use a timeout with request
        chat_completion = openai.ChatCompletion.create(
            model=CURR_MODEL_CHOICE,
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
            n=NUM_CHOICES,
        )
        return chat_completion

    # Retry once
    try:
        chat_completion = run_completion()
    except TimeoutError:
        time.sleep(1)
        print("Timeout error, retrying....")
        # This second time will raise error on error
        chat_completion = run_completion()

    responses = [c['message']['content'] for c in chat_completion['choices']]
    return responses

