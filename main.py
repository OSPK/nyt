from googlesearch import search
ser = search('intitle:pakistan site:nytimes.com', tbs='qdr:y', pause=3)

for result in ser:
    print(result)



# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# from selenium import webdriver

# search_query = "intitle:pakistan site:nytimes.com"
# # search_query = search_query.replace(' ', '+') #structuring our search query for search url.
# browser = webdriver.Chrome()


# for i in range(20):
#     browser.get("https://www.google.com/search?q=" + search_query + "&start=" + str(10 * i))
#     matched_elements = browser.find_elements_by_xpath('//a')
#     if matched_elements:
#         matched_elements[0].click()
#         break