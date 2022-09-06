# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 14:20:54 2022

@author: A2433
"""
import os
import pandas as pd
from utils import avi_foqc_crawler, raw_data, merge_data
pd.options.mode.chained_assignment = None

root_dir = os.path.abspath('.')
data_dir = os.path.join(root_dir,'data')
output_dir = os.path.join(root_dir,'output')
ai_dir = os.path.join(data_dir,'AI')
ai_table = os.path.join(ai_dir,'ai_all.csv')
fqc_dir = os.path.join(data_dir,'FQC')
oqc_dir = os.path.join(data_dir,'OQC')
exe_dir = os.path.join(root_dir,'msedgedriver.exe')


def pre_procss():
    print('STATUS: creating dirs')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.exists(ai_dir):
        os.mkdir(ai_dir)
    if not os.path.exists(fqc_dir):
        os.mkdir(fqc_dir)
    if not os.path.exists(oqc_dir):
        os.mkdir(oqc_dir)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)


if __name__ == '__main__':
    pre_procss()
    avi_foqc_crawler.do_crawl(exe_dir,fqc_dir,oqc_dir)
    raw_data.get_raw_data(ai_dir)
    weekly_result = merge_data.separate_concat(ai_table, fqc_dir, oqc_dir, 'P32872|P32873', 'M')
    merge_data.result_plt(weekly_result, output_dir)
    ai_df = pd.read_csv(ai_table)
    anova_df = merge_data.ai_data(ai_table)
    #daily_df = merge_data.daily_record(ai_table)
    #week_df_sample = merge_data.weekly_report(anova_df,'SAMPLE')
    output_dic = {}
    weekly_result['Filter rate'] = weekly_result['Filter rate']/100
    weekly_result['rejection'] = weekly_result['rejection']/100
    weekly_result['AVI_coverage'] = weekly_result['AVI_coverage']/100
    output_dic['weekly'] = weekly_result
    #output_dic['week_sample'] = week_df_sample
    output_dic['merge_by_lot'] = anova_df
    #output_dic['daily'] = daily_df
    output_dic['AI'] = ai_df
    merge_data.output_exl(output_dic, output_dir)
