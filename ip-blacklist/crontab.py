# 每5分钟
# 1.先sudo chomd 777 server.log
# 2.tail -n 1000 行
# 3.获取全部 ip ，判断不是指定区域的拉黑。

import re
import subprocess
from xdbSearcher import XdbSearcher
from loguru import logger
logger.add("server_log.log", enqueue=True, watch=True)
def searchWithVectorIndex(ip):
     # 1. 预先加载整个 xdb
    dbPath = "data/ip2region.xdb"
    vi = XdbSearcher.loadVectorIndexFromFile(dbfile=dbPath)
    # 2. 使用上面的缓存创建查询对象, 同时也要加载 xdb 文件
    searcher = XdbSearcher(dbfile=dbPath, vectorIndex=vi)
    # 3. 执行查询
    region_str = searcher.search(ip)
    # 4. 关闭searcher
    searcher.close()
    return region_str

subprocess.getoutput("sudo chmod 777 server.log")
ip_pattern = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}"
                        r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b")

log_list = subprocess.getoutput("tail -n1000 {}".format("server.log"))
log_list = log_list.split("\n")
ip_list = []
for each in log_list:
    ips = ip_pattern.findall(each)
    if ips:
        ip_list.extend(ips)
ip_list = list(set(ip_list))
import ipaddress

for each in ip_list:
    try:
        result = searchWithVectorIndex(each)
        if not re.search("广州",result):
            logger.info(f"ip 地址:{each},{result}")
            subprocess.getoutput("sudo fail2ban-client set sshd  banip {}".format(each))
    except:
        pass

# */1 * * * * cd /home/ubuntu/server && /home/ubuntu/miniconda3/bin/python crontab.py

