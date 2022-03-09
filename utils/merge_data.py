# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 14:45:31 2022

@author: A2433
"""

import pandas as pd
import os
from tqdm import tqdm
from datetime import timedelta

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
    result['Part_No'] = result['Part_No'].str[:9]
    result = result.replace(' ', '', regex=True)
    #result['lot']=result['lot'].str[:4]
    result.lot = pd.to_numeric(result.lot, errors='coerce')
    result.Date_Code = pd.to_numeric(result.Date_Code, errors='coerce')
    result_group = result.groupby(['Part_No','Date_Code','lot']).agg({'FQC_date':'last','Total_Strips':'sum','OK':'sum'}).reset_index()
    result_group['f_repeat'] = result_group.index
    return result_group


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
    result['OQC_AVI'] = 0
    result.loc[result['lot'].str.contains('V'),'OQC_AVI'] = 1
    result['lot']=result['lot'].str[:4]
    result['Part_No'] = result['Part_No'].str[:9]
    result.lot = pd.to_numeric(result.lot, errors='coerce')
    result.Date_Code = pd.to_numeric(result.Date_Code, errors='coerce')
    result.loc[result.reject_times != '退回','reject_times'] = 0
    result.loc[result.reject_times == '退回','reject_times'] = 1
    result_group = result.groupby(['Part_No','Date_Code','lot']).agg({'OQC_date':'last','check_times':'count','reject_times':'sum','OQC_AVI':'max'}).reset_index()
    result_group['o_repeat'] = result_group.index
    return result_group


def ai_data(ai_path):
    print('STATUS: arrange ai data')
    df = pd.read_csv(ai_path)
    df = df[['AVI','VRS','Part_No','lot','strips','CheckTime(min)','OK','NG','ALL','type','size','AI']]
    df['Part_No'] = df.Part_No.str[:9]
    df.lot = pd.to_numeric(df.lot, errors='coerce')
    df = df[df.AI == 'ON']
    df = df.drop('AI',axis = 1).reset_index()
    df['AVI'] = pd.to_datetime(df['AVI'], format='%Y%m%d')
    df = df.groupby(['Part_No','lot','size']).resample('14D', on='AVI').agg({'VRS':'last','strips':'sum','CheckTime(min)':'sum','OK':'sum','NG':'sum','ALL':'sum','type':'last'}).reset_index()
    df['repeat_check'] = df.index
    df = df.dropna()
    result = []
    for i in range(5):
        df_t = df.copy()
        df_t['Date_Code'] = (df_t['AVI'] - timedelta(days=7*abs(i))).dt.strftime('%U%y')
        result.append(df_t)
    result = pd.concat(result)
    result.lot = pd.to_numeric(result.lot, errors='coerce')
    result.Date_Code = pd.to_numeric(result.Date_Code, errors='coerce')
    return result
    
def all_concat(ai_path,fqc_path,oqc_path):
    ai_df = ai_data(ai_path)
    fqc_df = fqc_data(fqc_path)
    oqc_df = oqc_data(oqc_path)
    con_df = ai_df.merge(fqc_df.merge(oqc_df,on=['Part_No','lot','Date_Code'],how='left'),on=['Part_No','lot','Date_Code'],how='left')
    result = []
    for i in range(con_df.repeat_check.max()+1):
        row = con_df[con_df.repeat_check == i]
        row = row.sort_values(by=['OQC_date','FQC_date','VRS'],ascending=False)
        row = row.head(1)
        result.append(row)
    result = pd.concat(result)
    result.to_csv(TEST_SAVE)

if __name__ == '__main__':
    all_concat(AI_DIR,FQC_DIR,OQC_DIR)
    #ai_data(AI_DIR)