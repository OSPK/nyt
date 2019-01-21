import time, os
from selenium import webdriver
from paper import Story, db
import urllib
from tqdm import tqdm

# driver = webdriver.Chrome()

au = Story.query.all()

# for story in tqdm(au):
#     url = story.url
#     encurl = urllib.parse.quote_plus(url)
#     jfile = "newsdata/"+encurl+".txt"
#     exists = os.path.isfile(jfile)
#     if not exists:
#         driver.get(url)
#         driver.delete_all_cookies()
#         # Scroll page and wait 5 seconds
#         driver.execute_script("window.scrollTo(0,1000);")
#         textbox = driver.find_elements_by_css_selector("section[name='articleBody']")
#         f = open(jfile, "a")
#         for x in textbox:
#             f.write(x.text)

for story in tqdm(au):
    url = story.url
    encurl = urllib.parse.quote_plus(url)
    jfile = "newsdata/"+encurl+".txt"
    exists = os.path.isfile(jfile)
    if exists:
        f = open(jfile, "r")
        contents = f.read()
        contents = contents.replace("ADVERTISEMENT", "")
        contents = contents.replace("By The New York Times", "")
        contents = contents.replace("You have 4 free articles remaining.", "")
        contents = contents.replace("Subscribe to The Times", "")
        story.body = contents
        db.session.commit()