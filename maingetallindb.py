"Get all the problems already in db and save their pids to a pickle file set"

import os
import pickle

from aws_dyn_put import get_all_pids_in_dyn_table

PICKLE_FILE = 'pids_in_db.pickle'

def main():
    pids = get_all_pids_in_dyn_table()
    print("Got {} pids".format(len(pids)))
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(pids, f)

if __name__ == '__main__':
    main()

