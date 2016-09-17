'''
    查看所有elf可执行文件的依赖库的依赖频率
'''
import os
import re
import subprocess

restr = r'(.*?)=>(.*?)\(.*?\)'
ldpattern = re.compile(restr)


def getbinfilesld(basedir,lib=[]):
    fs = getsubfiles(basedir)
    if "bin" in fs and os.path.isdir(os.path.join(basedir, 'bin')):
        print(os.path.join(basedir,'bin'))
        bs = getsubfiles(os.path.join(basedir, "bin"))
        for b in bs:
            st = ldd(os.path.join(basedir,'bin',b))
            lb = parselibs(st)
            if lb == [] or len(lb) == 0:
                continue
            lib.append(lb)
        return

    for f in fs:
        if os.path.isdir(os.path.join(basedir, f)):
            getbinfilesld(os.path.join(basedir,f), lib)


def ldd(binfile):
    if os.path.exists(binfile):
        cmd = 'ldd %s'%binfile
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        rstr = r.stdout.read().decode()
        return rstr

def parselibs(ldd):
    rs = ldpattern.findall(ldd)
    libs = []
    if len(rs) == 0 :
        return []
    for r in rs:
        libs.append(r[0].strip())
    return libs


def getsubfiles(path, mode=""):
    if not os.path.exists(path): return
    subs = os.listdir(path)
    rets = []
    if mode == "" or mode.startswith("a"):
        return subs
    elif mode.startswith("d"):
        for f in subs:
            if os.path.isdir(os.path.join(path,f)):
                rets.append(f)
    elif mode.startswith("f"):
        for f in subs:
            if os.path.isfile(os.path.join(path,f)):
                rets.append(f)
    elif mode.startswith("e"):
        for f in subs:
            p = os.path.join(path,f)
            if os.path.isfile(f) and os.access(os.access(p,os.X_OK)):
                rets.append(f)
    return rets

def analysislibs(libss):
    libscount = {}
    for libs in libss:
        for lib in libs:
            if lib in libscount.keys():
                libscount[lib] += 1
            else:
                libscount[lib] = 1

    print("### binfile count: %d"% len(libss))
    libscount = sorted(libscount.items(), key=lambda e:e[1])
    for k,v in libscount:
        print(k, '      ' ,v)
    return libscount

if __name__ == "__main__":
    libs = []
    getbinfilesld("/opt", libs)
    analysislibs(libs)
