"""
ting_result = {'C6': ['B5', 'C7'], 'C7': ['C5', 'C8']}
print(ting_result.keys())
ting_card_lis= ['C6', 'C7']
for i in range(len(ting_result)):
    print(ting_result[ting_card_lis[i]])
    for j in range(len(ting_result[ting_card_lis[i]])):
        print((ting_result[ting_card_lis[i]])[j])
for j in range(7,4,-1):
    print(j)

list1 = [11, 5, 17, 18, 23]
print("列表元素之和为: ", sum(list1))

import numpy as np
a = [1,2,3]
b = [4,5,6]
c = [7,8,9]
print(np.sum([a,b,c], axis = 1))

import numpy as np
total = np.zeros(shape=(4, 9), dtype='i1')
for i in range(3):
    for j in range(9):
        total[i][j] = 4
print(total)
print(np.dtype('i1'))
print(np.dtype('i2'))
print(np.dtype('i4'))
print(np.dtype('i8'))
print(np.dtype('int'))

show = np.zeros(shape=(4, 9), dtype='i1')
un_show = total - show
print(un_show)

num = int(14 / 3)
print('*'*40)

for s in range(5):
    un_show_matrix = np.zeros(shape=(1, 10, 4, 9), dtype='i1')
    for i in range(2):
        un_show_matrix[0][i] = un_show

    print(un_show_matrix.shape)
    print('模拟第{}个听牌手牌矩阵{}'.format(s,un_show_matrix[0][s]))

# import random
#
# list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# slice = random.sample(list, 5)  # 从list中随机获取5个元素，作为一个片断返回
# print(slice)
# print(list)  # 原有序列并没有改变
#
# a = range(1,100)
# print(a)
# b = random.sample(a, 7)
# print(b)

import numpy as np
T = np.full((4, 6),3)
print(T)

# 推荐使用此方法
a = [1, 2, 3]
print(a, id(a))
a.clear()
print(a, id(a))

# 以下方法会产生内存碎片，虽然有垃圾回收机制，但回收本身要产生较大的开销
print('\n-------------\n')
a = [1, 2, 3]
print(a, id(a))
a = []
print(a, id(a))
"""
import random

a = [4,2,3,1]
# 求最大值
print(max(a))
# 求最大值的索引
print(a.index(max(a)))

print(a.index(min(a)))

import numpy as np
# 创建ndarray
a = np.array([4,2,6,7])
print(a)
# 将ndarray转换为list
list_a = a.tolist()
print((list_a))
# 求最大值
print(max(list_a))
# 求最大值的索引
print(list_a.index(max(list_a)))

# 创建ndarray
a = np.array([4,2,6,7])
# 求最大值的索引
print(np.argmax(a))
# 求最大值
print(a[np.argmax(a)])

listen_id = [-1, -1, -1, -1]
print()


def add(i):
    n = i**2
    return n
m = 2
add(m)
print(m)

i = 5
while True:
    for a in range(10):
        print('hhh')

    i += 1
    print('--1---', i)
    break
print('--2---', i)

for i in range(0, 52, 13):
    print(i)


majiang = 4*[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
def start():
	random.shuffle(majiang)
	majiang_split= []
	for i in range(0,52,13):
		majiang_split.append(majiang[i:i+13])
	return majiang_split
a = start()
print(a)
print(majiang, len(majiang))
for i in range(13):
    majiang.pop(0)
print(majiang, len(majiang))
print(a)


def _get_new_majiang(majiang):
    """确定庄家，获得一张牌，开始游戏"""
    majiang.pop(0)
print(majiang)
b = _get_new_majiang(majiang)
print(majiang)

list = [2, 3, 15, 8, 8, 14, 7, 3, 14, 6, 6, 10, 9, 12]
from random import choice
one = choice(list)
for i in range(30):
    print('列表中第{}次随机取出的元素是{}'.format(i,choice(list)))
"""
列表的无限循环
import time
def traversal_list(alist, i):
    while True:
        length = len(alist)
        i = i%(length)
        yield alist[i]
        i += 1

def traversal_list2(alist):
    i = 0
    f = traversal_list(alist, i)
    while True:
        a = next(f)
        print(a)
        time.sleep(1)
        i += 1

if __name__ == '__main__':
    alist = [1, 2, 3, 4, 5]
    traversal_list2(alist)
"""

aList = [123, 'xyz', 'zara', 'abc', 123];
bList = [2009, 'manni'];
aList.extend(bList[2:])

print("Extended List : ", aList)

win_sum = [1,2,3,3]
win_sum[3] += 1
print('win_sum:',win_sum)
num_sum = 10
new_list = [x/num_sum for x in win_sum]
print("rate:  :", new_list)

elw = []
if elw == []:
    print(True)
print(False)
