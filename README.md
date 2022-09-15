# AVI_AI
Auto_report_daily: The report includes AI results, FQC, and OQC reports. Merge three pieces of info to trace the status of AI.


## SUMMARY

       1. AI raw date update per 12 hours. Location:AVI_AI\utils\local_run. Export the .py to .exe and run on the local PC for crawling the ai info from EDGE.
       2. FQC & OQC report. Search and copy from the run card system. Automatic Update by module selenium and Edgedriver.
       3. Current merge keys: Part NUM., Lot NUM, and Date code. 
       4. Output: Daily processing record sorted by resolution, a summary of week & month, merge table, AI raw date.

## Process flows
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
          Parameters : 
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

       connect_test: check whether the link is available or not.
          connect_test(save_path)
          Parameters : 
                 save_path: string
                        The dir of ai documents

       get_raw_data:copy ai file to ai dir.
          get_raw_data(ai_data_dir)
          Parameters : 
                 ai_data_dir: string
                        the path of ai_all.csv

3.merge_data.py

       daily_record: sum ai history by day. un-activate
          daily_record(ai_path)
          Parameters : 
                 ai_path: string
                        The dir of ai_all.csv

       fqc_data:merge all CSV files in fqc folder. un-activate
          fqc_data(fqc_path)
          Parameters : 
                 fqc_path : string
                        The dir of fqc documents

       oqc_data:merge all csv files in oqc folder.
          oqc_data(oqc_path)
          Parameters : 
                 oqc_path : string
                        The dir of oqc documents

       ai_data: arrange the format of columns and filter out.
          ai_data(ai_path)
          Parameters : 
                 ai_path: string
                        The dir of ai_all.csv

       all_concat: merge ai, fqc and oqc tables. un-activate
          all_concat(ai_path,fqc_path,oqc_path)
          Parameters : 
                 ai_path: string
                        The dir of ai_all.csv
                 fqc_path : string
                        The dir of fqc documents 
                 oqc_path : string
                        The dir of oqc documents 

       weekly_report: output the result of contact by part_no and lot. un-activate
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
       
