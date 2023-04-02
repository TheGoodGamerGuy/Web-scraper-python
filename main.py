import urllib.request
from bs4 import BeautifulSoup
import html2text
import requests, json
import re
from datetime import datetime as d
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import base64
import time
import sys

h = html2text.HTML2Text()
h.ignore_links = False


token = 'secret_HdCv1TcbUqHS2GBdu7GpSuVF0q9j2dW90ke82qQQWg1'
ConfigID = "df4e43f9e44b4242aab19f6a730e7e7d"
LinksID = "14df0d80706d4376b87f377de349ab4c"
databaseId = "3e48c4cf-edec-4e3c-a902-3bc5a66cb9f0"
# token = sys.argv[1]
# ConfigID = sys.argv[2]
# LinksID = sys.argv[3]
# databaseId = sys.argv[4]
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Links = ['https://www.ss.com/lv/electronics/photo-optics/search-result/', 'https://www.facebook.com/groups/129711374321613/?mibextid=6NoCDW', 'https://www.facebook.com/groups/841245589269264/?mibextid=6NoCDW', 'https://www.skelbiu.lt/skelbimai/technika/foto-optika/', 'https://www.andelemandele.lv/perles/elektronika/fototehnika/#order:created']

# Links = ['https://www.facebook.com/groups/129711374321613/?mibextid=6NoCDW']

# ss.lv listlistings
def PullInfo(link):
    print(f"Pulling info from \033[1;36;40m{link}\033[0m...")
    req = urllib.request.Request(link)
    with urllib.request.urlopen(req) as response:
        html_doc = response.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup

def FindssListings(soup, keywords):
    print("Looking for listings matching the keywords...")
    FoundListings=[]
    for i in keywords:
        Listings=[]
        for j in range(len(soup.find_all('div', {"class": "d1"}))):
            if str(soup.find_all('div', {"class": "d1"})[j]).lower().find(i)!=(-1):
                Listings.append(soup.find_all('div', {"class": "d1"})[j])
        FoundListings.append(Listings)
    return FoundListings

def DeleteNewLines(string):
    NewString=""
    for i in string:
        NewString+=i.replace("\n","")
    return NewString

def GetAllssLinks(KeyWords,Link):
    print("Getting all links for found listings...")
    Listings = FindssListings(PullInfo(Link), KeyWords)
    AllLinks=[]
    for i in range(len(Listings)):
        links=[]
        for j in range(len(Listings[i])):
            desc = str(h.handle(str(Listings[i][j])))
            LinkRight = desc[desc.rfind("(")+1:-3]
            link = DeleteNewLines(f"https://www.ss.com/{LinkRight}")
            links.append(link)
        AllLinks.append(links)
    return AllLinks

def GetEverythingss(Link):
    print("Getting all links...")
    AllWords=SearchList()
    KeyWords=[]
    for i in range(len(AllWords)):
        KeyWords.append(AllWords[i][0])
    return GetAllssLinks(KeyWords,Link)



# ss.lv listings price
def PullInfoPrice(link):
    print(f"Pulling price from \033[1;36;40m{link}\033[0m")
    req = urllib.request.Request(link)
    with urllib.request.urlopen(req) as response:
        html_doc = response.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup

def FindssPrice(soup):
    price=str(soup.find_all('td', {"class": "ads_price"}))
    price=re.findall(r'\d+', str(h.handle(price)).replace(" ", ""))
    if len(price)!=0:
        price=int(price.pop())
        return price
    else:
        return 99999

def GetGoodssListings(Link):
    print("Searching for all listings that match the price criteria")
    AllLinks=GetEverythingss(Link)
    GoodListings=[]
    AllWords=SearchList()
    for i in range(len(AllLinks)):
        # RightListings=[]
        for j in range(len(AllLinks[i])):
            soup=PullInfoPrice(AllLinks[i][j])
            price=FindssPrice(soup)
            if price<=int(AllWords[i][1]):
                print(f"\033[1;32;40mPrice matches the price criteria\033[0m, {price} < {AllWords[i][1]}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                RightListing=[]
                RightListing.append(AllLinks[i][j])
                RightListing.append(AllWords[i][0])
                RightListing.append(price)
                date = d.now()
                RightListing.append(date.strftime("%d-%m-%Y %H:%M:%S"))
                GoodListings.append(RightListing)
            else:
                print(f"\033[1;31;40mPrice does not match the price criteria\033[0m, {price} > {AllWords[i][1]}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        # GoodListings.append(RightListings)
    return GoodListings



# skelbiu
def PullInfoSelenium(Link):
    options = Options()
    options.add_argument("--headless")
    # driver = webdriver.Chrome('C:/Users/Aorus/Documents/ChromeDriver/chromedriver.exe', options=options)
    driver = webdriver.Firefox(options=options)
    driver.get(Link)
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def GetGoodSkelbiuListings(Link):
    print("Searching for all listings that match the price criteria")
    AllLinks=GetEverythingSkelbiu(Link)
    prices=FindSkelbiuPrice(Link)
    GoodListings=[]
    AllWords=SearchList()
    for i in range(len(AllLinks)):
        # RightListings=[]
        for j in range(len(AllLinks[i])):
            if prices[i][j]<=int(AllWords[i][1]):
                print(f"\033[1;32;40mPrice matches the price criteria\033[0m, {prices[i][j]} < {AllWords[i][1]}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                RightListing=[]
                RightListing.append(AllLinks[i][j])
                RightListing.append(AllWords[i][0])
                RightListing.append(prices[i][j])
                date = d.now()
                RightListing.append(date.strftime("%d-%m-%Y %H:%M:%S"))
                GoodListings.append(RightListing)
            else:
                print(f"\033[1;31;40mPrice does not match the price criteria\033[0m, {prices[i][j]} > {AllWords[i][1]}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        # GoodListings.append(RightListings)
    return GoodListings

def GetEverythingSkelbiu(Link):
    print("Getting all links...")
    AllWords=SearchList()
    KeyWords=[]
    for i in range(len(AllWords)):
        KeyWords.append(AllWords[i][0])
    return GetAllSkelbiuLinks(KeyWords,Link)

def GetAllSkelbiuLinks(KeyWords,Link):
    print("Getting all links for found listings...")
    Listings = FindSkelbiuListings(PullInfoSelenium(Link), KeyWords)
    AllLinks=[]
    for i in range(len(Listings)):
        links=[]
        for j in range(len(Listings[i])):
            soupy = BeautifulSoup(str(Listings[i][j]), 'html.parser')
            a = soupy.find('a')
            link = f"https://www.skelbiu.lt/{a.get('href')}"
            links.append(link)
        AllLinks.append(links)
    return AllLinks

def FindSkelbiuListings(soup, keywords):
    print("Looking for listings matching the keywords...")
    FoundListings=[]
    for i in keywords:
        Listings=[]
        for j in range(len(soup.find_all('li', {"class": "simpleAds"}))):
            if str(soup.find_all('li', {"class": "simpleAds"})[j]).lower().find(i.lower())!=(-1):
                Listings.append(soup.find_all('li', {"class": "simpleAds"})[j])
        FoundListings.append(Listings)
    return FoundListings

def FindSkelbiuPrice(Link):
    print("Getting all prices for found listings...")
    AllWords=SearchList()
    KeyWords=[]
    for i in range(len(AllWords)):
        KeyWords.append(AllWords[i][0])
    Listings = FindSkelbiuListings(PullInfoSelenium(Link), KeyWords)
    AllPrices=[]
    for i in range(len(Listings)):
        prices=[]
        for j in range(len(Listings[i])):
            soupy = BeautifulSoup(str(Listings[i][j]), 'html.parser')
            price=soupy.find_all('div', {"class": "adsPrice"})[0]
            price=re.findall(r'\d+', str(price.find('span')))
            if len(price)>0:
                price=int(price.pop())
                prices.append(price)
            else:
                prices.append(99999)
        AllPrices.append(prices)
    return AllPrices
    


# Andele bļe
def GetPriceAM(Link):
    soup=PullInfo(Link)
    price_element = soup.find('span', class_='product__price')
    price = price_element.text.strip()
    price_int = int(re.search(r'^\d+', price).group())
    return price_int

def PullInfoAM(Link):
    options = Options()
    options.add_argument("--headless")
    # driver = webdriver.Chrome('C:/Users/Aorus/Documents/ChromeDriver/chromedriver.exe', options=options)
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(10)
    driver.get(Link)
    my_dynamic_element = driver.find_element(By.CLASS_NAME, "product-card__link")
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def GetAllAMLinks(Link):
    print("Getting all AM links")
    soup=PullInfoAM(Link)
    link_elements = soup.find_all("a", class_="product-card__link")
    links = []
    for element in link_elements:
        if "href" in element.attrs:
            AMLink=f'https://www.andelemandele.lv/{element["href"]}'
            links.append(AMLink)
    return links

def GetAllMatchingAMListings(Links,KeyWords):
    print("Gettings all matching listings")
    Soups=[]
    for i in Links:
        soup=PullInfo(i)
        Soups.append(soup)
    FoundListings=[]
    for i in KeyWords:
        Listings=[]
        for j in range(len(Soups)):
            soup=Soups[j]
            titles = soup.find_all(class_='product')
            for title in titles:
                if i.lower() in title.text.lower():
                    Listings.append(Links[j])
                    break
        FoundListings.append(Listings)
    return FoundListings

def GetEverythingAM(Link):
    print("Getting all links...")
    AllWords=SearchList()
    KeyWords=[]
    Links=GetAllAMLinks(Link)
    for i in range(len(AllWords)):
        KeyWords.append(AllWords[i][0])
    return GetAllMatchingAMListings(Links,KeyWords)

def GetGoodAMListings(Link):
    print("Searching for all listings that match the price criteria")
    AllLinks=GetEverythingAM(Link)
    GoodListings=[]
    AllWords=SearchList()
    for i in range(len(AllLinks)):
        # RightListings=[]
        for j in range(len(AllLinks[i])):
            price=GetPriceAM(AllLinks[i][j])
            if price<=int(AllWords[i][1]):
                print(f"\033[1;32;40mPrice matches the price criteria\033[0m, {price} < {AllWords[i][1]}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                RightListing=[]
                RightListing.append(AllLinks[i][j])
                RightListing.append(AllWords[i][0])
                RightListing.append(price)
                date = d.now()
                RightListing.append(date.strftime("%d-%m-%Y %H:%M:%S"))
                GoodListings.append(RightListing)
            else:
                print(f"\033[1;31;40mPrice does not match the price criteria\033[0m, {price} > {AllWords[i][1]}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        # GoodListings.append(RightListings)
    return GoodListings


# notion
def readDatabase(ConfigID, headers):
    print("Reading database (May take a while)...")
    readUrl = f"https://api.notion.com/v1/databases/{ConfigID}/query"
    res = requests.request("POST", readUrl, headers=headers)
    data = res.json()

    with open('./full-properties.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)
    return data

# print(readDatabase(databaseId, headers))


def SearchList():
    print("Searching for keywords and prices in config...")
    dict = readDatabase(ConfigID, headers)
    List=[]
    for page in dict['results']:
        x=[]
        if len(page['properties']['KeyWords']['title'])>0:
            title = page['properties']['KeyWords']['title'][0]['text']['content']
            price = page['properties']['price']['number']
            x.append(title.lower())
            x.append(price)
            List.append(x)
    return List

def SearchLink():
    print("Searching for links in database...")
    dict = readDatabase(databaseId, headers)
    List=[]
    for page in dict['results']:
        link = page['properties']['Link']['url']
        List.append(link)
    return List

def CheckIfExists(link,listings):
    print(f"Checking if listing \033[1;36;40m{link}\033[0m already exists")
    NotExists=True
    for i in range(len(listings)):
        if listings[i]==link:
            print("Listing already exists")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            NotExists=False
            break
    return NotExists

def updatePage(pageId, headers):
    updateUrl = f"https://api.notion.com/v1/pages/{pageId}"
    updateData = {
        "properties": {"Keyword": {"title": [{"text": {"content": "why"}}]}}}
    data = json.dumps(updateData)
    response = requests.request("PATCH", updateUrl, headers=headers, data=data)
    return(response.text)

def createPage(databaseId, headers, listings):
    print("Adding listings to database...")
    AllListings=SearchLink()
    for i in listings:
        createUrl = 'https://api.notion.com/v1/pages'
        ListingLink=i[0]
        KeyWord=i[1]
        Price=i[2]
        DateTime=i[3]
        if CheckIfExists(ListingLink, AllListings):
            print(f"Adding Listing - \033[1;36;40m{ListingLink}\033[0m")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            newPageData = {
                "parent": { "database_id": databaseId },
                "properties": {
                    "Keyword": {
                        "title": [
                            {
                                "text": {
                                    "content": KeyWord
                                }
                            }
                        ]
                    },
                    "Price": {
                        "number": Price
                    },
                    "Link": {
                        "url": ListingLink
                    },
                    "Date and time": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": DateTime
                                }
                            }
                        ]
                    }, "Select": {
                        "select": {
                            "id":"729d96dc-0964-4816-b582-04575a20c4f8",
                            "name":"unchecked",
                            "color":"red"
                        }
                    }
                }
            }
            data = json.dumps(newPageData)
            res = requests.request("POST", createUrl, headers=headers, data=data)
    return "done"


# Links
Links = []
print("Searching for all links")
dict = readDatabase(LinksID, headers)
for page in dict['results']:
    if len(page['properties']['Link']['title'])>0:
        title = page['properties']['Link']['title'][0]['text']['content']
        Links.append(title.lower())


# main loop
while True:
    for i in Links:
        if i.find("https://www.ss.com/")!=(-1):
            print("ss")
            print(createPage(databaseId,headers,GetGoodssListings(i)))
        elif i.find("https://www.skelbiu.lt/")!=(-1):
            print("skelbiu")
            print(createPage(databaseId,headers, GetGoodSkelbiuListings(i)))
        elif i.find("https://www.andelemandele.lv/")!=(-1):
            print("andelemandele")
            print(createPage(databaseId,headers, GetGoodAMListings(i)))