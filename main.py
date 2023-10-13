from scrape import scrape_description_and_solution
from scrape import scrape_for_problem_ids
from scrape_openai import request_hint
from aws_dyn_put import put_problem_hint_in_dyn_table

def main():
    problem_ids = scrape_for_problem_ids()
    if problem_ids is None:
        print("Error scraping for problem ids could not get any problem ids")
        return
    success_pids_set = set()
    for pid in problem_ids:
        problem_description, problem_solution = scrape_description_and_solution(pid)
        print("====PROBLEM DESCRIPTION====")
        print(problem_description)
        print("====PROBLEM SOLUTION====")
        print(problem_solution)

        print ("Requesting hint from OpenAi...")

        hint = request_hint(problem_description, problem_solution)
        print("====HINT====")
        print(hint)

        success = put_problem_hint_in_dyn_table(pid, hint)
        if success:
            print("Successfully put hint in table for problem id: {}".format(pid))
            success_pids_set.add(pid)
        else:
            print("Error putting hint in table for problem id: {}".format(pid))

    print("Successfully put hints in table for problem ids:\n{}".format(list(success_pids_set)))

if __name__ == '__main__':
    main()

