#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************************
#   > File Name : utils.py
#   > Author : Ray
#   > Mail : 
#   > Created Time : 14-11-21 10:57:38
#   > Comment : 
# *************************************************************************

import os
import hashlib

'''
    @brief : generation md5 sum
'''
def md5sum(filename) : 
    if os.path.exists(filename): 
        fcont = None
        with open(filename, "rb") as f : 
            fcont = f.read()
            
        if fcont : 
            fmd5 = hashlib.md5(fcont)
            
            return fmd5.hexdigest()
        
    return 0

'''
    @brief : create CPK dir's root dir
'''      
def create_dir(root_path) : 
    pwd = os.getcwd()
    os.chdir(pwd)
    
    # cpk dir is not exists, create cpk dir
    if root_path :  
        if not os.path.exists(root_path) : 
            try : 
                os.makedirs(root_path)
                
            except OSError as e : 
                print("generation cpk dir Error : ", e)
        
        os.chdir(root_path)
        

'''
    @brief : get file mode
'''
def fileMode(filename) : 
    st_mode = str(oct(os.stat(filename).st_mode)) or str(0o777)
    return st_mode[-4 : ]
        
