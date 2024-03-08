import requests
from jobMatcher.jobs import *

if __name__ == '__main__':
    JOB_KEYWORDS = 'risk management python'
    LOCATION = 'NY'
    SITE = 'USA'

    job_results_dict = get_jobs(JOB_KEYWORDS, LOCATION, SITE)

    max_salary_idx = max_salary_job(job_results_dict)

