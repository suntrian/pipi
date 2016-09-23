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
from multiprocessing import cpu_count

###########################################################################
##  config parameter
'''
    dir--文件夹名   filepath--文件绝对路径    dirpath--文件夹绝对路径
    /$basedirpath
    ----/$makecpkgdirpath
    ----/debfile
    ----/cpkfile
    ----/$debdir
    --------/DEBIAN
    --------/opt
    /opt
    ----/$softname
    --------/bin
    --------/lib
    --------/share
    /usr
    ----/share
'''
# 保存脚本当前执行步骤
step = 0
softname = ""
softversion = ""
softarch = ''
basedirpath = ""
debfilepath = ''
sourcedirpath = ""
makecpkgdirpath = ''
bindirpath = ''
execpath = ""
thisfile = ""
prefixbase = '/opt'
prefix = ''
passwd = 'qwer1234'
parameters = {}
controlinfo = {}

cpu_count = cpu_count()


def printhelp():
    h = '''
    本例实现c源码从编译安装到cpk打包的过程，需要提供源码路径
    "- and -- both will be ok for this"

    -builddep       ---apt-get build-dep
    -configure      ---configure
    -make           ---make
    -install        ---make install
    -copydep        ---deplist copy
    -copydir        ---copy to workdir
    -desktop        ---modify desktop
    -control        ---modify control
    -pack           ---dpkg -b
    -copydeb        ---copy deb to dest
    -all            ---do all above
    -h | help       ---showthis
    '''
    print(h)
    print("     softname     :   %s" % softname)
    print("     softversion  :   %s" % softversion)
    print("     softarch         :   %s" % softarch)
    print("     sourcefold   :   %s" % makecpkgdirpath)
    print("     workbase   :   %s" % basedirpath)


def configure(source='',args=''):
    if source == '':
        source = sourcedirpath
    if os.path.exists(os.path.join(source, 'configure')):
        param = r" --prefix=%s " % prefix
        param += r' LDFLAGS="-Wl,-rpath=' + r"'\$\$ORIGIN/../lib'" + r'"'
        cmd = "cd " + source + "; ./configure " + param
        return subprocess.call(cmd, shell=True)
    elif os.path.exists(os.path.join(source, 'CMakeLists.txt')):
        mkdir(os.path.join(source, 'build'))
        param = "-DCMAKE_INSTALL_PREFIX=%s " % prefix
        param += " -DCMAKE_INSTALL_RPATH=\"'\$ORIGIN/../lib'\""
        cmd = "cd %s; cmake .. %s " % (os.path.join(source, 'build'), param)
        return subprocess.call(cmd, shell=True)
    elif os.path.exists(os.path.join(source, 'SConstruct')):
        print('***************************************************')
        print('** SCON PROJECT')
        raise Exception('SCON')
    elif os.path.exists(os.path.join(source, softname + '.pro')):
        print('***************************************************')
        print('** QMAKE PROJECT')
        raise Exception('QMAKE')
    else:
        raise Exception('unknow')


def make(source='', param=''):
    if source == '': source = sourcedirpath
    if os.path.exists(os.path.join(source, 'makefile')) or os.path.exists(
            os.path.join(source, 'Makefile')) or os.path.exists(os.path.join(source, 'GNUmakefile')):
        cmd = "cd " + source + "; make -j" + str(cpu_count) + param
        return subprocess.call(cmd, shell=True)
    if os.path.exists(os.path.join(source, 'build', 'makefile')) or os.path.exists(
            os.path.join(source, 'build', 'Makefile')) or os.path.exists(os.path.join(source, 'build', 'GNUmakefile')):
        cmd = 'cd %s ; make -j%d' % (os.path.join(source, 'build'), cpu_count)
        return subprocess.call(cmd, shell=True)
    raise Exception('no makefile found')


def install(source=''):
    if source == '': source = sourcedirpath
    if os.path.exists(os.path.join(source, 'makefile')) or os.path.exists(
            os.path.join(source, 'Makefile')) or os.path.exists(os.path.join(source, 'GNUmakefile')):
        cmd = "cd " + source + "; echo " + passwd + " | sudo -S make install"
        return subprocess.call(cmd, shell=True)
    if os.path.exists(os.path.join(source, 'build', 'makefile')) or os.path.exists(
            os.path.join(source, 'build', 'Makefile')) or os.path.exists(os.path.join(source, 'build', 'GNUmakefile')):
        cmd = 'cd %s ; echo %s | sudo -S make install' % (os.path.join(source, 'build'), passwd)
        return subprocess.call(cmd, shell=True)
    return -1


def build_deps(name=''):
    if name == '': name = softname
    cmd = "echo %s | sudo -S apt-get build-dep %s -y" % (passwd, name)
    return subprocess.call(cmd, shell=True)


def readelf(execfile):
    if not os.path.exists(execfile):
        return
    cmd = "readelf -d %s | grep PATH" % execfile
    rstr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    rstr = rstr.stdout.read().decode().strip()

    re_str = '^.*?\(RPATH\)\s*?Library\s*?rpath:\s*?\[(.*?)\]$'
    re_str2 = '^.*?\(RUNPATH\)\s*?Library\s*?runpath:\s*?\[(.*?)\]$'
    k = re.match(re_str, rstr)
    if k:
        if not (k.group(1).strip() == '$ORIGIN/../lib' or k.group(1).strip() == prefix + 'lib'):
            t = re.match(re_str2, rstr)
            if t:
                if not t.group(1).strip() == '$ORIGIN/../lib' and not t.group(1).strip() == prefix + 'lib':
                    return False
        return True
    else:
        print(rstr)


def movetocpkgdir():
    global makecpkgdirpath, prefix, bindirpath
    mkdir(makecpkgdirpath)
    mkdir(os.path.join(makecpkgdirpath, 'opt'))
    mkdir(os.path.join(makecpkgdirpath, 'opt', softname + '-' + softversion))
    mkdir(os.path.join(makecpkgdirpath, 'DEBIAN'))
    mkdir(os.path.join(makecpkgdirpath, 'usr'))
    subs = getsubfiles(prefix)
    for sub in subs:
        if sub in ['share']:
            copy(os.path.join(prefix, 'share'), os.path.join(makecpkgdirpath, 'usr', 'share'))
        elif sub in ['bin', 'game', 'games']:
            copy(os.path.join(prefix, sub), os.path.join(makecpkgdirpath, 'opt', softname + '-' + softversion, sub))
            bindirpath = os.path.join(prefix, sub)


def copylddlibs():
    global bindirpath, makecpkgdirpath
    files = getsubfiles(bindirpath, 'file')
    retlibs = []
    for file in files:
        retlibs = ldd(os.path.join(bindirpath, file), retlibs)
    if len(retlibs) > 0:
        optlibpath = mkdir(os.path.join(makecpkgdirpath, 'opt', softname + '-' + softversion, 'lib'))
        copylibs(retlibs, optlibpath)


def ldd(execfilepath, retlibs=[]):
    if not os.path.exists(execfilepath): return False
    cmd = 'ldd %s' % execfilepath
    rst = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    restr = rst.stdout.readlines()
    if len(restr) <= 1:
        return retlibs
    print("%s has relate lib %d" % (execfilepath, len(restr)))
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
                t = re.match('^([a-zA-Z0-9_/\-.]*?)\s\(.*?\)$', line)
                if t:
                    libname, libpath = '', t.group(1).strip()
                else:
                    print('!!!%s not match' % line)
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
    if not os.path.exists(os.path.join(extractpath, 'usr', 'share', 'applications')):
        return ''
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
    if maintainer == '':
        return '', ''
    re_str = r'^(.*?)<(.*?)>$'
    r = re.findall(re_str, maintainer)
    if len(r) > 0:
        vendor = r[0][0].strip()
        email = r[0][1].strip()
        return vendor, email
    return '', ''


def parsecontrol(controlfile):
    with open(controlfile, 'r') as f:
        conf = {}
        formerkey = ''
        for line in f.readlines():
            m = re.match('^([\w\-]{3,20}):(.*)', line)
            if m:
                conf[m.group(1).strip()] = m.group(2).strip()
                formerkey = m.group(1).strip()
            else:
                conf[formerkey] = conf[formerkey] + '\n' + line
        return conf


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
def combineinfo(controlinfo, deskinfo):
    info = {}
    info['execpath'] = execpath if execpath != '' else input("Type in execute file path")
    info['softname'] = controlinfo.get('Package', softname)
    info['version'] = controlinfo.get('Version', softversion)
    info['arch'] = 'ft1500a' if controlinfo.get('Architecture', softarch) == 'aarch64' else controlinfo.get(
        'Architecture', softarch)
    info['homepage'] = controlinfo.get('Homepage', '')
    info['maintainer'] = controlinfo.get('Maintainer', '')
    info['depends'] = controlinfo.get('Depends', '')
    info['section'] = controlinfo.get('Section', '')
    info['instsize'] = controlinfo.get('Installed-Size', '')
    info['description'] = controlinfo.get('Description')
    info['essential'] = controlinfo.get('Essential', '0')
    info['priority'] = controlinfo.get('Priority', '')
    info['vendor'], info['vendoremail'] = parsevendor(info['maintainer'])

    for k, v in deskinfo.items():
        info[k] = v
    return info


def mkdir(path):
    if os.path.exists(path):
        return path
    os.mkdir(path)
    return path


def copy(source, dest):
    if not (os.path.isdir(source) or os.path.isfile(source)):
        return
    if os.path.isdir(source) and not os.path.exists(dest):
        return shutil.copytree(source, dest)
    elif os.path.isdir(source):
        pass
    else:
        return shutil.copy(source, dest)


def move(source, dest):
    if not (os.path.isdir(source) or os.path.isfile(source)):
        return
    return shutil.move(source, dest)


def dpkg_x(debpath, destpath):
    if not os.path.exists(debpath): return
    cmd = 'dpkg-deb -X %s %s' % (debpath, destpath)
    return subprocess.call(cmd, shell=True)


def dpkg_r(debpath, destpath):
    if not os.path.exists(debpath):
        return
    cmd = 'dpkg-deb -R %s %s ' % (debpath, destpath)
    return subprocess.call(cmd, shell=True)


# 得到需要转的deb包列表，可能不只有一个
def obtaindebs():
    global debfilepath, basedirpath, softname, makecpkgdirpath
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
    makecpkgdirpath = os.path.join(basedirpath, softname)
    return debs


def parseargs(args):
    if len(args) <= 1:
        printhelp()
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
                globals()['step'] = parameters['step'] = int(v)
                continue
            else:
                continue
            globals()[k] = parameters[k] = v
        elif os.path.exists(arg) and os.path.isfile(arg) and arg.endswith('.deb'):
            globals()['debfilepath'] = parameters['debfilepath'] = arg
        elif os.path.exists(arg) and os.path.isdir(arg):
            globals()['sourcedirpath'] = parameters['sourcedirpath'] = arg
        elif type(arg) is int:
            globals()['step'] = parameters['step'] = arg
        elif type(arg) is str:
            if arg == '-h' or arg == '--h' or arg.find('help') >= 0:
                printhelp()
            else:
                print(arg)
        else:
            continue
    tmpname = lambda e: e[0:e.find('-') if 0 < e.find('-') < e.find('_') or e.find('_') < 0 else e.find(
        '_') if e.find('_') > 0 else len(e)]
    if globals()['softname'] == '':
        globals()['softname'] = tmpname(os.path.basename(sourcedirpath))
    if globals()['softversion'] == '':
        globals()['softversion'] = input('softversion')
    if globals()['softarch'] == '':
        globals()['softarch'] = getsysarch()
    if globals()['sourcedirpath'] == '':
        while True:
            k = input('where is source folder')
            if os.path.exists(k):
                globals()['sourcedirpath'] = k
                break
    if globals()['prefix'] == '':
        globals()['prefix'] = os.path.join(globals()['prefixbase'],
                                           globals()['softname'] + '-' + globals()['softversion'])
    if globals()['basedirpath'] == '':
        globals()['basedirpath'] = os.path.join(sourcedirpath, '..')
    if globals()['makecpkgdirpath'] == '':
        globals()['makecpkgdirpath'] = os.path.join(sourcedirpath, '..', 'workdir')
    globals()['bindirpath'] = os.path.join(globals()['prefix'], 'bin')


def printargs():
    print('sourcepath: %s' % sourcedirpath)
    print('softname: %s' % softname)
    print('softversion: %s' % softversion)
    print('softarch: %s' % softarch)
    print('prefix: %s' % prefix)
    print('workdir: %s' % makecpkgdirpath)
    print('step: %s' % str(step))


def getsysarch():
    import platform
    a = platform.machine()
    if a == 'x86_64':
        return 'amd64'
    elif a == 'aarch64':
        return 'ft1500a'


# 修改自身文件，保存运行参数
def modifyself(thisfilepath, kvs):
    return
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


def getexecfilepath():
    subs = getsubfiles(prefix, mode='dir')
    for sub in subs:
        if sub in ['bin', 'game', 'games']:
            getdistinctpath(os.path.join(prefix, sub), mode='file')


def getdistinctpath(path, mode='', prefix='', suffix=''):
    if not os.path.exists(path): return ''
    files = getsubfiles(path, mode, prefix, suffix)
    if len(files) == 1:
        return os.path.join(path, files[0])
    else:
        if softname in files:
            return os.path.join(path, softname)
        else:
            for file in files:
                if file[0:file.find('.')] == softname:
                    return os.path.join(path, file)

        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(files)
        while True:
            f = input("TYPE IN NAMES:")
            if f in files:
                if os.path.isfile(os.path.join(path, f)):
                    return os.path.join(path, f)
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


def getdesktoppath():
    cmd = 'xdg-user-dir DESKTOP'
    rst = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    r = rst.stdout.read().decode().strip()
    if os.path.exists(r):
        return r
    else:
        if os.path.exists(os.path.expanduser('~/桌面')):
            return os.path.expanduser('~/桌面')
        elif os.path.exists(os.path.expanduser('~/Desktop')):
            return os.path.expanduser('~/Desktop')


def chmodx(desktopfilepath):
    cmd = 'chmod +x %s' % desktopfilepath
    return subprocess.call(cmd, shell=True)


def go():
    global makecpkgdirpath, step, execpath
    # debs = obtaindebs()
    # combineinfo(debs)

    if step <= 0:
        # 第一步：configure
        try:
            print("################################################################")
            print("Do BUILD DEPENDS")
            build_deps()
            print("################################################################")
            print("Do CONFIGURE")
            configure()
            print("################################################################")
            print("Do MAKE")
            make()
            print("################################################################")
            print("Do INSTALL")
            install()
            print("################################################################")
            print("Do CHECK Libs Reliable")
            execpath = getexecfilepath()
            if not readelf(execpath):
                raise Exception('Modify rpath failed')

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
            print("###############################################################")
            print("DO MOVE TO WORKDIR")
            movetocpkgdir()
            print("###############################################################")
            print("DO COPY LIBS")
            copylddlibs()
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
            print("###############################################################")
            print("DO MKDIR CPK")
            mkdir(makecpkgdirpath)
            cpkdirpath = mkdir(os.path.join(makecpkgdirpath, 'CPK'))
            icondirpath = mkdir(os.path.join(makecpkgdirpath, 'CPK', 'icons'))
            mkdir(os.path.join(makecpkgdirpath, 'CPK', 'screenshot'))

            print("###############################################################")
            print("DO MODIFY Desktop & MOVE files")
            execpath = getdistinctpath(bindirpath)
            parameters['execpath'] = execpath
            editdesktop(makecpkgdirpath, execpath)
            desktopfilepath = getdistinctpath(os.path.join(makecpkgdirpath, 'usr', 'share', 'applications'))
            copy(get48x48iconpath(makecpkgdirpath), icondirpath)
            copy(desktopfilepath, cpkdirpath)
            copy(desktopfilepath, getdesktoppath())  # copy to desktop
            chmodx(os.path.join(getdesktoppath(), os.path.basename(desktopfilepath)))  # 桌面文件加可执行权限
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
            print("###############################################################")
            print("DO FIND control FILE")
            if not os.path.exists(os.path.join(makecpkgdirpath, 'DEBIAN', 'control')):
                while not os.path.exists(os.path.join(makecpkgdirpath, 'DEBIAN', 'control')):
                    input('Waiting for control file,please add it manually')
            debinfo = parsecontrol(os.path.join(makecpkgdirpath, 'DEBIAN', 'control'))
            deskinfo = desktopinfo(getdistinctpath(os.path.join(makecpkgdirpath, 'usr', 'share', 'applications')))
            controlinfo = combineinfo(debinfo, deskinfo)
            print("###############################################################")
            print("DO GENERATE filelist")
            filelist.gen_filelist(makecpkgdirpath)
            print("###############################################################")
            print("DO GENERATE %s.install" % softname)
            install_sricpt.install_generation(makecpkgdirpath, softname)
            controlinfo['install'] = softname + ".install"
            print("###############################################################")
            print("DO GENERATE control.xml")
            controlsavepath = os.path.join(makecpkgdirpath, 'CPK', 'control.xml')
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
            print("###############################################################")
            print("DO CREATE '%s-%s_%s.cpk" % (softname, softversion, softarch))
            createcpk(makecpkgdirpath, os.path.join(basedirpath, '%s-%s_%s.cpk' % (softname, softversion, softarch)))
        except Exception as e:
            print(e)
            parameters['step'] = step
            modifyself(thisfile, parameters)
            return step
        finally:
            step += 1
    if step > 5:
        try:
            shutil.rmtree(makecpkgdirpath)
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
    printargs()
    go()
