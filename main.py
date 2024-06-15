import sys
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import hashlib
from termcolor import colored

def fetch_html(url):
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html_content = driver.page_source
    driver.quit()

    return html_content

def extract_poll_url_aft(html):
    soup = BeautifulSoup(html, 'html.parser')
    iframe_tag = soup.find('iframe')
    if iframe_tag:
        srcdoc = iframe_tag.get('srcdoc', '')
        srcdoc_soup = BeautifulSoup(srcdoc, 'html.parser')
        body_tag = srcdoc_soup.body
        if body_tag and 'data-origin' in body_tag.attrs:
            data_origin = body_tag['data-origin']
            num = data_origin.split('/')[-1].split('.')[0]
            return f"https://pollsystem-aftonbladet.s3.amazonaws.com/polls/{num}.html"
    return None

def extract_vote_alternatives_aft(html):
    alternatives = {}
    soup = BeautifulSoup(html, 'html.parser')
    vote_div = soup.find('div', class_='votes')
    if vote_div:
        alternative_labels = vote_div.find_all('label')
        for label in alternative_labels:
            text = label.get_text()
            value = label.find_previous('input')['value']
            alternatives[text] = value
    return alternatives

def send_vote_request_aft(url, alternative_id, counter):
    poll_id = hashlib.md5(url.split('/')[-1].replace('.html', '').encode()).hexdigest()
    vote_url = f"https://pollsystem-aftonbladet.emakinaapps.se/api/v1/polls/vote/{poll_id}/{alternative_id}"
    response = requests.post(vote_url)
    if response.status_code == 200:
        print(colored(f"Vote {counter} sent successfully.", 'green'), end='\r')
    else:
        print(colored(f"Failed to send vote {counter}. Status code: {response.status_code}", 'red'), end='\r')

def print_title():
    title = """
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⣿⣬⣷⢦⢀⠀⠀⠀⠀⠀⠀⣰⣦⣞⣳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣀⣠⣤⣤⣄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⢽⣿⣿⣼⡆⡀⠀⢰⢸⣠⣿⣾⣷⠞⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣤⣤⣀⣀⡀⠀⠀⠀⠀⠀
⠀⣠⣴⣾⠟⠛⠉⠉⠉⠉⠛⣿⠶⠶⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠿⠯⣿⣷⠇⡀⢸⣼⣿⣿⣿⠃⠀⠀⠀⠀⠀⢀⣀⣤⡶⠾⠟⠛⠉⣉⣿⠟⠉⠉⠛⢻⡶⣦⣀⠀
⢰⣿⣍⠸⣷⡀⠀⠀⠀⠀⠀⠈⢷⡀⠀⠈⠉⠙⠓⠲⠶⣶⣤⣤⣀⣀⣀⣀⣀⣙⣛⣿⣿⣿⣿⣿⣍⣭⣠⣤⣤⣴⣶⣶⣾⣛⡉⠁⠀⠀⠀⣠⣾⠟⠁⠀⠀⠀⢀⣿⠇⠈⢻⣇
⠈⢿⣷⡄⠈⠻⣦⣀⠀⠀⠀⠀⠀⠙⣦⡀⠀⠀⠀⠉⠀⠚⢷⣌⣭⣽⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡉⠉⢉⠟⠛⢻⣷⣿⡿⠇⠀⠀⠀⣠⣾⠟⠁⠀⠀⠀⠀⣠⡿⠃⠀⢠⣾⡟
⠀⠀⠙⢿⣷⣄⡀⢉⠛⠷⣄⠀⠀⠀⠈⠻⣦⡀⣀⣤⣤⡀⠀⠙⢿⣶⡛⢩⡥⠻⣿⣇⢉⡅⠈⣿⠁⠀⠁⠠⣤⡞⢉⣤⣴⣦⣤⣴⣿⠟⠁⠀⠀⠀⢀⣠⡾⠋⠀⣠⣼⣿⠟⠃
⠀⠀⠀⠀⠉⠛⢿⣷⣔⠀⠈⠻⣄⠀⠀⠀⠘⢿⡏⢭⡙⣿⡆⠀⠀⠈⠻⣆⠈⠿⣿⣿⣼⢱⣀⣿⠟⠃⡰⠃⠀⠀⣿⡇⡶⢾⣿⡏⠀⠀⠀⢀⣠⡶⠟⢁⢀⣤⣾⠿⠋⠁⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⢿⣧⡀⠀⠈⢷⣄⠀⠀⠸⠷⣶⣾⡿⢷⣄⠀⠀⠀⠙⣷⣤⣼⣿⣿⣈⣿⠿⢷⣿⣇⣀⣠⡴⠿⠷⢶⠾⠛⠁⠀⢀⣴⡿⠋⠀⣠⣾⡿⠋⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣄⠀⠀⠙⢦⣀⠀⠀⠀⠀⠀⠀⠈⠻⢦⣤⣼⡿⠟⠋⠙⣿⣿⠟⠀⠀⢷⠙⡻⣷⣤⡀⠀⠀⠀⠀⢀⣰⡿⠋⠀⢀⣴⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣷⣤⡂⠀⠛⢷⣄⡀⠀⢀⣀⣤⣾⡿⠟⠋⡀⠀⢀⣴⠛⣿⣄⠤⠀⣠⡾⠃⠀⠙⢻⣷⣦⣤⣴⣟⣋⣀⣀⣴⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⠿⠷⠶⢶⡾⠿⠷⠿⣿⣿⣯⡀⠀⠀⠈⠳⠶⠴⣦⣿⡄⠰⠿⠋⠀⠀⠀⢀⣼⣿⠉⠙⠿⠿⠿⠿⠿⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⡙⢿⣦⣀⡀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⣀⣴⠞⣹⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣦⡉⠛⠿⢷⣦⣤⣤⣼⣦⣤⡴⠶⠛⠋⣡⣼⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠿⣷⣤⣤⣄⣠⣼⡿⢿⣶⣦⣶⣾⡿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢉⡉⠛⠛⠉⠀⠀⢈⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
  _____                                      _____             _   _     
 |  __ \                                    |  __ \           | | | |    
 | |  | | ___ _ __ ___   ___   ___ _ __ __ _| |  | | ___  __ _| |_| |__  
 | |  | |/ _ \ '_ ` _ \ / _ \ / __| '__/ _` | |  | |/ _ \/ _` | __| '_ \ 
 | |__| |  __/ | | | | | (_) | (__| | | (_| | |__| |  __/ (_| | |_| | | |
 |_____/ \___|_| |_| |_|\___/ \___|_|  \__,_|_____/ \___|\__,_|\__|_| |_|                                             
    """
    print(colored(title, 'light_magenta'))

if __name__ == "__main__":
    print_title()

    if len(sys.argv) != 2:
        print(colored("Usage: python script.py <URL>", 'yellow'))
        sys.exit(1)

    url = sys.argv[1]
    
    html_content = fetch_html(url)
    if "aftonbladet.se" in url:
        url = extract_poll_url_aft(html_content)
        html_content = fetch_html(url)
        alternatives = extract_vote_alternatives_aft(html_content)
    elif "pollsystem-aftonbladet" in url:
        alternatives = extract_vote_alternatives_aft(html_content)

    print(colored("Vote Alternatives:", 'cyan'))
    for alternative, value in alternatives.items():
        print(f"{alternative}: {value}")

    alternative_id = input(colored("Enter the ID of the alternative you want to vote for: ", 'yellow'))
    num_votes = int(input(colored("Enter the number of votes you want to send: ", 'yellow')))

    print(colored("Sending votes...", 'cyan'))
    for i in range(1, num_votes+1):
        if "aftonbladet" in url:
            send_vote_request_aft(url, alternative_id, i)
        elif "expressen" in url:
            send_vote_request_exp(url, alternative_id, i)
    
    print(colored(f"\nTotal {num_votes} votes sent.", 'cyan'))

