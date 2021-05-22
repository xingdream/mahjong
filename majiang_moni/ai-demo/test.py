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