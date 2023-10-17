"""
Collect Problem IDs scraped from leetcode all problemset into an output pickle file
"""

import os
import pickle

from scrape import scrape_for_problem_ids

PROBLEM_IDS_PICKLE = 'problem_ids.pickle'

def main():
    problem_ids = scrape_for_problem_ids()
    if problem_ids is None:
        print("Error scraping for problem ids could not get any problem ids")
        return
    print("Scraped {} problem ids".format(len(problem_ids)))
    # Remove existing problem_ids.pickle
    try:
        os.remove(PROBLEM_IDS_PICKLE)
    except OSError:
        pass
    with open(PROBLEM_IDS_PICKLE, 'wb') as f:
        pickle.dump(problem_ids, f)

if __name__ == '__main__':
    main()

