#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************************
#   > File Name : install_sricpt.py
#   > Author : chengzb
#   > Mail : 
#   > Created Time : 2015-08-31
#   > Comment : 
# *************************************************************************
import os


def write_script(path,content):
    print("set_script-------------")
    if not os.path.exists(path): 
        try : 
            f=open(path)
            
        except Exception as e : 
            print("Install create path dir Error : ", e)
    f=open(path,"w+")
    f.writelines(content)
    f.close()  
    print("write new content success!")  

'''    
if __name__ == "__main__" :
    path = "/home/chengzb/文档/cpkstore_1.0.0_i386_cache/CPK/cpkstore.install"
    filename = "new content"
    write_script(path,filename)
'''

