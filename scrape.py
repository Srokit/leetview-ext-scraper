import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *

# Strings that are mistakes in the problemset page often
NOT_ALLOWED_PROBLEM_IDS = [
    "problems",
]

WAIT_FOR_LINKS_TO_LOAD_SEC = 2

# NOTE: There is about 50 problems per page so multiply that by this
# number to get the total number of problems to scrape
# -1 means scrape all pages
MAX_NUM_PAGES_FOR_PROBLEMSET = -1

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

    # Chromedriver potentially requires these weird options
    # https://stackoverflow.com/questions/48450594/selenium-timed-out-receiving-message-from-renderer
    options.add_argument("--start-maximized"); # https://stackoverflow.com/a/26283818/1689770
    options.add_argument("--enable-automation"); # https://stackoverflow.com/a/43840128/1689770
    options.add_argument("--no-sandbox"); #https://stackoverflow.com/a/50725918/1689770
    options.add_argument("--disable-dev-shm-usage"); #https://stackoverflow.com/a/50725918/1689770
    options.add_argument("--disable-browser-side-navigation"); #https://stackoverflow.com/a/49123152/1689770
    options.add_argument("--disable-gpu"); #https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc

    driver = webdriver.Chrome(chrome_options=options)
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(10)
    print("Started Browser and Driver")
    return driver

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
    except Exception as e:
        print("Error getting original problemset page : ", e)
        driver.quit()
        return None

    page_index = 0
    cond = page_index < MAX_NUM_PAGES_FOR_PROBLEMSET
    if MAX_NUM_PAGES_FOR_PROBLEMSET == -1:
        cond = True
    while cond:
        # Get all the a tags with attribute href starting with /problems/* and is not equal to /problems/
        try:
            # Wait before getting problem links to let them load in
            print("Waiting for links to load...")
            time.sleep(WAIT_FOR_LINKS_TO_LOAD_SEC)
            print("Looking for problem links...")
            problem_links = driver.find_elements_by_xpath("//a[starts-with(@href, '/problems/') and not(@href='/problems/')]")
            for link in problem_links:
                try:
                    problem_id = link.get_attribute('href').split('/')[-2]
                    if problem_id in NOT_ALLOWED_PROBLEM_IDS:
                        continue
                    print("Adding problem id: {} to set".format(problem_id))
                    set_of_problem_ids.add(problem_id)
                except:
                    print("Saw a link not work")
                    continue
        except Exception as e:
            print("Error while trying to find problem links: ", e)
            print("Skipping to next page")
            page_index += 1
            continue

        try:
            # If more pages to scrape, click the next page button and repeat
            # The next page button has attribute aria-label="next"
            # if it has attribute disabled, then there are no more pages to scrape
            print("Looking for next page button...")
            next_page_button = driver.find_element_by_xpath("//button[@aria-label='next']")
            if not next_page_button.get_attribute('disabled'):
                next_page_button.click()
            else:
                print("Saw no next button. No more pages to scrape")
                break
        except Exception as e:
            print("Error while trying to find and click next button: ", e)
            print("Ending loop")
            break
        page_index += 1
        print("Moving to next page now at index: {}".format(page_index))

    driver.quit()
    return list(set_of_problem_ids)

