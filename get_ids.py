import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv

base_url='https://www.avanza.se/aktier/lista.html'
PATH=r"C:\Program Files (x86)/chromedriver.exe." # Change this to your chromdriver path

#Last page can not be loaded on the website. Reversing the order of the website and extracting the first 100 fixes it.
def last_page(PATH):
	driver=webdriver.Chrome(PATH)
	driver.implicitly_wait(10)
	driver.get(base_url)
	search=driver.find_element_by_css_selector(".cookie-consent-btn")
	search.click()
	search_list=driver.find_element_by_xpath('//*[@id="main"]/div/div/div[5]/div/div[2]/div/div[6]/div[2]/div/div[2]/button/span[2]')
	search_list.click()
	driver.find_element_by_xpath('//*[@id="main"]/div/div/div[5]/div/div[2]/div/div[6]/div[2]/div/div[2]/ul/li/ul/li[1]').click()
	sleep(10)
	driver.find_element_by_xpath('//*[@id="main"]/div/div/div[5]/div/div[5]/div[1]').click()
	sleep(10)
	driver.find_element_by_xpath('//*[@id="main"]/div/div/div[5]/div/div[5]/div[1]/div/table[1]/thead/tr/th[2]/a').click()
	sleep(15)
	links=[]
	elems=driver.find_elements_by_class_name('orderbookName')
	for elem in elems:
	    links.append(elem.find_element_by_tag_name('a').get_attribute('href'))
	driver.quit()
	return links


def pages(PATH):
	'''Extract all links from all Swedish stocks'''
	driver=webdriver.Chrome(PATH)
	driver.implicitly_wait(10)
	driver.get(base_url)

	search=driver.find_element_by_css_selector(".cookie-consent-btn")
	search.click()

	search_list=driver.find_element_by_xpath('//*[@id="main"]/div/div/div[5]/div/div[2]/div/div[6]/div[2]/div/div[2]/button/span[2]')
	search_list.click()
	driver.implicitly_wait(20)
	sleep(10)
	driver.find_element_by_xpath('//*[@id="main"]/div/div/div[5]/div/div[2]/div/div[6]/div[2]/div/div[2]/ul/li/ul/li[1]').click() #This can be changed to get other stock data aside from "All Swedish"
	driver.implicitly_wait(10)
	sleep(10)
	show_more=driver.find_element_by_xpath('//*[@id="main"]/div/div/div[5]/div/div[5]/div[2]/button') 
	show_more.click()

	sleep(20)
	i=0
	while i<10:
	    sleep(30)
	    try:
	    	driver.find_element_by_xpath('//*[@id="main"]/div/div/div[5]/div/div[5]/div[2]/button').click()
	    except Exception as e:
	        break
	    i=i+1
	    
	sleep(15)
	links=[]
	elems=driver.find_elements_by_class_name('orderbookName')
	for elem in elems:
	    links.append(elem.find_element_by_tag_name('a').get_attribute('href'))
	driver.quit()
	return links

def get_ids(links):
	'''Extract the name and id for each stock'''
    name=[]
    ids=[]
    for link in links:
        id_match=re.search('[0-9]+', str(link))
        name_match=re.search('[^/]+(?=/$|$)',str(link))
        stock_id=int(id_match.group())
        stock_name=name_match.group()
        name.append(stock_name)
        ids.append(stock_id)
    return(ids,name)

def get_ticker(link):
	'''Finds the ticker for each stock'''
    r=requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')
    ticker=soup.find(class_='border XSText rightAlignText noMarginTop highlightOnHover thickBorderBottom noTopBorder').find('dd').text
    return ticker


def get_df():
	pages_list=pages(PATH)
	last_page_list=last_page(PATH)

	pages_list=[i for i in pages_list if i]
	last_page_list=[i for i in last_page_list if i]

	all_links=list(set(pages_list+last_page_list))

	ids,name=get_ids(all_links)

	df=pd.DataFrame({'name':name,'id':ids,'link':all_links})

	df['ticker']=df.apply(lambda x: get_ticker(x.link), axis=1)
	return df

if __name__ == "__main__":
	df=get_df()
	df.to_csv('stock_mapping',header=df.columns,index=False)