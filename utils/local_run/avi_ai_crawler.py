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
past_data_dir = os.path.join('..',ai_data_dir,'ai_all_true.csv')
#ip_address_check
def current_time():
    return '[{}]'.format(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

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
    ai_df = pd.DataFrame(columns=['AVI','part','Date_Code','VRS','Part_No','lot','vrs_id','strips','CheckTime(min)','OK','NG','ALL','filter rate','visper','AI','size','type','model'])


def merge_pics(df2, df, x_columns='Step_Xvalue', y_columns='Step_Yvalue', resolution=0.005, frame_pixel=350, limit_frame=30): #mm
    df2 = df2[['AVI_Image_Path', 'AI_Flag']]
    df = df.drop('AI_Flag', axis = 1)
    df = df.merge(df2, on='AVI_Image_Path', how='left')
    df = df[df['AI_Flag'].astype(str) != 'OK']
    side_list = list(dict.fromkeys(df['Side'].values.tolist()))
    for i in range(len(side_list)):
        df.loc[df['Side']==side_list[i], 'Step_Xvalue'] = df.loc[df['Side']==side_list[i], 'Step_Xvalue'] + 100*i
    df = df[['Step_Xvalue','Step_Yvalue']]
    df = df.sort_values(by='Step_Xvalue')
    frame_size = resolution * (frame_pixel - limit_frame)
    frame = frame_pixel * resolution
    #x,y = center
    df = df[[x_columns, y_columns]]
    df = df.reset_index()
    #df['x1'] = df[x_columns] - frame_size
    #df['y1'] = df[y_columns] - frame_size
    #df['x2'] = df[x_columns] + frame_size
    #df['y2'] = df[y_columns] + frame_size
    original_frame = np.array(df.values.tolist())
    x = original_frame[:,1]
    y = original_frame[:,2]
    index = original_frame[:,0]
    index = index.argsort()[::]
    #print(index)
    keep = []
    while index.size > 0:
        i = index[0]
        keep.append(i)
        x_distance = x[index[1:]] - x[i]
        y_distance = y[index[1:]] - y[i]
        idxx = np.where((x_distance>frame_size) | (x_distance<-1*frame_size))[0]
        idxy = np.where((y_distance>frame_size) | (y_distance<-1*frame_size))[0]
        idx = np.union1d(idxx, idxy)
        index = index[idx+1]

    #print(len(keep))
    #print(original_frame)
    return len(keep)


def check_unprocessed_date(check_dir,ai_df=ai_df):
    #print('STATUS:getting unprocessed date...')
    present_list = os.listdir(ai_edit_dir)
    last_date = '20210101'
    if len(ai_df) != 0:
        last_date = ai_df.iloc[-1]['AVI']
        last_date = (datetime.strptime(str(last_date), '%Y%m%d')-timedelta(days=5)).strftime('%Y%m%d')
    print('{} UPDATE FROM '.format(current_time()) +last_date)
    unprocessed_list = [i for i in present_list if (len(i)==8)&(i>=last_date)]
    #unprocessed_list = ['20220414']
    #print('STATUS:getting unprocessed date Done')
    return unprocessed_list

    
def check_unprocessed_lot(undo_date):
    if os.path.exists(past_data_dir):
        ai_df = pd.read_csv(past_data_dir)
    else:
        ai_df = pd.DataFrame(columns=['AVI','part','Date_Code','VRS','Part_No','lot','vrs_id','strips','CheckTime(min)','OK','NG','ALL','filter rate','visper','AI','size','type','model','OPID','VRSmachine','vrs_pics'])
    present_part_list = os.listdir(os.path.join(ai_edit_dir,undo_date))
    for a in present_part_list:
        lot_path = os.path.join(ai_edit_dir,undo_date,a)
        print('{} checking '.format(current_time()) + undo_date +' '+ a +' data is changed or not...')
        if len(glob.glob((os.path.join(lot_path,'*\*\VRS.OK')))) == ai_df[(ai_df.AVI.astype(int) == int(undo_date))&(ai_df.part.astype(str) == str(a))]['strips'].sum():
            print('{} checking '.format(current_time()) + undo_date +' '+ a +' data all Good')
            pass
        else:
            ai_df = ai_df[(ai_df.AVI.astype(int) != int(undo_date))|(ai_df.part.astype(str) != str(a))]
            print('{} updating '.format(current_time()) + undo_date +' '+ a +' data...')
            ai_df = get_lot_info(lot_path,ai_df)
            print('{} updating '.format(current_time()) + undo_date +' '+ a +' data Done')



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
                print('{} ReConneting'.format(current_time()))
        opid = ''
        machine = ''
        vrs_pics = 0
        for panel in panel_dir:
            try:
                vrs_time.append(os.path.getctime(os.path.join(lot_path,lot,panel,'VRS.OK')))
                if os.path.exists(os.path.join(lot_path,lot,panel,'VRS.csv')):
                    ai_status = 'unfiltered'
                    pre_df = pd.read_csv(os.path.join(lot_path,lot,panel,'VRS.csv'),header=9)
                else:
                    pre_df = pd.read_csv(os.path.join(lot_path,lot,panel,'AI.csv'),header=9)
                if len(str(machine)) < 1:
                    machine = str(pre_df.at[0,'VRSmachine'])
                if len(opid) < 4:
                    try:
                        id_df = pd.read_csv(os.path.join(lot_path,lot,panel,'VRS.csv'), nrows=8, header = None, index_col=0)
                    except:
                        id_df = pd.read_csv(os.path.join(lot_path,lot,panel,'AI.csv'), nrows=8, header = None, index_col=0)
                    current_id = id_df.at['OPID',1]
                    if len(str(current_id)) >= 4:
                        opid = str(current_id)
                try:
                    origin_df = pd.read_csv(os.path.join(lot_path,lot,panel,'AI.csv').replace('DataFiles(Edit)','DataFiles'), header=9)
                    vrs_pics += merge_pics(pre_df, origin_df)
                except Exception as e:
                    print(e)
                concat_df = pd.concat([concat_df,pre_df])
            except Exception as e:
                pass
        ##ARRANGE AI INFO  
        if len(vrs_time) > 0:
            vrs_spend = [vrs_time[n] - vrs_time[n-1] for n in range(1,len(vrs_time))]
            time_mean = np.mean([abs(t) for t in vrs_spend if abs(t)<600])
            spent_time = time_mean*len(vrs_spend)
            VRS = datetime.fromtimestamp(np.median(vrs_time)).strftime("%Y-%m-%d") 
            strips = len(vrs_time)
            try:
                Date_code = concat_df.sort_values(by = 'Step_Code').iloc[0,2]
            except:
                Date_code = np.nan
            try:
                OK_m = len(concat_df[concat_df.AI_Flag.astype(str) == 'OK'])
                NG_m = len(concat_df[concat_df.AI_Flag.astype(str) != 'OK'])
                if OK_m == 0:
                    AI = 'Unactivated'
                else:
                    AI = 'ON'
                ALL_m = OK_m + NG_m
                filter_rate = round(OK_m/ALL_m,2) 
            except Exception as e:
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
            if ai_status == 'unfiltered':
                AI = 'unfiltered'
            concat_list.append([AVI,part,Date_code,VRS,Part_No,tape_lot,vrs_id,strips,CheckTime,OK_m,NG_m,ALL_m,filter_rate,visper,AI,size,Type,model,opid,machine,vrs_pics])
    if len(concat_list) > 0:
        add_df = pd.DataFrame(np.array(concat_list),columns=['AVI','part','Date_Code','VRS','Part_No','lot','vrs_id','strips','CheckTime(min)','OK','NG','ALL','filter rate','visper','AI','size','type','model','OPID','VRSmachine','vrs_pics'])
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
        print('{} SLEEPING'.format(current_time()))
        time.sleep(43200)
        print('{} UPDATE'.format(current_time()))
