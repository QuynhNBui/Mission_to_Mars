# import dependences

from bs4 import BeautifulSoup as bs
import os
from splinter import Browser
from selenium import webdriver
import requests
import pandas as pd
import time
import re

def init_browser():
    #chromedriver executable path
    executable_path = {'executable_path':'/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless = False)

def scrape():
    browser = init_browser()
    mars_data = {}

    #Visit Mars News URL
    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)
    time.sleep(1)
    html = browser.html
    soup = bs(html, 'html.parser')
    news_title = soup.find('div', class_ = "content_title").text
    news_p = soup.find('div', class_ = "rollover_description_inner").text
    mars_data['news_title']=news_title
    mars_data['news_p'] = news_p

    # Visit JPL Featured Space Image
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)
    time.sleep(1)
    jpl_html = browser.html
    jpl_soup = bs(jpl_html, 'html.parser')
    img_relative = jpl_soup.find('article')['style']
    img_relative_link = img_relative.split(" ")[1][5:-3]
    main_url = 'https://www.jpl.nasa.gov'
    feature_image_url = main_url + img_relative_link
    mars_data['feature_image_url'] = feature_image_url

    # Visit tiwter url for Mars Weather
    weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(weather_url)
    time.sleep(1)
    weather_html = browser.html
    weather_soup = bs(weather_html, 'html.parser')
    mars_weather_texts = weather_soup.find_all("p", class_ = "TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")
    for text in mars_weather_texts:
        if text.find(text = re.compile("InSight")):
            mars_weather_text = text.text
            break
    mars_weather_link = weather_soup.find('a', class_="twitter-timeline-link u-hidden").text
    mars_weather = mars_weather_text[0:-len(mars_weather_link)]
    mars_data['mars_weather'] = mars_weather

    # Mars Fact
    fact_url = "https://space-facts.com/mars/"
    browser.visit(fact_url)
    time.sleep(1)
    fact_html = browser.html
    fact_soup = bs(fact_html,"html.parser")
    scrape_table = pd.read_html(fact_url)
    mars_fact_df = scrape_table[1]
    mars_fact_df.rename(columns = {0:'Description', 1:'Value'}, inplace = True)
    mars_fact_df = mars_fact_df.set_index('Description')
    mars_fact_table = mars_fact_df.to_html()
    mars_data['mars_fact_table'] = mars_fact_table

    # Mars Hemisphere
    base_hemi_url = "https://astrogeology.usgs.gov"
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)
    time.sleep(1)
    hemi_html = browser.html
    hemi_soup = bs(hemi_html, 'html.parser')
    hemispheres = hemi_soup.find_all('a', class_="itemLink product-item")
    hemisphere_dict = []
    for result in hemispheres:
        try:
            title = result.find('h3').text
            #print(title)
            link = result['href']
            full_link = base_hemi_url + link
            response = requests.get(full_link)
            soup = bs(response.text, 'html.parser')
            #print(full_link)
        
            try:
                full_img_cl = soup.find('div', class_ = "downloads")
                full_img_href = full_img_cl.find('a')['href']
                hemisphere_dict.append({"title": title, "img_url":full_img_href})
            
            except AttributeError as e:
                print(e)
        except AttributeError as e:
            print(e)

    mars_data['hemisphere_img_url'] = hemisphere_dict
    browser.quit()

    return mars_data 