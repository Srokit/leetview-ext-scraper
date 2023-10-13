from scrape import scrape_description_and_solution
from scrape_openai import request_hint
from aws_dyn_put import put_problem_hint_in_dyn_table

EX_PID = 'longest-substring-without-repeating-characters'

def main():
    problem_description, problem_solution = scrape_description_and_solution(EX_PID)
    print("====PROBLEM DESCRIPTION====")
    print(problem_description)
    print("====PROBLEM SOLUTION====")
    print(problem_solution)

    print ("Requesting hint from OpenAi...")

    hint = request_hint(problem_description, problem_solution)
    print("====HINT====")
    print(hint)

    success = put_problem_hint_in_dyn_table(EX_PID, hint)
    if success:
        print("Successfully put hint in table")
    else:
        print("Error putting hint in table")

if __name__ == '__main__':
    main()

