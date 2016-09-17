# encoding:utf-8

import os
import sys
import re
import pexpect
import subprocess
STEP=10
if STEP==0:
    print(3)

def cur_file_dir():
    # 获取脚本路径
    path = sys.path[0]
    # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

def modify(p,k,v):
    with open(p,'r+') as f:
        c = f.read()
        # print(c)
        re_str = r'^\s*?%s\s*?=\w*?\n'%k
        d = re.sub(re_str, "%s=%s\n"%(k,v),c,flags=re.MULTILINE)
        print(d)
        assert d == 0
        f.seek(0)
        f.truncate()

        f.write(d)

def testexpect():
    softname = "rosegarden"
    softname = "librtmp-dev"

    cmd = "sudo  apt-get build-dep %s"%softname
    cc = pexpect.spawn(cmd,encoding="utf-8", echo=True)
    cc.expect("密码：")
    cc.sendline("qwer1234")
    cc.expect("[Y/n]")
    cc.sendline("y")


if __name__ == "__main__":
    # print(cur_file_dir())
    p = sys.argv[0]
    abc = "abc"
    print(abc)
    modify(p,"STEP",'10')


    # testexpect()
