# encoding:utf-8

import os
import re
import shutil
import subprocess
import sys

from py import filelist
from py import install_sricpt
from py import create_controlxml
from py import debinfo

###########################################################################
##  config parameter
'''
    -basedir
'''
#######保存脚本当前执行步骤
step = 0
basedir = "/home/yuanxm/packsource/gcolor2"
# deb解压后的路径
extractdebpath = "/home/yuanxm/packsource/gcolor2/gcolor2"
softname = "gcolor2"
softversion = "0.4-2.1ubuntu1"
softarch = "amd64"
execpath = ""
iself = False
thisfile = ""
args = {}

restr = r'(.*?)=>(.*)'
ldpattern = re.compile(restr)


def inflatedeb(debpath, softname):
    '''
    解压deb包到包目录下包名文件夹
    :param debpath: deb包文件的绝对路径
    :return: 解压后的文件夹
    '''

    destdir = os.path.join(os.path.dirname(debpath), softname)
    mkdir(destdir)
    dpkg_x(debpath, destdir)
    dpkg_r(debpath, destdir)
    return destdir

def inflate_allsame_deb(debpath,softname):
    pa = debpath
    if os.path.exists(debpath) and os.path.isfile(debpath):
        pa = os.path.dirname(debpath)
    files = getsubfiles(pa,'file')
    for file in files:
        if file.startswith(softname) and file.endswith('.deb'):
            inflatedeb(os.path.join(pa,file),softname)
    return os.path.join(pa,softname)

def structdeb(debdirpath):
    '''
    把bin文件夹及可执行文件移动到opt/{myname}目录下
    再如果可执行文件是elf格式的，在opt/{myname}目录下创建lib文件夹
    :param debdirpath: deb解压后的目录
    :return: elf bin files
    '''
    path = modifystructure(debdirpath)
    if path == "": return False
    elfbinfiles = []
    files = getsubfiles(os.path.join(path, 'bin'), 'file')
    if len(files) > 0:
        for file in files:
            binpath = os.path.join(path, 'bin', file)
            if modifyrpath(binpath):
                iself = True
                elfbinfiles.append(binpath)
                mkdir(os.path.join(path, 'lib'))
    return elfbinfiles


def copyldlibs(elfbinfiles):
    if not type(elfbinfiles) is list or len(elfbinfiles) == 0:
        return
    retlibs = []
    for binfile in elfbinfiles:
        libs = ldd(binfile)
        retlibs = checklibrarys(libs, retlibs)
    copylibs(retlibs, os.path.join(os.path.dirname(elfbinfiles[0]), '..', 'lib'))


def parsername(path):
    filename = os.path.basename(path)
    dirname = os.path.dirname(path)
    re_str = r'^([\w,-]+?)_([0-9,\.]+?)[+,-].*?_(\w+?).deb'
    pat = re.compile(re_str)
    rst = pat.findall(filename)
    if rst:
        global softname, softversion, softarch
        softname = rst[0][0]
        softversion = rst[0][1]
        softarch = rst[0][2]
    else:
        print(filename)
        softname = input("GIVE ME A NAME!!!!!!!!!!!!!!!!\n")
        while filename.find(softname) < 0:
            softname = input("GIVE ME A NAME!!!!!!!!!!!!!!!!\n")
    return softname, softversion, softarch


def mkdir(path):
    if os.path.exists(path):
        return path
    os.mkdir(path)
    return path


def dpkg_x(debpath, destpath):
    if not os.path.exists(debpath): return
    cmd = 'dpkg-deb -X %s %s' % (debpath, destpath)
    return subprocess.call(cmd, shell=True)


def dpkg_r(debpath, destpath):
    if not os.path.exists(debpath): return
    cmd = 'dpkg-deb -R %s %s ' % (debpath, destpath)
    return subprocess.call(cmd, shell=True)


def modifystructure(dirpath):
    if not os.path.exists(dirpath): return
    dirs = getsubfiles(dirpath, "dir")
    if os.path.exists(dirpath + "/usr/bin"):
        mkdir(dirpath + "/opt")
        global softname
        assert softname.strip() != ""
        dp = mkdir(dirpath + "/opt/" + softname)
        try:
            move(dirpath + "/usr/bin", dp)
        except shutil.Error as e:
            if os.path.exists(os.path.join(dp, 'bin')):
                return dp
        return dp
    else:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        raise Exception("bin file NOT FOUND!")
        return ''


def getsubfiles(path, mode=""):
    if not os.path.exists(path): return
    subs = os.listdir(path)
    rets = []
    if mode == "" or mode == "all":
        return subs
    elif mode.startswith("d"):
        for f in subs:
            if os.path.isdir(os.path.join(path, f)):
                rets.append(f)
    elif mode.startswith("f"):
        for f in subs:
            if os.path.isfile(os.path.join(path, f)):
                rets.append(f)
    elif mode.startswith("e"):
        for f in subs:
            p = os.path.join(path, f)
            if os.path.isfile(f) and os.access(p, os.X_OK):
                rets.append(f)
    return rets


def copy(source, dest):
    if os.path.isdir(source):
        return shutil.copytree(source, dest)
    else:
        return shutil.copy(source, dest)


def move(source, dest):
    return shutil.move(source, dest)


def modifyrpath(binpath):
    if not os.path.exists(binpath): return False
    param = "--set-rpath"
    rpath = "'$ORIGIN/../lib'"
    cmd = "patchelf %s %s %s" % (param, rpath, binpath)
    rst = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res_str = rst.stderr.read().decode().strip()
    if res_str is "":
        return True
    elif res_str == "not an ELF executable":
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!%s says %s" % (binpath, res_str))
        return False
    return False


def ldd(binpath):
    if not os.path.exists(binpath): return False
    cmd = 'ldd %s' % binpath
    rst = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    restr = rst.stdout.read().decode()
    libs = ldpattern.findall(restr)
    if len(libs) == 0:
        return None
    else:
        return libs


def checklibrarys(libs, retlibs):
    islack = False

    for libname, libpath in libs:
        if libpath.strip() == "not found":
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!LACKS LIB: %s " % libname.strip())
            islack = True
        else:
            libpath = libpath.strip().split(' ')[0]
        if [libname.strip(), libpath] not in retlibs:
            retlibs.append([libname.strip(), libpath])

    if islack:
        while True:
            k = input("solve the problem manually,then input[N(ot)/y(es)/i(gnore)]")
            if k.startswith("n") or k.startswith("N"):
                assert libpath.strip() != "not found"
            elif k.lower().startswith("y"):
                break
            elif k.lower().startswith("i"):
                break
    return retlibs


def copylibs(libs, destdir):
    files = getsubfiles(destdir, 'file')
    for libname, libpath in libs:
        if os.path.exists(libpath):
            if not os.path.basename(libpath) in files:
                copy(libpath, destdir)
        else:
            print(libname, libpath, 'not found, continue?[N/y]')
            while True:
                ipt = input()
                if ipt.lower().startswith('y'):
                    break
                elif ipt.lower().startswith('n'):
                    raise Exception


def getdeblists(basedir):
    debs = []
    files = getsubfiles(basedir, 'file')
    for file in files:
        if file.endswith(".deb"):
            debs.append(os.path.join(basedir, file))
    return debs


def createcpk(workdir, dest):
    cmd = 'cpkg -b %s %s' % (workdir, dest)
    return subprocess.call(cmd, shell=True)


def create48x48icon(oripicpath, savepath):
    from PIL import Image
    oripic = Image.open(oripicpath)
    oripic.thumbnail((48, 48))  # 只能缩小
    # oripic.resize((48, 48), Image.ANTIALIAS)  # 能放大缩小
    oripic.save(savepath)
    return savepath


def get48x48iconpath(sharedir):
    x48icons = os.path.join(sharedir, 'icons', 'hicolor', '48x48', 'apps')
    if os.path.exists(x48icons):
        return getdistinctpath(x48icons, 'file')
    elif os.path.exists(os.path.join(sharedir, 'icons', 'hicolor')):
        iconsdirs = getsubfiles(os.path.join(sharedir, 'icons', 'hicolor'), 'dir')
        icondir = ''
        if '256x256' in iconsdirs:
            icondir = '256x256'
        if "128x128" in iconsdirs:
            icondir = '128x128'
        elif '64x64' in iconsdirs:
            icondir = '64x64'
        else:
            icondir = getdistinctpath(iconsdirs)

        icon = getdistinctpath(os.path.join(sharedir, 'icons', 'hicolor', icondir, 'apps'))
        mkdir(os.path.join(sharedir, 'icons', 'hicolor', '48x48'))
        x48iconsdir = os.path.join(sharedir, 'icons', 'hicolor', '48x48', 'apps')
        mkdir(x48iconsdir)
        return create48x48icon(icon, os.path.join(x48iconsdir, os.path.basename(icon)))
    elif os.path.exists(os.path.join(sharedir, 'pixmaps')):
        dirs = os.path.join(sharedir, 'pixmaps')
        ls = lambda e, t: print(e[e.rfind('/pixmaps') + 9:], end=t)
        print("#####################################################################")
        recursive(dirs, ls)

        while True:
            k = input("SELECT ICON FILE:")
            if os.path.exists(os.path.join(dirs, k)):
                return os.path.join(dirs, k)
                break

    else:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        raise Exception("ICONS NOT FOUND")


def recursive(path, callback=None):
    subs = getsubfiles(path)
    for sub in subs:
        if os.path.isfile(os.path.join(path, sub)):
            if callback != None: callback(path + "/" + sub, '\n')
        elif os.path.isdir(os.path.join(path, sub)):
            recursive(os.path.join(path, sub), callback)


def editdesktop(debdir, binfilepath):
    for desktop in getsubfiles(os.path.join(debdir, 'usr', 'share', 'applications'), 'file'):
        __editconfig(os.path.join(debdir, 'usr', 'share', 'applications', desktop), "Exec", binfilepath)
        __editconfig(os.path.join(debdir, 'usr', 'share', 'applications', desktop), "TryExec", binfilepath)


def __editconfig(path, key, value=""):
    r = r"\n(" + key + r"\s?=)(\S+)( *.*?)\n"
    # print(r)
    pat = re.compile(r)
    with open(path, 'r+') as f:
        cont = f.read()
        res = pat.findall(cont)
        nl = ''
        if len(res) > 0:
            if value == "":
                nl = '\n' + res[0][0] + '\n'
            else:
                nl = '\n' + res[0][0] + value + res[0][2] + '\n'
        ncont = pat.sub(nl, cont)
        f.seek(0)
        f.truncate()
        f.write(ncont)


def parsedesktop(path):
    r = r'^(.*?)=(.*?)$'
    ret = {}
    with open(path, 'r') as f:
        cont = f.read()
        res = re.findall(r, cont, flags=re.MULTILINE)
        for rs in res:
            ret[rs[0].strip()] = rs[1].strip()
        return ret


def desktopinfo(path):
    deskinfo = parsedesktop(path)
    retinfo = {}
    for k, v in deskinfo.items():

        if k == 'GenericName':
            retinfo['genericname_en'] = retinfo['genericname'] = deskinfo[k]
        if k.lower() == 'genericname[zh_cn]':
            retinfo['genericname_zh'] = deskinfo[k]

        if k == 'Comment':
            retinfo['summary_en'] = retinfo['summary'] = deskinfo[k]
        if k.lower() == 'comment[zh_cn]':
            retinfo['summary_zh'] = deskinfo[k]

        if k == 'Categories':
            # office, application, network, IM, graphics, multimedia, security, system, development, other
            vl = v.lower()
            if 'office' in vl or 'document' in vl:
                retinfo['category'] = 'office'
            elif 'game' in vl:
                retinfo['category'] = 'game'
            elif 'development' in vl or 'ide' in vl or 'database' in vl:
                retinfo['category'] = 'development'
            elif 'system' in vl or 'setting' in vl:
                retinfo['category'] = 'system'
            elif 'audio' in vl or 'video' in vl:
                retinfo['category'] = 'multimedia'
            elif 'graphics' in vl or 'photo' in vl:
                retinfo['category'] = 'graphics'
            elif 'network' in vl or 'p2p' in vl or 'transfer' in vl:
                retinfo['category'] = 'network'
            elif 'application' in vl:
                retinfo['category'] = 'application'
            else:
                retinfo['category'] = 'other'

                # if k == 'Keywords':
                #    retinfo['keyword_en'] = retinfo['keyword']
    return retinfo


def getdistinctpath(path, mode=''):
    files = getsubfiles(path, mode)
    if len(files) == 1:
        return os.path.join(path, files[0])
    else:
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(files)
        while True:
            f = input("TYPE IN NAMES:")
            if f in files:
                break

        return os.path.join(path, f)


def modifythis(thisfilepath, kvs):
    with open(thisfilepath, 'r+') as f:
        co = f.read()
        for k, v in kvs.items():
            co = re.sub(r'^%s\s*?=[\w \' "]*?$' % k, r'%s = %s' % (k, '"' + v + '"' if type(v) is str else v), co,
                        flags=re.MULTILINE)
        # print(co)
        try:
            f.seek(0)
            f.truncate()
            f.write(co)
        except Exception as e:
            f.seek(0)
            f.truncate()
            f.write(co)


def parsevendor(maintainer):
    re_str = r'^(.*?)<(.*?)>$'
    r = re.findall(re_str, maintainer)
    if len(r) > 0:
        vendor = r[0][0].strip()
        email = r[0][1].strip()
        return vendor, email
    return '', ''


def go(debpath, step):
    global extractdebpath,execpath,softname,softversion,softarch,basedir
    deb = debpath
    info = debinfo.getDebInfo(deb)
    info['vendor'], info['vendoremail'] = parsevendor(info['maintainer'])
    softname, softversion, softarch = parsername(deb)
    if info['softname'] != softname:
        softname = info['softname']
    if info['version'] != softversion:
        softversion = info['version']
    if info['arch'] != softarch:
        softarch = info['arch']
    args['basedir'] = basedir = os.path.dirname(debpath)
    args['softname'] = softname
    args['softversion'] = softversion
    args['softarch'] = softarch
    args['extractdebpath'] = extractdebpath
    args['execpath'] = execpath

    if step == 0:  ### 第一步，解包deb文件
        try:
            extractdebpath = inflate_allsame_deb(deb, softname)  # deb解压后的路径
            args['extractdebpath'] = extractdebpath
        except Exception as e:
            print(e)
            args['step'] = step
            modifythis(thisfile, args)
            return step
        finally:
            step += 1
    if step <= 1:  # 第二步， 移动可执行文件，并拷贝依赖库
        try:
            elfbinfiles = structdeb(extractdebpath)
            copyldlibs(elfbinfiles)
        except Exception as e:
            print(e)
            args['step'] = step
            modifythis(thisfile, args)
            return step
        finally:
            step += 1

    if step <= 2:  # 第三步， 获取图标文件和desktop文件到CPK
        try:
            mkdir(os.path.join(extractdebpath, 'CPK'))
            mkdir(os.path.join(extractdebpath, 'CPK', 'icons'))
            mkdir(os.path.join(extractdebpath, 'CPK', 'screenshot'))
            copy(get48x48iconpath(os.path.join(extractdebpath, 'usr', 'share')),
                 os.path.join(extractdebpath, "CPK", 'icons'))
            execpath = getdistinctpath(os.path.join(extractdebpath, 'opt', softname, 'bin'), mode='file')
            execpath = execpath[execpath.find('/opt'):]
            args['execpath'] = info['execpath'] = execpath
            editdesktop(extractdebpath, execpath)
            desktop = getdistinctpath(os.path.join(extractdebpath, 'usr', 'share', 'applications'), 'file')
            copy(desktop, os.path.join(extractdebpath, 'CPK'))
            deskinfo = desktopinfo(desktop)
            for k, v in deskinfo.items():
                info[k] = v
        except Exception as e:
            print(e)
            args['step'] = step
            modifythis(thisfile, args)
            return step
        finally:
            step += 1

    if step <= 3:  # 第四步 生成filelist, .install, control.xml文件
        try:
            filelist.gen_filelist(extractdebpath)
            install_sricpt.install_generation(extractdebpath, softname)
            info['install'] = softname + '.install'
            controlsavepath = os.path.join(extractdebpath, 'CPK', 'control.xml')
            create_controlxml.createcontrol(controlsavepath, info)
        except Exception as e:
            print(e)
            args['step'] = step
            modifythis(thisfile, args)
            return step
        finally:
            step += 1

    if step <= 4:  # 第五步， 生成CPK文件
        try:
            createcpk(extractdebpath, os.path.join(basedir, '%s_%s_%s.cpk' % (softname, softversion, softarch)))
        except Exception as e:
            print(e)
            args['step'] = step
            modifythis(thisfile, args)
            return step
        finally:
            step += 1

    if step >5:    #删除文件夹
        try:
            shutil.rmtree(extractdebpath)
        except Exception as e:
            print(e)
            args['step'] = step
            modifythis(thisfile, args)
            return step
        finally:
            step += 1
    return step


if __name__ == "__main__":
    thisfile = sys.argv[0]

    # m = debinfo.getDebMaintainer('/home/yuanxm/packsource/gcolor2/gcolor2_0.4-2.1ubuntu1_amd64.deb')
    # print(m)
    # print(parsevendor(m))

    if len(sys.argv) > 1:
        ls = sys.argv[1]
        print(ls)
        debs = []
        if os.path.exists(ls) and os.path.isfile(ls) and ls.endswith('.deb'):
            debs.append(ls)
        elif os.path.exists(ls) and os.path.isdir(ls):
            subs = getsubfiles(ls, 'file')
            debs.extend(os.path.join(ls, subs))
        elif type(ls) is list:
            debs.extend(ls)

        for deb in debs:
            if deb.endswith('.deb'):
                go(deb, step)

                # get48x48iconpath('/home/yuanxm/packsource/deb/glpeces_5.2.1/opt/glpeces-5.2/share')
