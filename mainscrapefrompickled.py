"""
Scrape the problems from leetcode.com w/ the problem IDs pickled from maincollectpids.py
"""

import pickle
import time

from aws_dyn_put import put_problem_hint_in_dyn_table
from aws_dyn_put import check_if_problem_in_dyn_table

from scrape import scrape_description_and_solution
from scrape import init_driver

from scrape_openai import request_hints

HINT_JOINING_STRING = "##"
PROB_DES_MAX_CHARS = 10

def make_des_and_sol_scrape_progress_info_str(num_total, num_scraped, time_elapsed):
    eta_sec = (num_total - num_scraped) * (time_elapsed / num_scraped)
    eta_min = eta_sec / 60
    eta_hr = eta_min / 60
    # floats to 2 decimal places
    eta_sec = "{:.2f}".format(eta_sec)
    eta_min = "{:.2f}".format(eta_min)
    eta_hr = "{:.2f}".format(eta_hr)
    time_elapsed = "{:.2f}".format(time_elapsed)
    return "Scraped {}/{} problems. Time elapsed: {} seconds. ETA: {} seconds, {} minutes, {} hours".format(num_scraped, num_total, time_elapsed, eta_sec, eta_min, eta_hr)

def load_pickled_problem_ids():
    with open('problem_ids.pickle', 'rb') as f:
        return pickle.load(f)

def main():
    problem_ids = load_pickled_problem_ids()
    print("ABOUT TO SCRAPE {} PROBLEMS".format(len(problem_ids)))
    success_pids_set = set()
    start_time = time.time()
    num_scraped = 0
    total_num = len(problem_ids)
    print_eta_interval = 20
    # Make driver for all pids
    try:
        driver = init_driver()
    except Exception as e:
        print("Error initializing driver: ", e)
        return
    for pid in problem_ids:
        # Check if problem already in table
        if check_if_problem_in_dyn_table(pid):
            print("SKIPPIING Problem id: {} already in table".format(pid))
            continue
        problem_description, problem_solution = scrape_description_and_solution(pid, driver)
        if problem_description is None or problem_solution is None:
            print("Error scraping for problem description and solution for problem id: {}".format(pid))
            continue
        print("====PROBLEM DESCRIPTION====")
        print(problem_description[:PROB_DES_MAX_CHARS])
        print("====PROBLEM SOLUTION====")
        print(problem_solution[:PROB_DES_MAX_CHARS])

        print ("Requesting hint from OpenAi...")

        hints = request_hints(problem_description, problem_solution)
        hints_joined = HINT_JOINING_STRING.join(hints)
        print("====HINTS====")
        print(hints_joined[:PROB_DES_MAX_CHARS])

        success = put_problem_hint_in_dyn_table(pid, hints_joined)
        if success:
            print("Successfully put hint in table for problem id: {}".format(pid))
            success_pids_set.add(pid)
        else:
            print("Error putting hint in table for problem id: {}".format(pid))

        num_scraped += 1
        if num_scraped % print_eta_interval == 0:
            time_elapsed = time.time() - start_time
            print(make_des_and_sol_scrape_progress_info_str(total_num, num_scraped, time_elapsed))

    print("Successfully put hints in table for {} problem ids".format(len(success_pids_set)))
    print("ProblemIds that were success:")
    print(success_pids_set)

if __name__ == '__main__':
    main()

