# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 11:41:43 2022

@author: A2433
"""

import os
#import avi_ai_crawler
import avi_foqc_crawler
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

base_data_dir = os.path.join('..', 'data')
ai_data_dir = os.path.join(base_data_dir, 'AI')
fqc_data_dir = os.path.join(base_data_dir, 'FQC')
oqc_data_dir = os.path.join(base_data_dir, 'OQC')
output_dir = os.path.join('..', 'output')


def preset():
    folders_list = [base_data_dir,output_dir,ai_data_dir,fqc_data_dir,oqc_data_dir]
    print('STATUS:initsetting...')
    for create_folder in folders_list:
        if not os.path.exists(create_folder):
                os.makedirs(create_folder)
    print('STATUS:initsetting Done')


def date_code_mapping():
    fqc_list = []
    for f in os.listdir(fqc_data_dir):
        fdf = pd.read_excel(os.path.join(fqc_data_dir,f),sheet='sheet1',header=5)
        last_col = fdf.columns.tolist()[-1]
        fdf = fdf[['Time','Q Stamp','Part No.','Date Code','Lot No.','Total Strips','OK & X-Out(Strips)',last_col]]
        fqc_list += fdf.values.tolist()
    fqc_df = pd.DataFrame(np.array(fqc_list),columns=['FQC_date','Q Stamp','Part_No','Date_Code','lot','Total_Strips','FQC_OK','concat_no'])
    concat_fqc = fqc_df[['FQC_date','Part_No','Date_Code','lot','Total_Strips','FQC_OK']]
    concat_fqc['Part_No'] = concat_fqc.loc[:,'Part_No'].str[:9]
    concat_fqc['lot'] = concat_fqc['lot'].astype(str).str[:4]
    concat_fqc['Date_Code'] = concat_fqc['Date_Code'].astype(str).str[:4]
    concat_fqc['Date_Code'] = concat_fqc['Date_Code'].str.replace('.','').apply(lambda x: x.zfill(4))
    concat_fqc = concat_fqc.groupby(['Part_No','lot','Date_Code']).agg({'FQC_date': 'last', 'Total_Strips': 'sum', 'FQC_OK': 'sum'}).reset_index()
    concat_fqc = concat_fqc[concat_fqc.Total_Strips != 0].reset_index(drop=True)
    concat_fqc = concat_fqc[(concat_fqc.lot != 'REPAIR') & (concat_fqc.lot != 'MIX')]
    """
    oqc_list = []
    for o in os.listdir(oqc_data_dir):
        odf = pd.read_excel(os.path.join(oqc_data_dir,o),sheet='sheet1',header=4)
        oqc_list += odf.values.tolist()
    oqc_df = pd.DataFrame(np.array(oqc_list),columns=['OQC編號','檢驗次數','狀態','檢驗別','班別','批號','板子種類','料號','批量','檢驗數量','OQC檢驗員','FQC Q章','FQC檢驗員','新增者','D/C','檢驗日期','開始時間','結束時間','備註','缺點代碼','缺點名稱','缺點數量','發生面','是否共同'])
    #oqc_df.dropna(subset=['批號'])
    oqc_df = oqc_df[oqc_df['批號'].str.contains('V',na=False)]
    
    oqc_df = oqc_df[['檢驗次數','狀態','檢驗日期']]
    oqc_df['rejection'] = 0
    oqc_df.loc[oqc_df['狀態'] == '退回', 'rejection'] = 1 
    oqc_df.drop('狀態',axis =1)
    oqc_df = oqc_df[['檢驗日期','檢驗次數','rejection']]
    
    oqc_df['檢驗日期'] = pd.to_datetime(oqc_df['檢驗日期'])
    oqc_df = oqc_df.set_index('檢驗日期')
    oqc_week = oqc_df.resample('W-Sun').agg({'檢驗次數': 'count','rejection':'sum'}).reset_index().sort_values(by='檢驗日期')
    oqc_month = oqc_df.resample('M').agg({'檢驗次數': 'count','rejection':'sum'}).reset_index().sort_values(by='檢驗日期')
    """
    oqc_list = []
    for o in os.listdir(oqc_data_dir):
        odf = pd.read_excel(os.path.join(oqc_data_dir,o),sheet='sheet1',header=4)
        oqc_list += odf.values.tolist()
    oqc_df = pd.DataFrame(np.array(oqc_list),columns=['OQC編號','檢驗次數','狀態','檢驗別','班別','批號','板子種類','料號','批量','檢驗數量','OQC檢驗員','FQC Q章','FQC檢驗員','新增者','D/C','檢驗日期','開始時間','結束時間','備註','缺點代碼','缺點名稱','缺點數量','發生面','是否共同'])
    concat_oqc = oqc_df
    concat_oqc = concat_oqc[concat_oqc['批號'].astype(str).str.contains('V')]
    concat_oqc['料號'] = concat_oqc['料號'].str[:9]
    concat_oqc['批號'] = concat_oqc['批號'].astype(str).str[:4]
    concat_oqc['reject'] = 0
    concat_oqc.loc[concat_oqc['狀態'] == '退回','reject'] = 1
    concat_oqc = concat_oqc[['reject','批號','檢驗次數','料號','檢驗日期','D/C']]
    concat_oqc['批號'] = concat_oqc['批號'].astype(str).str[:4]
    concat_oqc['D/C'] = concat_oqc['D/C'].astype(str).str[:4]
    concat_oqc['D/C'] = concat_oqc['D/C'].str.replace('.','').apply(lambda x: x.zfill(4))
    concat_oqc = concat_oqc.groupby(['料號','批號','D/C']).agg({'檢驗日期': 'last', '檢驗次數': 'count', 'reject': 'sum'}).reset_index()
    
    concat_oqc = concat_oqc[['檢驗日期','料號','D/C','批號','檢驗次數','reject']]
    concat_oqc['檢驗次數'] += concat_oqc['reject']
    concat_oqc.columns= ['OQC_date','Part_No','Date_Code','lot','OQC_strips','OQC_rejection']
    
    
    result_foqc = concat_fqc.merge(concat_oqc, how='left', on=['Date_Code','lot','Part_No'])
    result_foqc.to_csv(r'D:\Project\AVI_AI\test3.csv')
    return result_foqc


def ai_mapping(foqc_df,mapping_range=8):
    ai_df = pd.read_csv(os.path.join(ai_data_dir,'ai_all.csv'))
    #check the ai on or off & only count the on one
    ai_df.loc[(ai_df.model != 'R1') & (ai_df.model != 'Z1') & (ai_df.AI != 'Unactivated'),'AI'] = 'OFF'
    ai_df = ai_df[ai_df.AI == 'ON'].reset_index(drop=True)
    #ai_df['key'] = ai_df.part.str.split('-').str[1]
    ai_df['Part_No'] = ai_df['Part_No'].astype(str).str[:9]
    ai_df['date_sort'] = pd.to_datetime(ai_df.VRS)
    ai_df = ai_df.groupby(['Part_No','lot','model','size']).resample('14D', on='date_sort').agg({'AVI': 'last','visper': 'last','part': 'last','VRS': 'last','type': 'last','vrs_id': 'last','strips': 'sum','CheckTime(min)': 'sum','OK': 'sum','NG': 'sum','ALL': 'sum','filter rate': 'sum'}).reset_index()
    ai_df.to_csv(r'D:\Project\AVI_AI\test11.csv')
    ai_df = ai_df[ai_df.strips != 0]
    ai_df['year'] = ai_df.AVI.astype(str).str[2:4]
    
    #AVI	part	VRS	Part_No	lot	vrs_id	strips	CheckTime(min)	OK	NG	ALL	filter rate	visper	AI	size	type	model
    ai_df['year'] = ai_df[ai_df.strips != 0].AVI.astype(str).str[2:4].astype(int)
    #df['DataFrame Column'] = pd.to_datetime(df['DataFrame Column'], format=specify your format)
    ai_df['week'] = pd.to_datetime(ai_df['AVI'],format='%Y%m%d').dt.strftime('%U').astype(int) + 2
    add_df = ai_df.copy()
    for a in range(1,mapping_range):
        add_df['week'] = add_df['week'] - a
        ai_df = pd.concat([ai_df,add_df])
    
    ai_df.loc[ai_df.week < 1,'year'] -= 1
    ai_df.loc[ai_df.week < 1,'week'] += 52
    ai_df['Date_Code'] = (ai_df.week * 100 + ai_df.year).astype(str).apply(lambda x: x.zfill(4))
    
    ai_df['lot'] = ai_df['lot'].astype(str).str[:4]
    anova = ai_df.merge(foqc_df,on = ['Date_Code','Part_No','lot'],how = 'left')
    anova.to_csv(r'D:\Project\AVI_AI\test8.csv')
    anova['FQC_date'] = pd.to_datetime(anova['FQC_date'])
    anova['OQC_date'] = pd.to_datetime(anova['OQC_date'])
    anova['VRS'] = pd.to_datetime(anova['VRS'])
    anova['fqc_date_check'] = anova.apply(lambda x: timedelta(days=100) if pd.isnull(x['FQC_date']) else x['FQC_date']-x['VRS'],axis=1)
    anova['oqc_date_check'] = anova.apply(lambda x: timedelta(days=100) if pd.isnull(x['OQC_date']) else x['OQC_date']-x['VRS'],axis=1)    
    anova.fqc_date_check = anova.fqc_date_check.abs()
    anova.oqc_date_check = anova.oqc_date_check.abs()
    anova.loc[anova['fqc_date_check']>=timedelta(days = 14),['FQC_date','OQC_date']] = [np.timedelta64('NAT'),np.timedelta64('NAT')]
    anova.loc[anova['fqc_date_check']>=timedelta(days = 14),['FQC_OK','Total_Strips','OQC_strips','OQC_rejection']] = [np.nan,np.nan,np.nan,np.nan]
    anova.loc[anova['oqc_date_check']>=timedelta(days = 14),['OQC_date']] = [np.timedelta64('NAT')]
    anova.loc[anova['oqc_date_check']>=timedelta(days = 14),['OQC_strips','OQC_rejection']] = [np.nan,np.nan]
    anova = anova.sort_values(['fqc_date_check']).reset_index()
    anova.to_csv(r'D:\Project\ai\Data\test.csv')
    anova = anova.groupby(['Part_No','lot','date_sort']).first().reset_index()
    anova_preprocess = anova[['Part_No','lot','Date_Code','strips']]
    anova_preprocess = anova_preprocess.groupby(['Part_No','lot','Date_Code']).count().reset_index()
    anova_preprocess = anova_preprocess[anova_preprocess.strips >1]
    
    loop_use = anova_preprocess[['Part_No','lot','Date_Code','strips']].sort_values('strips').reset_index(drop=True).values.tolist()
    for bb,cc,dd,ee in loop_use:
        index_no = anova[(anova.Part_No == bb) & (anova.lot == cc) & (anova.Date_Code == dd)].index[1]
        anova.loc[index_no,['FQC_date','OQC_date']] = [np.timedelta64('NAT'),np.timedelta64('NAT')]
        anova.loc[index_no,['FQC_OK','Total_Strips','OQC_strips','OQC_rejection']] = [np.nan,np.nan,np.nan,np.nan]
    
    
    anova = anova.reset_index(drop=True)
    
    anova['VRS'] = pd.to_datetime(anova['VRS']).dt.date
    #anova['UPH'] = round(anova['UPH'],2)
    #anova['filter_rate'] = round(anova['filter_rate'],2)
    #anova['point_avg'] = round(anova['point_avg'],2)
    #anova['yield'] = round(anova['yield'],2)
    #anova['rejection_rate'] = round(anova['rejection_rate'],2)
    anova.to_csv(r'D:\Project\AVI_AI\test8.csv')
    anova1 = anova[(anova.type != 'Sample') & (anova.type != 'Sample2')]

    first_row = pd.DataFrame(np.array([['non-AI base',90,'6.2%']]),columns = ['Week','UPH','Reject rate'])
    anova_week = anova1.reset_index()
    anova_week['VRS'] = pd.to_datetime(anova_week['VRS'])
    anova_week.set_index('VRS')
    
    anova_part = anova_week.groupby('size').resample('W-Sun', on='VRS').sum().reset_index().sort_values(by='VRS')
    anova_part['Week'] = anova_part['size']
    
    anova_month = anova_week.resample('M', on='VRS').sum().reset_index().sort_values(by='VRS')
    anova_month['Week'] = [str(i.strftime("%m"))+'月總計' for i in anova_month.VRS]
    anova_month.to_csv(r'D:\Project\AVI_AI\test6.csv')
    
    anova_week = anova_week.resample('W-Sun', on='VRS').sum().reset_index().sort_values(by='VRS')
    anova_week['Week'] = ['W'+str(i + 11)+' 合計' for i in anova_week.index]

    
    anova_week['VRS'] = ''
    anova_week = pd.concat([anova_week,anova_part,anova_month])
    anova_week['Pics/strip'] = round(anova_week['ALL']/anova_week['strips'],0)
    anova_week['Filer rate'] = round(anova_week['OK']/anova_week['ALL']*100,1).astype(str) + '%'
    anova_week['UPH'] = round(anova_week['strips']/anova_week['CheckTime(min)']*60,0)
    anova_week['Yield'] =  round(anova_week['FQC_OK']/anova_week['Total_Strips']*100,1).astype(str) + '%'
    anova_week['Reject rate'] = round(anova_week['OQC_rejection']/anova_week['OQC_strips']*100,1).astype(str) + '%'
    anova_week = pd.concat([first_row,anova_week])
    anova_week = anova_week[['Week','strips','Pics/strip','Filer rate','UPH','Reject rate']]
    anova_week.to_csv(r'D:\Project\AVI_AI\test6.csv')
    
if __name__ == '__main__':
    
    avi_foqc_crawler.do_crawl()
    #avi_ai_crawler.update_ai_data(ai_data_dir)
    #foqc = date_code_mapping()
    #ai_mapping(foqc)
    #preset()
    
    
    '''
    preset()
    avi_foqc_crawler.do_crawl()
    avi_ai_crawler.update_ai_data(ai_data_dir)
    '''