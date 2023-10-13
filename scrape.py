from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *

def problem_desc_url(pid):
    return 'https://leetcode.com/problems/{}/description/'.format(pid)

def problem_all_solutions_url(pid):
    return 'https://leetcode.com/problems/{}/solutions/'.format(pid)

def problem_single_solution_url(pid, sid):
    return 'https://leetcode.com/problems/{}/solutions/{}/'.format(pid, sid)

def scrape_description_and_solution(pid):
    print("START scrape")
    try:
        # Init driver
        options = Options()
        options.add_argument("--headless") # Runs Chrome in headless mode.
        driver = webdriver.Chrome(chrome_options=options)
        print("Started Browser and Driver")
        driver.get(problem_desc_url(pid))

        # Get the text content of the element with attribute data-track-load="description_content"
        driver.implicitly_wait(10)
        element = driver.find_element_by_xpath("//div[@data-track-load='description_content']")
        problem_description = element.text

        # Go to the page with all the problem solutions
        driver.get(problem_all_solutions_url(pid))

        # Get the first a tag with attribute href starting with /problems/${problemId}/solutions/* and does not equal /problems/${problemId}/solutions/
        solution_link = driver.find_element_by_xpath("//a[starts-with(@href, '/problems/{}/solutions/') and not(@href='/problems/{}/solutions/')]".format(pid, pid))

        # Follow the link to the solution page
        solution_link.click()

        # Get the problem solution text from a div where class="break-words"
        element = driver.find_element_by_xpath("//div[@class='break-words']")
        problem_solution = element.text

        return problem_description, problem_solution

    except Exception as e:
        print("Error: ", e)
    finally:
        driver.quit()
        print("END scrape")
