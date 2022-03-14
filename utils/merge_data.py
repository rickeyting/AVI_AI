# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 14:45:31 2022

@author: A2433
"""

import pandas as pd
import os
from tqdm import tqdm
import numpy as np
from datetime import timedelta, datetime, date

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
    result.columns = ['FQC_date','Part_No','Date_Code','lot','FQC_Strips','OK_Strips']
    result['Part_No'] = result['Part_No'].str[:9]
    result = result.replace(' ', '', regex=True)
    #result['lot']=result['lot'].str[:4]
    result.lot = pd.to_numeric(result.lot, errors='coerce')
    result.Date_Code = pd.to_numeric(result.Date_Code, errors='coerce')
    result_group = result.groupby(['Part_No','Date_Code','lot']).agg({'FQC_date':'last','FQC_Strips':'sum','OK_Strips':'sum'}).reset_index()
    result_group['f_repeat'] = result_group.index
    return result_group


def oqc_data(oqc_path):
    result = []
    print('STATUS: concat OQC data')
    for i in tqdm(os.listdir(oqc_path)):
        path = os.path.join(oqc_path,i)
        df = pd.read_excel(path, sheet='sheet1', header=4)
        df = df[['檢驗日期','料號','D/C','批號','檢驗次數','狀態','批量']]
        result.append(df)
    result = pd.concat(result)
    result.columns = ['OQC_date','Part_No','Date_Code','lot','check_times','reject_times','OQC_Strips']
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
    result = result[result.OQC_AVI == 1]
    result_group = result.groupby(['Part_No','Date_Code','lot']).agg({'OQC_date':'last','check_times':'count','reject_times':'sum','OQC_AVI':'max','OQC_Strips':'sum'}).reset_index()
    return result_group


def ai_data(ai_path):
    print('STATUS: arrange ai data')
    df = pd.read_csv(ai_path)
    df = df[['AVI','VRS','Part_No','lot','strips','CheckTime(min)','OK','NG','ALL','type','size','AI','Date_Code']]
    df['Part_No'] = df.Part_No.str[:9]
    df.lot = pd.to_numeric(df.lot, errors='coerce')
    df = df[df.AI == 'ON']
    df = df.drop('AI',axis = 1).reset_index()
    df.Date_Code = df.Date_Code.str[3:7]
    df.Date_Code = df.Date_Code.fillna(0)
    df.Date_Code = pd.to_numeric(df.Date_Code, errors='coerce')
    result_group = df.groupby(['Part_No','Date_Code','lot']).agg({'AVI':'first','VRS':'last','strips':'sum','CheckTime(min)':'sum','OK':'sum','NG':'sum','ALL':'sum','type':'last','size':'last'}).reset_index()
    result_group['AVI'] = pd.to_datetime(result_group['AVI'], format='%Y%m%d')
    return result_group
    

def all_concat(ai_path,fqc_path,oqc_path):
    ai_df = ai_data(ai_path)
    fqc_df = fqc_data(fqc_path)
    oqc_df = oqc_data(oqc_path)
    con_df = ai_df.merge(fqc_df.merge(oqc_df,on=['Part_No','lot','Date_Code'],how='left'),on=['Part_No','lot','Date_Code'],how='left').sort_values(by='VRS')
    print('STATUS: repeated occurrences happened when merge -- {}'.format(any(con_df[con_df.f_repeat.notna()].f_repeat.duplicated())))
    con_df.drop(['f_repeat','type'],axis=1)
    return con_df
    

def weekly_report(anova_df,status = 'MP'):
    df = anova_df
    if status == 'MP':
        df = df[df['size'] != '5UM']
    else:
        df = df[df['size'] == '5UM']
    df.loc[:,'VRS'] = pd.to_datetime(df.loc[:,'VRS'])
    df_m = df.resample('M',on='VRS').sum().reset_index()
    df_m.VRS = df_m.VRS.dt.month.astype(str) + '月總計'
    #df_w = df.resample('W',on='VRS').sum().reset_index()
    #df_w.VRS = 'W' + df_w.VRS.dt.week+1
    df_s = df.groupby('size').resample('W',on='VRS').sum().reset_index()
    df_s.VRS = df_s.VRS.astype(str) + 'W' + (df_s.VRS.dt.week+1).astype(str).str.rjust(2, "0")
    df_s = df_s.sort_values(by=['VRS','size'])
    df_s.VRS = df_s.VRS.str[10:]
    result = pd.concat([df_m,df_s],sort=False)
    result['Pics/strip'] = round(result['ALL']/result['strips'],0)
    result['Filer rate'] = round(result['OK']/result['ALL']*100,1).astype(str) + '%'
    result['UPH'] = round(result['strips']/result['CheckTime(min)']*60,0)
    result['Yield'] =  round(result['OK_Strips']/result['FQC_Strips']*100,1).astype(str) + '%'
    result['Reject rate'] = round(result['reject_times']/result['check_times']*100,1).astype(str) + '%'
    first_row = pd.DataFrame(np.array([['non-AI base',90,'6.2%']]),columns = ['VRS','UPH','Reject rate'])
    result = pd.concat([first_row,result],sort=False)
    result = result[['VRS','size','strips','Pics/strip','Filer rate','UPH','Reject rate']]
    result.columns = ['VRS','','strips','Pics/strip','Filer rate','UPH','Reject rate']
    return result

    
def format_color_groups(df):
    colors = ['gold', 'lightblue']
    x = df.copy()
    x['strips'] = x['strips'].astype(str)
    factors = list(x['strips'].unique())
    i = 0
    for factor in factors:
        style = f'background-color: {colors[i]}'
        x.loc[x['strips'] == factor, :] = style
        i = not i
    return x


def output_exl(sheets,output_path):
    output_dir = os.path.join(output_path,'AI測試報表_{}.xls'.format(datetime.today().strftime('%Y%m%d')))
    with pd.ExcelWriter(output_dir) as writer:
        for i in sheets:
            sheets[i].to_excel(writer, sheet_name=i,index=False)

    
if __name__ == '__main__':
    all_concat(AI_DIR,FQC_DIR,OQC_DIR)
    #ai_data(AI_DIR).to_csv(TEST_SAVE)
    