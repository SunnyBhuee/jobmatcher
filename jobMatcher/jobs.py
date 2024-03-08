import numpy as np
import re
import requests
from bs4 import BeautifulSoup
from careerjet_api_client import CareerjetAPIClient


def indeed_url_generator(job_title, location):
    """
    This function takes a job title and location and generates the url for Indeed.ca.
    :param job_title: str - The job title
    :param location: str - The location of the job
    :return: str - url to Indeed.ca
    """
    job_title = job_title.replace(" ", "+")
    location = location.replace(" ", "+")

    url = f'https://ca.indeed.com/jobs?q={job_title}&l={location}'

    return url


def html_to_job_description(resp):
    """
    Takes response from Indeed.ca in text format and returns a job description.
    :param resp: str - response from Indeed.ca
    :return: str - job description
    """

    soup = BeautifulSoup(resp.text, 'html.parser')
    all_data = soup.find("ul", {"class": "jobsearch-ResultsList css-0"})

    return all_data


def url_opener(url):
    """
    Opens a UR using requests library.
    :param url: str URL of the website
    :return: str - response content
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    result = requests.get(url, headers=headers)

    return result


def jobs_api_user(keywords, location, site='CANADA'):
    """
        This function takes a job keywords and location and pulls jobs from CareerJet website using their API
        :param keywords: str - The job keywords
        :param location: str - The location of the job
        :param site: str - The site to be used i.e. Canada, USA, or UK
        :return: result_json - str - JSON response from CareerJet
        """

    site = site.upper()
    assert site in ['CANADA', 'USA', 'UK']

    temp = {'CANADA': 'en_CA', 'USA': 'en_US', 'UK': 'en_GB'}

    locale = temp[site]

    cj = CareerjetAPIClient(locale)

    result_json = cj.search({
        'location': location,
        'keywords': keywords,
        'affid': '213e213hd12344552',  # ignore
        'user_ip': '11.22.33.44',  # ignore
        'url': 'http://www.example.com',  # ignore
        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0'
    })

    return result_json


def empty_salary_handler(dict_, key_):
    """
    Function to handle empty salary data. It makes it zero in original dictionary.
    :param dict_ - Dictionary with salary data
    :param key_ - String key to be used i.e. salary, salary_max, or salary_min
    :return: updated dictionary with salary data
    """
    assert key_ in ['salary', 'salary_max', 'salary_min'], "Key must be in ['salary', 'salary_max', 'salary_min']"

    if key_ not in dict_.keys():
        dict_[key_] = '0'
    elif dict_[key_] == '':
        dict_[key_] = '0'
    else:
        dict_[key_] = '' + str(dict_[key_])

    return dict_


def get_jobs(keywords, location, site):
    """
    Function to retrieve job details from API.
    :param keywords - List of keywords
    :param location - Location of the job
    :param site - website location of the job you want

    :return: dictionary with all the job details for top results.
    """
    result_json = jobs_api_user(keywords, location, site)

    salaries = []
    min_salaries = []
    max_salaries = []
    locs = []
    job_titles = []
    job_desc = []
    sites = []
    urls = []
    employers = []

    text_salary = []

    for j in result_json['jobs']:

        j = empty_salary_handler(j, 'salary')
        j = empty_salary_handler(j, 'salary_max')
        j = empty_salary_handler(j, 'salary_min')

        text_salary.append(j['salary'])

        salary = re.findall(r'[\d]*[.][\d]+|[\d]*[\d]', j['salary'])
        salary = [float(i) for i in salary]

        min_salary = re.findall(r'[\d]*[.][\d]+|[\d]*[\d]', j['salary_min'])
        min_salary = float(min_salary[-1])
        # print('MIN Salary=',min_salary)

        max_salary = re.findall(r'[\d]*[.][\d]+|[\d]*[\d]', j['salary_max'])
        max_salary = float(max_salary[-1])
        # print('MAX Salary=', max_salary)

        if len(salary) > 1:
            salary = np.mean(salary)
        else:
            salary = salary[-1]

        # print('SALARY=',salary)

        if 'salary_type' in j.keys() and j['salary_type'] == 'H':
            salary = salary * 2000
            max_salary = max_salary * 2000
            min_salary = min_salary * 2000

        min_salaries.append(min_salary)
        salaries.append(salary)
        max_salaries.append(max_salary)
        locs.append(j['locations'])
        job_titles.append(j['title'])
        job_desc.append(j['description'])
        sites.append(j['site'])
        urls.append(j['url'])
        employers.append(j['company'])

        # print('-------\n\n')

    return {
        'min_salaries': min_salaries,
        'salaries': salaries,
        'max_salaries': max_salaries,
        'locs': locs,
        'job_titles': job_titles,
        'job_desc': job_desc,
        'sites': sites,
        'urls': urls,
        'employers': employers,
    }


def max_salary_job(job_results_dict):
    """
    Returns the results of the maximum salary job from the query.
    :param job_results_dict: Dictionary with the results of the query.
    :return: index of the highest salary job.
    """
    min_salaries = job_results_dict['min_salaries']
    salaries = job_results_dict['salaries']
    max_salaries = job_results_dict['max_salaries']
    locs = job_results_dict['locs']
    job_titles = job_results_dict['job_titles']
    job_desc = job_results_dict['job_desc']
    urls = job_results_dict['urls']
    employers = job_results_dict['employers']
    # print(max_salaries)

    # stats
    highest_salary = max(salaries)
    lowest_salary = min(salaries)
    highest_salary_idx = np.argmax(salaries)
    lowest_salary_idx = np.argmin(salaries)

    highest_max_salary = max(max_salaries)
    highest_max_salary_idx = np.argmax(max_salaries)

    lowest_min_salary = min(min_salaries)
    lowest_min_salary_idx = np.argmin(min_salaries)

    print(
        f'Highest salary job as {job_titles[highest_salary_idx]} found in {locs[highest_salary_idx]} at {employers[highest_salary_idx]}. ' +
        f'\n- Job title: ${highest_salary:,}/Yr  in .' +
        f'\n- Min salary: ${min_salaries[highest_salary_idx]:,}' +
        f'\n -Max salary: ${max_salaries[highest_salary_idx]:,}' +
        f'\n - Link: {urls[highest_salary_idx]}')

    print(f'Job description:\n{job_desc[highest_salary_idx]}')

    return highest_salary_idx

