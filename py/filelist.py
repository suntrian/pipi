#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************************
#   > File Name : install_sricpt.py
#   > Author : chengzb
#   > Mail : 
#   > Created Time : 2015-08-27
#   > Comment : 
# *************************************************************************
from py import cutils
import os
import time

'''
    @brief : generation filelist file
'''
def gen_filelist(path) :
    cutils.create_dir(path)
    if not len(path):
        pwd = os.getcwd()
    else:
        pwd = path
    dirlist = os.walk(pwd)     

    if not os.path.exists("CPK") : 
        try : 
            os.mkdir("CPK")
            
        except Exception as e : 
            print(("Filelist create CPK Error : ", e))
    
    f = open(path+"/CPK/filelist", "w") 
    try : 
        if f : 
            eof = os.linesep
            file_count = 0
            dir_count = 0
            link_count = 0
            total = 0
            
            for root, dirs, files in dirlist :
                relative_path = str(root)[len(str(pwd)): ] or "/"
                if cmp(relative_path, "/CPK") : 
                    if root and cmp(str(root), str(pwd)) : 
                        dir_size = os.path.getsize(root)
                        st_mode = cutils.fileMode(root)
                        
                        cont_str = "D," + relative_path + "," + str(dir_size) \
                                    + "," + st_mode + "," + str(time.time()) + eof

                        # if os.path.isdir(relative_path) : 
                        dir_count += 1
                        
                        f.writelines(cont_str)
                        
                        for filename in files : 
                            # 类别, 文件名, 文件大小, Mask, 最后修改时间, md5sum值 
                            cont_str = ""
                            abs_path = os.path.join(root, filename)
                            
                            relative_filepath = os.path.join(relative_path, filename)

                            if os.path.exists(abs_path) : 
                                file_size = os.path.getsize(abs_path)
                                total += file_size
                                st_mode = cutils.fileMode(abs_path)
                                    
                                '''
                                if os.path.isdir(abs_path) :
                                    dir_count += 1
                                    print dir_count
                                    cont_str = "D," + str(relative_filepath) + "," + str(file_size) + "," \
                                            + st_mode + "," + str(time.time()) + eof
                                '''

                                if os.path.isfile(abs_path) :
                                    file_count += 1
                                    md5 = cutils.md5sum(abs_path)
                                    cont_str = "F," + str(relative_filepath) + "," + str(file_size) + "," \
                                            + st_mode + "," + str(time.time()) + "," + str(md5) + eof
                                    
                                elif os.path.islink(abs_path) :
                                    link_count += 1
                                    relpath = os.readlink(abs_path)
                                    cont_str = "S," + str(relative_filepath) + "," + str(file_size) + "," \
                                            + st_mode + "," + str(time.time()) + "," + str(relpath) + eof

                            else : 
                                link_count += 1
                                relpath = os.readlink(abs_path)
                                cont_str = "S," + str(relative_filepath) + "," + str(file_size) + "," \
                                        + st_mode + "," + str(time.time()) + "," + str(relpath) + eof
                                                        
                            f.writelines(cont_str)
                        
            cont_str = "I," + str(file_count) + "," + str(dir_count) + "," \
                        + str(link_count) + "," + str(total)
            f.writelines(cont_str)
        
    except Exception as e : 
        print(("Filelist write file Error : ", e))
        
    finally : 
        f.close()

def cmp(a,b):
    return (a > b) - (a < b)


if __name__ == "__main__" :
    print("start ...")
    path = "/home/yuanxm/packsource/codelite/codelite"
    gen_filelist(path)



