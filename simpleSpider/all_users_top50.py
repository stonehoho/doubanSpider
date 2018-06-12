import re, os, sys
import subprocess, time

userPath = "./data/user"
groupPath = "./data/group"

def get_all_groups(userid):
    cmd = "mkdir {}/{}".format(userPath, userid)
    rc = subprocess.call(cmd, shell=True)
    cmd = "wget 'https://www.douban.com/group/people/{0}/joins' -O {1}/{0}/joinsGroup".format(userid, userPath)
    rc = subprocess.call(cmd, shell=True)
    time.sleep(1)
    joinfile_path = "{0}/{1}/joinsGroup".format(userPath, userid)
    f = open(joinfile_path, "rb")
    rawdata = f.readlines()
    datalines = "".join(rawdata)
    formatdata = datalines.replace("\n", "")
    groups_list = re.findall('a href="https://www.douban.com/group/([0-9a-zA-Z\.]*?)/"' ,formatdata)
    print groups_list, "1111111111111111111"
    group_names = re.findall('a title="(.*?)" href="https://www.douban.com/group/([0-9a-zA-Z\.]*?)/"', formatdata)
    return groups_list, group_names

def get_groups_info(groupList):
    for each in groupList[:15]:
        topicSet = set()
        path = "{}/{}".format(groupPath, each)
        cmd = "mkdir {}".format(path)
        rc = subprocess.call(cmd, shell=True)
        fileList = os.listdir(path)
        for item in fileList:
            filepath = "{}/{}".format(path, item)
            f = open(filepath, 'rb')
            rawdata = f.readlines()
            datalines = "".join(rawdata)
            formatdata = datalines.replace("\n", "")
            href = re.findall('href="(https://www.douban.com/group/topic/.*?)"', formatdata)
            for i in href:
                topicSet.add(i)
            f.close()
        for i in range(0, 2000, 25):
            saved_file = "./data/group/{0}/{2}_{1}".format(each, i, time.time())
            cmd = "wget 'https://www.douban.com/group/{0}/discussion?start={1}' -O {2}".format(each, i, saved_file)
            rc = subprocess.call(cmd, shell=True)
            f = open(saved_file, "rb")
            rawdata = f.readlines()
            datalines = "".join(rawdata)
            formatdata = datalines.replace("\n", "")
            f.close()
            href = re.findall('href="(https://www.douban.com/group/topic/.*?)"', formatdata)
            count = 0
            for j in href:
                if j in topicSet:
                    count += 1
                else:
                    topicSet.add(j)
            if count >= 10:
                break
            time.sleep(3)

def parse(item):
    title = re.findall('title="(.*?)"', item)
    href = re.findall('href="(.*?)"', item)
    name = re.findall('/" class="">(.*?)</a></td>', item)
    posterid = re.findall('people/(.*?)/', item)
    current = re.findall('<td nowrap="nowrap" class="time">(.*?)</td>' , item)
    return title, href, name, posterid, current

def group_analysis(groupList, userid, groupname_map):
    cmd = "mkdir {}/{}".format(userPath, userid)
    rc = subprocess.call(cmd, shell=True)
    saved_file = "{}/{}/total".format(userPath, userid)
    fuser = open(saved_file, 'w')
    if len(groupList) == 0:
        path = "{}/".format(groupPath)
        groupList = os.listdir(path)
        for each in groupList:
            groupname_map[each] = 'no internet'
    print groupList, "kkkkkkkkkkkkkkkkkkkkkk"
    for each in groupList:
        path = "{}/{}/".format(groupPath, each)
        fileList = os.listdir(path)
        for item in fileList:
            filepath = "{}/{}".format(path, item)
            f = open(filepath, 'rb')
            rawdata = f.readlines()
            datalines = "".join(rawdata)
            formatdata = datalines.replace("\n", "")
            f.close()
            topics = re.findall('<tr class="">(.*?)</tr>' ,formatdata)
            for i in topics:
                title, href, name, posterid, current = parse(i)
                if len(title)>0 and len(href)>0 and len(name)>0 and len(posterid)>0 and len(current)>0:
                    tempdata = '{} {} {} {} {} {} {}\n'.format(groupname_map[each], each, title[0], href[0], name[0], posterid[0], current[0])
                    fuser.write(tempdata)
    fuser.close()

def filter_results(userid):
    saved_file = "{}/{}/self".format(userPath, userid)
    fuser = open(saved_file, 'w')
    source_file = "{}/{}/total".format(userPath, userid)
    ftotal = open(source_file, 'rb')
    userid_topics_map = {}
    for each in ftotal:
        rawdata = each.split(' ')
        userid = rawdata[-3]
        userid_topics_map.setdefault(userid, []).append(each)
    sorted_map = sorted(userid_topics_map.items(), key=lambda x: len(x[1]), reverse=True)
    count = 0
    for each in sorted_map:
        count += 1
        print each[0], len(each[1])
        for item in each[1]:
            fuser.write(item)
    ftotal.close()
    fuser.close()

def main():
    if len(sys.argv) < 2:
        print "print input userid"
        exit(0)
    userid = sys.argv[1]
    if len(sys.argv) == 3:
        download_strategy = sys.argv[2]
        groupList, groupNames = [], []
    else:
        groupList, groupNames = get_all_groups(userid)
    groupname_map = {}
    for each in groupNames:
        groupname_map[each[1]] = each[0]
    get_groups_info(groupList)

    group_analysis(groupList, userid, groupname_map)
    filter_results(userid)
    print "Done"
    cmd = "cat ./data/user/{}/self".format(userid)
    rc = subprocess.call(cmd, shell="True")

if __name__ == "__main__":
    main()


