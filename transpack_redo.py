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
    dir--文件夹名   filepath--文件绝对路径    dirpath--文件夹绝对路径
    /$basedirpath
    ----/$softname($extractdebdirpath)
    --------/usr
    ------------/share
    ----------------/applications
    ----------------/icons
    ------------/bin
    ------------/lib
    ------------/game(optional)
    ------------/pixmaps(optional)
    --------/opt
    ------------/$softname($bindirpath)
    ----------------/bin
    --------------------/$execpath
    ----------------/lib
    --------/DEBIAN
    --------/CPK($cpkdirpath)
    ------------/icons
    ------------/screenshots
    ----/debfile
    ----/cpkfile
'''
#######保存脚本当前执行步骤
step = 0
basedirpath = "/home/yuanxm/packsource/goldendict"
debfilepath = ''
extractdebdirpath = ''
bindirpath = ''
softname = ''
softversion = ''
softarch = ''
execpath = ''
thisfile = ""
passwd = 'qwer1234'
parameters = {}
controlinfo = {}


def printhelp():
    h = '''
    -h|--h|help for this help manual
    debfilepath or basedirpath + softname either is needed
    & tired to continue
    after all , only myself use this script
    '''
    print(h)


def movebinandlib():
    global extractdebdirpath, softname, bindirpath
    if not os.path.exists(extractdebdirpath): return
    if os.path.exists(os.path.join(extractdebdirpath, 'usr')):
        mkdir(os.path.join(extractdebdirpath, 'opt'))
        optpath = mkdir(os.path.join(extractdebdirpath, 'opt', softname))
        tomove = ['bin', 'game']  # to be considered whether lib should be moved
        subs = getsubfiles(os.path.join(extractdebdirpath, 'usr'))
        for sub in subs:
            if sub in tomove:
                try:
                    move(os.path.join(extractdebdirpath, 'usr', sub), optpath)
                except:
                    pass
                bindirpath = os.path.join(optpath, sub)
    return bindirpath

def build_deps(softname):
    cmd = "echo %s | sudo -S apt-get build-dep %s -y" % (passwd, softname)
    return subprocess.call(cmd, shell=True)

def modifyexecfiles():
    global bindirpath, extractdebdirpath, softname
    files = getsubfiles(bindirpath, 'file')
    retlibs = []
    for file in files:
        if modifyexecrpath(os.path.join(bindirpath, file)):
            retlibs = ldd(os.path.join(bindirpath, file), retlibs)
    if len(retlibs) > 0:
        optlibpath = mkdir(os.path.join(extractdebdirpath, 'opt', softname, 'lib'))
        copylibs(retlibs, optlibpath)


def modifyexecrpath(execfilepath):
    if not os.path.exists(execfilepath): return False
    param = "--set-rpath"
    rpath = "'$ORIGIN/../lib'"
    cmd = "patchelf %s %s %s" % (param, rpath, execfilepath)
    rst = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res_str = rst.stderr.read().decode().strip()
    if res_str is "":
        return True
    elif res_str == "not an ELF executable":
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!%s says %s" % (os.path.basename(execfilepath), res_str))
        return False
    return False


def ldd(execfilepath, retlibs=[]):
    if not os.path.exists(execfilepath): return False
    cmd = 'ldd %s' % execfilepath
    rst = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    restr = rst.stdout.readlines()
    print("%s has relate lib %d"%(execfilepath,len(restr)))
    for line in restr:
        line = line.decode().strip()
        t = re.match('^(.*?)=>(.*?)\(\w*?\)$', line)
        libname, libpath = '', ''
        if t:
            libname, libpath = t.group(1).strip(), t.group(2).strip()
        else:
            t = re.match('^(.*?)=>\s*?(not found)\s*?$', line)
            if t:
                libname, libpath = t.group(1).strip(), t.group(2)
                for i in range(3):
                    print('%s not found' % libname)
                    k = input('solve this MANUALLY or AUTO or IGNORE or FAILED choose:[Y/a/i/n]')
                    if k.lower().startswith('i'):
                        break
                    elif k.lower().startswith('n'):
                        raise Exception('lib not found')
                    elif k.lower().startswith('a'):
                        build_deps(softname)
                        return ldd(execfilepath, retlibs)
                    elif k.lower().startswith('y'):
                        return ldd(execfilepath, retlibs)
            else:
                t = re.match('^([a-zA-Z0-9_/\-\.]*?)\s\(.*?\)$', line)
                if t:
                    libname, libpath = '', t.group(1).strip()
                else:
                    print('!!!%s not match'%line)
        if (libname, libpath != '', '') and ((libname, libpath) not in retlibs):
            retlibs.append((libname, libpath))

    return retlibs


def copylibs(libs, destdir):
    files = getsubfiles(destdir, mode='file')
    for libname, libpath in libs:
        if libpath != '' and libpath != "not found":
            if os.path.basename(libpath) not in files:
                copy(libpath, destdir)


def create48x48icon(oripicpath, savepath):
    from PIL import Image
    oripic = Image.open(oripicpath)
    oripic.thumbnail((48, 48))  # 只能缩小
    # oripic.resize((48, 48), Image.ANTIALIAS)  # 能放大缩小
    oripic.save(savepath)
    return savepath


def get48x48iconpath(workdir):
    x48icondir = os.path.join(workdir, 'usr', 'share', 'icons', 'hicolor', '48x48', 'apps')
    if os.path.exists(x48icondir):
        return getdistinctpath(x48icondir, mode='file')
    if os.path.exists(os.path.join(workdir, 'usr', 'share', 'icons', 'hicolor')):
        subdirs = getsubfiles(os.path.join(workdir, 'usr', 'share', 'icons', 'hicolor'), mode='dir')
        if '256x256' in subdirs:
            icondirs = '256x256'
        elif '128x128' in subdirs:
            icondirs = '128x128'
        elif '64x64' in subdirs:
            icondirs = '64x64'
        else:
            icondirs = getdistinctpath(os.path.join(workdir, 'usr', 'share', 'icons', 'hicolor'), mode='dir')
        originaliconfilepath = getdistinctpath(
            os.path.join(workdir, 'usr', 'share', 'icons', 'hicolor', icondirs, 'apps'), mode='file')

        mkdir(os.path.join(workdir, 'usr', 'share', 'icons', 'hicolor', '48x48'))
        mkdir(os.path.join(workdir, 'usr', 'share', 'icons', 'hicolor', '48x48', 'apps'))
        return create48x48icon(originaliconfilepath, os.path.join(x48icondir, os.path.basename(originaliconfilepath)))
    elif os.path.exists(os.path.join(workdir, 'usr', 'share', 'pixmaps')):
        from PIL import Image
        iconfilepath = getdistinctpath(os.path.join(workdir, 'usr', 'share', 'pixmaps'))
        iconpic = Image.open(iconfilepath)
        if iconpic.width > 48:
            iconpic.thumbnail((48, 48))
            iconpic.save(iconfilepath)
        return iconfilepath
    else:
        raise Exception('ICON NOT FOUND')


def editdesktop(extractpath, binfilepath):
    for desktop in getsubfiles(os.path.join(extractpath, 'usr', 'share', 'applications'), 'file'):
        __editconfig(os.path.join(extractpath, 'usr', 'share', 'applications', desktop), "Exec", binfilepath)
        __editconfig(os.path.join(extractpath, 'usr', 'share', 'applications', desktop), "TryExec", binfilepath)


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


def getdebinfo(debs):
    global controlinfo
    dinfos = []
    for deb in debs:
        dinfo = debinfo.getDebInfo(deb)
        dinfos.append(dinfo)
    if len(dinfos) == 0:
        raise Exception('no debinfo found~~')
    if len(dinfos) == 1:
        controlinfo = dinfos[0]
    else:
        c = len(dinfos)
        keys = debinfo.info.keys()
        for key in keys:
            value = set()
            for i in range(c):
                v = dinfos[i].get(key, '')
                if v != '':
                    value.add(v)
            if len(value) == 0:
                controlinfo[key] = ''
            elif len(value) == 1:
                controlinfo[key] = value.pop()
            else:
                print(value)
                while True:
                    v = input("SELECT ONE")
                    if v in value:
                        controlinfo[key] = v
                        break
    controlinfo['vendor'], controlinfo['vendoremail'] = parsevendor(controlinfo.get('maintainer', ''))

    return controlinfo

def parsername(path):
    filename = os.path.basename(path)
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


def parsevendor(maintainer):
    if maintainer == '': return '', ''
    re_str = r'^(.*?)<(.*?)>$'
    r = re.findall(re_str, maintainer)
    if len(r) > 0:
        vendor = r[0][0].strip()
        email = r[0][1].strip()
        return vendor, email
    return '', ''


def parsedesktop(deskpath):
    r = r'^(.*?)=(.*?)$'
    ret = {}
    with open(deskpath, 'r') as f:
        cont = f.read()
        res = re.findall(r, cont, flags=re.MULTILINE)
        for rs in res:
            ret[rs[0].strip()] = rs[1].strip()
        return ret


def desktopinfo(deskpath):
    deskinfo = parsedesktop(deskpath)
    retinfo = {}
    for k, v in deskinfo.items():

        if k == 'GenericName':
            retinfo['genericname_en'] = retinfo['genericname'] = v
        elif k.lower() == 'genericname[zh_cn]':
            retinfo['genericname_zh'] = v
        elif k == 'Comment':
            retinfo['summary_en'] = retinfo['summary'] = v
        elif k.lower() == 'comment[zh_cn]':
            retinfo['summary_zh'] = v
        elif k == 'Categories':
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
                # elif k == 'Keywords':
                #    retinfo['keyword_en'] = retinfo['keyword']
    return retinfo


# 结合control和desktop里的信息，用于生成control.xml
def combineinfo(debs):
    controlinfo = getdebinfo(debs)
    global softversion,softarch
    softversion = controlinfo.get('version','0') if softversion == '' else softversion
    softarch = controlinfo.get('arch','amd64') if softarch == '' else softarch
    if not os.path.exists(os.path.join(extractdebdirpath, 'usr', 'share', 'applications')): return controlinfo
    desktopfilepath = getdistinctpath(os.path.join(extractdebdirpath, 'usr', 'share', 'applications'), 'file')
    deskinfo = desktopinfo(desktopfilepath)
    for k, v in deskinfo.items():
        controlinfo[k] = v
    return controlinfo


def extractdeb(debpath):
    '''
    解压deb包到包目录下包名文件夹
    :param debpath: deb包文件的绝对路径
    :return: 解压后的文件夹
    '''

    mkdir(extractdebdirpath)
    dpkg_x(debpath, extractdebdirpath)
    dpkg_r(debpath, extractdebdirpath)
    return extractdebdirpath


# 解压所有deb包
def extractall(debs):
    for deb in debs:
        extractdeb(deb)


def mkdir(path):
    if os.path.exists(path):
        return path
    os.mkdir(path)
    return path


def copy(source, dest):
    if os.path.isdir(source):
        return shutil.copytree(source, dest)
    else:
        return shutil.copy(source, dest)


def move(source, dest):
    return shutil.move(source, dest)


def dpkg_x(debpath, destpath):
    if not os.path.exists(debpath): return
    cmd = 'dpkg-deb -X %s %s' % (debpath, destpath)
    return subprocess.call(cmd, shell=True)


def dpkg_r(debpath, destpath):
    if not os.path.exists(debpath): return
    cmd = 'dpkg-deb -R %s %s ' % (debpath, destpath)
    return subprocess.call(cmd, shell=True)


# 得到需要转的deb包列表，可能不只有一个
def obtaindebs():
    global debfilepath, basedirpath, softname, extractdebdirpath
    if debfilepath != '':
        if basedirpath == '':
            basedirpath = os.path.dirname(debfilepath)
    debs = []
    tmpname = lambda e: e[0:e.find('-') if e.find('-') < e.find('_') else e.find('_')]
    files = getsubfiles(basedirpath, mode='file', suffix='.deb')
    if len(files) == 0:
        raise Exception("No deb file found~~~")
    elif len(files) == 1:
        softname = tmpname(files[0])
        debs.append(os.path.join(basedirpath, files[0]))
    else:
        if softname == '':

            snames = []
            for file in files:
                name = tmpname(file)
                if name not in snames:
                    snames.append(name)

            if len(snames) == 1:
                softname = snames[0]
            else:
                print(snames)
                while True:
                    n = input("GIVE ME A NAME!!!")
                    if n in snames:
                        softname = n
                        break
            for file in files:
                if file.startswith(softname):
                    debs.append(os.path.join(basedirpath, file))
    extractdebdirpath = os.path.join(basedirpath, softname)
    return debs


def parseargs(args):
    if len(args) <= 1:
        return None
    for arg in args[1:]:
        if arg.find('=') > 1:
            t = arg.split('=')
            k = t[0].strip()
            v = t[1].strip()
            if k in ['name', 'softname']:
                k = 'softname'
            elif k in ['version', 'softversion', 'ver']:
                k = 'softversion'
            elif k in ['arch', 'softarch', 'architecture']:
                k = 'softarch'
            elif k in ['base', 'basedir', 'basedirpath', 'workdir']:
                k = 'basedirpath'
            elif k in ['step', ]:
                k = 'step'
            else:
                continue
            globals()[k] = parameters[k] = v
        elif os.path.exists(arg) and os.path.isfile(arg) and arg.endswith('.deb'):
            # globals()['basedirpath'] = parameters['basedirpath'] = os.path.dirname(arg)
            globals()['debfilepath'] = parameters['debfilepath'] = arg
        elif os.path.exists(arg) and os.path.isdir(arg):
            globals()['basedirpath'] = parameters['basedirpath'] = arg
        elif type(arg) is int:
            globals()['step'] = parameters['step'] = arg
        elif type(arg) is str:
            if arg == '-h' or arg == '--h' or arg.find('help') >= 0:
                printhelp()
            else:
                print(arg)
        else:
            continue


# 修改自身文件，保存运行参数
def modifyself(thisfilepath, kvs):
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
                if os.path.isfile(os.path.join(path, f)):
                    return os.path.join(path, f)
                    break
                elif os.path.isdir(os.path.join(path, f)):
                    return getdistinctpath(os.path.join(path, ), mode)
    return ''


def getsubfiles(path, mode="", prefix='', suffix=''):
    '''
    :param path: path to search
    :param mode: return all | files | dirs
    :param suffix: return files endswith suffix
    :return:
    '''
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
    if suffix != '' and type(suffix) is str:
        retss = rets.copy()
        for ret in retss:
            if os.path.isfile(os.path.join(path, ret)) and not ret.endswith(suffix):
                rets.remove(ret)
    if prefix != '' and type(prefix) is str:
        retss = rets
        for ret in retss:
            if not ret.startswith(prefix):
                rets.remove(ret)

    return rets


def createcpk(workdir, dest):
    cmd = 'cpkg -b %s %s' % (workdir, dest)
    return subprocess.call(cmd, shell=True)


def go():
    global extractdebdirpath, step
    debs = obtaindebs()
    combineinfo(debs)

    if step <= 0:
        # 第一步：解包
        try:
            extractall(debs)
            desktopfilepath = getdistinctpath(os.path.join(extractdebdirpath, 'usr', 'share', 'applications'), 'file')
            deskinfo = desktopinfo(desktopfilepath)
            for k, v in deskinfo.items():
                controlinfo[k] = v

        except Exception as e:
            print(e)
            parameters['step'] = step
            modifyself(thisfile, parameters)
            return step
        finally:
            step += 1
    if step <= 1:
        # 第二步：移动执行文件和库文件
        try:
            movebinandlib()
            modifyexecfiles()
        except Exception as e:
            print(e)
            parameters['step'] = step
            modifyself(thisfile, parameters)
            return step
        finally:
            step += 1
    if step <= 2:
        # 第三步: 改变desktop文件中执行文件路径然后拷贝48x48图标文件路径和desktop文件到CPK
        try:
            cpkdirpath = mkdir(os.path.join(extractdebdirpath, 'CPK'))
            icondirpath = mkdir(os.path.join(extractdebdirpath, 'CPK', 'icons'))
            mkdir(os.path.join(extractdebdirpath, 'CPK', 'screenshot'))
            execpath = getdistinctpath(bindirpath)
            execpath = execpath[execpath.find('/opt'):]
            parameters['execpath'] = controlinfo['execpath'] = execpath
            editdesktop(extractdebdirpath, execpath)
            desktopfilepath = getdistinctpath(os.path.join(extractdebdirpath, 'usr', 'share', 'applications'))
            copy(get48x48iconpath(extractdebdirpath), icondirpath)
            copy(desktopfilepath, cpkdirpath)
        except Exception as e:
            print(e)
            parameters['step'] = step
            modifyself(thisfile, parameters)
            return step
        finally:
            step += 1
    if step <= 3:
        # 第四步:生成filelist,.install和control.xml
        try:
            filelist.gen_filelist(extractdebdirpath)
            install_sricpt.install_generation(extractdebdirpath, softname)
            controlinfo['install'] = softname + ".install"
            controlsavepath = os.path.join(extractdebdirpath, 'CPK', 'control.xml')
            create_controlxml.createcontrol(controlsavepath, controlinfo)
        except Exception as e:
            print(e)
            parameters['step'] = step
            modifyself(thisfile, parameters)
            return step
        finally:
            step += 1
    if step <= 4:
        # 第五步:生成cpk文件
        try:
            createcpk(extractdebdirpath, os.path.join(basedirpath, '%s-%s_%s.cpk' % (softname, softversion, softarch)))
        except Exception as e:
            print(e)
            parameters['step'] = step
            modifyself(thisfile, parameters)
            return step
        finally:
            step += 1
    if step > 5:
        try:
            shutil.rmtree(extractdebdirpath)
        except Exception as e:
            print(e)
            parameters['step'] = step
            modifyself(thisfile, parameters)
            return step
        finally:
            step += 1
    return step


if __name__ == "__main__":
    thisfile = sys.argv[0]
    parseargs(sys.argv)
    go()
