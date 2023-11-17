import requests
import re
from bs4 import BeautifulSoup
import os
import subprocess


def remove_emojis(text):

    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  
                               u"\U0001F300-\U0001F5FF"  
                               u"\U0001F680-\U0001F6FF"  
                               u"\U0001F1E0-\U0001F1FF"  
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def scrape_internships(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table')

    internships = []

    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            a_tag = cell.find('a')
            if a_tag and a_tag.has_attr('href'):
                url = a_tag['href']

                if os.getenv('format') in url:
                    company_name = url.split('/')[-1]
                    row_data.append(company_name)
                else:
                    row_data.append(url)
            else:
                cell_text = remove_emojis(cell.get_text(strip=True))
                row_data.append(cell_text)

        if row_data:
            internships.append(row_data)

    return internships


def create_markdown_table(data):
    if not data or not data[0]:
        return "No data available."


    headers = ["Company", "Role", "Location", "Links", "Date Posted"]
    markdown = "| " + " | ".join(headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for row in data:
        row = [cell.replace('\n', '<br>') for cell in row]

        row[2] = row[2].replace(',', '<br>')

        row[3] = f'<a href="{row[3]}">Link</a>' if row[3].startswith('http') else row[3]

        markdown += "| " + " | ".join(row) + " |\n"

    return markdown

if __name__ =="__main__":

    intro_text = """
# Software Engineering Internships
    
    Welcome to the Software Engineering Internships repository! This repository serves as a resource for students and aspiring software engineers seeking internship opportunities in the tech industry. Our goal is to provide an up-to-date and easily accessible collection of internship positions across various companies and locations.
    
# About This Repository
    This repository is the result of an automated web scraping project that aims to compile information about available software engineering internships. We understand how challenging and time-consuming it can be to search for internships, and this project is here to simplify that process.
    
# What You'll Find Here
In this repository, you will find a curated list of software engineering internships, including details such as:
    
Company: The name of the company offering the internship.
    
Role: Specific title or role of the internship position.
    
Location: Geographical location or remote availability.
    
Application: Direct links to the application or job posting.
    
Date Posted: The date when the internship opportunity was listed.
    
# How It Works
Our script runs daily to scrape and update the list of internships from various reputable sources. The gathered data is then formatted into a Markdown table in the README.md file for easy viewing.
    
# Contributing
We welcome contributions to this project! If you have suggestions for additional sources to scrape, improvements to the script, or any other contributions, please feel free to open an issue or submit a pull request.
    
# Disclaimer
Please note that while we strive to keep the information accurate and up-to-date, we rely on external sources. Always verify the details on the respective company's website or contact point.
    
# License
This project is open source and available under <https://unlicense.org> .
    
    """
    URL = os.getenv('SCRAPER_URL')
    scraped_data = scrape_internships(URL)

    markdown_table = create_markdown_table(scraped_data)
    complete_readme = intro_text + "\n "+ markdown_table


    with open('Software_Engineering_Internships/README.md', 'w', encoding='utf-8') as file:
        file.write(complete_readme)

    subprocess.run(["git", "add", "README.md"])
    subprocess.run(["git", "commit", "-m", "Updated dataset"])
    subprocess.run(["git", "push"])
