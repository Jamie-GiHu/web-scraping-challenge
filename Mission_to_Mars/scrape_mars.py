from bs4 import BeautifulSoup as bs
from time import sleep
import pandas as pd
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)

# Defining scrape function that executes all scraping functions below 
# and to return data in 1 Python dictionary
def scrape():
    browser = init_browser()
    scraped_data = {}

    # Retrieve NASA Mars News and store results in a variable
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)
    sleep(5)
    soup = bs(browser.html, "html.parser")
    results = soup.find_all("li",class_="slide")
    news_title = results[0].find("div",class_="content_title").text
    news_p = results[0].find("div",class_="article_teaser_body").text
    news_all = [news_title, news_p]

    # Retrieve JPL Mars Space Images - Featured Image and store results in a variable
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    sleep(1)
    soup = bs(browser.html, "html.parser")
    transform = soup.article["style"]
    start = transform.rfind("url('") + len("url('") 
    end = transform.rfind("')")
    main_url = "https://www.jpl.nasa.gov"
    featured_image_url = main_url + transform[start:end]

    # Retrieve Mars Facts and store results in a variable
    url = "https://space-facts.com/mars/"
    tables = pd.read_html(url)
    mars_planet_profile_df = tables[0]
    mars_planet_profile_df.rename(columns={0: "", 1: "Mars"}, inplace=True) 
    mars_planet_profile_df.set_index([""], inplace=True)  
    mars_planet_profile_html = mars_planet_profile_df.to_html()
    mars_planet_profile_html = mars_planet_profile_html.replace("    <tr>\n      <th></th>\n      <th></th>\n    </tr>\n","")

    # Retrieve Mars Hemispheres and store results in a variable
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    sleep(1)
    soup = bs(browser.html, "html.parser")
    items = soup.find_all("div",class_="item")
    
    image_destinations = list()
    main_url = "https://astrogeology.usgs.gov"

    for item in items:
        link = list(item.children)[0]["href"]
        image_destinations.append(main_url + link)
    
    hemisphere_image_urls = list()

    for image_destination in image_destinations:
        browser.visit(image_destination)
        sleep(1)
        soup = bs(browser.html, "html.parser")
        title = soup.h2.text.replace(" Enhanced","")
        img_url = soup.li.a["href"]
        hemisphere_image_urls.append({"title": title, "img_url": img_url})

    # Store data in a dictionary
    scraped_data["news_title"] = news_all[0]
    scraped_data["news_paragraph"] = news_all[1]
    scraped_data["mars_featured_image"] = featured_image_url
    scraped_data["mars_facts"] = mars_planet_profile_html
    scraped_data["mars_hemispheres"] = hemisphere_image_urls

    # Quit the browser after scraping
    browser.quit()

    return scraped_data

# if running from command line, show the scraped data results
if __name__ == "__main__":
    result = scrape()
    print(result)