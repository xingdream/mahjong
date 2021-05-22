# -*- coding: utf-8 -*- 
# @Time    : 2020/4/8 11:11
# @Author  : WangHong 
# @FileName: log_config.py
# @Software: PyCharm
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )
