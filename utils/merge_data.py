# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 14:45:31 2022

@author: A2433
"""

import pandas as pd
import os
from tqdm import tqdm

BASE_DIR = os.path.abspath(os.path.join('..','data'))
TEST_SAVE = os.path.join(BASE_DIR,'test.csv')
FQC_DIR = os.path.join(BASE_DIR,'FQC')
OQC_DIR = os.path.join(BASE_DIR,'OQC')
AI_DIR = os.path.join(BASE_DIR,'AI','ai_all.csv')

def daily_record(ai_path):
    df = pd.read_csv(ai_path)
    df['VRS'] = pd.to_datetime(df['VRS'])
    df.loc[(df.model != 'R1') & (df.model != 'Z1'),'AI'] = 'OFF'
    df = df[df.AI == 'ON']
    df = df[['VRS','strips','CheckTime(min)','OK','NG','ALL','size']]
    df = df.groupby(['VRS','size']).sum().reset_index()
    df = df.sort_values('VRS')
    return df


def fqc_data(fqc_path):
    result = []
    print('STATUS: concat FQC data')
    for i in tqdm(os.listdir(fqc_path)):
        path = os.path.join(fqc_path,i)
        df = pd.read_excel(path, sheet='sheet1', header=5)
        df = df.dropna(subset=['Part No.'])
        df = df[['Time','Part No.','Date Code','Lot No.','Total Strips','OK & X-Out(Strips)']]
        result.append(df)
    result = pd.concat(result)
    result.columns = ['FQC_date','Part_No','Date_Code','lot','Total_Strips','OK']
    result_group = result.groupby(['Part_No','Date_Code','lot']).agg({'FQC_date':'last','Total_Strips':'sum','OK':'sum'}).reset_index()
    return result,result_group


def oqc_data(oqc_path):
    result = []
    print('STATUS: concat OQC data')
    for i in tqdm(os.listdir(oqc_path)):
        path = os.path.join(oqc_path,i)
        df = pd.read_excel(path, sheet='sheet1', header=4)
        df = df[['檢驗日期','料號','D/C','批號','檢驗次數','狀態']]
        result.append(df)
    result = pd.concat(result)
    result.columns = ['OQC_date','Part_No','Date_Code','lot','check_times','reject_times']
    result['OQC_date'] = result['OQC_date'].astype(str).str[:10]
    result['OQC_date'] = pd.to_datetime(result['OQC_date'])
    result['lot'] = result['lot'].astype(str)
    result = result[result['lot'].str.contains('V')]
    result['lot']=result['lot'].str[:4]
    result['Part_No'] = result['Part_No'].str[:9]
    result.check_times = 1
    result.loc[result.reject_times == '退回'] = 1
    result.loc[result.reject_times != '退回'] = 0
    print(len(result))
    result_group = result.groupby(['Part_No','Date_Code','lot']).agg({'OQC_date':'last','check_times':'sum','reject_times':'sum'}).reset_index()
    print(len(result_group))
    return result,result_group
    


if __name__ == '__main__':
    a,b = oqc_data(OQC_DIR)
    b.to_csv(TEST_SAVE)