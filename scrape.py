from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *

MAX_NUM_PROBLEMS_TO_SCRAPE = 25

def problem_desc_url(pid):
    return 'https://leetcode.com/problems/{}/description/'.format(pid)

def problem_all_solutions_url(pid):
    return 'https://leetcode.com/problems/{}/solutions/'.format(pid)

def problem_single_solution_url(pid, sid):
    return 'https://leetcode.com/problems/{}/solutions/{}/'.format(pid, sid)

# Const problemset all url
PROBLEMSET_ALL_URL = 'https://leetcode.com/problemset/all/'

def init_driver():
    options = Options()
    options.add_argument("--headless") # Runs Chrome in headless mode.
    driver = webdriver.Chrome(chrome_options=options)
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(10)
    print("Started Browser and Driver")
    return driver

def scrape_description_and_solution(pid):
    print("START scrape desc and sol for problem id: {}".format(pid))
    problem_description = None
    problem_solution = None
    try:
        # Init driver
        driver = init_driver()

        print("Going to problem description page")
        driver.get(problem_desc_url(pid))

        # Get the text content of the element with attribute data-track-load="description_content"
        element = driver.find_element_by_xpath("//div[@data-track-load='description_content']")
        problem_description = element.text

        print("Going to problem all solutions page")
        # Go to the page with all the problem solutions
        driver.get(problem_all_solutions_url(pid))

        # Get the first a tag with attribute href starting with /problems/${problemId}/solutions/* and does not equal /problems/${problemId}/solutions/
        solution_link = driver.find_element_by_xpath("//a[starts-with(@href, '/problems/{}/solutions/') and not(@href='/problems/{}/solutions/')]".format(pid, pid))

        print("Going to problem solution page")
        # Follow the link to the solution page
        solution_link.click()

        # Get the problem solution text from a div where class="break-words"
        element = driver.find_element_by_xpath("//div[@class='break-words']")
        problem_solution = element.text

    except Exception as e:
        print("Error: ", e)
    finally:
        driver.quit()
        print("END scrape")

    return problem_description, problem_solution

def scrape_for_problem_ids():
    "Returns a list of problem ids (strings) by scraping leetcode problem set page"

    set_of_problem_ids = set()

    try:
        driver = init_driver()
        driver.get(PROBLEMSET_ALL_URL)

        driver.save_screenshot('screenshot.png')

        page_index = 0
        while page_index < MAX_NUM_PROBLEMS_TO_SCRAPE:
            # Get all the a tags with attribute href starting with /problems/* and is not equal to /problems/
            problem_links = driver.find_elements_by_xpath("//a[starts-with(@href, '/problems/') and not(@href='/problems/')]")
            for link in problem_links:
                try:
                    problem_id = link.get_attribute('href').split('/')[-2]
                    print("Adding problem id: {} to set".format(problem_id))
                    set_of_problem_ids.add(problem_id)
                except:
                    print("Saw a link not work")
                    continue

            # If more pages to scrape, click the next page button and repeat
            # The next page button has attribute aria-label="next"
            # if it has attribute disabled, then there are no more pages to scrape
            # next_page_button = driver.find_element_by_xpath("//button[@aria-label='next']")
            break
            if not next_page_button.get_attribute('disabled'):
                next_page_button.click()
            else:
                break
            page_index += 1

    except Exception as e:
        print("Error: ", e)
        raise e

    return list(set_of_problem_ids)

