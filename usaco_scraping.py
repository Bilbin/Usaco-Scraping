from bs4 import BeautifulSoup
import requests
import os
from zipfile import ZipFile
import string

different_years = ["2011", "2012", "2013"]
problem_chars = string.ascii_uppercase + string.ascii_lowercase + " "
to_scrape = ["Bronze"]
main_r = requests.get("http://www.usaco.org/index.php?page=contests")

def scrape():
    soup = BeautifulSoup(main_r.content, "html.parser")
    panel = soup.find("div", {'class': 'panel'})
    years = [h2 for h2 in panel.findAll('h2') if "Season" in h2.text]

    for year in years:
        year_name = year.text[len("Previous Contests: ") + 1: -len(" Season")]
        year_path = os.path.join("Algorithms", "USACO", year_name)
    
        os.mkdir(year_path)
        raw_contests = [el for el in year.findAllNext() if el.name == 'a' or el.name == "h2"]
        contests = []

        i = 0
        current = raw_contests[i]
        while current.name != "h2":
            if current.name == "a":
                contests.append(current)
            i += 1
            current = raw_contests[i]
        
        scrape_contests(contests, year_path, year_name)

def scrape_contests(contests, year_path, year_name):
    for contest in contests:
        contest_path = os.path.join(year_path, contest.text[:-len(" Results")])
        os.mkdir(contest_path)
        contest_r = requests.get("http://www.usaco.org/" + contest['href'])

        if any(year in year_name for year in different_years):
            soup = BeautifulSoup(contest_r.content, 'html.parser')
            div = soup.find('div', {'class': 'panel'})
            link = "http://www.usaco.org/" + div.find('a')['href']
            contest_r = requests.get(link)
            
        soup = BeautifulSoup(contest_r.content, 'html.parser')
        chosen_contests = [h2 for h2 in soup.findAll('h2') if any(tier in h2.text for tier in to_scrape)]

        nexts = chosen_contests[0].findAllNext()
        problem_divs = []
        i = 0
        current = nexts[i]
        while current.name != "h2" and current.name != "h3":
            if current.name == 'div':
                try:
                    if current['class'] == ['panel', 'historypanel']:
                        problem_divs.append(current)
                except KeyError:
                    pass
            current = nexts[i]
            i += 1

        scrape_problem(problem_divs, contest_path)
        print("Scraped: " + year_name + " | " + contest.text[:-len(" Results")])
        
def scrape_problem(problem_divs, contest_path):
    for ind, problem_div in enumerate(problem_divs):
        raw_name = problem_div.b.text
        name = str(ind + 1) + ") " + "".join(char for char in raw_name if char in problem_chars)
        problem_path = os.path.join(contest_path, name)
        os.mkdir(problem_path)
        links = problem_div.findAll('a')
        problem_r = requests.get("http://www.usaco.org/" + links[0]['href'])
        soup = BeautifulSoup(problem_r.content, 'html.parser')
        desc = soup.find('div', {'class': 'problem-text'}).text
        
        with open(os.path.join(problem_path, "description.txt"), 'w') as f:
            f.write(desc)

        data_path = os.path.join(problem_path, 'test_data')
        os.mkdir(data_path)
        
        data_r = requests.get("http://www.usaco.org/" + links[1]['href'])

        with open("data.zip", "wb") as f:
            f.write(data_r.content)

        z = ZipFile("data.zip", 'r')
        z.extractall(data_path)

        solution_path = os.path.join(problem_path, "solution.py")
        with open(solution_path, 'w') as f:
            pass
        
        

scrape()
