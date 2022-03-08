# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 14:14:05 2022

@author: A2433
"""

import os
import glob
import pandas as pd
from datetime import date, datetime, timedelta
import numpy as np
import time

#pd.options.mode.chained_assignment = None

today = date.today()
today_date = today.strftime("%Y%m%d")
base_data_dir = os.path.join('..', 'data')
ai_data_dir = os.path.join(base_data_dir, 'AI')
past_data_dir = os.path.join(ai_data_dir,'ai_all.csv')

#ip_address_check
if os.path.exists(r'\\10.19.13.40\DataFiles(Edit)'):
    ip_address = '10.19.13.40'
if os.path.exists(r'\\192.168.0.111\DataFiles(Edit)'):
    ip_address = '192.168.0.111'
    
if ip_address == '192.168.0.111':
    past_data_dir = r'\\{}\ScanImages\ai_all.csv'.format(ip_address)

if os.path.exists(past_data_dir):
    ai_edit_dir = r'\\{}\DataFiles(Edit)\visper-1'.format(ip_address)
    ai_df = pd.read_csv(past_data_dir)
    check_last = min(os.listdir(ai_edit_dir))
    if int(check_last) > ai_df.iloc[-1]['AVI']:
        ai_edit_dir = r'\\{}\ScanImagesBK\DataFiles_Edit\visper-1'.format(ip_address)
else:
    ai_edit_dir = r'\\{}\ScanImagesBK\DataFiles_Edit\visper-1'.format(ip_address)
    ai_df = pd.DataFrame(columns=['AVI','part','VRS','Part_No','lot','vrs_id','strips','CheckTime(min)','OK','NG','ALL','filter rate','visper','AI','size','type','model'])

print('Date from ' + ai_edit_dir)

def check_unprocessed_date(check_dir,ai_df=ai_df):
    #print('STATUS:getting unprocessed date...')
    present_list = os.listdir(ai_edit_dir)
    last_date = '20210101'
    if len(ai_df) != 0:
        last_date = ai_df.iloc[-1]['AVI']
        last_date = (datetime.strptime(str(last_date), '%Y%m%d')-timedelta(days=7)).strftime('%Y%m%d')
    print('UPDATE FROM ' +last_date)
    unprocessed_list = [i for i in present_list if (len(i)==8)&(i>=last_date)]
    #print('STATUS:getting unprocessed date Done')
    return unprocessed_list

    
def check_unprocessed_lot(undo_date):
    if os.path.exists(past_data_dir):
        ai_df = pd.read_csv(past_data_dir)
    else:
        ai_df = pd.DataFrame(columns=['AVI','part','VRS','Part_No','lot','vrs_id','strips','CheckTime(min)','OK','NG','ALL','filter rate','visper','AI','size','type','model'])
    present_part_list = os.listdir(os.path.join(ai_edit_dir,undo_date))
    for a in present_part_list:
        lot_path = os.path.join(ai_edit_dir,undo_date,a)
        print('STATUS:checking ' + undo_date +' '+ a +' data is changed or not...')
        if len(glob.glob((os.path.join(lot_path,'*\*\VRS.OK')))) == ai_df[(ai_df.AVI.astype(int) == int(undo_date))&(ai_df.part.astype(str) == str(a))]['strips'].sum():
            print('STATUS:checking ' + undo_date +' '+ a +' data all Good')
            pass
        else:
            ai_df = ai_df[(ai_df.AVI.astype(int) != int(undo_date))|(ai_df.part.astype(str) != str(a))]
            print('STATUS:updating ' + undo_date +' '+ a +' data...')
            ai_df = get_lot_info(lot_path,ai_df)
            print('STATUS:updating ' + undo_date +' '+ a +' data Done')



def get_lot_info(lot_path,ai_df):
    concat_list = []
    for lot in os.listdir(lot_path):
        concat_df = pd.DataFrame()
        vrs_time = []
        ai_status = 'ON'
        while True:
            try:
                panel_dir = os.listdir(os.path.join(lot_path,lot))
                break
            except:
                print('ReConneting')
        for panel in panel_dir:
            try:
                vrs_time.append(os.path.getctime(os.path.join(lot_path,lot,panel,'VRS.OK')))
                if os.path.exists(os.path.join(lot_path,lot,panel,'VRS.csv')):
                    ai_status = 'unfiltered'
                pre_df = pd.read_csv(os.path.join(lot_path,lot,panel,'AI.csv'),header=9)
                concat_df = pd.concat([concat_df,pre_df])
            except:
                pass
        ##ARRANGE AI INFO  
        if len(vrs_time) > 0:
            vrs_spend = [vrs_time[n] - vrs_time[n-1] for n in range(1,len(vrs_time))]
            time_mean = np.mean([abs(t) for t in vrs_spend if abs(t)<600])
            spent_time = time_mean*len(vrs_spend)
            VRS = datetime.fromtimestamp(np.median(vrs_time)).strftime("%Y-%m-%d") 
            strips = len(vrs_time)
            try:
                OK_m = len(concat_df[concat_df.AI_Flag.astype(str) == 'OK'])
                NG_m = len(concat_df[concat_df.AI_Flag.astype(str) != 'OK'])
                if OK_m == 0:
                    AI = 'Unactivated'
                else:
                    AI = 'ON'
                if ai_status == 'unfiltered':
                    AI = 'unfiltered'
                ALL_m = OK_m + NG_m
                filter_rate = round(OK_m/ALL_m,2) 
            except:
                OK_m = np.nan
                NG_m = np.nan
                ALL_m = np.nan
                filter_rate = np.nan
                AI = 'OFF'
            CheckTime = round(spent_time/60,0)
            pics_path = os.path.join(lot_path,lot)
            path_list = pics_path.split('\\')
            idx = len(path_list)
            vrs_id = path_list[idx-1]
            tape_lot = vrs_id[vrs_id.find('[')+1 : vrs_id.find('-')]
            try:
                tape_lot = int(tape_lot)
                if tape_lot < 1000:
                    tape_lot += 1000
            except:
                tape_lot = np.nan
            AVI = path_list[idx-3]
            part = path_list[idx-2]
            part_arrange = part.replace('-300','')
            try:
                visper = part_arrange.split('-')[0]
                Part_No = part_arrange.split('-')[1]
                size = part_arrange.split('-')[2]
                if (size != '10UM') & (size != '5UM'):
                    size = '18UM'
                model = part_arrange.split('-')[-1]
                Type = part_arrange.split('-')[-2]
            except:
                visper = np.nan
                Part_No = np.nan
                size = np.nan
                model = np.nan
                Type = np.nan
                
            concat_list.append([AVI,part,VRS,Part_No,tape_lot,vrs_id,strips,CheckTime,OK_m,NG_m,ALL_m,filter_rate,visper,AI,size,Type,model])
    if len(concat_list) > 0:
        add_df = pd.DataFrame(np.array(concat_list),columns=['AVI','part','VRS','Part_No','lot','vrs_id','strips','CheckTime(min)','OK','NG','ALL','filter rate','visper','AI','size','type','model'])
        add_df = add_df[(add_df.visper.astype(str) == 'V1')|(add_df.visper.astype(str) == 'V2')|(add_df.visper.astype(str) == 'V3')|(add_df.visper.astype(str) == 'V4')|(add_df.visper.astype(str) == 'V5')|(add_df.visper.astype(str) == 'V6')]
        ai_df = pd.concat([ai_df,add_df],sort=False)
        ai_df.AVI = ai_df.AVI.astype(int)
        ai_df = ai_df.sort_values(by='AVI').reset_index(drop=True)
        ai_df.loc[(ai_df.model != 'R1') & (ai_df.model != 'Z1') & (ai_df.AI != 'Unactivated'),'AI'] = 'OFF'
        ai_df.to_csv(past_data_dir,index=False)
    return ai_df


def update_ai_data(check_dir):
    date_list = check_unprocessed_date(check_dir)
    for d in date_list:
        check_unprocessed_lot(d)


if __name__ == '__main__':
    while True:
        try:
            update_ai_data(ai_data_dir)
        except Exception as e:
            print(e)
        print('SLEEPING')
        time.sleep(43200)
        print('UPDATE')
