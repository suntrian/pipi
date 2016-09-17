# encoding:utf-8

#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************************
#   > File Name : install_sricpt.py
#   > Author : chengzb
#   > Mail : 
#   > Created Time : 2015-08-27
#   > Comment : 
# *************************************************************************
import os

def instll_content() : 
    cont = '\
#! /usr/bin/bash\n\
\n\
pre_install()\n\
{\n\
  :\n\
} \n\
post_install()\n\
{\n\
  :\n\
} \n\
pre_remove()\n\
{\n\
  :\n\
} \n\
post_remove()\n\
{\n\
  :\n\
} \n\
pre_upgrade()\n\
{\n\
  :\n\
} \n\
post_upgrade()\n\
{\n\
  :\n\
} \n\
pre_downgrade()\n\
{\n\
  :\n\
} \n\
post_downgrade()\n\
{\n\
  :\n\
} \n\
    '
    
    return cont


'''
    @brief : create CPK dir's root dir
'''      

def install_generation(path,filename) : 
    write(path,filename)
    b = write_all_script(path,filename)
    return b


def write(path,filename) : 
    inst_path = path +"/CPK/"+filename+".install"
    print(inst_path)
    f = open(inst_path, "w")
    try :
        if f : 
            f.writelines(instll_content())
    finally : 
        f.close()

def write_all_script(path,filename):
    preinst_path = path + "/DEBIAN/preinst"
    postinst_path = path + "/DEBIAN/postinst"
    prerm_path = path + "/DEBIAN/prerm"
    postrm_path = path + "/DEBIAN/postrm"

    if os.path.exists(preinst_path):
        fileadd = open(preinst_path)
        inst_path = path + "/CPK/"+filename+".install"
        f = open(inst_path)
        content = f.read()
        allline = ""
        try:
            contentadd = fileadd.readlines()
            for eachline in contentadd:
                eachline = "  " + eachline
                allline = allline + eachline

            the_flag = "pre_install()\n\
{\n\
  :\n"
            pos = content.find(the_flag)
            if pos != -1:
                pos = pos + len(the_flag)
                content = content[:(pos-4)] + allline + content[pos:]
                f = open(inst_path, "w")
                f.write(content)
                f.close()
            #print "Write postinst OK" 
        finally:
            fileadd.close()

    if os.path.exists(postinst_path):
        fileadd = open(postinst_path)
        inst_path = path + "/CPK/"+filename+".install"
        f = open(inst_path)
        content = f.read()
        allline = ""
        try:
            contentadd = fileadd.readlines()
            for eachline in contentadd:
                eachline = "  " + eachline
                allline = allline + eachline

            the_flag = "post_install()\n\
{\n\
  :\n"
            pos = content.find(the_flag)
            if pos != -1:
                pos = pos + len(the_flag)
                content = content[:(pos-4)] + allline + content[pos:]
                f = open(inst_path, "w")
                f.write(content)
                f.close()
            #print "Write postinst OK" 
        finally:
            fileadd.close()

    if os.path.exists(prerm_path):
        fileadd = open(prerm_path)
        inst_path = path + "/CPK/"+filename+".install"
        f = open(inst_path)
        content = f.read()
        allline = ""
        try:
            contentadd = fileadd.readlines()
            for eachline in contentadd:
                eachline = "  " + eachline
                allline = allline + eachline

            the_flag = "pre_remove()\n\
{\n\
  :\n"
            pos = content.find(the_flag)
            if pos != -1:
                pos = pos + len(the_flag)
                content = content[:(pos-4)] + allline + content[pos:]
                f = open(inst_path, "w")
                f.write(content)
                f.close()
            #print "Write postinst OK" 
        finally:
            fileadd.close()

    if os.path.exists(postrm_path):
        fileadd = open(postrm_path)
        inst_path = path + "/CPK/"+filename+".install"
        f = open(inst_path)
        content = f.read()
        allline = ""
        try:
            contentadd = fileadd.readlines()
            for eachline in contentadd:
                eachline = "  " + eachline
                allline = allline + eachline

            the_flag = "post_remove()\n\
{\n\
  :\n"
            pos = content.find(the_flag)
            if pos != -1:
                pos = pos + len(the_flag)
                content = content[:(pos-4)] + allline + content[pos:]
                f = open(inst_path, "w")
                f.write(content)
                f.close()
            #print "Write postinst OK" 
        finally:
            fileadd.close()


#读取全部内容并返回
    inst_path = path + "/CPK/"+filename+".install"
    all_the_data = open(inst_path).read()
    return all_the_data




if __name__ == "__main__" :
    path = "/home/yuanxm/packsource/codelite/codelite"
    filename = "codelite"
    s = install_generation(path,filename)
    print("s:" + s)


