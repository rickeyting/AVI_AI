# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 13:19:25 2022

@author: A2433
"""
import os
import sys
import shutil
from datetime import datetime, date
import pandas as pd

BASE_DATA_DIR = os.path.abspath(os.path.join('..', 'data'))
AI_DIR = os.path.join(BASE_DATA_DIR, 'AI')
target_dir = r'\\10.19.13.40\ScanImages\ai_all.csv'


def connect_test(save_path):
    if os.path.exists(target_dir):
        print('STATUS: check ai_all.csv exists')
        shutil.copyfile(target_dir, save_path)
    else:
        sys.exit('Check the link to EDGE is avaliable')


def get_raw_data(ai_data_dir):
    save_path = os.path.join(ai_data_dir,'ai_all.csv')
    if os.path.exists(save_path):
        os.rename(save_path,os.path.join(ai_data_dir,'ai_all_{}.csv'.format(datetime.now().strftime('%Y-%m-%d_%M_%S'))))
    connect_test(save_path)
      
    
if __name__ == '__main__':
    #get_raw_data(AI_DIR)
    pass