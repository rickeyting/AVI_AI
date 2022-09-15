# AVI_AI
The report includes AI results, FQC, and OQC reports. Merge three pieces of info to trace the status of AI.


## SUMMARY

       1. AI raw date update per 12 hours. Location:AVI_AI\utils\local_run. Export the .py to .exe and run on the local PC for crawling the ai info from EDGE.
       2. FQC & OQC report. Search and copy from the run card system. Automatic Update by module selenium and Edgedriver.
       3. Current merge keys: Date and AVI status. 
       4. Output: Processing record sorted by 'MP', 'SAMPLE', 'GAN' and 'OTHER'. Summary by month.

## Notice

Change Edge IP: there are two path in .py files must be changed when Edge IP is changed.

       raw_data.py(row 15)
              target_dir = r'\\10.19.13.40\ScanImages\ai_all.csv'
              
       avi_ai_crawler.py(row 26~32)
              if os.path.exists(r'\\10.19.13.40\DataFiles(Edit)'):
                  ip_address = '10.19.13.40'
              if os.path.exists(r'\\192.168.0.111\DataFiles(Edit)'):
                  ip_address = '192.168.0.111'

              if ip_address == '192.168.0.111':
                  past_data_dir = r'\\{}\ScanImages\ai_all.csv'.format(ip_address)

Process logic: 

       OQC:
       merge_data.py oqc_data
       1. Get '檢驗日期', '料號', 'D/C', '批號', '檢驗次數', '狀態' and '批量'
       2. AVI status = ON: lot contains 'V'; OFF': lot not contains 'V'
       3. reject_times = count of '檢驗次數' and '狀態'='退回'
       4. check_times = count of '檢驗次數'
       merge_data.py separate_concat
       1. oqc sample = part number contains 'P328' and the date before '2022/07/01'; part number contains 'P3285' after '2022/07/01'
       2. oqc mp = part number contains 'P328', the date after '2022/07/01' and not contains 'P3285'; part number contains 'P329' or 'PJ5'
       3. oqc gan = part number contains 'GAN'
       4. oqc other = part number contains 'P32872' and 'P32873'
       5. Groupby date and AVI status
       FQC:
       merge_data.py avi_cover_rate
       1. Get 'Time', 'Part No.', 'Date Code', 'Lot No.', 'Total Strips', 'OK & X-Out(Strips)' and 'Remark'
       2. AVI status = ON: Remark contains 'V'; OFF': Remark not contains 'V'
       merge_data.py separate_concat
       1. fqc sample = part number contains 'P328' and the date before '2022/07/01'; part number contains 'P3285' after '2022/07/01'
       2. fqc mp = part number contains 'P328', the date after '2022/07/01' and not contains 'P3285'; part number contains 'P329' or 'PJ5'
       3. fqc gan = part number contains 'GAN'
       4. fqc other = part number contains 'P32872' and 'P32873'
       5. Groupby date and AVI status
       AI:
       merge_data.py ai_data
       1. Get 'AVI', 'VRS', 'Part_No', 'lot', 'strips', 'CheckTime(min)', 'OK', 'NG', 'ALL', 'type', 'size', 'AI', 'Date_Code' and 'model'
       2. Filter 'AI' = 'ON'
       merge_data.py separate_concat
       1. AI sample = part number contains 'P328' and the date before '2022/07/01'; part number contains 'P3285' after '2022/07/01'
       2. AI mp = part number contains 'P328', the date after '2022/07/01' and not contains 'P3285'; part number contains 'P329' or 'PJ5'
       3. AI gan = part number contains 'GAN'
       4. AI other = part number contains 'P32872' or 'P32873'
       5. Groupby date
       Output:
       merge_data.py separate_concat
       1. Merge FQC, OQC and AI
       2. Keep the data after '2022/1/1'
       3. Avg. Points = 'ALL'/'strips'
       4. UPH = 'strips'/'CheckTime(min)'
       5. Effciency = 'UPH'/90
       6. Filter rate = 'OK'/'ALL'
       7. rejection = 'reject_times'/'check_times'
       8. AVI_coverage = 'FQC_Strips'/('FQC_Strips' of AVI Status = 'ON' + 'FQC_Strips' of AVI Status = 'OFF') 
    
    
# Weekly Report Process flows(main.py)
* pre_process: create the folders for saving files
* avi_foqc_crawler.do_crawl: crawling fqc and oqc files
* raw_data.get_raw_data : copy ai_all.csv file
* merge_data.separate_concat: merge ai, fqc, and oqc files
* merge_data.result_plt: plot trend charts
* Arrange all sheets and export excel.       
       
## FUNCTIONS

1.avi_foqc_crawler.py

       fqc_crawl: crawling fqc data from the run-card browser.
          fqc_crawl(driver, start_date, end_date, fqc_path)
          Parameters : 'reject_times'/'check_times'
                 driver: web-drive
                 start_date : time
                        The start date to download the file
                 end_date: time
                        The end date to download the file
                 fqc_path : string
                        The dir of fqc documents

       oqc_crawl: crawling on data from the run-card browser.
          oqc_crawl(driver, start_date, end_date, oqc_path)
          Parameters : 
                 driver: web-drive
                 start_date : time
                        The start date to download the file
                 end_date: time
                        The end date to download the file
                 oqc_path : string
                        The dir of oqc documents

       get_start_date: check the last download history to make sure when should be started at this time. It will delete the last file and output the date of the second to last date(filename) plus 1 day.
          get_start_date(fqc_path, oqc_path)
          Parameters : 
                 fqc_path : string
                        The dir of fqc documents
                 oqc_path : string
                        The dir of oqc documents

       do_crawl: combine above to do "activate browser" "insert info" and "download"
          do_crawl(exe_path, fqc_path, oqc_path)
          Parameters : 
                 exe_path: the path of msedgedriver.exe
                 fqc_path : string
                        The dir of fqc documents
                 oqc_path : string
                        The dir of oqc documents

2.raw_data.py

       connect_test: check whether the link is available or not and copy from Edge.
          connect_test(save_path)
          Parameters : 
                 save_path: string
                        The dir of ai documents

       get_raw_data: rename the current ai file.
          get_raw_data(ai_data_dir)
          Parameters : 
                 ai_data_dir: string
                        the path of ai_all.csv

3.merge_data.py

       daily_record: sum ai history by day. unactivated
          daily_record(ai_path)
          Parameters : 
                 ai_path: string
                        The dir of ai_all.csv

       fqc_data:merge all CSV files in fqc folder. unactivated
          fqc_data(fqc_path)
          Parameters : 
                 fqc_path : string
                        The dir of fqc documents

       oqc_data:merge all csv files in oqc folder.
          oqc_data(oqc_path)
          Parameters : 
                 oqc_path : string
                        The dir of oqc documents

       ai_data: arrange the format of columns and filter 'AI' = ON.
          ai_data(ai_path)
          Parameters : 
                 ai_path: string
                        The dir of ai_all.csv

       all_concat: merge ai, fqc and oqc tables. unactivated
          all_concat(ai_path,fqc_path,oqc_path)
          Parameters : 
                 ai_path: string
                        The dir of ai_all.csv
                 fqc_path : string
                        The dir of fqc documents 
                 oqc_path : string
                        The dir of oqc documents 

       weekly_report: output the result of contact by part_no and lot. unactivated
          weekly_report(anova_df,status = 'MP')
          Parameters : 
                 anova_df: dataframe
                        the dataframe merged by part_no and lot

       avi_cover_rate:same with function fqc_data. Count in the AVI off data for cover rate.
          avi_cover_rate(fqc_path)
          Parameters : 
                 fqc_path : string
                        The dir of fqc documents

       separate_concat: merge AI, FQC, and OQC files by month and output sample, mp, and Gan result.
          separate_concat(ai_path,fqc_path,oqc_path,other_conditions=None, other_freq='M')
          Parameters : 
                 ai_path: string
                        The dir of ai_all.csv
                 fqc_path : string
                        The dir of fqc documents 
                 oqc_path : string
                        The dir of oqc documents
                 other_conditions : string ex:'P32872|P32873' output 872 and 873 result.
                        conditions to output other result
                 other_freq : 'd' 'W' 'M'
                        The frequency of group up.

       result_plt: plot the trend chart.
          result_plt(df, output_path)
          Parameters : 
                 df: dataframe
                        The dataframe from function "separate_concat"

       output_exl: export the excel.
          output_exl(sheets,output_path)
          Parameters : 
                 sheets: dictionary
                        The sheets will be converted to excel
                                   
4.main.py

       pre_procss():create the folders for saving files
       
       
# Daily Update Process flows
* pre_process: create the folders for saving files
* avi_foqc_crawler.do_crawl: crawling fqc and oqc files
* raw_data.get_raw_data : copy ai_all.csv file
* merge_data.separate_concat: merge ai, fqc, and oqc files
* merge_data.result_plt: plot trend charts
* Arrange all sheets and export excel.


## FUNCTIONS

1.avi_ai_crawler.py
       
       merge_pics: Get the numbers of image which will be showed on VRS
          merge_pics(df2, df, x_columns='Step_Xvalue', y_columns='Step_Yvalue', resolution=0.005, frame_pixel=350, limit_frame=30)
          Parameters : 
                 df2: dataframe
                     The ai.csv in Datafile(edit)
                 df : dataframe
                     The ai.csv in Datafile
                 x_columns: string
                     The column name if x-axis
                 y_columns : string
                     The column name if y-axis
                 resolution : float
                     Scan resolution(5um, 10um and 18um)
                 frame_pixel: int
                     The merge size. Pics will be merge 
                 limit_frame : int
                     The puffer of frame
       
       check_unprocessed_date: Check the last processed date in ai_all.csv and subtract 5 days to be the start date. (Output the date list from start date to current date. The code won't update the content which out of the list)
          check_unprocessed_date(ai_df)
          Parameters : 
                 ai_df: dataframe
                     The ai_all.csv file to dataframe
       
       check_unprocessed_lot: Check all part_no below the date. Skip the part number which numbers of VRS.OK are same with content of ai_csv file. 
          check_unprocessed_lot(undo_date)
          Parameters : 
                 undo_date: string
                     The date in undo list(output from check_unprocessed_date function)
       
       get_lot_info: calculate 'Scan date', 'part number from the path', 'VRS checked date', 'Part_No','lot','lot from the path','strip numbers','CheckTime(min)','point numbers','filter rate','machine code','AI status','scan resolution','scan type','activated ai model', 'Date_Code of first panel','OPID','VRS code' and 'pic number showed on vrs'
          get_lot_info(lot_path,ai_df)
          Parameters : 
                 lot_path: string
                     The dir of lot
                 ai_df: dataframe
                     The ai_all.csv file to dataframe
                 
                 
                     
                     
# merge_pics       

![image](https://user-images.githubusercontent.com/28131615/190298681-f5e12a0f-6761-4f82-aacd-df292dfee34d.png)

The center of images in the box(350-30)*(350-30) will be merged to one. There are three images. After merge only two images will be showed up on VRS. Coz the Image A is out of range.


