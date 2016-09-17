# encoding:utf-8

intro = """
    this script automatic execute the configure;make;make install progress
    must set config parameters first

    -configure      --configure
    -make           --make
    -install        --make install
    -copydep        --deplist copy
    -copydir        --copy to workdir
    -desktop        --modify desktop
    -control        --modify control
    -pack           --dpkg -b
    -copydeb        --copy deb to dest
    -builddep       --apt-get build-dep
    -all            --do all above
    -h | help       --showthis

    arch = "amd64"
    name={softname}
    softversion = "1.5.0"
    sourcefold = "goldendict-1.5.0~git20150923"
    sourcebase={sourcebase}
    dest={copy deb to dest}
"""

import os
import subprocess
from multiprocessing import cpu_count
import configparser
import re
import sys

cpu_count = cpu_count()

config = configparser.ConfigParser()
###################################################################################
passwd = "qwer1234"
sourcebase = "/home/yuanxm/packsource"
installbase = "/opt"
sourcefold = "goldendict-1.5.0~git20150923"
softname = "goldendict"
softversion = "1.5.0"
arch = "amd64"
destdir = sourcebase + "/deb"
####################################################################################
argvlist = ['arch','softname','softversion','sourcefold','sourcebase','destdir','passwd']
argv_list = {'configure':2, 'make':5, 'install':10, 'copydep':15, 'copydir':20, 'desktop':25, 'control':26, 'pack':30, 'copydeb':35, 'builddep':0, 'h':-5, 'help':-5, 'all':1}

softfold = softname + "-" + softversion
prefix = installbase + "/" + softfold  # 程序安装目录
binpath = prefix + "/bin"  # 程序可执行文件目录
libpath = prefix + "/lib"
workbasedir = sourcebase + "/" + softname
workdir = workbasedir + "/workdir"  # 打包根目录
sourcepath = workbasedir + "/" + sourcefold  # 源代码目录
sharepath = workdir + "/opt/" + softfold + "/share"
desktoppath = sharepath + "/applications"  # desktop文件目录
iconpath = sharepath + "/icons/hicolor"  # icon文件目录
debname = softfold + "_" + arch + ".deb"

def printhelp():
    h = '''
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
    print("     arch         :   %s"%arch)
    print("     softname     :   %s"%softname)
    print("     softversion  :   %s"%softversion)
    print("     sourcefold   :   %s"%sourcefold)
    print("     sourcebase   :   %s"%sourcebase)
    print("     destdir      :   %s"%destdir)

def configure(path, param=""):
    if os.path.exists(path + "/configure"):
        param = " --prefix=/opt/" + softname + "-" + softversion
        param += " LDFLAGS=-Wl,-rpath='\$\$ORIGIN/../lib'"
        cmd = "cd " + path + "; ./configure " + param
        return subprocess.call(cmd, shell=True)
    elif os.path.exists(path + "/CMakeLists.txt"):
        param = "-DCMAKE_INSTALL_PREFIX=%s"%prefix
        param += ""
        # cmd = "cd %s; cmake . -DCMAKE_INSTALL_PREFIX=%s -DCMAKE_INSTALL_LIBDIR=\"'\$ORIGIN/../lib'\"  -DCMAKE_INSTALL_RPATH=\"'\$ORIGIN/../lib'\" "% (path, prefix)
        cmd = "cd %s; cmake . %s " % (path, param)
        return subprocess.call(cmd, shell=True)
    elif os.path.exists(path + "/" + softname + ".pro"):
        print("**************************************************************************")
        print("QMAKE PROJECT")
    elif os.path.exists(path + "/SConstruct"):
        print("***************************************************************************")
        print("SCON PRONECT")
    else:
        return -1

def make(path, param=""):
    if os.path.exists(path + "/makefile") or os.path.exists(path + "/Makefile") or os.path.exists(path + "/GNUmakefile"):
        cmd = "cd " + path + "; make -j" + str(cpu_count) + param
        return subprocess.call(cmd, shell=True)
    return -1

def install(path):
    if os.path.exists(path + "/makefile") or os.path.exists(path + "/Makefile") or os.path.exists(path + "/GNUmakefile"):
        cmd = "cd " + path + "; echo " + passwd + " | sudo -S make install"
        return subprocess.call(cmd, shell=True)
    return -1

def builddep():
    cmd = "echo %s | sudo -S apt-get build-dep %s "%(passwd, softname)
    return subprocess.call(cmd,shell=True)

def deplist(path):
    cmd = "ldd " + path + " | awk '{if (match($3, \"/\")){print $3}}'"
    dep = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    lis = dep.stdout.read().decode()
    lis = lis.replace("\n", ' ')
    return lis


def sudocopy(source, dest, param=""):
    if not os.path.exists(dest):
        cmd = "echo %s | sudo -S mkdir %s"% (passwd, dest)
        subprocess.call(cmd, shell=True)
    if not source is None or not source == "":
        cmd = "echo " + passwd + " |sudo -S cp " + param + " " + source + " " + dest
        # print("CMD:%s"%cmd)
        return subprocess.call(cmd, shell=True)
    return 1


def normalcopy(source, dest, param=""):
    if not source is None or not source == "":
        cmd = "cp " + param + " " + source + " " + dest
        # print("CMD:%s"%cmd)
        return subprocess.call(cmd, shell=True)
    return 1

def createdeskentry():
    desk = os.environ['HOME'] + "/桌面"
    if os.path.exists(desk) :
        assert normalcopy(getdesktoppath(), desk ) == 0
        cmd = "chmod +x %s"% os.path.join(desk, os.path.basename(getdesktoppath()))
        return subprocess.call(cmd, shell=True)

def __parseconfig(path, key, value=""):
    file = config.read(path)
    sections = config.sections()
    config.set(sections[0], key, value)
    with open(file, 'w+') as f:
        config.write(f)

def __editcontrol(path,key,value=""):
    r = r"\n%s:.*?\n"%key
    with open(path, 'r+') as f :
        c = f.read()
        c = re.sub(r,'\n%s:%s\n'%(key,value),c)
        f.seek(0)
        f.truncate()
        f.write(c)

def __editconfig(path, key, value=""):
    r = r"\n(" + key + r"\s?=)(\S+)( *.*?)\n"
    print(r)
    pat = re.compile(r)
    with open(path, 'r+') as f:
        cont = f.read()
        res = pat.findall(cont)
        print(res)
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


def makeworkdir():
    if (not os.path.exists(workdir)):
        os.mkdir(workdir)
    if not os.path.exists(workdir + "/opt"):
        os.mkdir(workdir + "/opt")
    if not os.path.exists(workdir + "/DEBIAN"):
        os.mkdir(workdir + "/DEBIAN")


def package():
    cmd = "dpkg -b " + workdir + " " + workbasedir + "/" + debname
    return subprocess.call(cmd, shell=True)


def editcontrol(path):
    t = 0
    while not os.path.exists(path):
        n = input("WAIT FOR CONTROL FILE:")
        t += 1
        if t== 4:
            print("TERMINATED")
            return
    __editcontrol(path, "Depends", "")



def editdesktop(path):
    __editconfig(path, "Exec", getexecpath())

    ic = geticonpath()
    __editconfig(path, "Icon", ic)


def getfiles(path):
    fis = os.listdir(path)
    return fis


def getexecfiles(path):
    fis = getfiles(path)
    for f in fis:
        filepath = os.path.join(path, f)
        if os.path.isdir(filepath):
            fis.remove(f)
        if not os.access(filepath, os.X_OK):
            fis.remove(f)
    return fis


def getsubfolders(path):
    fis = getfiles(path)
    for f in fis:
        filepath = os.path.join(path, f)
        if not os.path.isdir(filepath):
            fis.remove(f)
    return fis


def geticonpath():
    icpath = ''
    folders = getsubfolders(sharepath)
    if "icons" in folders:
        folders2 = getsubfolders(iconpath)
        folders2c = []
        for f in folders2:
            _pa = iconpath + "/" + f + "/apps"
            if os.path.exists(_pa) and len(getfiles(_pa)) > 0:
                folders2c.append(f)

        pa = ''
        if "scalable" in folders2c:
            pa = iconpath + "/scalable/apps"
        elif "64x64" in folders2c:
            pa = iconpath + "/64x64/apps"
        elif "48x48" in folders2c:
            pa = iconpath + "/48x48/apps"
        else:
            pa = iconpath + "/" + folders2[0] + "/apps"

        ics = getfiles(pa)
        if len(ics) == 1:
            icpath = os.path.join(pa, ics[0])
        elif len(ics) == 0:
            pass
        else:
            formersize = 0
            for ic in ics:
                filepath = os.path.join(pa, ic)
                filesize = os.path.getsize(filepath)
                if filesize > formersize:
                    icpath = filepath
                    formersize = filesize

        icpath = os.path.join(pa, icpath)
        i = icpath.find("/opt")
        icpath = icpath[i:]
        return icpath
    elif "pixmaps" in folders:
        print("******************************************************************")
        print("PIXMAPS")
    else:
        print("******************************************************************")
        print("NOT FOUND ICONS")


def getdesktoppath():
    return getdistinctfile(desktoppath)


def getexecpath():
    return getdistinctfile(binpath)


def getdistinctfile(path):
    files = getfiles(path)
    if len(files) == 1:
        return os.path.join(path, files[0])
    else:
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(files)
        execname = input("TYPE IN NAMES:")
        while not os.path.exists(os.path.join(path, execname)):
            execname = input("TYPE IN NAMES AGAIN:")

        return os.path.join(path, execname)


def create48x48icon(oripicpath, savepath):
    from PIL import Image
    oripic = Image.open(oripicpath)
    oripic.thumbnail((48,48))                           # 只能缩小
    # oripic.resize((48, 48), Image.ANTIALIAS)  # 能放大缩小
    oripic.save(savepath)


def check48x48icon():

    oripic = workdir + "/" + geticonpath()
    name = os.path.basename(oripic)

    files = getsubfolders(iconpath)
    if not "48x48" in files:
        os.mkdir(iconpath + "/48x48")
        os.mkdir(iconpath + "/48x48/apps")
    else:
        files = getsubfolders(iconpath + "/48x48")
        if not "apps" in files:
            os.mkdir(iconpath + "/48x48/apps")
        else:
            files = getfiles(iconpath + "/48x48/apps")
            if len(files) > 0:
                return True

    create48x48icon(oripic, iconpath + "/48x48/apps/" + name)

def modifythis(thisfilepath, kvs):
    with open(thisfilepath, 'r+') as f:
        co = f.read()
        for k,v in kvs.items():
            co = re.sub(r'%s\s*?=.*?\n'%k, r'%s = "%s"\n'%(k,v), co)

        f.seek(0)
        f.truncate()
        f.write(co)

def argsort(args):
    retlist = []

    for arg in args:
        if arg.find('=') > 0:
            try:
                k,v = arg.split('=')
                if k in argvlist:
                    retlist.append(arg)
                continue
            except:
                continue
        elif arg.startswith('--'):
            arg = arg[2:]
        elif arg.startswith('-'):
            arg = arg[1:]
        if arg in argv_list.keys():
            retlist.append(arg)
            continue

    gv = lambda k: argv_list[k] if k in argv_list.keys() else -100

    for i in range(len(retlist)):
        for j in range(i+1, len(retlist)):
            vi = gv(retlist[i])
            vj = gv(retlist[j])
            if vi > vj:
                tmp = retlist[i]
                retlist[i] = retlist[j]
                retlist[j] = tmp

    return retlist




if __name__ == "__main__":

    if len(sys.argv) == 1:
        printhelp()

    incargs = argsort(sys.argv)

    conf = {}
    for arg in incargs:
        if arg.find('=') > 0:
            k, v = arg.split('=')
            if k in argvlist:
                if globals()[k] == v:
                    continue
                globals()[k] = v
                conf[k] = v

            else:
                print(k, v)

        else:
            cmd = arg
            if cmd == 'h' or cmd == "help":
                printhelp()
            elif cmd == 'builddep':
                builddep()
            elif cmd == 'configure':
                configure(sourcepath)
            elif cmd == 'make':
                make(sourcepath)
            elif cmd == 'install':
                install(sourcepath)
            elif cmd == 'copydep':
                execfile = getexecpath()
                deps = deplist(execfile)
                sudocopy(deps, libpath)
            elif cmd == 'copydir':
                makeworkdir()
                normalcopy(prefix, workdir + "/opt", '-r')
            elif cmd == 'copydeb':
                normalcopy(workbasedir + "/" + debname, destdir)
            elif cmd == 'pack':
                package()
            elif cmd == 'desktop':
                check48x48icon()
                editdesktop(getdesktoppath())
            elif cmd == 'control':
                editcontrol(workdir + "/DEBIAN/control")
            elif cmd == 'all':
                assert configure(sourcepath) == 0
                assert make(sourcepath) == 0
                assert install(sourcepath) == 0

                execfile = getexecpath()
                deps = deplist(execfile)
                sudocopy(deps, libpath)

                makeworkdir()
                normalcopy(prefix, workdir + "/opt", '-r')

                check48x48icon()
                editdesktop(getdesktoppath())
                editcontrol(workdir + "/DEBIAN/control")

                package()
                normalcopy(workbasedir + "/" + debname, destdir)

                createdeskentry()

                break
            else:
                print(arg)

    if len(conf) > 0:
        print(conf)
        modifythis(sys.argv[0], conf)