# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 16:30:53 2022

@author: A2433
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.select import Select
from msedge.selenium_tools import EdgeOptions
from datetime import date, datetime, timedelta
import os
import shutil
import glob
import getpass
import time


download_path = os.path.join(r'C:\Users',getpass.getuser(),'Downloads')
FQC_PATH = os.path.abspath(os.path.join('..','data','FQC'))
OQC_PATH = os.path.abspath(os.path.join('..','data','OQC'))
EXE_PATH = os.path.abspath(os.path.join('..','msedgedriver.exe'))
options = EdgeOptions()
options.use_chromium = True
#options.add_argument("headless")
options.add_argument("disable-gpu")
#options.add_argument("javascript.enabled", True)

def fqc_crawl(driver,start_date,end_date,fqc_path):
    driver.find_element_by_id('IWTreeView1Item3').click()
    driver.find_element_by_link_text('外觀檢驗清單').click()
    
    driver.find_element_by_id('ESDATE').clear()
    driver.find_element_by_id('ESDATE').send_keys(start_date)
    driver.find_element_by_id('EEDATE').clear()
    driver.find_element_by_id('EEDATE').send_keys(end_date.strftime('%Y/%m/%d'))
    
    sel = Select(driver.find_element_by_id('CBINSPCNT'))
    sel.select_by_value('1')
    
    driver.find_element_by_id('CHKREPAIR_CHECKBOX').click()
    driver.find_element_by_id('CHKSCRAP_CHECKBOX').click()
    driver.find_element_by_id('CHKXOUT1_CHECKBOX').click()
    driver.find_element_by_id('CHKXOUT2_CHECKBOX').click()    

    driver.find_element_by_id('IWBUTTON2').click()
    time.sleep(60)
    copy_div = glob.glob(os.path.join(download_path,'*.xls'))[0]
    shutil.copyfile(copy_div, os.path.join(fqc_path,'{}.xls'.format(end_date.strftime('%Y-%m-%d'))))
    os.remove(copy_div)
    return 1

def oqc_crawl(driver,start_date,end_date,oqc_path):
    driver.find_element_by_id('IWTreeView1Item4').click()
    driver.find_element_by_link_text('外觀檢驗及需複驗清單').click()

    driver.find_element_by_id('ESDATE').clear()
    driver.find_element_by_id('ESDATE').send_keys(start_date)
    driver.find_element_by_id('EEDATE').clear()
    driver.find_element_by_id('EEDATE').send_keys(end_date.strftime('%Y/%m/%d'))
    
    driver.find_element_by_id('IWBUTTON1').click()
    time.sleep(60)
    copy_div = glob.glob(os.path.join(download_path,'*.xls'))[0]
    shutil.copyfile(copy_div, os.path.join(oqc_path,'{}.xls'.format(end_date.strftime('%Y-%m-%d'))))
    os.remove(copy_div)
    return 1

def get_start_date(fqc_path,oqc_path):
    if len(os.listdir(fqc_path)) == 0:
        fqc_start = datetime.strptime('2021/03/16','%Y/%m/%d')
    else:
        fqc_start = os.listdir(fqc_path)[-2][:10]
        last_week = os.path.join(fqc_path,os.listdir(fqc_path)[-1])
        os.remove(last_week)
        fqc_start = datetime.strptime(fqc_start,'%Y-%m-%d')
        fqc_start = fqc_start+timedelta(days=1)
    if len(os.listdir(oqc_path)) == 0:
        oqc_start = datetime.strptime('2021/03/16','%Y/%m/%d')
    else:
        oqc_start = os.listdir(oqc_path)[-2][:10]
        last_week = os.path.join(oqc_path,os.listdir(oqc_path)[-1])
        os.remove(last_week)
        oqc_start = datetime.strptime(oqc_start,'%Y-%m-%d')
        oqc_start = oqc_start+timedelta(days=1)
        
    return fqc_start,oqc_start
    
def do_crawl(exe_path,fqc_path,oqc_path):
    end_date= datetime.today()-timedelta(days=1)
    fqc_start,oqc_start = get_start_date(fqc_path,oqc_path)
    start = min(fqc_start,oqc_start)
    end = start+timedelta(days=6)    
    if start < end_date:
        if end > end_date:
            end = end_date
        while True:
            print('STATUS:crawling ' + start.strftime('%Y/%m/%d') +'~'+ end.strftime('%Y/%m/%d') +' FQC & OQC data...')
            check_status = 0
            while check_status != 2:
                try:
                    driver = webdriver.Chrome(executable_path=exe_path,options=options) 
                    url = 'http://10.13.65.74:1014/'
                    driver.get(url)
                    driver.find_element_by_id('BTNSY').click()
                    driver.set_page_load_timeout(600)
                    check_status += oqc_crawl(driver,start.strftime('%Y/%m/%d'),end,oqc_path)
                    check_status += fqc_crawl(driver,start.strftime('%Y/%m/%d'),end,fqc_path)
                except Exception as e:
                    print(e)
                    driver.close()
                    check_status = 0
                try:
                    driver.close()
                    time.sleep(2)
                except:
                    pass
            print('STATUS:crawling ' + start.strftime('%Y/%m/%d') +'~'+ end.strftime('%Y/%m/%d') +' Done')
            start += timedelta(days=7)
            end += timedelta(days=7)
            if end > end_date:
                end = end_date
            if start > end:
                break
              
                
if __name__ == '__main__':
    #do_crawl(EXE_PATH,FQC_PATH,OQC_PATH)
    pass