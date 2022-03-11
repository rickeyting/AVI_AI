# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 14:45:31 2022

@author: A2433
"""

import pandas as pd
import os
from tqdm import tqdm
import numpy as np
from datetime import timedelta, datetime

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
    df.Date_Code = pd.to_numeric(df.Date_Code, errors='coerce')
    result_group = df.groupby(['Part_No','Date_Code','lot','size']).agg({'AVI':'first','VRS':'last','strips':'sum','CheckTime(min)':'sum','OK':'sum','NG':'sum','ALL':'sum','type':'last'}).reset_index()
    #result_group['repeat_check'] = result_group.index
    result_group['AVI'] = pd.to_datetime(result_group['AVI'], format='%Y%m%d')
    '''
    df = df.groupby(['Part_No','lot','size']).resample('14D', on='AVI').agg({'VRS':'last','strips':'sum','CheckTime(min)':'sum','OK':'sum','NG':'sum','ALL':'sum','type':'last'}).reset_index()
    
    df = df.dropna()
    result = []
    for i in range(5):
        df_t = df.copy()
        df_t['Date_Code'] = (df_t['AVI'] - timedelta(days=7*abs(i))).dt.strftime('%U%y')
        result.append(df_t)
    result = pd.concat(result)
    result.lot = pd.to_numeric(result.lot, errors='coerce')
    result.Date_Code = pd.to_numeric(result.Date_Code, errors='coerce')
    '''
    return result_group
    
def all_concat(ai_path,fqc_path,oqc_path):
    ai_df = ai_data(ai_path)
    fqc_df = fqc_data(fqc_path)
    oqc_df = oqc_data(oqc_path)
    con_df = ai_df.merge(fqc_df.merge(oqc_df,on=['Part_No','lot','Date_Code'],how='left'),on=['Part_No','lot','Date_Code'],how='left')
    print('STATUS: repeated occurrences happened when merge -- {}'.format(any(con_df[con_df.f_repeat.notna()].f_repeat.duplicated())))
    con_df.drop(['f_repeat','type'],axis=1)
    '''
    result = []
    for i in range(con_df.repeat_check.max()+1):
        row = con_df[con_df.repeat_check == i]
        row = row.sort_values(by=['OQC_date','FQC_date','VRS'],ascending=False)
        row = row.head(1)
        result.append(row)
    result = pd.concat(result)
    '''
    return con_df
    
    '''
    fqc_origin = fqc_origin[fqc_origin.FQC_date > datetime.strptime('2022-01-01', '%Y-%m-%d')]
    oqc_origin = oqc_origin[oqc_origin['檢驗日期'] > datetime.strptime('2022-01-01', '%Y-%m-%d')]
    output_dir = os.path.join(OUTPUT_DATA,'AI測試報表_{}.xls'.format(datetime.today().strftime('%m%d')))
    with pd.ExcelWriter(output_dir) as writer:
        anova_week.to_excel(writer, sheet_name='ANOVA_WEEK',index=False)
        anova.to_excel(writer, sheet_name='ANOVA',index=False)
        df_mail.to_excel(writer, sheet_name='DAILY')
        df_mass_5.to_excel(writer, sheet_name='5um')
        df_mass_10.to_excel(writer, sheet_name='10+18um')
        df_sample.to_excel(writer, sheet_name='sample')
        df.to_excel(writer, sheet_name='AI',index=False)
        fqc_origin.to_excel(writer, sheet_name='FQC',index=False)
        oqc_origin.to_excel(writer, sheet_name='OQC',index=False)
    '''
def weekly_report(anova_df):
    df = anova_df
    df['VRS'] = pd.to_datetime(df['VRS'])
    df = df.groupby('size').resample('W-Sun', on='VRS').sum().reset_index().sort_values(by='VRS')
    df_m = df.resample('M',on='VRS').sum().reset_index()
    df_w = df.resample('W',on='VRS').sum().reset_index()
    df_s = df.groupby('size').resample('W',on='VRS').sum().reset_index()
    result = pd.concat[df_m,df_w,df_s]
    result['Pics/strip'] = round(result['check_all']/result['strips'],0)
    result['Filer rate'] = round(result['OK']/result['ALL']*100,1).astype(str) + '%'
    result['UPH'] = round(result['strips']/result['CheckTime(min)']*60,0)
    result['Yield'] =  round(result['OK']/result['Total_Strips']*100,1).astype(str) + '%'
    result['Reject rate'] = round(result['OQC_rejection']/result['OQC_strips']*100,1).astype(str) + '%'
    first_row = pd.DataFrame(np.array([['non-AI base',90,'6.2%']]),columns = ['Week','UPH','Reject rate'])
    result = pd.concat([first_row,result])
    result = result[['VRS','strips','Pics/strip','Filer rate','UPH','Reject rate']]
    return result
    
def output_exl(sheets,output_path):
    output_dir = os.path.join(output_path,'AI測試報表_{}.xls'.format(datetime.today().strftime('%Y%m%d')))
    with pd.ExcelWriter(output_dir) as writer:
        for i in sheets:
            sheets[i].to_excel(writer, sheet_name=i,index=False)

    
if __name__ == '__main__':
    all_concat(AI_DIR,FQC_DIR,OQC_DIR)
    #ai_data(AI_DIR).to_csv(TEST_SAVE)
    