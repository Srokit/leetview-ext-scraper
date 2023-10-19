import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Options
from selenium.webdriver.chrome.service import Service as Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *

# Strings that are mistakes in the problemset page often
NOT_ALLOWED_PROBLEM_IDS = [
    "problems",
]

WAIT_FOR_LINKS_TO_LOAD_SEC = 1

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

CHROMEDRIVER_LOCATION = "/Users/srok/Dev/libs/chromedriver/chromedriver_mac64/chromedriver"

CHROME_LOCATION = "/Users/srok/Dev/libs/chromium/mac_arm-114.0.5735.133/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"

def login_to_leetcode(driver):
    print("START login")
    driver.get("https://leetcode.com/accounts/login/")
    time.sleep(3)
    driver.find_element(By.ID, "id_login").send_keys(os.environ['LC_USER'])
    driver.find_element(By.ID, "id_password").send_keys(os.environ['LC_PASS'])
    driver.find_element(By.ID, "signin_btn").click()
    time.sleep(3)
    print("Logged in")

def init_driver():
    options = Options()
    # options.add_argument("--headless") # Runs Chrome in headless mode.

    # # Chromedriver potentially requires these weird options
    # # https://stackoverflow.com/questions/48450594/selenium-timed-out-receiving-message-from-renderer
    # options.add_argument("--start-maximized"); # https://stackoverflow.com/a/26283818/1689770
    # options.add_argument("--enable-automation"); # https://stackoverflow.com/a/43840128/1689770
    # options.add_argument("--no-sandbox"); #https://stackoverflow.com/a/50725918/1689770
    # options.add_argument("--disable-dev-shm-usage"); #https://stackoverflow.com/a/50725918/1689770
    # options.add_argument("--disable-browser-side-navigation"); #https://stackoverflow.com/a/49123152/1689770
    # options.add_argument("--disable-gpu"); #https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc

    # Set chromedriver location to CHROMEDRIVER_LOCATION
    # set chrome location
    # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    options.binary_location = CHROME_LOCATION
    service = Service(CHROMEDRIVER_LOCATION)
    # set chromedriver location
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(10)
    print("Init driver done")

    login_to_leetcode(driver)

    return driver

def maybe_close_out_of_modal(driver):
    # If the modal is on screen, with a button with text content contains "Try Out", click it
    try:
        print("Looking for modal")
        driver.implicitly_wait(2)
        MODAL_CLASS_CONTAINS = "z-base-9 absolute right-4 top-4 cursor-pointer"
        # Find modal div whose class contains text MODAL_CLASS_CONTAINS
        modal = driver.find_element(By.XPATH, "//div[contains(@class, '{}')]".format(MODAL_CLASS_CONTAINS))
        print("Found modal")
        modal.click()
        print("Clicked modal")
    except NoSuchElementException as e:
        print("No modal found")

def scrape_description_and_solution(pid, driver):
    print("START scrape desc and sol for problem id: {}".format(pid))
    problem_description = None
    problem_solution = None
    try:

        print("Going to problem description page")
        driver.get(problem_desc_url(pid))

        maybe_close_out_of_modal(driver)

        # This may be a locked problem therefor set a low implicit wait to see it quick
        driver.implicitly_wait(1)
        # Get the text content of the element with attribute data-track-load="description_content"
        element = driver.find_element(By.XPATH, "//div[@data-track-load='description_content']")
        # Back to normal
        driver.implicitly_wait(10)
        problem_description = element.text

        print("Going to problem all solutions page")
        # Go to the page with all the problem solutions
        driver.get(problem_all_solutions_url(pid))

        # Get the first a tag with attribute href starting with /problems/${problemId}/solutions/* and does not equal /problems/${problemId}/solutions/
        solution_link = driver.find_element(By.XPATH, "//a[starts-with(@href, '/problems/{}/solutions/') and not(@href='/problems/{}/solutions/')]".format(pid, pid))

        print("Going to problem solution page")
        # Follow the link to the solution page
        solution_link.click()

        # Get the problem solution text from a div where class="break-words"
        element = driver.find_element(By.XPATH, "//div[@class='break-words']")
        problem_solution = element.text

    except Exception as e:
        print("Error: ", e)
    finally:
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
        # Get all the a tags with attribute href starting with /problems/* and is not equal to /problems/ and whose class attribute does not contain the class opacity-60
        try:
            # Wait before getting problem links to let them load in
            print("Waiting for links to load...")
            time.sleep(WAIT_FOR_LINKS_TO_LOAD_SEC)
            print("Looking for problem links...")
            problem_links = driver.find_elements(By.XPATH, "//a[starts-with(@href, '/problems/')]")
            for link in problem_links:
                parts = link.get_attribute('href').split('/')
                if len(parts) < 2:
                    print("LINKPROB: Not have problem_id")
                    continue
                problem_id = parts[-1]
                if problem_id.startswith('?'):
                    print("LINKPROB: ?")
                    continue
                if problem_id in set_of_problem_ids:
                    print("LINKPROB: duplicate: {}".format(problem_id))
                    continue
                if problem_id in NOT_ALLOWED_PROBLEM_IDS:
                    print("LINKPROB: Not allowed: {}".format(problem_id))
                    continue
                class_attr = link.get_attribute('class')
                if class_attr is not None and 'truncate' in class_attr:
                    print("LINKPROB: Truncate: {}".format(problem_id))
                    continue
                if class_attr is not None and 'opacity-60' in class_attr:
                    print("LINKPROB: Premium: {}".format(problem_id))
                    continue
                print("LINKSUCC: {}".format(problem_id))
                set_of_problem_ids.add(problem_id)
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
            next_page_button = driver.find_element(By.XPATH, "//button[@aria-label='next']")
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

