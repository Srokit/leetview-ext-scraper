"""
Request open ai api with the saved pickle data from scraping the problem description and solution for each problem
"""

import pickle
import time

from aws_dyn_put import put_problem_hint_in_dyn_table

from scrape_openai import request_hints

HINT_JOINING_STRING = "##"

PICKLE_FILE = 'desc_and_sol.pickle'
EXISTING_PIDS_PICKLE_FILE = 'pids_in_db.pickle'

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

def load_desc_and_sol_dict_from_pickle():
    with open(PICKLE_FILE, 'rb') as f:
        return pickle.load(f)

def load_existing_pids_from_pickle():
    with open(EXISTING_PIDS_PICKLE_FILE, 'rb') as f:
        return pickle.load(f)

def main():
    desc_and_sol_dict = load_desc_and_sol_dict_from_pickle()
    existing_pids_set = load_existing_pids_from_pickle()
    total_num = len(desc_and_sol_dict) - len(existing_pids_set)
    print("ABOUT TO SCRAPE {} PROBLEMS".format(total_num))
    start_time = time.time()
    num_scraped = 0
    print_eta_interval = 20
    # Make driver for all pids
    for pid in desc_and_sol_dict:

        if pid in existing_pids_set:
            continue

        desc = desc_and_sol_dict[pid]['desc']
        sol = desc_and_sol_dict[pid]['sol']
        # Check if problem already in table
        print ("Requesting hint from OpenAi...")

        hints = request_hints(desc, sol)
        hints_joined = HINT_JOINING_STRING.join(hints)

        print("Got hint from OpenAi")

        success = put_problem_hint_in_dyn_table(pid, hints_joined)
        if success:
            print("Successfully put hint in table for problem id: {}".format(pid))
        else:
            print("Error putting hint in table for problem id: {}".format(pid))

        num_scraped += 1
        if num_scraped % print_eta_interval == 0:
            time_elapsed = time.time() - start_time
            if total_num > 0:
                print(make_des_and_sol_scrape_progress_info_str(total_num, num_scraped, time_elapsed))
            else:
                print("Scraped {} problems. Time elapsed: {} seconds".format(num_scraped, time_elapsed))

    print("Successfully put hints in table for {} problem ids".format(num_scraped))

if __name__ == '__main__':
    main()

