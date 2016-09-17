# encoding:utf-8
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import sys
from apt import debfile
# *************************************************************************
#   > File Name : debinfo.py
#   > Author : chengzb
#   > Mail : 
#   > Created Time : 2015-08-28
#   > Comment :
#   > Modified: 2016-09-12
#   > Modifiedby: suntrian
# ********************************************************************

info={
    "softname":"",
    "version":"",
    "arch":"",
    "homepage":"",
    "section":"",
    "essential":"",
    "maintainer":"",
    "instsize":"",
    "predepends":"",
    "depends":"",
    "description":"",
    "recommends":"",
    "suggests":"",
    "breaks":"",
    "provides":"",
    "enhances":"",
    "conflicts":"",
    "replaces":"",
    "xulappid":""
}

#获取deb包里的相关信息
def getDebInfo(debfile_path):
    debpkg = debfile.DebPackage(debfile_path)
    info['softname'] = deb_name = debgetitem(debpkg,"Package")
    info['version'] = deb_version = debgetitem(debpkg,"Version")
    info['arch'] = deb_arch = debgetitem(debpkg,"Architecture")
    info['homepage'] = deb_homepage = debgetitem(debpkg,"Homepage")
    info['description'] = deb_description = debgetitem(debpkg,"Description")
    info['essential'] = deb_essential = debgetitem(debpkg,"Essential")
    info['section'] = deb_section = debgetitem(debpkg, "Section")
    info['maintainer'] = deb_maintainer = debgetitem(debpkg,"Maintainer")
    info['instsize'] = deb_installed_size = debgetitem(debpkg,"Installed-Size")
    info['depends'] = deb_depends = debgetitem(debpkg,"Depends")
    info['predepends'] = deb_predepends = debgetitem(debpkg,"Pre-Depends")
    info['recommends'] = deb_recommends = debgetitem(debpkg,"Recommends")
    info['suggest'] = deb_suggests = debgetitem(debpkg,"Suggests")
    info['breaks'] = deb_breaks = debgetitem(debpkg,"Breaks")
    info['conflicts'] = deb_conflicts = debgetitem(debpkg,"Conflicts")
    info['replaces'] = deb_replaces = debgetitem(debpkg,"Replaces")
    info['enhances'] = deb_enhances = debgetitem(debpkg,"Enhances")
    info['provides'] = deb_provides = debgetitem(debpkg,"Provides")
    info['xulappid'] = deb_xulappid = debgetitem(debpkg,"Xul-Appid")
    deb_info = deb_name+"&"+deb_version+"&"+deb_arch+"&"+deb_maintainer+"&"+deb_installed_size+"&"+deb_section+"&"+deb_homepage
    # print (deb_info)
    return info

def getDebDescription(debfile_path):
    debpkg = debfile.DebPackage(debfile_path)
    deb_description = debgetitem(debpkg,"Description")
    result = ' '.join(deb_description.split())
    #print deb_description
    return result

def getDebName(debfile_path):
    debpkg = debfile.DebPackage(debfile_path)
    deb_name = debpkg.__getitem__("Package")
    #print deb_name
    return deb_name

def getDebVersion(debfile_path):
    debpkg = debfile.DebPackage(debfile_path)
    deb_version = debpkg.__getitem__("Version")
    #print deb_version
    return deb_version

def getDebArch(debfile_path):
    debpkg = debfile.DebPackage(debfile_path)
    deb_arch = debpkg.__getitem__("Architecture")
    #print deb_arch
    return deb_arch

def getDebMaintainer(debfile_path):
    debpkg = debfile.DebPackage(debfile_path)
    deb_maintainer = debpkg.__getitem__("Maintainer")
    #print deb_maintainer
    return deb_maintainer

def getDebInstalledSize(debfile_path):
    debpkg = debfile.DebPackage(debfile_path)
    deb_installed_size = debpkg.__getitem__("Installed-Size")
    #print deb_installed_size
    return deb_installed_size

def getDebSection(debfile_path):
    debpkg = debfile.DebPackage(debfile_path)
    deb_section = debpkg.__getitem__("Section")
    #print deb_section
    return deb_section

def getMissingDepends(debfile_path):
    pass


#获得deb数据，没有该项则返回空值
def debgetitem(debpkg,key):
    #---------------------------------------------- if debpkg.__contains__(key):
        #---------------------------------------- return debpkg.__getitem__(key)
    sections = debpkg._sections
    if key in sections:
        return debpkg.__getitem__(key)
    else:
        return ""


if __name__=="__main__":
    debpath = "/home/yuanxm/packsource/codelite/codelite_9.1+dfsg-2_amd64.deb"
    i = getDebInfo(debpath)
    print(i)
