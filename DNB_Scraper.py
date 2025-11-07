import pandas as pd, random
from time import sleep
from bs4 import BeautifulSoup as bs
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


browser_count = 1

def create_driver():
    global browser_count

    if browser_count % 2:
        # 🦊 Firefox setup
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        options = FirefoxOptions()
        options.set_preference("webdriver_accept_untrusted_certs", True)
        options.set_preference("webdriver_assume_untrusted_issuer", False)
        options.set_preference("network.proxy.type", 0)  # no proxy
        options.set_preference("security.enterprise_roots.enabled", True)

        options.set_preference("security.ssl.enable_ocsp_stapling", False)
        options.set_preference("security.ssl.require_safe_negotiation", False)
        options.set_preference("security.cert_pinning.enforcement_level", 0)
        options.set_preference("network.stricttransportsecurity.preloadlist", False)
        options.set_preference("network.http.spdy.enabled", False)
        options.set_preference("network.http.spdy.enabled.http2", False)

        driver = webdriver.Firefox(options=options)
        
    else:
        # chrome_options = chrome_op()
        # if proxy:
        #     chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # driver = webdriver.Chrome()
        options = uc.ChromeOptions()
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
        # options.add_argument("--no-sandbox")
        # if proxy:
        #     options.add_argument(f'--proxy-server={proxy}')
        driver = uc.Chrome(options=options)
    browser_count+=1

    return driver
    
def clearfirefox():
    driver.get("about:preferences#privacy")
    
    # Wait for the page to load
    sleep(2)
    
    # Click on the "Clear History..." button (located under History section)
    clear_history_button = driver.find_element(By.ID, "clearSiteDataButton")
    clear_history_button.click()
    
    # Wait for the dialog to appear
    sleep(2)
    
    action = ActionChains(driver)
    action.send_keys(Keys.DOWN*3+Keys.TAB*5+Keys.ENTER).perform()
    sleep(60)
def clearchrome():
    driver.get('chrome://settings/clearBrowserData')
    sleep(2)
    action = ActionChains(driver)
    action.send_keys(Keys.SHIFT+Keys.TAB*4+Keys.DOWN*2).perform()
    sleep(2)
    action.send_keys(Keys.TAB*5+Keys.ENTER).perform()
    # browser.save_screenshot("clearhistory.png")
    sleep(60)
def check_page(driver, url, soup):
    if soup.find('h1').text == "Access Denied":
        print("Bloked... Changing Proxy")
        driver.quit()
        driver = create_driver()
        sleep(3)
        driver.get(url)
        sleep(random.uniform(5,15))
        soup = bs(driver.page_source,'html.parser')
        driver, soup = check_page(driver, url, soup)
    return driver, soup
        
        
def dnb_company_data(driver,url):
        
        print(url)
        try:
            driver.get(url)
            sleep(random.uniform(5,15))
            s2 = bs(driver.page_source,'html.parser')
            driver,s2 = check_page(driver,url2, s2)
        except Exception as e:
            print(e)
            return driver,{
        'DNB_Url' : url}
        
        try:
            
            company_name_element = WebDriverWait(driver, 35).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'company-profile-header-title'))
            )
            s1 = bs(driver.page_source,'html.parser')
            company_name_element = s1.find('div',{'class':'company-profile-header-title'})
            if company_name_element:
                company_name_text = company_name_element.text.strip()
            else:
                company_name_text = ""
            # print(company_name_text)
            # ratio = SequenceMatcher(None,company_name_text.lower(),co.lower()).ratio()*100
            # if ratio<80:
            #     return {
            # 'search_query': search_query,
            # 'Url' : None}
            principal_name_element = s1.find('span',{'class':'company_data_point','name':'key_principal'})
            if principal_name_element:
                principal_name_text = principal_name_element.text.strip()
            else:
                principal_name_text = ""
            substrings_to_remove = ['Principal Name:', 'Key Principal:', 'See more contacts']
            for substring in substrings_to_remove:
                principal_name_text = principal_name_text.replace(substring, '').strip()
            if s1.find('span',{'class':'company_data_point','name':'industry_links'}):
                industry_links_element = s1.find('span',{'class':'company_data_point','name':'industry_links'}).find("a")
            else:
                industry_links_element = ""
            if industry_links_element:
                industry_links_text = industry_links_element.text
            
            company_website_href = None
            try:
                company_website_element = s1.find('div',{'class':'company-profile-rank'}).find('a',{'class':'ext-icon','target':'_blank'})
                company_website_href = company_website_element.get("href") if company_website_element is not None else 'NaN'
            except:
                print("Company website not found. Appending NaN values.")

            address = None
            address_href = None
            ext_icon_elements = s1.findAll('a',{'class':'ext-icon'})
            for ext_icon_element in ext_icon_elements:
                href_value = ext_icon_element.get("href")
                if (href_value and href_value.startswith('https://maps.google.com/')):
                    address = ext_icon_element.text.strip() if ext_icon_element.text else None
                    address_href = href_value
                    break
            contact = None
            contact_pos = None
            contact_body = s1.find('div',{'class':'contacts-body'})
            if contact_body:
                try:
                    contact = contact_body.find('li').find('div',{'class':'name'}).text
                    contact_pos = contact_body.find('li').find('div',{'class':'position'}).text
                except:
                    contact = None
                    contact_pos = None
            print('DNB_Data_Found', company_name_text)
            return driver,{
                'DNB_Url':url,
                'company_name': company_name_text,  
                'DNB_key_principal': principal_name_text,
                'DNB_industry': industry_links_text,
                'DNB_website': company_website_href,
                'DNB_address': address,
                'DNB_contact_person':contact,
                'DNB_contact_person_position':contact_pos
            }
        except Exception as e:
            print("Company data not found within the specified time.")
            print(e)
            driver.quit()
            driver = create_driver()
            return driver,{
                'DNB_Url': url
            }
url = "https://www.dnb.com/business-directory.html"
driver = create_driver()
driver.get(url)
#%%
sleep(random.uniform(5,15))
s1 = bs(driver.page_source,'html.parser')
driver,s1 = check_page(driver,url, s1)
links = s1.findAll('a',{'class':'gridLink anchor-hover-none'})
l = []
#%%
for i in links[1:]:
    print(i.text)
    if i.text.strip() != "Aerospace Product and Parts Manufacturing":
        continue
    url2 = "https://www.dnb.com"+i['href']
    driver.get(url2)
    sleep(random.uniform(5,15))
    s2 = bs(driver.page_source,'html.parser')
    driver,s2 = check_page(driver,url2, s2)
    if s2.find('div',{'class':'text-center text-md-start px-30'}):
        cou = s2.find('div',{'class':'text-center text-md-start px-30'}).findAll('a',{'class':'sideLink'})
    else:
        cou = []
    for j in cou:
        if 'india' in j.text.strip().lower():
            print(j.text.strip().lower())
            count = int(j.text.strip()[7:-1].replace(',',""))
            for p in range(1,11):
                if len(l)==20:
                    break
                category_url = "https://www.dnb.com"+j['href']+f"?page={p}"
                print(i.text)
                try:
                    driver.get(category_url)
                except:
                    driver.quit()
                    driver = create_driver()
                    sleep(3)
                    driver.get(category_url)
                sleep(random.uniform(5,15))
                category_s2 = bs(driver.page_source,'html.parser')
                driver,category_s2 = check_page(driver,category_url, category_s2)
                if category_s2.find('div',{'id':'companyResults'}):
                    companies = category_s2.find('div',{'id':'companyResults'}).findAll('a',{'class':'companyName'})
                else:
                    companies = []
                for com in companies:
                    company_url = "https://www.dnb.com"+com['href']
                    driver,data = dnb_company_data(driver,company_url)
                    
                    data = {"Category":i.text}|data
                    l.append(data)
            df = pd.DataFrame(l)
            df.to_excel(f'{i.text.strip()}.xlsx',index=False)
            break
    break