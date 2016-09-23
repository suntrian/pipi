# encoding:utf-8

import xml
from xml.dom.minidom import Document
import os
import time

doc = Document()
root = doc.createElement("CpkInfo")
soft = doc.createElement("Software")
soft_name_attr = doc.createAttribute("name")
soft_id = doc.createElement("id")
soft_genericname = doc.createElement("genericname")
genericname_keyword_en = doc.createElement("keyword")
genericname_keyword_en.setAttribute("lang","en")
genericname_keyword_zh = doc.createElement("keyword")
genericname_keyword_zh.setAttribute("lang","zh")
genericname_type_attr = doc.createAttribute("type")         # "desktop" or ""for temporary
# genericname_type_en_lang_attr = doc.createAttribute("lang")
# genericname_type_zh_lang_attr = doc.createAttribute("lang")
soft_permission = doc.createElement("permission")
soft_classification = doc.createElement("classification")   #L0,L1,L2,L3,other; 公开,秘密,机密,绝密,其他
soft_is_patch = doc.createElement("is_patch")
soft_summary = doc.createElement("summary")
summary_keyword_en = doc.createElement("keyword")
summary_keyword_en_attr = doc.createAttribute("lang")
summary_keyword_en.setAttribute(summary_keyword_en_attr.name,"en")
summary_keyword_zh = doc.createElement("keyword")
summary_keyword_zh_attr = doc.createAttribute("lang")
summary_keyword_zh.setAttribute(summary_keyword_zh_attr.name,"zh")
soft_description = doc.createElement("description")
description_keyword_en = doc.createElement("keyword")
description_keyword_en.setAttribute("lang","en")
description_keyword_zh = doc.createElement("keyword")
description_keyword_zh.setAttribute("lang","zh")
soft_version = doc.createElement("version")
soft_essential = doc.createElement("essential")
soft_license = doc.createElement("license")
soft_catagory = doc.createElement("category")           #office,application,network,IM,graphics,multimedia,security,system,development,other
soft_architecture = doc.createElement("architecture")   #amd64,
soft_exec = doc.createElement("exec")
soft_install = doc.createElement("install")
soft_homepage = doc.createElement("homepage")
soft_vendor = doc.createElement("vendor")
vendor_type_attr = doc.createAttribute("type")          # company or personal
vendor_name = doc.createElement("name")
vendor_telephone = doc.createElement("telephone")
vendor_email = doc.createElement("email")
vendor_url = doc.createElement("url")
vendor_description = doc.createElement("description")
vendor_description_keywork_en = doc.createElement("keyword")
vendor_description_keywork_en.setAttribute("lang","en")
vendor_description_keywork_zh = doc.createElement("keyword")
vendor_description_keywork_zh.setAttribute("lang","zh")
soft_pkgs_count = doc.createElement("pkgs_count")
soft_pkgs = doc.createElement("pkgs")
pkgs_dateline = doc.createElement("dateline")
pkgs_self_size = doc.createElement("self_size")
pkgs_inst_size = doc.createElement("inst_size")
pkgs_depends = doc.createElement("depends")         # ccf1 (>= 1.0.0),ccf1 (>= 2.0.0)
pkgs_source = doc.createElement("source")

permissions = [
                "ccf.permission.USE_ROOT",
                "ccf.permission.USE_SUDO",
                "ccf.permission.USE_IPC",
                "ccf.permission.ACCESS_NETWORK_STATE",
                "ccf.permission.ACCESS_NETWORK",
                "ccf.permission.ACCESS_XORG",
                "ccf.permission.USER_MANAGER",
                "ccf.permission.USER_GROUP_MANAGER",
                "ccf.permission.SYSTEM_VARIABLE",
                "ccf.permission.DEVICE_MANAGER",
                "ccf.permission.OPEN_INPUT_METHOD",
                "ccf.permission.APP_MANAGER",
                "ccf.permission.SYSTEM_SETTING",
                "ccf.permission.CHANGE_CONFIGURATION",
                "ccf.permission.CLEAR_APP_CACHE",
                "ccf.permission.CLEAR_APP_USER_DATA",
                "ccf.permission.ACCESS_UNDERLY",
                "ccf.permission.DELETE_CACHE_FILES",
                "ccf.permission.DIAGNOSTIC",
                "ccf.permission.DUMP",
                "ccf.permission.CHANGE_DEFAULT_APP",
                "ccf.permission.CHANGE_START_MENU",
                "ccf.permission.CHANGE_TASK_BAR",
                "ccf.permission.GET_TASKS",
                "ccf.permission.GLOBAL_SEARCH",
                "ccf.permission.KILL_BACKGROUND_PROCESSES",
                "ccf.permission.MASTER_CLEAR",
                "ccf.permission.MODIFY_AUDIO_SETTINGS",
                "ccf.permission.MOUNT_FORMAT_FILESYSTEMS",
                "ccf.permission.MOUNT_UNMOUNT_FILESYSTEMS",
                "ccf.permission.READ_FRAME_BUFFER",
                "ccf.permission.READ_INPUT_STATE",
                "ccf.permission.READ_LOGS",
                "ccf.permission.REBOOT",
                "ccf.permission.RECEIVE_BOOT_COMPLETED",
                "ccf.permission.SET_PROCESS_LIMIT",
                "ccf.permission.SET_TIME",
                "ccf.permission.SET_TIME_ZONE",
                "ccf.permission.USE_CREDENTIALS",
                "com.ccf.browser.permission.CHANGE_BROWSER_HOME",
                "com.ccf.browser.permission.READ_HISTORY_BOOKMARKS",
                "com.ccf.browser.permission.WRITE_HISTORY_BOOKMARKS",
                "ccf.permission.ACCESS_WIFI_STATE",
                "ccf.permission.CHANGE_WIFI_STATE",
                "ccf.permission.USE_BLUETOOTH",
                "ccf.permission.BLUETOOTH_MANAGER",
                "ccf.permission.DEVICE_POWER"
               ]

def construct(softname,softid="",type="desktop",genericname_en="",genericname_zh="",permission="",classification="L0",ispatch="0",
              summary_en="", summary_zh="", description_en="",description_zh="",version="",essential="0",license="GPL",
              category="",arch="amd64",execpath="",install="",homepage="",vendor="",vendortype="",vendortele="",vendoremail="",
              vendorurl="",vendordescription_en="",vendordescription_zh="",pkgs_count="",pkgdateline="",pkgselfsize="",
              pkginstsize="",pkgdepends="",source="",savepath=""
              ):
    doc.appendChild(root)
    root.appendChild(soft)
    soft.setAttribute(soft_name_attr.name,softname)
    soft.appendChild(soft_id)
    soft_id.appendChild(doc.createTextNode(softid))

    soft.appendChild(soft_genericname)
    soft_genericname.setAttribute(genericname_type_attr.name, type)
    soft_genericname.appendChild(genericname_keyword_en)
    genericname_keyword_en.appendChild(doc.createTextNode(genericname_en))
    soft_genericname.appendChild(genericname_keyword_zh)
    genericname_keyword_zh.appendChild(doc.createTextNode(genericname_zh))

    soft.appendChild(soft_permission)
    soft_permission.appendChild(doc.createTextNode(permission))

    soft.appendChild(soft_classification)
    soft_classification.appendChild(doc.createTextNode(classification))

    soft.appendChild(soft_is_patch)
    soft_is_patch.appendChild(doc.createTextNode(ispatch))

    soft.appendChild(soft_summary)
    soft_summary.appendChild(summary_keyword_en)
    summary_keyword_en.appendChild(doc.createTextNode(summary_en))
    soft_summary.appendChild(summary_keyword_zh)
    summary_keyword_zh.appendChild(doc.createTextNode(summary_zh))

    soft.appendChild(soft_description)
    soft_description.appendChild(description_keyword_en)
    description_keyword_en.appendChild(doc.createTextNode(description_en))
    soft_description.appendChild(description_keyword_zh)
    description_keyword_zh.appendChild(doc.createTextNode(description_zh))

    soft.appendChild(soft_version)
    soft_version.appendChild(doc.createTextNode(version))
    soft.appendChild(soft_essential)
    soft_essential.appendChild(doc.createTextNode(essential))
    soft.appendChild(soft_license)
    soft_license.appendChild(doc.createTextNode(license))
    soft.appendChild(soft_catagory)
    soft_catagory.appendChild(doc.createTextNode(category))
    soft.appendChild(soft_architecture)
    soft_architecture.appendChild(doc.createTextNode(arch))
    soft.appendChild(soft_exec)
    soft_exec.appendChild(doc.createTextNode(execpath))
    soft.appendChild(soft_install)
    soft_install.appendChild(doc.createTextNode(install))
    soft.appendChild(soft_homepage)
    soft_homepage.appendChild(doc.createTextNode(homepage))

    soft.appendChild(soft_vendor)
    soft_vendor.setAttribute(vendor_type_attr.name,vendortype)
    soft_vendor.appendChild(vendor_name)
    vendor_name.appendChild(doc.createTextNode(vendor))
    soft_vendor.appendChild(vendor_telephone)
    vendor_telephone.appendChild(doc.createTextNode(vendortele))
    soft_vendor.appendChild(vendor_email)
    vendor_email.appendChild(doc.createTextNode(vendoremail))
    soft_vendor.appendChild(vendor_url)
    vendor_url.appendChild(doc.createTextNode(vendorurl))
    soft_vendor.appendChild(vendor_description)
    vendor_description.appendChild(vendor_description_keywork_en)
    vendor_description_keywork_en.appendChild(doc.createTextNode(vendordescription_en))
    vendor_description.appendChild(vendor_description_keywork_zh)
    vendor_description_keywork_zh.appendChild(doc.createTextNode(vendordescription_zh))

    soft.appendChild(soft_pkgs_count)
    soft_pkgs_count.appendChild(doc.createTextNode(pkgs_count))
    soft.appendChild(soft_pkgs)
    soft_pkgs.appendChild(pkgs_dateline)
    pkgs_dateline.appendChild(doc.createTextNode(pkgdateline))
    soft_pkgs.appendChild(pkgs_self_size)
    pkgs_self_size.appendChild(doc.createTextNode(pkgselfsize))
    soft_pkgs.appendChild(pkgs_inst_size)
    pkgs_inst_size.appendChild(doc.createTextNode(pkginstsize))
    soft_pkgs.appendChild(pkgs_depends)
    pkgs_depends.appendChild(doc.createTextNode(pkgdepends))

    soft.appendChild(pkgs_source)
    pkgs_source.appendChild(doc.createTextNode(source))

    if not savepath=="":
        xfile = open(savepath, "wb")
        xfile.write(doc.toprettyxml(encoding="GB2312", indent="  "))
        xfile.close()

    return doc

def createcontrol(savepath,info):
    path = os.path.join(savepath,"CPK","control.xml")

    doc = construct(
        softname = info.get('softname',''),     # needed
        softid=info.get('softid',''),
        type=info.get('type','desktop'),
        genericname_en=info.get('genericname_en',info.get('genericname',info.get('softname',''))),
        genericname_zh=info.get('genericname_zh',info.get('genericname',info.get('softname',''))),
        permission=info.get('permission',''),
        classification=info.get('classification','L0'),
        ispatch=info.get('ispatch','0'),
        summary_en=info.get('summary_en',''),
        summary_zh=info.get('summary_zh',''),
        description_en=info.get('description_en',info.get('description')),
        description_zh=info.get('description_zh',''),
        version=info.get('version',''),         # needed
        essential=info.get('essential','0'),
        license=info.get('license','GPL'),
        category=info.get('category','Application'),       # needed
        arch=info.get('arch',"amd64"),
        execpath=info.get('execpath',''),       # needed
        install=info.get('install',''),         # needed
        homepage=info.get('homepage',''),
        vendor=info.get('vendor',''),
        vendortype=info.get('vendortype',''),
        vendortele=info.get('vendortele',''),
        vendoremail=info.get('vendoremail',''),
        vendorurl=info.get('vendorurl',''),
        vendordescription_en=info.get('vendordescription_en',''),
        vendordescription_zh=info.get('vendordescription_zh',''),
        pkgs_count=info.get('pkgscount',''),
        pkgdateline=info.get('dateline',str(int(time.time()))),
        pkgselfsize=info.get('selfsize',''),
        pkginstsize=info.get('instsize',''),
        pkgdepends=info.get('ccfdepends','ccf1 (>= 1.0.0)'),
        source=info.get('source',''),
        savepath=savepath
    )


if __name__ == "__main__":

    fpath = "/home/yuanxm/packsource/codelite/codelite/CPK/control.xml"
    debpath = "/home/yuanxm/packsource/codelite/codelite_9.1+dfsg-2_amd64.deb"

    createcontrol(fpath,{"softname":"focuswriter",'version':'2.2.2','vendor':'vendorr','category':'develop'})

    # debinfo = debinfo.getDebInfo(debpath)

    # xfile = open(fpath,"w")

    # construct("focuswriter",version="1.1.25",vendor="vendor",category="office")

    # xfile.write(doc.toprettyxml(encoding="GB2312").decode())
    # xfile.close()
