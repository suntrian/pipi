'''
    递归查看某目录下所有desktop文件的category
'''
import os
import re

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

def recursive(path,files=[]):
    subs = getsubfiles(path,'all')
    for sub in subs:
        subpath = os.path.join(path,sub)
        if os.path.isdir(subpath):
            fs = recursive(subpath,files)
            files.extend(fs)
        elif os.path.isfile(subpath):
            if sub.endswith('.desktop'):
                files.append(os.path.join(path,sub))
    return files

def parsedesk(path):

    with open(path,'r') as f:
        c = f.read()
        r = re.findall(r'^(.*?)=(.*?)$',c,flags=re.MULTILINE)
        for rr in r:
            if rr[0].strip() == 'Categories':
                return rr[1].strip()
    return ''

def parseall(path='/usr/share/applications',savepath='/home/yuanxm/desktopcategory.txt'):
    files = []
    files = recursive(path,files)

    with open(savepath,'w') as file:

        for f in files:
            r = parsedesk(f)
            if r != '':
                print(r)
                file.write(r + '\n')

def parsecategory(path='/home/yuanxm/desktopcategory.txt'):
    result = {}
    count = 0
    with open(path,'r') as f:
        for line in f.readlines():
            ll = line.split(';')
            for l in ll:
                l = l.strip()
                if l == '' : continue
                if l in result.keys():
                    result[l] += 1
                else:
                    result[l] = 1
                count += 1

        print("category COUNT:%d"%count)
        print(len(result))
        rs = sorted(result.items(),key=lambda e:e[1])
        count2 = 0
        for k, v in rs:
            print(k,'\t\t',v)
            count2 += v
        print("COUNT2:%d"%count2)


if __name__ == "__main__":
    #parseall()
    parsecategory()