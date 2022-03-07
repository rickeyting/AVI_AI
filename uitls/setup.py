# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 13:54:14 2021

@author: A2433
"""

# =============================================================================
#    Author: Kenneth Perkins
#    Date:   Jul 25, 2013
#    Updated: Feb 12, 2021
#    Taken From: http://programmingnotes.org/
#    File:  setup.py
#    Description: This is the cx_Freeze setup file for creating an exe program
# =============================================================================
from cx_Freeze import setup, Executable
# NOTE: you can include any other necessary external imports here aswell

includefiles = [] # include any files here that you wish
excludes = []
packages = ['numpy']

exe = Executable(
 # what to build
 
   script = "avi_ai_crawler.py", # the name of your main python script goes here 
   init_script = None,
   base = 'Console', # if creating a GUI instead of a console app, type "Win32GUI"
   target_name = "avi_ai_crawler.exe", # this is the name of the executable file
   icon = None # if you want to use an icon file, specify the file name here
)

setup(
 # the actual setup & the definition of other misc. info
    name = "avi_ai_crawler", # program name
    version = "0.1",
    description = 'flask',
    author = "rich_ting",
    author_email = "mick7832421@gmail.com",
    options = {"build_exe": {"excludes":excludes,"packages":packages,
      "include_files":includefiles,'includes': ['numpy']}},
    executables = [exe]
)
# http://programmingnotes.org/
