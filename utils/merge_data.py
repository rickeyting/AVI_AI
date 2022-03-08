# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 14:45:31 2022

@author: A2433
"""

import pandas as pd
import os

BASE_DIR = os.path.abspath(os.path.join('..','data'))
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


def fqc_date(fqc_path):
    result = []
    for i in os.listdir(fqc_path):
        path = os.path.join(fqc_path,i)
        df = pd.read_excel(path, sheet='sheet1', header=5)
        df = df.dropna(subset=['Part No.'])

if __name__ == '__main__':
    #fqc_date(AI_DIR)