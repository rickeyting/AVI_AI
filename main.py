# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 14:20:54 2022

@author: A2433
"""
import os
from utils import avi_foqc_crawler, raw_data

root_dir = os.path.abspath('.')
data_dir = os.path.join(root_dir,'data')
output_dir = os.path.join(root_dir,'output')
ai_dir = os.path.join(data_dir,'AI')
fqc_dir = os.path.join(data_dir,'FQC')
oqc_dir = os.path.join(data_dir,'OQC')
exe_dir = os.path.join(root_dir,'msedgedriver.exe')

def pre_procss():
    print('STATUS: creating dirs')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(ai_dir):
        os.mkdir(ai_dir)
    if not os.path.exists(fqc_dir):
        os.mkdir(fqc_dir)
    if not os.path.exists(oqc_dir):
        os.mkdir(oqc_dir)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

if __name__ == '__main__':
    #pre_procss()
    #avi_foqc_crawler.do_crawl(exe_dir,fqc_dir,oqc_dir)
    raw_data.get_raw_data(ai_dir)