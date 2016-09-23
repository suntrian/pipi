import re


def getContent(file):
    try:
        f = open(file, 'r')
        # ff = open('/home/yuanxm/PycharmProjects/PackagesInfo_kord_main','a')
        c = f.read()
        r = r'(Package:.*?\n\n)'
        p = re.compile(r, re.DOTALL)
        s = p.findall(c)
        print(len(s))
        l = list()
        keys = set()
        for i in s:
            m = dict()
            rr = r'(.*?):\s?(.*)\n'
            ss = re.findall(rr, i)
            for si in ss:
                m[si[0]] = si[1]
                keys.add(si[0])
            # l.append([m['Package'], m['Version']])        # 加入包名和版本号
            # l.append(m['Maintainer'] + "\n")

            # ff.write('Package' + ':' + m['Package'] + '\n')
            # ff.write('Version' + ':' + m['Version'] + '\n')
            # ff.write('Filename' + ':' + m['Filename'] + '\n')
            # ff.write('\n')
        print(keys)

        return l

    except Exception:
        pass
    finally:
        f.close()
        # ff.close()


def compare(l1, l2):
    cmpreslut = "/home/yuanxm/文档/cmp.txt"
    f = open(cmpreslut, "w")
    for lk1, lv1 in l1:
        for lk2, lv2 in l2:
            if lk1 == lk2:
                f.write(lk1 + ":" + lv1 + "\n")
                f.write(lk2 + ":" + lv2 + "\n")
                f.write("\n")




if __name__ == "__main__":
    u1 = '/home/yuanxm/PycharmProjects/Packages'
    u2 = '/home/yuanxm/文档/Packages_ustc_main'
    # l1 = getContent(u1)
    # l2 = getContent(u2)
    # compare(l1,l2)

    l1 = getContent(u1)
    # with open('/home/yuanxm/PycharmProjects/package_maintainer.txt','w') as f:
    #     f.writelines(l1)