# -*- coding: utf-8 -*- 
# @Time    : 2020/4/8 11:10
# @Author  : WangHong 
# @FileName: game_config.py
# @Software: PyCharm
# 牌的集合

from itertools import islice
import os
import codecs

card_set = ('C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
            'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9',
            'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9',
            'WE', 'WW', 'WS', 'WN', 'AC', 'AF', 'AB', 'UN')

# 动作集合
action_set = ['Win', 'Chow', 'Pon', 'Kon', 'Discard', 'GiveUp', 'Listen']


def LoadData(filename):
    '''
    加载胡牌的索引表
    :param filename:
    :return:
    '''
    file = codecs.open(filename, 'r', 'utf-8')
    HuData = {}
    for line in islice(file, 1, None):  # islice对迭代器做切片
        line = line.strip().split(',')
        Result = []
        op = map(int, line[1].split())
        for suo in op:
            Result.append(suo)
        HuData[int(line[0])] = Result
    return HuData


curpath = os.path.dirname(os.path.realpath(__file__))  # 当前文件路径
HuTable = LoadData(curpath + '/HuIndex.csv')

card_kind = 27

# 牌的编码
dict_index = {0: 'B1', 1: 'B2', 2: 'B3', 3: 'B4', 4: 'B5', 5: 'B6', 6: 'B7', 7: 'B8', 8: 'B9',
              9: 'C1', 10: 'C2', 11: 'C3', 12: 'C4', 13: 'C5', 14: 'C6', 15: 'C7', 16: 'C8', 17: 'C9',
              18: 'D1', 19: 'D2', 20: 'D3', 21: 'D4', 22: 'D5', 23: 'D6', 24: 'D7', 25: 'D8', 26: 'D9'}

# 吃牌动作的编码
index_chi = {0: 'B1B2B3', 1: 'B2B3B4', 2: 'B3B4B5', 3: 'B4B5B6', 4: 'B5B6B7', 5: 'B6B7B8', 6: 'B7B8B9',
             9: 'C1C2C3', 10: 'C2C3C4', 11: 'C3C4C5', 12: 'C4C5C6', 13: 'C5C6C7', 14: 'C6C7C8', 15: 'C7C8C9',
             18: 'D1D2D3', 19: 'D2D3D4', 20: 'D3D4D5', 21: 'D4D5D6', 22: 'D5D6D7', 23: 'D6D7D8', 24: 'D7D8D9'}


