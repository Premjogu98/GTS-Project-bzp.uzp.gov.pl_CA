from selenium import webdriver
import time
from datetime import datetime
import global_var
import html
import ctypes
import wx
import sys, os
from googletrans import Translator
from selenium.webdriver.chrome.options import Options
from Scraping_Things import Scraping_data
app = wx.App()


def ChromeDriver():
    browser = webdriver.Chrome(executable_path=str(f"C:\\chromedriver.exe"))
    browser.get('http://searchbzp.uzp.gov.pl/Search.aspx')
    browser.maximize_window()
    time.sleep(3)

    for From_Date in browser.find_elements_by_xpath('//*[@id="MainContent_dateDataPublikacjiOd_I"]'):
        From_Date.send_keys(str(global_var.From_Date))
        time.sleep(1.5)
        break

    for To_Date in browser.find_elements_by_xpath('//*[@id="MainContent_dateDataPublikacjiDo_I"]'):
        To_Date.send_keys(str(global_var.To_Date))
        time.sleep(1.5)
        break

    for Order_Mode in browser.find_elements_by_xpath('//*[@id="MainContent_ddlOrderMode_B-1"]'):
        Order_Mode.click()
        time.sleep(1.5)
        for Order_Mode1 in browser.find_elements_by_xpath('//*[@id="MainContent_ddlOrderMode_DDD_L_LBI1T0"]'):
            Order_Mode1.click()
            time.sleep(1.5)
        break

    for Type_of_advertisement in browser.find_elements_by_xpath('//*[@id="MainContent_ddlAnnouncementType2_B-1"]'):
        Type_of_advertisement.click()
        time.sleep(1.5)
        for Type_of_advertisement1 in browser.find_elements_by_xpath('//*[@id="MainContent_ddlAnnouncementType2_DDD_L_LBI3T0"]'):
            Type_of_advertisement1.click()
            time.sleep(1.5)
        break

    for Search in browser.find_elements_by_xpath('//*[@id="MainContent_btnSzukaj"]'):
        Search.click()
        break

    time.sleep(2)

    Nav_link(browser)

def Nav_link(browser):
    pages = ''
    for pages in browser.find_elements_by_xpath('//*[@class="dxp-lead dxp-summary"]'):
        pages = pages.get_attribute('innerText').strip()   # Eg :  Strona 1 z 40 (elementy 791)
        if 'Strona' in pages:
            pages = pages.partition('Strona 1 z')[2].partition('(')[0].strip()  # Collecting pages range
        if 'Page' in pages:
            pages = pages.partition('Page 1 of')[2].partition('(')[0].strip()
        break
    if pages == "":
        pages = "1"
    main_detail_list = []
    for i in range(int(pages)):
        tr = 2
        error = True
        while error == True:
            try:
                for tr_range in browser.find_elements_by_xpath('//*[@id="MainContent_gvSzukaj_DXMainTable"]/tbody/tr'):
                    browser.execute_script("arguments[0].scrollIntoView();", tr_range)
                    detail_list = []
                    for publish_date in browser.find_elements_by_xpath(f'//*[@id="MainContent_gvSzukaj_DXMainTable"]/tbody/tr[{str(tr)}]/td[4]'):
                        publish_date = publish_date.get_attribute('innerText').strip()
                        datetime_object = datetime.strptime(publish_date, '%Y-%m-%d')
                        publish_date1 = datetime_object.strftime("%Y-%m-%d")
                        if publish_date1 >= global_var.From_Date:
                            detail_list.append(publish_date)
                            tender_href_text = ''
                            for tender_href in browser.find_elements_by_xpath(f'//*[@id="MainContent_gvSzukaj_DXMainTable"]/tbody/tr[{str(tr)}]/td[1]/a'):
                                tender_href_text = tender_href.get_attribute('href').strip()
                                detail_list.append(tender_href_text)
                                print(tender_href_text)
                                break
                            if tender_href_text == '':
                                detail_list.append('NA')

                            tender_id_text = ''
                            for tender_id in browser.find_elements_by_xpath(f'//*[@id="MainContent_gvSzukaj_DXMainTable"]/tbody/tr[{str(tr)}]/td[3]'):
                                tender_id_text = tender_id.get_attribute('innerText').strip()
                                detail_list.append(tender_id_text)
                                break
                            if tender_id_text == '':
                                detail_list.append('NA')

                            purchaser_text = ''
                            for purchaser in browser.find_elements_by_xpath(f'//*[@id="MainContent_gvSzukaj_DXMainTable"]/tbody/tr[{str(tr)}]/td[5]'):
                                purchaser_text = purchaser.get_attribute('innerText').strip()
                                detail_list.append(purchaser_text)
                                break
                            if purchaser_text == '':
                                detail_list.append('NA')
                            
                            Title_text = ''
                            for Title in browser.find_elements_by_xpath(f'//*[@id="MainContent_gvSzukaj_DXMainTable"]/tbody/tr[{str(tr)}]/td[8]'):
                                Title_text = Title.get_attribute('innerText').strip()
                                detail_list.append(Title_text)
                                break
                            if Title_text == '':
                                detail_list.append('NA')
                            
                            refrence_no_text = ''
                            for refrence_no in browser.find_elements_by_xpath(f'//*[@id="MainContent_gvSzukaj_DXMainTable"]/tbody/tr[{str(tr)}]/td[9]'):
                                refrence_no_text = refrence_no.get_attribute('innerText').strip()
                                detail_list.append(refrence_no_text)
                                break
                            if refrence_no_text == '':
                                detail_list.append('NA')
                            main_detail_list.append(detail_list)
                        tr +=1
                a = True
                while a == True:
                    try:
                        for next_page in browser.find_elements_by_xpath('//*[@id="MainContent_gvSzukaj_DXPagerBottom_PBN"]'):
                            browser.execute_script("arguments[0].scrollIntoView();", next_page)
                            next_page.click()
                            time.sleep(4)
                            a = False
                            break
                    except:
                        print('Error On Next Page Button')
                        a = True
                error = False    
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
                error = True   
    clicking_process(browser,main_detail_list)

def clicking_process(browser,main_detail_list) :

    dist_main_detail_list = []
    dist_main_detail_list.extend(x for x in main_detail_list if x not in dist_main_detail_list) # remove Duplicate List From List
    dist_main_detail_list1 = list(dist_main_detail_list)

    for deatail_list in dist_main_detail_list1:
        browser.get(deatail_list[1])
        time.sleep(2)
        Url = deatail_list[1]
        purchaser = deatail_list[3]
        reference_number = deatail_list[5]
        Title = deatail_list[4]
        Tender_id = deatail_list[2]
        get_htmlSource = ''
        for Web_page in browser.find_elements_by_xpath('//*[@id="printContentId"]'):
            get_htmlSource = Web_page.get_attribute("outerHTML").replace('href="../', 'href="https://bzp.uzp.gov.pl/').replace("""<input type="button" value="Drukuj" onclick="printElement('printContentId')">""", '')
            break
        Scraping_data(get_htmlSource,purchaser,reference_number,Title,Tender_id,Url)
        print(f" Total: {str(len(dist_main_detail_list1))} Duplicate: {str(global_var.duplicate)} Inserted: {str(global_var.inserted)} Contract Award Date Not Given: {str(global_var.deadline_Not_given)}\n")
    ctypes.windll.user32.MessageBoxW(0, f"Total: {str(len(dist_main_detail_list1))}\nDuplicate: {str(global_var.duplicate)}\nInserted: {str(global_var.inserted)}\nContract Award Date Not Given: {str(global_var.deadline_Not_given)}", "bzp.uzp.gov.pl CA", 1)
    browser.close()
    sys.exit()

ChromeDriver()