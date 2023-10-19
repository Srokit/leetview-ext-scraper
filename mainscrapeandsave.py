"""
Scrape description and solution for each problem so that
a separate script which does the OpenAI calls can proceed separately.
"""

import os
import pickle
import time

from aws_dyn_put import put_problem_hint_in_dyn_table

from scrape import scrape_description_and_solution
from scrape import init_driver

PICKLE_FILE_NAME = 'desc_and_sol.pickle'

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

def load_existing_desc_and_sol():
    try:
        with open(PICKLE_FILE_NAME, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("No existing desc and sol pickle file found. Creating new")
        return {}

def main():
    problem_ids = load_pickled_problem_ids()
    print("ABOUT TO SCRAPE {} PROBLEMS".format(len(problem_ids)))
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

    desc_and_sol_by_pid_dict = load_existing_desc_and_sol()
    for pid in problem_ids:
        if pid.strip() == '':
            continue
        if pid in desc_and_sol_by_pid_dict:
            print("SKIPPING Problem id: {} already scraped".format(pid))
            continue
        problem_description, problem_solution = scrape_description_and_solution(pid, driver)
        if problem_description is None or problem_solution is None:
            print("Error scraping for problem description and solution for problem id: {}".format(pid))
            continue

        desc_and_sol_by_pid_dict[pid] = {'desc': problem_description, 'sol': problem_solution}
        print ("Saved problem description and solution for problem id: {}".format(pid))

        num_scraped += 1
        if num_scraped % print_eta_interval == 0:
            time_elapsed = time.time() - start_time
            print(make_des_and_sol_scrape_progress_info_str(total_num, num_scraped, time_elapsed))

    print("Saved desc and solution now exist for {} problems".format(len(desc_and_sol_by_pid_dict)))

    print("Saving scraped problem descriptions and solutions to pickle file")

    # Remove if exists
    try:
        os.remove(PICKLE_FILE_NAME)
    except OSError:
        pass
    with open(PICKLE_FILE_NAME, 'wb') as f:
        pickle.dump(desc_and_sol_by_pid_dict, f)

if __name__ == '__main__':
    main()

