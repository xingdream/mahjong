# -*- coding: utf-8 -*- 
# @Time    : 2020/4/2 10:04
# @Author  : WangHong 
# @FileName: dazhong_mahjong.py
# @Software: PyCharm
import random
import sys
import os
import numpy as np

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from src.mahjong_no_state import *


class Pubilc_MahJong(MahJong_NO_State_Base):
    '''
    二人麻将无状态AI，第一版本
    '''

    def __init__(self, mess_data):  # mess_date 是穿过来的test_str
        super(Pubilc_MahJong, self).__init__(mess_data)
        self.un_show_count = np.zeros(shape=(4, 9), dtype='i1')  # 未摸牌矩阵
        self.simulate_all_listener_possible = np.zeros(shape=(4, 5, 4, 9))  # 4个玩家，每种玩家四种手牌情况，手牌用4行9列矩阵存贮
        self.next = np.ones(shape=(1, 40), dtype='i1')  # 该矩阵用来查看出牌是否点炮，点炮了换到下一个
        self.matrix_un_show = np.zeros(shape=(1, 10, 4, 9), dtype='i1')  # 用来拷贝10份未知矩阵
        self.listen__id = []  # fire_hu()种需要来获得听牌者的ID 号
        self._ai_del_logic()

    def _ai_del_logic(self):
        '''
        ai的处理逻辑
        :return:
        '''
        card_num = self.StateData[self.player_seat, 0].sum()
        # 天听动作
        if card_num == 13 and self.is_tting:
            is_can_tting, ting_result = self._check_ting(self.player_seat, t_ting=True)
            # 如果可以天听，并且天听的牌的种类超过两种就天听
            if is_can_tting:
                for key in ting_result.keys():
                    self._conv_req_mess('Listen', key, '')
                    return
            else:
                self._conv_req_mess('Pass', '', '')
        # 自己摸牌，从最后的牌开始打
        elif card_num % 3 == 2:  # 证明这里是自己接牌，才14%3=2，然后自己开始出牌
            print('开始打自己的牌...')
            self._del_ourself_drw()  # 处理自己的摸牌动作
            is_can_tting, ting_result = self._check_ting(self.player_seat, t_ting=False)  # 出牌后检查自己能否 听
            if is_can_tting:  # 可以听，差一张胡牌
                for key in ting_result.keys():
                    print('我能听牌了吗：{}'.format(is_can_tting))
                    self._conv_req_mess('Listen', key, '')  # 听，拿啥打啥
                    return
            return
        # 对手打牌
        elif card_num % 3 == 1:  # 这里是对方出牌，自己判读是否杠、碰、吃；
            self._del_other_out()  # 处理对手的出牌动作
        else:
            logging.error("相公")
            self._conv_req_mess('相公了', 'Self')  # 组装回复数据

    def _del_ourself_drw(self):
        self._think_and_deal()  # 自己出牌

    def _get_linstener_history(self):  # 获得听牌玩家所有打出去、吃、碰、杠的牌，存贮在linstener_*中；
        pass_history = self.MessData['history']
        print('有人听牌，小心点炮！！！')
        had_listen = 0
        listen_id = [-1, -1, -1, -1, ]  # 假设最多有三个对手听牌了，
        # 找出听牌的人，并在listen_id里面写出听牌的座位号0-3；
        for i in range(len(pass_history)):
            id = pass_history[i][0]
            if pass_history[i][2] == 'L':  # 该位置有听牌的
                print('{} 玩家听了'.format(pass_history[i][0]))
                if id == '0':
                    if self.player_seat != 0:
                        listen_id[0] = 0  # 在听牌的位置上赋值
                        continue
                if id == '1':
                    if self.player_seat != 1:
                        listen_id[1] = 1  # 在听牌的位置上赋值
                        continue
                if id == '2':
                    if self.player_seat != 2:
                        listen_id[2] = 2  # 在听牌的位置上赋值
                        continue
                if id == '3':
                    if self.player_seat != 3:
                        listen_id[3] = 3  # 在听牌的位置上赋值
                        continue
        self.listen__id = listen_id
        listener_0 = []
        listener_1 = []
        listener_2 = []
        listener_3 = []
        listener_all = [listener_0, listener_1, listener_2,
                        listener_3, ]  # listener_all 最后会作simulate_lintener_hand(listener_hand=[])中的参数
        # 把听过牌的玩家的手牌拿出来
        for i in range(4):
            if listen_id[i] != -1:
                print('获得玩家 {} 的手牌...'.format(i))
                if i == 0:
                    ii = '0'
                if i == 1:
                    ii = '1'
                if i == 2:
                    ii = '2'
                if i == 3:
                    ii = '3'
                for j in range(len(pass_history)):  # 浏览json中的history，
                    if pass_history[j][0] == ii:  # 把对应听牌玩家座位号0-3的打出的牌分别存储到对应的玩家手中
                        if i == 0:
                            listener_0.append(pass_history[j])
                        if i == 1:
                            listener_1.append(pass_history[j])
                        if i == 2:
                            listener_2.append(pass_history[j])
                        if i == 3:
                            listener_3.append(pass_history[j])
        print('listener_3', listener_3)
        print('listener_0', listener_0)
        self.simulate_lintener_hand(listener_all)  # 开始模拟玩家的手牌
        # simulat_listenr_hand(listen_id,un_show_count)
        # 把听牌的座位号、未知牌矩阵传过去，
        # 根据听牌者出的牌，吃、碰、杠的牌近似模拟出他的手牌*******
        # 假设模拟出10种手牌，看打出去点炮的次数*******
        # 该函数放在每一个出牌之前，判断出该牌是点炮可能性大，
        # 如果可能性小于50%，打出改牌
        # 反之，重新执行出牌判断的过程，重新找一张牌重复上面几步，找到合适的牌输出。

    # 模拟玩家的手牌
    def simulate_lintener_hand(self, listener_hand):  # listener_hand 里面存贮听牌玩家的所有打出的手牌历史，list = [listener1,listener2...]
        if listener_hand != '':
            for i in range(len(listener_hand)):  # 提取某一听牌玩家的手牌
                time_C, time_P, time_K = 0, 0, 0  # 统计吃碰杠的次数，方便计算余下的牌怎样模拟
                if len(listener_hand[i]) != 0:  # 该seat玩家听牌
                    print('当前在处理{}号玩家的打出的手牌：{}'.format(i, listener_hand[i]))
                    for j in range(len(listener_hand[i])):  # 开始查看该听牌玩家打牌的历史list
                        if listener_hand[i][j][2] == 'C':  # 吃牌处理
                            time_C += 1  # 吃次数+1
                            c1 = listener_hand[i][j][-1]  # 获得‘0,Discard,B9’中的9
                            c2 = listener_hand[i][j][-2]  # 获得‘0,Discard,B9’中的D
                            card1 = c2 + c1  # 组装这张牌 D+9 = D9
                            print('吃的一张牌：', card1)
                            line1, row1 = self._get_card_index(card1)
                            for c in range(5):
                                self.simulate_all_listener_possible[i][c][line1][row1] = 1
                            c3 = listener_hand[i][j][-3]  # 获得‘0,Discard,B9’中的9
                            c4 = listener_hand[i][j][-4]  # 获得‘0,Discard,B9’中的D
                            card2 = c4 + c3
                            print('吃的一张牌：', card2)
                            line2, row2 = self._get_card_index(card2)
                            for c in range(5):
                                self.simulate_all_listener_possible[i][c][line2][row2] += 1
                            c5 = listener_hand[i][j][-5]  # 获得‘0,Discard,B9’中的9
                            c6 = listener_hand[i][j][-6]  # 获得‘0,Discard,B9’中的D
                            card3 = c6 + c5
                            print('吃的一张牌：', card3)
                            line3, row3 = self._get_card_index(card3)  # 获得改牌的 line row 好在下面的调用中直接去矩阵中对应位置修改
                            for c in range(5):
                                self.simulate_all_listener_possible[i][c][line3][row3] = 1
                        if listener_hand[i][j][2] == 'P':  # 碰牌处理
                            time_P += 1  # 碰的次数+1
                            c1 = listener_hand[i][j][-1]  # 获得‘0,Discard,B9’中的9
                            c2 = listener_hand[i][j][-2]  # 获得‘0,Discard,B9’中的D
                            card = c2 + c1  # 组装这张牌 D+9 = D9
                            print('碰的一张牌：', card)
                            line, row = self._get_card_index(card)  # 获得改牌的 line row 好在下面的调用中直接去矩阵中对应位置修改
                            for c in range(5):
                                self.simulate_all_listener_possible[i][c][line][row] = 3
                        if listener_hand[i][j][2] == 'K':  # 杠牌处理
                            time_K += 1  # 杠的次数+1
                            c1 = listener_hand[i][j][-1]  # 获得‘0,Discard,B9’中的9
                            c2 = listener_hand[i][j][-2]  # 获得‘0,Discard,B9’中的D
                            card = c2 + c1  # 组装这张牌 D+9 = D9
                            print('杠的一张牌：', card)
                            line, row = self._get_card_index(card)  # 获得改牌的 line row 好在下面的调用中直接去矩阵中对应位置修改
                            for c in range(5):
                                self.simulate_all_listener_possible[i][c][line][row] = 4
                        if listener_hand[i][j][2] == 'D':  # 打牌处理，不能让这些牌再在手牌中出现，又有点难做。。。。。
                            c1 = listener_hand[i][j][-1]  # 获得‘0,Discard,B9’中的9
                            c2 = listener_hand[i][j][-2]  # 获得‘0,Discard,B9’中的D
                            card = c2 + c1  # 组装这张牌 D+9 = D9
                            # print('打出的一张牌：', card)
                            line, row = self._get_card_index(card)  # 获得改牌的 line row 好在下面的调用中直接去矩阵中对应位置修改
                else:
                    continue  # 该seat玩家没听牌
                # 吃、碰、杠、之后看自己还应该模拟几张牌，然后进行模拟其他牌，得到最终的手牌矩阵****
                # 1.看玩家剩余的牌，
                simulate_num = 13 - time_C * 3 - time_P * 3 - time_K * 3  # 杠也按*3来算，只为方便计算，不会对最终有影响
                # 2.根据剩余个数进行模拟
                self._simulate_rest_card(simulate_num, i, 5)  # i是seat,size是模拟出几种不同类型的手牌,假设先模仿一种手牌

    # 模拟玩家吃碰杠之后的牌（差一张胡）
    def _simulate_rest_card(self, num, seat, size):
        hand_cards_num = size  # 用来决定生成几种手牌
        # 得到未莫的牌的矩阵
        show_count = self.ShowCount
        print('当前以知的手牌矩阵')
        print(show_count)
        # 初始化牌，每张牌都有四张
        total = np.zeros(shape=(4, 9), dtype='i1')
        for i in range(3):
            for j in range(9):
                total[i][j] = 4
        # 当前未揭牌矩阵
        self.un_show_count = total - show_count - self.StateData[self.player_seat, 0]
        for i in range(10):
            self.matrix_un_show[0][i] = self.un_show_count
        # 现有一个分析的函数，来检测筒、条、万、分别能提供多少顺子、刻字、对子；
        if num == 1:  # 假设D1D2D3D4D5D6D7D8D9C1C1C1,B1,至少有一对，
            # 一张单
            half_duizi = self._get_nhalf_duizi(10)
            print('获得的这张牌的line:{},row:{}'.format(half_duizi[0][0], half_duizi[0][1]))
            line, row = half_duizi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # 生成hand_cards_num个手牌种类的个数
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    print('重复执行...')
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][half_duizi[ran][0]][half_duizi[ran][1]] += 1  # 手牌怎加一张单牌
                list_ran.append(ran)
        if num == 4:  # 假设D1D2D3D4D5D6D7D8D9,B1B1D2D3,至少有一对，
            # 一张单
            half_duizi = self._get_nhalf_duizi(10)
            print('获得的这张牌的line:{},row:{}'.format(half_duizi[0][0], half_duizi[0][1]))
            line, row = half_duizi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # 生成hand_cards_num个手牌种类的个数
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][half_duizi[ran][0]][half_duizi[ran][1]] += 1  # 手牌怎加一张单牌
                list_ran.append(ran)
            # 一个顺子
            shunzi = self._get_nshunzi(10)  # 获取一个顺子
            line1, row = shunzi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # size是看增加几副不同的手牌,
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][shunzi[ran][0]][shunzi[ran][1]] += 1  # 手牌+顺子第1张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][2]][shunzi[ran][3]] += 1  # 手牌+顺子第2张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][4]][shunzi[ran][5]] += 1  # 手牌+顺子第3张
                list_ran.append(ran)
        if num == 7:  # 假设D1D2D3D4D5D6D,B1B1D1D2D3D9D9,可以没有对子，有顺子或者刻子，半顺或者半刻子12或者11
            # 一张单
            half_duizi = self._get_nhalf_duizi(10)
            print('获得的这张牌的line:{},row:{}'.format(half_duizi[0][0], half_duizi[0][1]))
            line, row = half_duizi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # 生成hand_cards_num个手牌种类的个数
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][half_duizi[ran][0]][
                    half_duizi[ran][1]] += 1  # 手牌怎加一张单牌
                list_ran.append(ran)
            # 一个顺子
            shunzi = self._get_nshunzi(10)  # 获取一个顺子
            line1, row = shunzi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # size是看增加几副不同的手牌,
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][shunzi[ran][0]][shunzi[ran][1]] += 1  # 手牌+顺子第1张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][2]][shunzi[ran][3]] += 1  # 手牌+顺子第2张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][4]][shunzi[ran][5]] += 1  # 手牌+顺子第3张
                list_ran.append(ran)
            # 一个刻字
            kezi = self._get_nkezi(10)
            line2, row = kezi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # line是看增加几副不同的手牌
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][kezi[ran][0]][kezi[ran][1]] += 3  # 手牌+刻子一组
                list_ran.append(ran)
        if num == 10:  # 可以没有对子，剩下的顺子和刻字共2个，半顺或者半刻子12或者11
            # 一张单
            half_duizi = self._get_nhalf_duizi(10)
            print('获得的这张牌的line:{},row:{}'.format(half_duizi[0][0], half_duizi[0][1]))
            line, row = half_duizi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # 生成hand_cards_num个手牌种类的个数
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][half_duizi[ran][0]][
                    half_duizi[ran][1]] += 1  # 手牌怎加一张单牌
                list_ran.append(ran)
            # 一个顺子
            shunzi = self._get_nshunzi(10)  # 获取一个顺子
            line1, row = shunzi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # size是看增加几副不同的手牌,
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][shunzi[ran][0]][shunzi[ran][1]] += 1  # 手牌+顺子第1张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][2]][shunzi[ran][3]] += 1  # 手牌+顺子第2张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][4]][shunzi[ran][5]] += 1  # 手牌+顺子第3张
                list_ran.append(ran)
                # 生成第二个顺子，因为10张牌需要2个顺子，一个刻字，一个单，这里没有考虑对子
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][shunzi[ran][0]][shunzi[ran][1]] += 1  # 手牌+顺子第1张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][2]][shunzi[ran][3]] += 1  # 手牌+顺子第2张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][4]][shunzi[ran][5]] += 1  # 手牌+顺子第3张
                list_ran.append(ran)
            # 一个刻字
            kezi = self._get_nkezi(10)
            line2, row = kezi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # line是看增加几副不同的手牌
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][kezi[ran][0]][kezi[ran][1]] += 3  # 手牌+刻子一组
                list_ran.append(ran)
        if num == 13:  # 可以没有对子，剩下都是刻字和顺子，差一张拼够对子
            # 一张单
            half_duizi = self._get_nhalf_duizi(10)
            print('获得的这张牌的line:{},row:{}'.format(half_duizi[0][0], half_duizi[0][1]))
            line, row = half_duizi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # 生成hand_cards_num个手牌种类的个数
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][half_duizi[ran][0]][half_duizi[ran][1]] += 1  # 手牌怎加一张单牌
            # 一个顺子
            shunzi = self._get_nshunzi(10)  # 获取一个顺子
            line1, row = shunzi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # size是看增加几副不同的手牌,
                list_ran = []  # 存储生成的随机数，确保用过的顺子不会重复使用
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][shunzi[ran][0]][shunzi[ran][1]] += 1  # 手牌+顺子第1张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][2]][shunzi[ran][3]] += 1  # 手牌+顺子第2张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][4]][shunzi[ran][5]] += 1  # 手牌+顺子第3张
                list_ran.append(ran)
                # 生成第二个顺子，因为10张牌需要2个顺子，一个刻字，一个单，这里没有考虑对子
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][shunzi[ran][0]][shunzi[ran][1]] += 1  # 手牌+顺子第1张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][2]][shunzi[ran][3]] += 1  # 手牌+顺子第2张
                self.simulate_all_listener_possible[seat][i][shunzi[ran][4]][shunzi[ran][5]] += 1  # 手牌+顺子第3张
                list_ran.append(ran)
            # 一个刻字
            kezi = self._get_nkezi(10)
            line2, row = kezi.shape  # line,提供不同单牌的个数，row没啥用，
            for i in range(hand_cards_num):  # line是看增加几副不同的手牌
                list_ran = []
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][kezi[ran][0]][kezi[ran][1]] += 3  # 手牌+刻子一组
                list_ran.append(ran)
                # 同理，这里生成第二个刻字，2顺+2刻+1单 = 13
                ran = random.randint(0, 9)  # 随机获得一个0-9的数
                list_ran.append(ran)
                while half_duizi[ran][0] != -1 and ran in list_ran:
                    ran = random.randint(0, 9)  # 随机获得一个0-9的数
                self.simulate_all_listener_possible[seat][i][kezi[ran][0]][kezi[ran][1]] += 3  # 手牌+刻子一组
                list_ran.append(ran)

    # 1.获得n个对子
    def _get_nduizi(self, size):  # size 对子的个数，直接提供对子的最大个数
        print('提供对子...')
        temp_size = size - 1
        duizi = np.zeros(shape=(temp_size + 1, 2), dtype='i1')  # 矩阵可以提供size个对子，用一个n行2列的矩阵来存储；第一列村line,第二列存row
        line = 0  # line 用来给duizi矩阵赋值，
        for i in range(temp_size):
            for j in range(2):
                duizi[i][j] = -1  # 给对子矩阵初试画一下，
        # 在un_show_count_array中寻找值为2的点，为其提供size的个数，
        for i in range(3):
            if temp_size == -1:
                break
            for j in range(9):
                if self.un_show_count[i][j] == 2:
                    duizi[line][0] = i
                    duizi[line][1] = j
                    line += 1  # 行数+1
                    self.matrix_un_show[0][temp_size][i][j] -= 2  # 未知矩阵中的数值也更新
                    temp_size -= 1  # 提供的对子个数-1
                    if temp_size == -1:
                        break  # 个数够了，就可以退出
        # 如果为2的点不够size，再去找为3的点
        if temp_size >= 0:
            for i in range(3):
                if temp_size == -1:
                    break
                for j in range(9):
                    if self.un_show_count[i][j] == 3:
                        duizi[line][0] = i
                        duizi[line][1] = j
                        line += 1  # 行数+1
                        self.matrix_un_show[0][temp_size][i][j] -= 2
                        temp_size -= 1  # 提供的对子个数-1
                        if temp_size == -1:
                            break
        # 如果为3的点不够size，再去找为4的点
        if temp_size >= 0:
            for i in range(3):
                if temp_size == -1:
                    break
                for j in range(9):
                    if self.un_show_count[i][j] == 4:
                        duizi[line][0] = i
                        duizi[line][1] = j
                        line += 1  # 行数+1
                        self.matrix_un_show[0][temp_size][i][j] -= 2
                        temp_size -= 1  # 提供的对子个数-1
                        if temp_size == -1:
                            break
        if temp_size >= 0:
            print('Error_dazhong_majiang,_get_nduizi()，line -- 222 出错')
        elif temp_size == -1:
            return duizi

    # 2.获得n个刻子
    def _get_nkezi(self, size):  # size 刻子的个数，
        print('提供刻子...')
        temp_size = size - 1
        kezi = np.zeros(shape=(temp_size + 1, 2), dtype='i1')  # 矩阵可以提供size个对子，用一个n行2列的矩阵来存储；第一列村line,第二列存row
        line = 0  # line 用来给刻zi矩阵赋值，
        for i in range(temp_size):
            for j in range(2):
                kezi[i][j] = -1  # 给刻子矩阵初试画一下，
        # 在un_show_count_array中寻找值为3的点，为其提供size的个数，
        for i in range(3):
            if temp_size == -1:
                break
            for j in range(9):
                if self.un_show_count[i][j] == 3:
                    kezi[line][0] = i
                    kezi[line][1] = j
                    line += 1  # 行数+1
                    self.matrix_un_show[0][temp_size][i][j] -= 3
                    temp_size -= 1  # 提供的对子个数-1
                    if temp_size == -1:
                        break
        # 如果为2的点不够size，再去找为4的点
        if temp_size >= 0:
            for i in range(3):
                if temp_size == -1:
                    break
                for j in range(9):
                    if self.un_show_count[i][j] == 4:
                        kezi[line][0] = i
                        kezi[line][1] = j
                        line += 1  # 行数+1
                        self.matrix_un_show[0][temp_size][i][j] -= 3
                        temp_size -= 1  # 提供的对子个数-1
                        if temp_size == -1:
                            break
        # 如果为4的点不够size，报错
        if temp_size >= 0:
            print('Error_dazhong_majiang,_get_nkezi()，line -- 267 出错')
        elif temp_size == -1:
            return kezi

    # 3.获得n个顺子
    def _get_nshunzi(self, size):  # size 顺子的个数
        print('提供顺子...')
        temp_size = size - 1
        shunzi = np.zeros(shape=(temp_size + 1, 6), dtype='i1')  # 矩阵可以提供size个对子，用一个n行2列的矩阵来存储；第一列村line,第二列存row
        line = 0  # line 用来给shunzi矩阵行数变化，
        for i in range(temp_size):
            for j in range(6):
                shunzi[i][j] = -1  # 给顺子矩阵初试画一下，
        # 直接从矩阵中值大于0的值，组成顺子
        for i in range(3):
            if temp_size == -1:
                break
            for j in range(9):
                if self.un_show_count[i][j] > 0:
                    if j == 0 and self.un_show_count[i][j + 1] > 0 and self.un_show_count[i][j + 2] > 0:
                        shunzi[line][0] = i
                        shunzi[line][1] = j  # 顺子第一张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j + 1  # 顺子第一张牌
                        shunzi[line][4] = i
                        shunzi[line][5] = j + 2  # 顺子第一张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1
                        self.matrix_un_show[0][temp_size][i][j + 1] -= 1  # 在未知矩阵中减掉这些值
                        self.matrix_un_show[0][temp_size][i][j + 2] -= 1
                        temp_size -= 1  # 需要顺子个数-1
                        if temp_size == -1:
                            break
                    elif j == 1:
                        shunzi[line][0] = i
                        shunzi[line][1] = j - 1  # 顺子第1张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j  # 顺子第2张牌
                        shunzi[line][4] = i
                        shunzi[line][5] = j + 1  # 顺子第3张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j - 1] -= 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1  # 在未知矩阵中减掉这些值
                        self.matrix_un_show[0][temp_size][i][j + 1] -= 1
                        temp_size -= 1  # 需要顺子个数
                        if temp_size == -1:
                            break
                    elif j > 1 and j < 8:
                        if self.un_show_count[i][j - 2] > 0 and self.un_show_count[i][j - 1] > 0:
                            shunzi[line][0] = i
                            shunzi[line][1] = j - 2  # 顺子第1张牌
                            shunzi[line][2] = i
                            shunzi[line][3] = j - 1  # 顺子第2张牌
                            shunzi[line][4] = i
                            shunzi[line][5] = j  # 顺子第3张牌
                            line += 1
                            self.matrix_un_show[0][temp_size][i][j] -= 1
                            self.matrix_un_show[0][temp_size][i][j - 1] -= 1  # 在未知矩阵中减掉这些值
                            self.matrix_un_show[0][temp_size][i][j - 2] -= 1
                            temp_size -= 1  # 需要顺子个数-1
                            if temp_size == -1:
                                break
                        elif self.un_show_count[i][j - 1] > 0 and self.un_show_count[i][j + 1] > 0:
                            shunzi[line][0] = i
                            shunzi[line][1] = j - 1  # 顺子第1张牌
                            shunzi[line][2] = i
                            shunzi[line][3] = j  # 顺子第2张牌
                            shunzi[line][4] = i
                            shunzi[line][5] = j + 1  # 顺子第3张牌
                            line += 1
                            self.matrix_un_show[0][temp_size][i][j - 1] -= 1
                            self.matrix_un_show[0][temp_size][i][j] -= 1  # 在未知矩阵中减掉这些值
                            self.matrix_un_show[0][temp_size][i][j + 1] -= 1
                            temp_size -= 1  # 需要顺子个数-1
                            if temp_size == -1:
                                break
                    elif j == 8 and self.un_show_count[i][j - 2] > 0 and self.un_show_count[i][j - 1] > 0:
                        shunzi[line][0] = i
                        shunzi[line][1] = j - 2  # 顺子第1张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j - 1  # 顺子第2张牌
                        shunzi[line][4] = i
                        shunzi[line][5] = j  # 顺子第3张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1
                        self.matrix_un_show[0][temp_size][i][j - 1] -= 1  # 在未知矩阵中减掉这些值
                        self.matrix_un_show[0][temp_size][i][j - 2] -= 1
                        temp_size -= 1  # 需要顺子个数-1
                        if temp_size == -1:
                            break
        if temp_size == -1:
            return shunzi
        elif temp_size >= 0:
            print('Error_get_shunzi line : 318')

    # 4.获得n个半顺子，e:12,13...
    def _get_nhalf_shunzi(self, size):  # size 半个顺子的个数，一个就够了
        print('提供半个顺子...')
        temp_size = size - 1
        shunzi = np.zeros(shape=(temp_size + 1, 4), dtype='i1')  # 矩阵可以提供size个对子，用一个n行2列的矩阵来存储；第一列村line,第二列存row
        line = 0  # line 用来给shunzi矩阵行数变化，
        for i in range(temp_size):
            for j in range(4):
                shunzi[i][j] = -1  # 给半个顺子矩阵初试画一下，
        # 直接从矩阵中找大于0的点
        for i in range(3):
            if temp_size == -1:
                break
            for j in range(9):
                if self.un_show_count[i][j] > 0:
                    if j == 0 and self.un_show_count[i][j + 1] > 0:
                        shunzi[line][0] = i
                        shunzi[line][1] = j  # 顺子第1张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j + 1  # 顺子第2张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1
                        self.matrix_un_show[0][temp_size][i][j + 1] -= 1  # 在未知矩阵中减掉这些值
                        temp_size -= 1  # 需要顺子个数-1
                        if temp_size == -1:
                            break
                    elif j == 0 and self.un_show_count[i][j + 2] > 0:
                        shunzi[line][0] = i
                        shunzi[line][1] = j  # 顺子第1张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j + 2  # 顺子第2张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1
                        self.matrix_un_show[0][temp_size][i][j + 2] -= 1
                        temp_size -= 1  # 需要顺子个数-1
                        if temp_size == -1:
                            break
                    elif j == 1 and self.un_show_count[i][j - 1] > 0:
                        shunzi[line][0] = i
                        shunzi[line][1] = j - 1  # 顺子第1张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j  # 顺子第2张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j - 1] -= 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1  # 在未知矩阵中减掉这些值
                        temp_size -= 1  # 需要顺子个数-1
                        if temp_size == -1:
                            break
                    elif j == 1 and self.un_show_count[i][j + 1] > 0:
                        shunzi[line][0] = i
                        shunzi[line][1] = j  # 顺子第1张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j + 1  # 顺子第2张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1
                        self.matrix_un_show[0][temp_size][i][j + 1] -= 1  # 在未知矩阵中减掉这些值
                        temp_size -= 1  # 需要顺子个数-1
                        if temp_size == -1:
                            break
                    elif j == 1 and self.un_show_count[i][j + 2] > 0:
                        shunzi[line][0] = i
                        shunzi[line][1] = j  # 顺子第1张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j + 2  # 顺子第2张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1
                        self.matrix_un_show[0][temp_size][i][j + 2] -= 1  # 在未知矩阵中减掉这些值
                        temp_size -= 1  # 需要顺子个数-1
                        if temp_size == -1:
                            break
                    elif j > 1 and j < 8:
                        if self.un_show_count[i][j - 1] > 0:
                            shunzi[line][0] = i
                            shunzi[line][1] = j - 1  # 顺子第1张牌
                            shunzi[line][2] = i
                            shunzi[line][3] = j  # 顺子第2张牌
                            line += 1
                            self.matrix_un_show[0][temp_size][i][j - 1] -= 1
                            self.matrix_un_show[0][temp_size][i][j] -= 1  # 在未知矩阵中减掉这些值
                            temp_size -= 1  # 需要顺子个数-1
                            if temp_size == -1:
                                break
                        elif self.un_show_count[i][j - 2] > 0:
                            shunzi[line][0] = i
                            shunzi[line][1] = j - 2  # 顺子第1张牌
                            shunzi[line][2] = i
                            shunzi[line][3] = j  # 顺子第2张牌
                            line += 1
                            self.matrix_un_show[0][temp_size][i][j - 2] -= 1
                            self.matrix_un_show[0][temp_size][i][j] -= 1  # 在未知矩阵中减掉这些值
                            temp_size -= 1  # 需要顺子个数-1 
                            if temp_size == -1:
                                break
                        elif self.un_show_count[i][j + 1] > 0:
                            shunzi[line][0] = i
                            shunzi[line][1] = j  # 顺子第1张牌
                            shunzi[line][2] = i
                            shunzi[line][3] = j + 1  # 顺子第2张牌
                            line += 1
                            self.matrix_un_show[0][temp_size][i][j] -= 1
                            self.matrix_un_show[0][temp_size][i][j + 1] -= 1
                            temp_size -= 1  # 需要顺子个数-1
                            if temp_size == -1:
                                break
                        elif self.un_show_count[i][j + 2] > 0:
                            shunzi[line][0] = i
                            shunzi[line][1] = j  # 顺子第1张牌
                            shunzi[line][2] = i
                            shunzi[line][3] = j + 2  # 顺子第2张牌
                            line += 1
                            self.matrix_un_show[0][temp_size][i][j] -= 1
                            self.matrix_un_show[0][temp_size][i][j + 2] -= 1  # 在未知矩阵中减掉这些值
                            temp_size -= 1  # 需要顺子个数-1
                            if temp_size == -1:
                                break
                    elif j == 8 and self.un_show_count[i][j - 2] > 0:
                        shunzi[line][0] = i
                        shunzi[line][1] = j - 2  # 顺子第1张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j  # 顺子第2张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j - 2] -= 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1  # 在未知矩阵中减掉这些值
                        temp_size -= 1  # 需要顺子个数-1
                        if temp_size == -1:
                            break
                    elif j == 8 and self.un_show_count[i][j - 1] > 0:
                        shunzi[line][0] = i
                        shunzi[line][1] = j - 1  # 顺子第1张牌
                        shunzi[line][2] = i
                        shunzi[line][3] = j  # 顺子第2张牌
                        line += 1
                        self.matrix_un_show[0][temp_size][i][j - 1] -= 1
                        self.matrix_un_show[0][temp_size][i][j] -= 1
                        temp_size -= 1  # 需要顺子个数-1
                        if temp_size == -1:
                            break
        if temp_size == -1:
            return shunzi
        elif temp_size >= 0:
            print('Error__gethalf_shunzi() line : 514')

    # 5.获得一张单排，去组对子
    def _get_nhalf_duizi(self, size):  # 单个的只可能要一个
        print('提供{}ge 半对子...'.format(size))
        temp_size = size - 1
        duizi = np.zeros(shape=(temp_size + 1, 2), dtype='i1')  # 矩阵可以提供size个单牌，用一个n行2列的矩阵来存储；第一列村line,第二列存row
        line = 0  # line 用来给shunzi矩阵行数变化，
        for i in range(size):
            for j in range(2):
                duizi[i][j] = -1  # 给单牌矩阵初试画一下，
        # 直接从未知矩阵中寻找值>0的值
        for i in range(3):
            if temp_size == -1:
                break
            for j in range(9):
                if self.un_show_count[i][j] > 0:
                    duizi[line][0] = i
                    duizi[line][1] = j  # 单牌
                    line += 1
                    self.matrix_un_show[0][temp_size][i][j] -= 1
                    temp_size -= 1  # 需要单牌个数-1
                    if temp_size == -1:
                        break
        if temp_size == -1:
            return duizi
        elif temp_size >= 0:
            print('Error_get_nhalf_single() line : 538')

    # 将要打的牌的line,row发过去，看一下该牌是否会胡,next_id,是第几个判断
    def _fire_hu(self, line, row, next_id):
        listener__id = self.listen__id
        print('帝豪：',listener__id)
        for i in range(len(listener__id)):
            if listener__id[i] == 0:
                fire_times = 0  # 统计点炮次数，大于1则换一张牌出
                for j in range(5):
                    print('对面0号听牌了，模拟的他的第{}种手牌矩阵是：'.format(j))
                    print(self.simulate_all_listener_possible[0][j])
                    self.simulate_all_listener_possible[0][j][line][row] += 1
                    is_hu, _ = self._check_hu(self.simulate_all_listener_possible[0][j])  # 把模拟的手牌传过去，看点炮否
                    if is_hu:  # 点炮去寻找下一个
                        fire_times += 1
                        print('可能点炮了，最好换一张牌出！')
                if fire_times > 0:
                    self.next[0][next_id] = 0  # 让寻找另一张牌打出的判断成立
                    self._del_ourself_drw()  # 再次运行该程序，诏另一张牌
            if listener__id[i] == 1:
                fire_times = 0  # 统计点炮次数，大于1则换一张牌出
                for j in range(5):
                    print('对面1号听牌了，模拟的他的第{}种手牌矩阵是：'.format(j))
                    print(self.simulate_all_listener_possible[1][j])
                    self.simulate_all_listener_possible[1][j][line][row] += 1
                    is_hu, _ = self._check_hu(self.simulate_all_listener_possible[1][j])  # 把模拟的手牌传过去，看点炮否
                    if is_hu:  # 点炮去寻找下一个
                        fire_times += 1
                        print('可能点炮了，最好换一张牌出！')
                if fire_times > 0:
                    self.next[0][next_id] = 0  # 让寻找另一张牌打出的判断成立
                    self._del_ourself_drw()  # 再次运行该程序，诏另一张牌
            if listener__id[i] == 2:
                fire_times = 0  # 统计点炮次数，大于1则换一张牌出
                for j in range(5):
                    print('对面2号听牌了，模拟的他的第{}种手牌矩阵是：'.format(j))
                    print(self.simulate_all_listener_possible[2][j])
                    self.simulate_all_listener_possible[2][j][line][row] += 1
                    is_hu, _ = self._check_hu(self.simulate_all_listener_possible[2][j])  # 把模拟的手牌传过去，看点炮否
                    if is_hu:  # 点炮去寻找下一个
                        fire_times += 1
                        print('可能点炮了，最好换一张牌出！')
                if fire_times > 0:
                    self.next[0][next_id] = 0  # 让寻找另一张牌打出的判断成立
                    self._del_ourself_drw()  # 再次运行该程序，诏另一张牌
            if listener__id[i] == 3:
                fire_times = 0  # 统计点炮次数，大于1则换一张牌出
                for j in range(5):
                    print('对面3号听牌了，模拟的他的第{}种手牌矩阵是：'.format(j))
                    print(self.simulate_all_listener_possible[3][j])
                    self.simulate_all_listener_possible[3][j][line][row] += 1
                    is_hu, _ = self._check_hu(self.simulate_all_listener_possible[3][j])  # 把模拟的手牌传过去，看点炮否
                    if is_hu:  # 点炮去寻找下一个
                        fire_times += 1
                        print('可能点炮了，最好换一张牌出！')
                if fire_times > 0:
                    self.next[0][next_id] = 0  # 让寻找另一张牌打出的判断成立
                    self._del_ourself_drw()  # 再次运行该程序，诏另一张牌
        print('line:655 _fire_hu():不会点炮放心出吧...')

    # 玩家摸牌后的或者吃碰之后的处理
    def _think_and_deal(self):
        '''
        处理自己的牌，并思考如何打什么牌
        :return:
        '''
        # 获得当前的手牌
        print('自己的程序运行了。。')
        now_hand_card1 = self.MessData['hand']
        print('deal_ourself当前的手牌是啥：', now_hand_card1)
        print('上一玩家出的牌是{}'.format(self.Now_Deal))
        # print('deal_ourself_out正在处理的牌是：', self.Now_Deal)
        # 当前的手牌矩阵
        now_hand_card = copy.deepcopy(self.StateData[self.player_seat, 0])
        # 判断接到该牌是否胡了
        is_hu, _ = self._check_hu(now_hand_card)
        logging.debug("胡牌判断：%s", is_hu)
        if is_hu:
            # 胡牌前看一下剩余牌的矩阵
            show_count = self.ShowCount
            # 初始化牌，每张牌都有四张
            total = np.zeros(shape=(4, 9), dtype='i1')
            for i in range(3):
                for j in range(9):
                    total[i][j] = 4
            un_show_count = total - show_count - self.StateData[self.player_seat, 0]
            print('输出当前未摸牌的矩阵：')
            print(un_show_count)
            self._conv_req_mess('Win', self.Now_Deal)
            return
        # 查看是否有人听牌，有人听牌，就开始模拟听牌玩家的手牌，然后判断点炮否？
        pass_history = self.MessData['history']
        had_listen = 0
        # 找出听牌的人，并在listen_id里面写出听牌的座位号0-3；
        for i in range(len(pass_history)):
            id = pass_history[i][0]
            if pass_history[i][2] == 'L':  # 该位置有听牌的
                if id == '0':
                    if self.player_seat != 0:
                        had_listen = 1  # 有人听牌，不是自己，小心点炮
                        break
                if id == '1':
                    if self.player_seat != 1:
                        had_listen = 1  # 有人听牌，不是自己，小心点炮
                        break
                if id == '2':
                    if self.player_seat != 2:
                        had_listen = 1  # 有人听牌，不是自己，小心点炮
                        break
                if id == '3':
                    if self.player_seat != 3:
                        had_listen = 1  # 有人听牌，不是自己，小心点炮
                        break
        if had_listen:
            self._get_linstener_history()
        # 暗杠
        can_gang, gang_count = self._check_gang(self.player_seat, is_self=True)
        if can_gang:
            self._conv_req_mess('Kon', self._get_card_str(gang_count[0][0], gang_count[0][1]) * 4, '')
            logging.debug(self.ReqMess)
            print("暗杠")
            return
        # 补杠
        pon_hand_card = self.MessData['pon_hand']
        print('输出当前的已经碰的牌是啥：', pon_hand_card)
        if pon_hand_card != "":
            can_gang, gang_count = self._check_gang(self.player_seat, is_self=False)
            if can_gang:
                self._conv_req_mess('Kon', self._get_card_str(gang_count[0][0], gang_count[0][1]) * 4, '')
                logging.debug(self.ReqMess)
                print("补杠")
                return
        # 遍历手牌矩阵，找到适合的牌输出
        for line in range(3):  # 0:B, 1:C, 2:D.
            for row in range(9):
                if row == 0 and now_hand_card[line][row] == 1 and now_hand_card[line][row + 1] == 0 and self.next[0][
                    0] == 1:  # 判断在最左侧的牌10
                    print('打出的牌是{}'.format(self._get_card_str(line, row)))
                    print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                    if had_listen:
                        self._fire_hu(line, row, 0)  # 检查下是否有点炮可能
                    self._conv_req_mess('Discard最左10', self._get_card_str(line, row), '')  # 那就直接输出
                    return
                elif row == 8 and now_hand_card[line][row] == 1 and now_hand_card[line][row - 1] == 0 and self.next[0][
                    1] == 1:  # 判断在最右侧的牌01
                    print('打出的牌是{}'.format(self._get_card_str(line, row)))
                    print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                    if had_listen:
                        self._fire_hu(line, row, 1)  # 检查下是否有点炮可能
                    self._conv_req_mess('Discard最右01', self._get_card_str(line, row), '')  # 那就直接输出改牌
                    return
                elif row > 0 and row < 8 and now_hand_card[line][row] == 1 and now_hand_card[line][row - 1] == 0 and \
                        now_hand_card[line][row + 1] == 0 and self.next[0][2] == 1:  # 010，标准单牌
                    print('打出的牌是{}'.format(self._get_card_str(line, row)))
                    print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                    if had_listen:
                        self._fire_hu(line, row, 2)  # 检查下是否有点炮可能
                    self._conv_req_mess('Discard两边010', self._get_card_str(line, row), '')  # 那就直接输出改牌
                    return
                # 判断对子，并找对子附近得牌打出
                elif now_hand_card[line][row] == 2:
                    if row == 0 and now_hand_card[line][row] == 2 and now_hand_card[line][row + 1] == 1 \
                            and now_hand_card[line][row + 2] == 0 and self.next[0][3] == 1:  # 112打出2
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row + 1))
                        if had_listen:
                            self._fire_hu(line, row + 1, 3)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard双边7889', self._get_card_str(line, row + 1), '')
                    elif row == 0 and now_hand_card[line][row] == 2 and now_hand_card[line][row + 1] == 1 and \
                            now_hand_card[line][row + 2] == 1 and now_hand_card[line][row + 3] == 0 and self.next[0][
                        4] == 1:  # 1123时打出 1
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row, 4)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard双边7889', self._get_card_str(line, row), '')  # 把1123打出去1变为123
                    elif row < 7 and row > 0 and now_hand_card[line][row] == 2 and now_hand_card[line][row - 1] == 1 and \
                            now_hand_card[line][row + 1] == 1 \
                            and now_hand_card[line][row + 2] == 0 and self.next[0][5] == 1:  # 双边对子1223
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row, 5)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard双边6778', self._get_card_str(line, row), '')  # 1223那就打2变为123
                        return
                    elif row == 7 and now_hand_card[line][row - 1] == 0 and now_hand_card[line][row] == 2 \
                            and now_hand_card[line][row + 1] == 1 and self.next[0][6] == 1:  # 889,打出9
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row + 1))
                        if had_listen:
                            self._fire_hu(line, row + 1, 6)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard双边6678', self._get_card_str(line, row + 1), '')  # 889打出9
                        return
                    elif row == 7 and now_hand_card[line][row - 2] == 0 and now_hand_card[line][row - 1] == 1 and \
                            now_hand_card[line][row] == 2 and now_hand_card[line][row + 1] == 1 and self.next[0][
                        7] == 1:
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row, 7)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard双边6678', self._get_card_str(line, row), '')  # 7889打出8变为789
                        return
                    elif row == 8 and now_hand_card[line][row - 1] == 1 and now_hand_card[line][row] == 2 and \
                            now_hand_card[line][row - 2] == 0 and self.next[0][8] == 1:  # 899,打出9
                        print('打出的牌是{}'.format(self._get_card_str(line, row - 1)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row - 1))
                        if had_listen:
                            self._fire_hu(line, row - 1, 8)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard双边6678', self._get_card_str(line, row - 1), '')  # 889打出9
                        return
                    elif row == 8 and now_hand_card[line][row - 3] == 0 and now_hand_card[line][row - 2] == 1 and \
                            now_hand_card[line][row - 1] == 1 and now_hand_card[line][row] == 2 and self.next[0][
                        9] == 1:  # 7899,打出9
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row, 9)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard双边6678', self._get_card_str(line, row), '')  # 7899打出9
                        return
                elif row == 0 and now_hand_card[line][row] == 1 and now_hand_card[line][row + 1] == 1 and \
                        now_hand_card[line][row + 2] == 1 \
                        and now_hand_card[line][row + 3] == 1 and now_hand_card[line][row + 4] == 1 and \
                        now_hand_card[line][row + 5] == 0 and self.next[0][10] == 1:  # 4连1234，再接一张5，打出5
                    print('打出的牌是{}'.format(self._get_card_str(line, row + 4)))
                    print('4+1,打1；；打出牌的位置是lin={},ro={}'.format(line, row + 4))
                    if had_listen:
                        self._fire_hu(line, row + 4, 10)  # 检查下是否有点炮可能
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row + 4), '')  # 12345没6接5，打5
                    return
                elif row == 1 and now_hand_card[line][row - 1] == 1 and now_hand_card[line][row] == 1 and \
                        now_hand_card[line][row + 1] == 1 and now_hand_card[line][row + 2] == 1 \
                        and now_hand_card[line][row + 3] == 1 and now_hand_card[line][row + 4] == 1 and \
                        now_hand_card[line][row + 5] == 0 and self.next[0][11] == 1:  # 4连2345，再接一张1，没6打出1
                    print('打出的牌是{}'.format(self._get_card_str(line, row - 1)))
                    print('4+1,打1；；打出牌的位置是lin={},ro={}'.format(line, row - 1))
                    if had_listen:
                        self._fire_hu(line, row - 1, 11)  # 检查下是否有点炮可能
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row - 1), '')  # 2345没6接1，打1
                    return
                elif row >= 1 and row <= 3 and now_hand_card[line][row] == 1 and now_hand_card[line][row + 1] == 1 and \
                        now_hand_card[line][row + 2] == 1 \
                        and now_hand_card[line][row + 3] == 1 and now_hand_card[line][row + 4] == 1 and \
                        now_hand_card[line][row + 5] == 0 and self.next[0][12] == 1:  # 4连2345，再接一张5，打出5
                    print('打出的牌是{}'.format(self._get_card_str(line, row + 4)))
                    print('4+1,打5；；打出牌的位置是lin={},ro={}'.format(line, row + 4))
                    if had_listen:
                        self._fire_hu(line, row + 4, 12)  # 检查下是否有点炮可能
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row + 4), '')  # 那就直接输出改牌
                    return
                elif row == 4 and now_hand_card[line][row - 1] == 0 and now_hand_card[line][row] == 1 and \
                        now_hand_card[line][row + 1] == 1 and now_hand_card[line][row + 2] == 1 \
                        and now_hand_card[line][row + 3] == 1 and now_hand_card[line][row + 4] == 1 and self.next[0][
                    13] == 1:  # 4连5678没4，再接一张9，打出5
                    print('打出的牌是{}'.format(self._get_card_str(line, row)))
                    print('4+1,打5；；打出牌的位置是lin={},ro={}'.format(line, row))
                    if had_listen:
                        self._fire_hu(line, row, 13)  # 检查下是否有点炮可能
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row), '')  # 5678，没4接9，打5
                    return
                elif row == 4 and now_hand_card[line][row - 2] == 0 and now_hand_card[line][row - 1] == 1 and \
                        now_hand_card[line][row] == 1 and now_hand_card[line][row + 1] == 1 and now_hand_card[line][
                    row + 2] == 1 \
                        and now_hand_card[line][row + 3] == 1 and now_hand_card[line][row + 4] == 0 and self.next[0][
                    14] == 1:  # 4连5678，没9，没3再接一张4，打出8
                    print('打出的牌是{}'.format(self._get_card_str(line, row + 3)))
                    print('4+1,打5；；打出牌的位置是lin={},ro={}'.format(line, row + 3))
                    if had_listen:
                        self._fire_hu(line, row + 3, 14)  # 检查下是否有点炮可能
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row + 3), '')  # 5678，没4，接4.打8
                    return
                elif row == 5 and now_hand_card[line][row - 2] == 0 and now_hand_card[line][row - 1] == 1 and \
                        now_hand_card[line][row] == 1 and now_hand_card[line][row + 1] == 1 and \
                        now_hand_card[line][row + 2] == 1 and now_hand_card[line][row + 3] == 1 and self.next[0][
                    15] == 1:  # 6789,没4，接5，打5
                    print('打出的牌是{}'.format(self._get_card_str(line, row - 1)))
                    print('4+1,打5；；打出牌的位置是lin={},ro={}'.format(line, row - 1))
                    if had_listen:
                        self._fire_hu(line, row - 1, 15)  # 检查下是否有点炮可能
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row - 1), '')  # 5678，没4，接4.打8
                    return
                elif row < 6 and now_hand_card[line][row] == 1 and now_hand_card[line][row + 3] == 1:  # 手牌1234
                    if now_hand_card[line][row + 1] == 2 and now_hand_card[line][row + 2] == 1 and self.next[0][
                        16] == 1:  # 手牌1234，接到2，打出1
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row, 16)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard4连（1234）接2', self._get_card_str(line, row), '')
                        return
                    elif now_hand_card[line][row + 1] == 1 and now_hand_card[line][row + 2] == 2 and \
                            now_hand_card[line][row + 3] == 0 and self.next[0][17] == 1:  # 手牌1234，接到3，打出4
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 3)))  # 1234,没5，接3打4
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row + 3, 17)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard4连（1234）接3', self._get_card_str(line, row + 3), '')
                        return
                elif row < 2 and now_hand_card[line][row] == 1 and now_hand_card[line][row + 1] == 1 and \
                        now_hand_card[line][row + 2] == 1 and \
                        now_hand_card[line][row + 3] == 1 and now_hand_card[line][row + 4] == 1 and now_hand_card[line][
                    row + 5] == 1 and \
                        now_hand_card[line][row + 6] == 1:
                    if now_hand_card[line][row + 7] == 1 and self.next[0][18] == 1:  # 测试这里B2B3B3B4B4B8B9B9
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 7)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row + 7, 18)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 7), '')  # 手牌1234567，接到一张8，打出8
                        return
                elif row < 3 and now_hand_card[line][row] == 1 and now_hand_card[line][row + 3] == 1 and \
                        now_hand_card[line][row + 6] == 1:  # 7连1234567
                    if now_hand_card[line][row + 1] == 2 and now_hand_card[line][row + 2] == 1 and now_hand_card[line][
                        row + 4] == 1 \
                            and now_hand_card[line][row + 5] == 1 and self.next[0][19] == 1:
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row, 19)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row), '')  # 手牌1234567，接到一张2，打出1
                        return
                    elif now_hand_card[line][row + 1] == 1 and now_hand_card[line][row + 2] == 2 and \
                            now_hand_card[line][row + 4] == 1 \
                            and now_hand_card[line][row + 5] == 1 and self.next[0][20] == 1:
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 3)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row + 3, 20)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 3), '')  # 手牌1234567，接到一张3，打出4
                        return
                    elif now_hand_card[line][row + 1] == 1 and now_hand_card[line][row + 2] == 1 and \
                            now_hand_card[line][row + 4] == 2 \
                            and now_hand_card[line][row + 5] == 1 and self.next[0][21] == 1:
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 3)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        if had_listen:
                            self._fire_hu(line, row + 3, 21)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 3), '')  # 手牌1234567，接到一张5，打出4
                        return
                    elif now_hand_card[line][row + 1] == 1 and now_hand_card[line][row + 2] == 1 and \
                            now_hand_card[line][row + 4] == 1 \
                            and now_hand_card[line][row + 5] == 2 and self.next[0][22] == 1:
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 6)))
                        if had_listen:
                            self._fire_hu(line, row + 6, 22)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 6), '')  # 手牌1234567，接到一张6，打出7
                        return
                elif now_hand_card[line][row] == 3:  # 打出刻子31旁边的1这章单牌
                    if row == 0 and now_hand_card[line][row + 1] == 1 and now_hand_card[line][row + 2] == 0 and \
                            self.next[0][23] == 1:  # 1112打出2
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row + 1))
                        if had_listen:
                            self._fire_hu(line, row + 1, 23)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 1), '')  # 手牌2223打出2
                        return
                    elif row < 7 and row > 0 and now_hand_card[line][row + 1] == 1 and now_hand_card[line][
                        row + 2] == 0 and self.next[0][24] == 1:  # 122
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row + 1))
                        if had_listen:
                            self._fire_hu(line, row + 1, 24)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 1), '')  # 手牌2223打出3
                        return
                    elif row == 1 and now_hand_card[line][row - 1] == 1 and self.next[0][25] == 1:  # 1222,打出1
                        print('打出的牌是{}'.format(self._get_card_str(line, row - 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row - 1))
                        if had_listen:
                            self._fire_hu(line, row - 1, 25)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row - 1), '')  # 手牌1222打出3
                        return
                    elif row == 1 and now_hand_card[line][row + 1] == 1 and now_hand_card[line][row + 2] == 0 and \
                            self.next[0][26] == 1:
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row + 1))
                        if had_listen:
                            self._fire_hu(line, row + 1, 26)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 1), '')  # 手牌1222打出3
                        return
                    elif row < 7 and row > 1 and now_hand_card[line][row + 1] == 0 and now_hand_card[line][row - 1] == 1 \
                            and now_hand_card[line][row - 2] == 0 and self.next[0][27] == 1:  # 2333
                        print('打出的牌是{}'.format(self._get_card_str(line, row - 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row - 1))
                        if had_listen:
                            self._fire_hu(line, row - 1, 27)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row - 1), '')  # 手牌#2333打出2
                        return
                    elif row == 7:  # 手牌7888，8889打出7 或者9  /  8999 打出8
                        if now_hand_card[line][row - 2] == 0 and now_hand_card[line][row - 1] == 1 and self.next[0][
                            28] == 1:
                            print('打出的牌是{}'.format(self._get_card_str(line, row - 1)))
                            print('打出牌的位置是lin={},ro={}'.format(line, row - 1))
                            if had_listen:
                                self._fire_hu(line, row - 1, 28)  # 检查下是否有点炮可能
                            self._conv_req_mess('Discard', self._get_card_str(line, row - 1), '')  # 手牌8999打出8
                            return
                        elif now_hand_card[line][row - 2] == 0 and now_hand_card[line][row + 1] == 1 and self.next[0][
                            29] == 1:
                            print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                            print('打出牌的位置是lin={},ro={}'.format(line, row + 1))
                            if had_listen:
                                self._fire_hu(line, row + 1, 29)  # 检查下是否有点炮可能
                            self._conv_req_mess('Discard', self._get_card_str(line, row + 1), '')  # 手牌8889打出9
                            return
                    elif row == 8 and now_hand_card[line][row - 2] == 0 and now_hand_card[line][row - 1] == 1 and \
                            self.next[30] == 1:  # 8999打出8
                        print('打出的牌是{}'.format(self._get_card_str(line, row - 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row - 1))
                        if had_listen:
                            self._fire_hu(line, row - 1, 30)  # 检查下是否有点炮可能
                        self._conv_req_mess('Discard', self._get_card_str(line, row - 1), '')  # 手牌8889打出9
                        return
                # 如果这些都没有那就得在补充了

    def _del_other_out(self):
        '''
        处理对手玩家打牌
        :return:
        '''
        temp_hand_count = copy.deepcopy(self.StateData[self.player_seat, 0])
        # print('deal_other_out输出当前手牌的矩阵：')
        # print( temp_hand_count)
        line, row = self._get_card_index(self.Now_Deal)
        print('Now_Deal: line = {},row = {}'.format(line, row))
        # print('输出下line ={},row={}'.format(line,row))
        temp_hand_count[line, row] += 1
        print('line row 位置上的值是：', temp_hand_count[line][row])
        print(temp_hand_count)
        print('deal_outher_out正在处理的牌是：', self.Now_Deal)
        is_hu, _ = self._check_hu(temp_hand_count)
        logging.debug("胡牌判断：%s", is_hu)
        if is_hu:
            self._conv_req_mess('Win', self.Now_Deal)
            return
        try:
            can_gang, gang_count = self._check_gang(self.player_seat, is_self=False)
            if can_gang:  # 补扛
                self._conv_req_mess('Kon', self._get_card_str(gang_count[0][0], gang_count[0][1]) * 4, '')
                logging.debug(self.ReqMess)
                return
            can_pen, pen_count = self._check_peng(self.player_seat)
            if can_pen:
                self._conv_req_mess('Pon', self._get_card_str(pen_count[0][0], pen_count[0][1]) * 3, '')
                logging.debug(self.ReqMess)
                return
            can_chi, chi_count = self._check_chi(self.player_seat)
            logging.debug(chi_count)
            if can_chi:
                action_index = self._get_card_cod(chi_count[0][0], chi_count[0][1])
                logging.debug(action_index)
                # 对子  刻子 旁边不吃  分别判断三个位置，
                '''
                print('row == 0')
                if row == 0 and (temp_hand_count[line][row+1] == 2 and temp_hand_count[line][row+2] == 2) or (temp_hand_count[line][row+1] == 3 and temp_hand_count[line][row+2] == 3 ):  #2233，不能吃1
                    self._conv_req_mess('Pass1', '', '')   #2233，不能吃1
                    return
                print('row == 1')
                if row == 1 and (temp_hand_count[line][row-1] == 2 and temp_hand_count[line][row+1] == 2 ) or \
                    temp_hand_count[line][row + 1] == 2 and temp_hand_count[line][row+2] == 2 or (temp_hand_count[line][row-1] == 3 and temp_hand_count[line][row+1] == 3 ) or \
                    temp_hand_count[line][row + 1] == 3 and temp_hand_count[line][row+2] == 3:  #11233 不吃2 23344,不吃2
                    self._conv_req_mess('Pass2', '', '')    #1133 不吃2 23344，不吃2
                    return
                print('row  >=2 row <= 6')
                if row >= 2 and row <= 6 and temp_hand_count[line][row-2] == 0 and temp_hand_count[line][row-1] == 0 and temp_hand_count[line][row+1] == 0 and  ( temp_hand_count[line][row-2] == 2 \
                  and temp_hand_count[line][row-1] == 2 or temp_hand_count[line][row-1] == 2 and temp_hand_count[line][row+1] == 2\
                  or temp_hand_count[line][row+1] == 2 and temp_hand_count[line][row+2] == 2 ) or ( temp_hand_count[line][row-2] == 3 \
                  and temp_hand_count[line][row-1] == 3 or temp_hand_count[line][row-1] == 3 and temp_hand_count[line][row+1] == 3\
                  or temp_hand_count[line][row+1] == 3 and temp_hand_count[line][row+2] == 3 ):  #1122,不吃3，34455，不吃3...56677，不吃5，55667，不吃7
                     self._conv_req_mess('Pass3', '', '')  # 56677不吃5；55677不吃6；55667不吃7；
                     return
                print('row == 7')
                if row == 7 and temp_hand_count[line][row-1] == 2 and temp_hand_count[line][row+1] == 2 or temp_hand_count[line][row-2] == 2 and \
                     temp_hand_count[line][row-1] == 2 or temp_hand_count[line][row-1] == 3 and temp_hand_count[line][row+1] == 3 or temp_hand_count[line][row-2] == 3 and \
                     temp_hand_count[line][row-1] == 3: #77899不吃8，66778,不吃8
                    self._conv_req_mess('Pass4', '', '')  #77899不吃8，
                    return
                print('row == 8')
                if row == 8 and temp_hand_count[line][row-2] == 2 and temp_hand_count[line][row-1] == 2 or \
                        temp_hand_count[line][row-2] == 3 and temp_hand_count[line][row-1] == 3:
                    self._conv_req_mess('Pass5', '', '') #77889不吃9
                    return
                '''
                line1, row1 = self._get_card_index(index_chi[action_index][0:2])
                line2, row2 = self._get_card_index(index_chi[action_index][2:4])
                line3, row3 = self._get_card_index(index_chi[action_index][4:6])
                if (temp_hand_count[line1, row1] == 2 and temp_hand_count[line2, row2] == 2) or (
                        temp_hand_count[line1, row1] == 2 and temp_hand_count[line3, row3] == 2) or (
                        temp_hand_count[line2, row2] == 2 and temp_hand_count[line3, row3] == 2) or temp_hand_count[
                    line1, row1] == 3 or temp_hand_count[line2, row2] == 3 or temp_hand_count[line3, row3] == 3:
                    self._conv_req_mess('Pass', '', '')
                    return
                self._conv_req_mess('Chow', index_chi[action_index], '')
                return
            self._conv_req_mess('Pass6', '', '')
        except:
            logging.error("消息处理失败")


if __name__ == "__main__":
    import json

    # 用字典测试  dealer:庄家  seat:玩家座号 0,discard,B2
    test_str = {"pon_hand": "", "kon_hand": "", "chow_hand": "", "hand": "C1C1C1C6C6C6D4D4D4B2B2B5B5B8",
                "history": ['0,Discard,B1', '1,Discard,B4', '2,Pon,D1D1D1', '3,Discard,D8',
                            '0,Discard,B2', '1,Discard,B4', '2,Pon,D2D2D2', '3,Discard,D8',
                            '0,Discard,B3', '1,Discard,B4', '2,Pon,D3D3D3', '3,Discard,D8',
                            '0,Discard,B4', '1,Listen,C5', '2,Pon,D4D4D4', '3,Discard,D8'
                            ],
                "dealer": 0, "seat": 3, "special": ""}
    test = Pubilc_MahJong(json.dumps(test_str))
    Req_Mess = test.get_game_req()
    print('看下Req_Mess是啥：', Req_Mess)
