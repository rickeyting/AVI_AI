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
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

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
        df = pd.read_excel(path, sheet_name='Sheet1', header=5)
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
        df = pd.read_excel(path, sheet_name='Sheet1', header=4)
        df = df[['檢驗日期','料號','D/C','批號','檢驗次數','狀態','批量']]
        result.append(df)
    result = pd.concat(result)
    result.columns = ['OQC_date','Part_No','Date_Code','lot','check_times','reject_times','OQC_Strips']
    result['OQC_date'] = result['OQC_date'].astype(str).str[:10]
    result['OQC_date'] = pd.to_datetime(result['OQC_date'])
    result['lot'] = result['lot'].astype(str)
    result['OQC_AVI'] = 'OFF'
    result.loc[result['lot'].str.contains('V'),'OQC_AVI'] = 'ON'
    result['lot']=result['lot'].str[:4]
    result['Part_No'] = result['Part_No'].str[:9]
    result.lot = pd.to_numeric(result.lot, errors='coerce')
    result.Date_Code = pd.to_numeric(result.Date_Code, errors='coerce')
    result.loc[result.reject_times != '退回','reject_times'] = 0
    result.loc[result.reject_times == '退回','reject_times'] = 1
    result['check_times'] = 1
    #result_group = result.groupby(['Part_No','Date_Code','lot']).agg({'OQC_date':'last','check_times':'count','reject_times':'sum','OQC_AVI':'max','OQC_Strips':'sum'}).reset_index()
    return result


def ai_data(ai_path):
    print('STATUS: arrange ai data')
    df = pd.read_csv(ai_path)
    df = df[['AVI','VRS','Part_No','lot','strips','CheckTime(min)','OK','NG','ALL','type','size','AI','Date_Code','model']]
    df['Part_No'] = df.Part_No.str[:9]
    #df.loc[(df['model'] != 'R1') & (df['model'] != 'Z1') & (df.AI != 'Unactivated') & (df.AI != 'unfiltered'),'AI'] = 'OFF'
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
    df = df.fillna(0)
    df_m = df.resample('M',on='VRS').sum().reset_index()
    df_m.VRS = df_m.VRS.dt.month.astype(str) + '月總計'
    df_s = df.groupby('size').resample('W',on='VRS').sum().reset_index()
    df_s.VRS = df_s.VRS.astype(str) + 'W' + (df_s.VRS.dt.week+1).astype(str).str.rjust(2, "0")
    df_s = df_s.sort_values(by=['VRS','size'])
    df_s.VRS = df_s.VRS.str[10:]
    result = pd.concat([df_m, df_s], sort=False)
    result['Pics/strip'] = round(result['ALL']/result['strips'],0)
    result['Filer rate'] = round(result['OK']/result['ALL']*100,1).astype(str) + '%'
    result['UPH'] = round(result['strips']/result['CheckTime(min)']*60,0)
    result['Yield'] =  round(result['OK_Strips']/result['FQC_Strips']*100,1).astype(str) + '%'
    result['Reject rate'] = round(result['reject_times']/result['check_times']*100,1).astype(str) + '%'
    result.loc[result['Reject rate']==0,'Reject rate'] = None
    first_row = pd.DataFrame(np.array([['non-AI base',90,'6.2%']]),columns = ['VRS','UPH','Reject rate'])
    result = pd.concat([first_row,result],sort=False)
    result = result[['VRS','size','strips','Pics/strip','Filer rate','UPH','Reject rate']]
    result.columns = ['VRS','','strips','Pics/strip','Filer rate','UPH','Reject rate']
    return result

def avi_cover_rate(fqc_path,sorting=['907','908']):
    result = []
    print('STATUS: concat FQC data')
    for i in tqdm(os.listdir(fqc_path)):
        path = os.path.join(fqc_path,i)
        df = pd.read_excel(path, sheet_name='Sheet1', header=5)
        df = df.dropna(subset=['Part No.'])
        df = df[['Time','Part No.','Date Code','Lot No.','Total Strips','OK & X-Out(Strips)','Remark']]
        result.append(df)
    result = pd.concat(result)
    result.columns = ['FQC_date','Part_No','Date_Code','lot','FQC_Strips','OK_Strips','AVI']
    result.loc[result['AVI'].str.contains('V', na=False),'AVI'] = 'ON'
    result.loc[result['AVI'] != 'ON','AVI'] = 'OFF'
    result['Part_No'] = result['Part_No'].str[:9]
    result = result.replace(' ', '', regex=True)
    return result
    
def separate_concat(ai_path,fqc_path,oqc_path,other_conditions=None, other_freq='M'):
    oqc_df = oqc_data(oqc_path)
    mp_date = datetime.strptime('2022/07/01', '%Y/%m/%d')
    oqc_df = oqc_df[['OQC_date', 'Part_No', 'check_times', 'reject_times', 'OQC_Strips','OQC_AVI']]
    oqc_df['reject_times'] = oqc_df['reject_times'].astype(int)
    oqc_df['OQC_date'] = pd.to_datetime(oqc_df['OQC_date'])
    oqc_df_Z01_sample = oqc_df.loc[oqc_df['Part_No'].str.contains('P328', na=False)]
    oqc_df_mp = oqc_df_Z01_sample.loc[oqc_df_Z01_sample['OQC_date'] >= mp_date]  ##
    oqc_df_Z01_sample = oqc_df_Z01_sample.loc[oqc_df_Z01_sample['OQC_date'] < mp_date] ##
    print(len(oqc_df_mp))
    oqc_df_sp = oqc_df_mp.loc[oqc_df_mp['Part_No'].str.contains('P3285', na=False)]
    oqc_df_mp = oqc_df_mp.loc[~oqc_df_mp['Part_No'].str.contains('P3285', na=False)]
    print(len(oqc_df_mp), len(oqc_df_sp))
    oqc_df_Z01_sample = pd.concat([oqc_df_Z01_sample, oqc_df_sp])

    oqc_df_Z01_sample.loc[:, 'Part_No'] = 'SAMPLE'
    oqc_df_Z01 = oqc_df.loc[oqc_df['Part_No'].str.contains('P329|PJ5', na=False)]
    oqc_df_Z01 = pd.concat([oqc_df_Z01, oqc_df_mp]) ##
    oqc_df_Z01.loc[:, 'Part_No'] = 'MP'
    oqc_df_GAN = oqc_df.loc[oqc_df['Part_No'].str.contains('GAN', na=False)]
    oqc_df_GAN.loc[:, 'Part_No'] = 'GAN'
    ts = pd.DataFrame()
    if other_conditions != None:
        ts = oqc_df.loc[oqc_df['Part_No'].str.contains(other_conditions, na=False)]
        ts.loc[:, 'Part_No'] = 'other'
        ts = ts.groupby(['Part_No', 'OQC_AVI']).resample(other_freq, on='OQC_date').sum()

    oqc_df_Z01_sample = oqc_df_Z01_sample.groupby(['Part_No', 'OQC_AVI']).resample('M', on='OQC_date').sum()
    oqc_df_Z01 = oqc_df_Z01.groupby(['Part_No', 'OQC_AVI']).resample('M', on='OQC_date').sum()
    oqc_df_GAN = oqc_df_GAN.groupby(['Part_No', 'OQC_AVI']).resample('M', on='OQC_date').sum()
    oqc_all = pd.concat([oqc_df_Z01_sample,oqc_df_Z01,oqc_df_GAN, ts]).reset_index()
    oqc_all = oqc_all.rename(columns={"OQC_date":"Date", 'OQC_AVI':'AVI'})

    ai_df = pd.read_csv(ai_path)
    ai_df.loc[ai_df['model'] == 'G1', 'AI'] = 'ON'
    ai_df.loc[(ai_df['model'] == 'G1') & (ai_df['OK'] == 0), 'AI'] = 'OFF'
    ai_df = ai_df[['VRS','Part_No','strips','CheckTime(min)','OK','NG','ALL','AI']]
    ai_df.loc[(ai_df['AI']=='ON') | (ai_df['AI']=='Beta'), 'AI'] = 'ON'
    ai_df.loc[(ai_df['AI']!='ON'), 'AI'] = 'OFF'
    ai_df['VRS'] = pd.to_datetime(ai_df['VRS'])
    ai_df = ai_df.loc[ai_df['AI']=='ON']
    #ai_df.loc[ai_df['AI'] == 'OFF', 'off_strip'] = ai_df.loc[ai_df['AI'] == 'OFF', 'strips']
    #ai_df.loc[ai_df['AI'] == 'OFF', 'strips'] = 0
    ai_df = ai_df[['VRS','Part_No','strips','CheckTime(min)','OK','NG','ALL']]
    ai_df_Z01_sample = ai_df.loc[ai_df['Part_No'].str.contains('P328', na=False)]
    ai_df_mp = ai_df_Z01_sample.loc[ai_df_Z01_sample['VRS'] >= mp_date]  ##
    ai_df_Z01_sample = ai_df_Z01_sample.loc[ai_df_Z01_sample['VRS'] < mp_date]  ##
    ai_df_sp = ai_df_mp.loc[ai_df_mp['Part_No'].str.contains('P3285', na=False)]
    ai_df_mp = ai_df_mp.loc[~ai_df_mp['Part_No'].str.contains('P3285', na=False)]
    ai_df_Z01_sample = pd.concat([ai_df_Z01_sample, ai_df_sp])
    ai_df_Z01_sample.loc[:, 'Part_No'] = 'SAMPLE'
    ai_df_Z01 = ai_df.loc[ai_df['Part_No'].str.contains('P329|PJ5', na=False)]
    ai_df_Z01 = pd.concat([ai_df_Z01, ai_df_mp])  ##
    #ai_df_Z01.to_csv(r'D:\Project\AVI_AI\123.csv')
    ai_df_Z01.loc[:, 'Part_No'] = 'MP'
    ai_df_GAN = ai_df.loc[ai_df['Part_No'].str.contains('GAN', na=False)]
    ai_df_GAN.loc[:, 'Part_No'] = 'GAN'
    ai_df_Z01 = ai_df_Z01.groupby(['Part_No']).resample('M', on='VRS').sum().reset_index()
    ai_df_Z01_sample = ai_df_Z01_sample.groupby(['Part_No']).resample('M', on='VRS').sum().reset_index()
    ai_df_GAN = ai_df_GAN.groupby(['Part_No']).resample('M', on='VRS').sum().reset_index()
    ai_all = pd.concat([ai_df_Z01_sample,ai_df_Z01,ai_df_GAN])
    ai_all['AVI'] = 'ON'
    ai_all = ai_all.rename(columns={"VRS":"Date"})
    
    fqc_df = avi_cover_rate(fqc_path)
    fqc_df['FQC_date'] = pd.to_datetime(fqc_df['FQC_date'])
    fqc_df = fqc_df[['Part_No','FQC_date','FQC_Strips','OK_Strips','AVI']]
    cover_result_Z01_sample = fqc_df.loc[fqc_df['Part_No'].str.contains('P328', na=False)]
    FQC_df_mp = cover_result_Z01_sample.loc[cover_result_Z01_sample['FQC_date'] >= mp_date]  ##
    cover_result_Z01_sample = cover_result_Z01_sample.loc[cover_result_Z01_sample['FQC_date'] < mp_date]  ##
    FQC_df_sp = FQC_df_mp.loc[FQC_df_mp['Part_No'].str.contains('P3285', na=False)]
    FQC_df_mp = FQC_df_mp.loc[~FQC_df_mp['Part_No'].str.contains('P3285', na=False)]
    cover_result_Z01_sample = pd.concat([cover_result_Z01_sample, FQC_df_sp])

    cover_result_Z01_sample.loc[:, 'Part_No'] = 'SAMPLE'

    cover_result_Z01_sample = cover_result_Z01_sample.groupby(['Part_No','AVI']).resample('M',on='FQC_date').sum().reset_index()
    cover_result_Z01 = fqc_df.loc[fqc_df['Part_No'].str.contains('P329|PJ5', na=False)]
    cover_result_Z01 = pd.concat([cover_result_Z01, FQC_df_mp])  ##
    cover_result_Z01.loc[:, 'Part_No'] = 'MP'
    cover_result_Z01 = cover_result_Z01.groupby(['Part_No','AVI']).resample('M',on='FQC_date').sum().reset_index()
    cover_result_GAN = fqc_df.loc[fqc_df['Part_No'].str.contains('GAN', na=False)]
    cover_result_GAN.loc[:, 'Part_No'] = 'GAN'
    cover_result_GAN = cover_result_GAN.groupby(['Part_No','AVI']).resample('M',on='FQC_date').sum().reset_index()
    ts = pd.DataFrame()
    if other_conditions != None:
        ts = fqc_df.loc[fqc_df['Part_No'].str.contains(other_conditions, na=False)]
        ts.loc[:, 'Part_No'] = 'other'
        ts = ts.groupby(['Part_No', 'AVI']).resample(other_freq, on='FQC_date').sum().reset_index()
    fqc_all = pd.concat([cover_result_Z01_sample,cover_result_Z01,cover_result_GAN,ts])
    fqc_all = fqc_all.rename(columns={"FQC_date":"Date"})
    result = fqc_all.merge(oqc_all ,on=['Part_No','AVI','Date'], how='left').merge(ai_all, on=['Part_No','AVI','Date'], how='left')
    result['Date'] = pd.to_datetime(result['Date'])
    result = result.loc[result['Date'] > datetime.strptime('2022/1/1', '%Y/%m/%d')]
    result['Avg. Points'] = result['ALL'] / result['strips']
    result['UPH'] = result['strips'] / result['CheckTime(min)'] * 60
    result['Effciency'] = result['UPH']/90
    result.loc[:, 'Filter rate'] = result['OK'] / result['ALL'] * 100
    result.loc[:, 'rejection'] = result['reject_times'] / result['check_times'] * 100
    result.loc[:, 'rejection'] = result.loc[:, 'rejection'].fillna(0)
    coverage = result[['Part_No', 'Date', 'FQC_Strips']].groupby(['Part_No', 'Date']).sum()
    coverage = coverage.rename(columns={"FQC_Strips": "FQC_ALL"})
    result = result.merge(coverage, on=['Part_No', 'Date'], how='left')
    result['AVI_coverage'] = result['FQC_Strips'] / result['FQC_ALL'] * 100
    return result

def result_plt(df, output_path):
    result = df
    types = list(set(result['Part_No'].values.tolist()))
    #result['AI_coverage'] = result['strips']/(result['strips']+result['off_strip'])*result['AVI_coverage']
    
    for i in types:
        fig = plt.figure()
        #ax1 = plt.subplot(4,1,(1,2))
        ax1 = plt.subplot()
        ax1.set_title('AI-performance',x=0.11,y=0.89)
        plt.rcParams['axes.facecolor'] = 'white'
        line11 = ax1.bar(result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'Date'].astype(str),result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'UPH'],color = 'skyblue')
        text_lit = result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON')][['Date', 'UPH']].values.tolist()
        for d in text_lit:
            ax1.text(d[0].strftime('%Y-%m-%d'), d[1]+5, "{:.0f}".format(d[1]),fontsize=12, ha="center", color='black')
        ax1.set_ylim(0, 500)
        ax11=ax1.twinx()
        line12, = ax11.plot(result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'Date'].astype(str),result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'Filter rate'],color="darkblue",marker = "o", linestyle= "-",linewidth = '0.8')
        text_lit = result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON')][['Date', 'Filter rate']].values.tolist()
        for d in text_lit:
            ax11.text(d[0].strftime('%Y-%m-%d'), d[1]+5, "{:.1f}%".format(d[1]),fontsize=12, ha="center", color='darkblue')
        if i == 'MP':
            ax1.plot([-0.5,7.5], [90,90], '--', linewidth = 0.7, color='dimgray')
            ax1.text(-0.5,95,'base-90',color='dimgray')
        ax11.set_ylim(0, 100)
        #ax1.set_xticks([])
        ax1.set_yticks([100,200,300,400])
        ax11.set_yticks([20,40,60,80])
        ax1.legend([line11,line12],['UPH','Filter rate'], loc='upper right')
        fig.set_figheight(3)
        fig.set_figwidth(12)
        fig.savefig('{}\{}_ai.jpg'.format(output_path, i), dpi = 200,bbox_inches='tight')
        
        
        fig = plt.figure()
        #ax2 = plt.subplot(413)
        ax2 = plt.subplot()
        ax2.set_title('OQC-rejection',x=0.08,y=0.85)
        line21, = ax2.plot(result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'Date'].astype(str),result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'rejection'],color="darkgreen",marker = "o", linestyle= "-",linewidth = '0.8')
        line22, = ax2.plot(result.loc[(result['Part_No'] == i) & (result['AVI'] == 'OFF'), 'Date'].astype(str),result.loc[(result['Part_No'] == i) & (result['AVI'] == 'OFF'), 'rejection'],color="darkorange",marker = "o", linestyle= "-",linewidth = '0.8')
        text_lit = result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON')][['Date', 'rejection']].values.tolist()
        for d in text_lit:
            ax2.text(d[0].strftime('%Y-%m-%d'), d[1]-4, "{:.1f}%".format(d[1]),fontsize=12, ha="center", color='darkgreen')
        text_lit = result.loc[(result['Part_No'] == i) & (result['AVI'] == 'OFF')][['Date', 'rejection']].values.tolist()
        for d in text_lit:
            ax2.text(d[0].strftime('%Y-%m-%d'), d[1]+2, "{:.1f}%".format(d[1]),fontsize=12, ha="center", color='darkorange')
        ax2.set_ylim(-10, 30)
        ax2.set_yticks([0,10,20])
        if i == 'MP':
            ax2.plot([0,7], [6.2,6.2], '--', linewidth = 0.7, color='dimgray')
            ax2.text(-0.45,5.5,'base-6.2%',color='dimgray')
        #ax2.set_xticks([])
        ax2.legend([line21,line22],['AVI-ON','AVI-OFF'], loc='upper center')
        fig.set_figheight(2)
        fig.set_figwidth(12)
        fig.savefig('{}\{}_oqc.jpg'.format(output_path, i), dpi = 200,bbox_inches='tight')
        
        fig = plt.figure()
        #ax3 = plt.subplot(414)
        ax3 = plt.subplot()
        ax3.set_title('FQC-coverage',x=0.08,y=0.85)
        line31, = ax3.plot(result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'Date'].astype(str),result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'AVI_coverage'],color="firebrick",marker = "o", linestyle= "-",linewidth = '0.8')
        #line32, = ax3.plot(result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'Date'].astype(str),result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON'), 'AI_coverage'],color="purple",marker = "o", linestyle= "-",linewidth = '0.8')
        text_lit = result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON')][['Date', 'AVI_coverage']].values.tolist()
        for d in text_lit:
            ax3.text(d[0].strftime('%Y-%m-%d'), d[1]+2, "{:.1f}%".format(d[1]),fontsize=12, ha="center", color='firebrick')
        #text_lit = result.loc[(result['Part_No'] == i) & (result['AVI'] == 'ON')][['Date', 'AI_coverage']].values.tolist()
        #for d in text_lit:
        #    ax3.text(d[0].strftime('%Y-%m-%d'), d[1]-10, "{:.1f}%".format(d[1]),fontsize=12, ha="center", color='purple')
        ax3.set_ylim(0, 110)
        ax3.set_yticks([0,50,100])
        ax3.legend([line31],['AVI'], loc='upper center')
        fig.set_figheight(2)
        fig.set_figwidth(12)
        fig.savefig('{}\{}_fqc.jpg'.format(output_path, i), dpi = 200,bbox_inches='tight')

'''    
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
'''

def output_exl(sheets,output_path):
    output_dir = os.path.join(output_path,'AI測試報表_{}.xls'.format(datetime.today().strftime('%Y%m%d')))
    with pd.ExcelWriter(output_dir) as writer:
        for i in sheets:
            sheets[i].to_excel(writer, sheet_name=i,index=False)

    
if __name__ == '__main__':
    #test_plt()
    #all_concat(AI_DIR,FQC_DIR,OQC_DIR)
    #ai_data(AI_DIR).to_csv(TEST_SAVE)
    pass