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

from scrape_config import MODEL

MAX_RETRIES = 4

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

OPENAI_KEY = os.environ.get("OPENAI_KEY")
if OPENAI_KEY is None:
    raise Exception("OPENAI_KEY environment variable not set.")

def request_hints(problem_description, problem_solution):
    """
    Request a list of hints from the OpenAI API.
    """

    def create_system_message(desc, sol):
        return """
You are an interviewer for a software engineering position. You are interviewing a candidate. The candidate is working on the following problem:

{}

The solution to the problem is:

{}

Give the candidate a small hint that will help them solve the problem.
Do not give the candidate the full solution.
    """.format(desc, sol)

    openai.api_key = OPENAI_KEY

    limit_response_message = "Limit the response to 1 short sentence."

    user_asking_message = "I am stuck can I please have a hint?"

    @timeout(10)
    def run_completion(problem_description, problem_solution, cut_solution_in_half=False):
        # Use a timeout with request
        if cut_solution_in_half:
            problem_solution = problem_solution[:len(problem_solution)//2]
        sys_mess = create_system_message(problem_description, problem_solution)
        chat_completion = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": sys_mess,
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

    MAX_UNKNOWN_NUM_RETRIES = 3
    unknown_num_retries = 0
    cut_solution_in_half = False
    # retry MAX_RETRIES times
    for i in range(MAX_RETRIES):
        try:
            if i > 0:
                print("Retrying {} out of {} times".format(i, MAX_RETRIES))
            chat_completion = run_completion(problem_description, problem_solution, cut_solution_in_half=cut_solution_in_half)
            break
        except openai.error.InvalidRequestError as e:
            print("REQUEST HAS TOO MANY TOKENS")
            print("Cutting solution in half")
            cut_solution_in_half = True
            continue
        except TimeoutError:
            print("Timeout error, retrying...")
            continue
        except Exception as e:
            unknown_num_retries += 1
            print("Unkown Error: {}".format(e))
            if unknown_num_retries > MAX_UNKNOWN_NUM_RETRIES:
                raise Exception("Failed to get hint from OpenAI API. Retried {} times.".format(MAX_UNKNOWN_NUM_RETRIES))
            print("Trying again...")
            continue
    else:
        raise Exception("Failed to get hint from OpenAI API. Retried {} times.".format(MAX_RETRIES))

    responses = [c['message']['content'] for c in chat_completion['choices']]
    return responses

