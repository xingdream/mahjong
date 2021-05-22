# -*- coding: utf-8 -*- 
# @Time    : 2020/4/2 10:04
# @Author  : WangHong 
# @FileName: dazhong_mahjong.py
# @Software: PyCharm
import time

from src.mahjong_no_state import *
import random


class Pubilc_MahJong(MahJong_NO_State_Base):
    '''
    二人麻将无状态AI，第一版本
    '''
    def __init__(self, mess_data):
        super(Pubilc_MahJong, self).__init__(mess_data)
        self.simulate_random_shou = np.zeros(shape=(4, 10, 4, 9), dtype='i1')  # 随机模拟5副可听牌的手牌
        print("我自己程序开始运行")
        self._ai_del_logic()

    def _ai_del_logic(self):
        '''
        ai的处理逻辑
        :return:
        '''
        # 判断自己是否为庄家 若是直接调用出牌
        now_hand_card = self.MessData['hand']
        print('输出当前的手牌是啥：', now_hand_card)
        # print('当前接到得牌是{}'.format(self.Now_Deal))
        # if self.Now_Deal == []:
        #     self._del_ourself_drw()

        card_num = self.StateData[self.player_seat, 0].sum()
        # 天听动作
        if card_num == 13 and self.is_tting:
            is_can_tting, ting_result = self._check_ting(self.player_seat, t_ting=True)
            # 如果可以天听，并且天听的牌的种类超过两种就天听
            if is_can_tting:
                print("天听")
                for key in ting_result.keys():
                    self._conv_req_mess('Listen', key, '')
                    return
            else:
                self._conv_req_mess('Pass', '', '')
        # 自己摸牌，从最后的牌开始打
        elif card_num % 3 == 2:
            print("自己打牌")
            self._del_ourself_drw()
            print("自己打牌后判断是否听牌")
            is_can_tting, ting_result = self._check_ting(self.player_seat, t_ting=False)
            print("ting_result:", ting_result)
            # 听牌有效数 选择最大有效数听牌
            if is_can_tting:
                print("ting_result.keys:", ting_result.keys())
                # print(type(ting_result))
                ting_card_lis = list(ting_result)
                print('ting_card_lis:', ting_card_lis)
                max_len = []
                max_key = ' '
                num = 0
                show_num = 0
                for i in range(len(ting_result)):
                    show_num = 0
                    print(ting_result[ting_card_lis[i]])
                    for j in range(len(ting_result[ting_card_lis[i]])):
                        line, row = self._get_card_index(ting_result[ting_card_lis[i]][j])
                        show_num += self.ShowCount[line, row]
                        print('%d%d已经打的牌数为%d张' % (line, row, self.ShowCount[line, row]))
                        print('ting_result[ting_card_lis[%d]]即%d,%d已经打出去的牌数是%d' % (i,line, row, show_num))
                    num = 4*len(ting_result[ting_card_lis[i]]) - show_num
                    max_len.append(num)
                print('听牌有效数列表',max_len)
                for i in range(len(ting_result)):
                    index = max_len.index(max(max_len))
                    max_key = ting_card_lis[index]
                    # if len(ting_result[ting_card_lis[i]]) > max_len:
                    #     max_len = len(ting_result[ting_card_lis[i]])
                    #     max_key = ting_card_lis[i]
                # 听牌有效数小于2放弃停牌
                if max_len[index] < 2:
                    self._conv_req_mess('Pass', '', '')
                    return
                print("max_key:", max_key)
                self._conv_req_mess('Listen', max_key, '')
                return

                # for key in ting_result.keys():
                #     self._conv_req_mess('Listen', key, '')
                #     return
            print("别人打牌")
            # discard_history = self.MessData['history']
            # print('已经打出去的牌是：', discard_history)
            # if len(discard_history) > 1:
            #     print("判杠")
            #     self._check_gang(self.player_seat, is_self=False)
            #     print("判碰")
            #     self._check_peng(self.player_seat)
            #     return

        # 对手打牌
        elif card_num % 3 == 1:
            self._del_other_out()
            # print("判杠")
            # self._check_gang(self.player_seat, is_self=False)
            # print("判碰")
            # self._check_peng(self.player_seat)
            # print("判吃")
            # self._check_chi(self.player_seat)
            return
        else:
            logging.error("相公")
            self._conv_req_mess('相公了', 'Self')

    def _del_ourself_drw(self):
        '''
        处理自己的摸牌动作
        :return:
        '''
        hand_array = copy.deepcopy(self.StateData[self.player_seat, 0])

        hand_array_chow = copy.deepcopy(self.StateData[self.player_seat, 1])
        hand_array_pon = copy.deepcopy(self.StateData[self.player_seat, 2])
        hand_array_kon = copy.deepcopy(self.StateData[self.player_seat, 3])
        # print('已经吃的牌是\n', hand_array_chow)
        # print('已经碰的牌是\n', hand_array_pon)
        # print('已经杠的牌是\n', hand_array_kon)
        pon_hand_card = self.MessData['pon_hand']
        print('输出当前已经碰的牌是啥：', pon_hand_card)
        chow_hand_card = self.MessData['chow_hand']
        print('输出当前已经吃的牌是啥：', chow_hand_card)
        kon_hand_card = self.MessData['kon_hand']
        print('输出当前已经杠的牌是啥：', kon_hand_card)

        # if self.Now_Deal != {}:
        #     line, row = self._get_card_index(self.Now_Deal)
        #     print(line, row)
        hand_array_cupple = []
        hand_array_triplet = []
        # 手牌中对子刻子个数
        for i in range(3):
            for j in range(9):
                if hand_array[i, j] == 2:
                    hand_array_cupple.append([i, j])
                if hand_array[i, j] == 3:
                    hand_array_triplet.append([i, j])

        is_hu, _ = self._check_hu(hand_array)
        logging.debug("胡牌判断：%s", is_hu)
        # 先判断是否可以自摸
        if is_hu:
            print("我糊了")
            self._conv_req_mess('Win', self.Now_Deal)
            return
        # 不能自摸先判断是否可以杠
        try:
            # 对子数大于等于5寻求7对胡牌       应该是要加吃碰牌为空判断
            if len(hand_array_cupple)<5 and pon_hand_card!="" and chow_hand_card!="":
                can_gang, gang_count = self._check_gang(self.player_seat, is_self=True)
                # 暗杠
                if can_gang:
                    self._conv_req_mess('Kon', self._get_card_str(gang_count[0][0], gang_count[0][1]) * 4, '')
                    logging.debug(self.ReqMess)
                    print("暗杠")
                    return
                # 补杠
                if pon_hand_card != "":
                    can_gang, gang_count = self._check_gang(self.player_seat, is_self=True)
                    if can_gang:
                        self._conv_req_mess('Kon', self._get_card_str(gang_count[0][0], gang_count[0][1]) * 4, '')
                        logging.debug(self.ReqMess)
                        print("补杠")
                        return

            # 然后整理牌面 做出弃牌选择后再判断是否可以听
            hand_array_else_first = []
            hand_array_else_second = []
            hand_array_else_third = []
            hand_array_else_last = []

            discard_history = self.ShowCount - hand_array
            print('已经打出去的牌是\n', discard_history)
            # chow_hand_card = self.MessData['chow_hand']
            # print('输出当前的已经吃的牌是啥：', chow_hand_card)

            # 杂牌第一优先级 单张左右两位置都为0
            for i in range(3):
                if hand_array[i,0]==1 and hand_array[i,1]==0 and hand_array[i,2]==0:
                    hand_array_else_first.append([i, 0])
                if hand_array[i,8]==1 and hand_array[i,7]==0 and hand_array[i,6]==0:
                    hand_array_else_first.append([i, 8])
                if hand_array[i,1]==1 and hand_array[i,0]==0 and hand_array[i,2]==0 and hand_array[i,3]==0:
                    hand_array_else_first.append([i, 1])
                if hand_array[i,7]==1 and hand_array[i,8]==0 and hand_array[i,6]==0 and hand_array[i,5]==0:
                    hand_array_else_first.append([i, 7])
            for x in range(3):
                for j in range(2,7):
                    if hand_array[x,j]==1 and hand_array[x,j-2]==0 and hand_array[x,j-1]==0 and hand_array[x,j+1]==0 and hand_array[x,j+2]==0:
                        hand_array_else_first.append([x,j])

            # 第二优先级 单张间距1位置0 间距2位置1
            for j in range(3):
                # 679 6779
                if hand_array[j,8]==1 and hand_array[j,7]==0 and hand_array[j,6]!=0 and hand_array[j,5]==1:
                    hand_array_else_second.append([j, 8])
                # 689 6889
                if hand_array[j,8]==1 and hand_array[j,7]!=0 and hand_array[j,6]==0 and hand_array[j,5]==1:
                    hand_array_else_second.append([j, 8])
                # 134 1334
                if hand_array[j,0]==1 and hand_array[j,1]==0 and hand_array[j,2]!=0 and hand_array[j,3]==1:
                    hand_array_else_second.append([j, 0])
                # 124 1224
                if hand_array[j,0]==1 and hand_array[j,1]!=0 and hand_array[j,2]==0 and hand_array[j,3]==1:
                    hand_array_else_second.append([j, 0])
                # 123400
                if hand_array[j,0]==1 and hand_array[j,1]==1 and hand_array[j,2]==1 and hand_array[j,3]==1 and hand_array[j,4]==0 and hand_array[j,5]==0:
                    hand_array_else_second.append([j, 0])
                # 987600
                if hand_array[j,8]==1 and hand_array[j,7]==1 and hand_array[j,6]==1 and hand_array[j,5]==1 and hand_array[j,4]==0 and hand_array[j,3]==0:
                    hand_array_else_second.append([j, 8])

                # 103,120
                if (hand_array[j,0]==1 and hand_array[j,1]==0 and hand_array[j,2]==1) or (hand_array[j,0]==1 and hand_array[j,1]==1 and hand_array[j,2]==0):
                    hand_array_else_second.append([j, 0])
                # 907,980
                if (hand_array[j,8]==1 and hand_array[j,7]==0 and hand_array[j,6]==1) or (hand_array[j,8]==1 and hand_array[j,7]==1 and hand_array[j,6]==0):
                    hand_array_else_second.append([j, 8])

            for i in range(3):
                if len(hand_array_cupple) > 1:
                    #  1223和7889打2和8
                    if hand_array[i,0]==1 and hand_array[i,1]==2 and hand_array[i,2]==1 and hand_array[i,3]==0:
                        hand_array_else_second.append([i,1])
                    if hand_array[i,8]==1 and hand_array[i,7]==2 and hand_array[i,6]==1 and hand_array[i,5]==0:
                        hand_array_else_second.append([i,7])

            for i in range(3):
                # (1) 2450,24450or2455
                if (hand_array[i, 1]==1 and hand_array[i, 2]==0 and hand_array[i, 3]!=0 and hand_array[i, 4]==1 and hand_array[i, 0]!=1) or (hand_array[i, 1]==1 and hand_array[i, 2]==0 and hand_array[i, 3]==1 and hand_array[i, 4]!=0 and hand_array[i, 0]!=1):
                    hand_array_else_second.append([i, 1])
                # 5680,56680,55680 (1)
                if (hand_array[i, 7]==1 and hand_array[i, 6]==0 and hand_array[i, 5]!=0 and hand_array[i, 4]==1 and hand_array[i, 8]!=1) or (hand_array[i, 7]==1 and hand_array[i, 6]==0 and hand_array[i, 5]==1 and hand_array[i, 4]!=0 and hand_array[i, 8]!=1):
                    hand_array_else_second.append([i, 7])
            for i in range(3):
                # 00356,3556,3566(1)-00578,5778,5788(1)
                for j in range(2,5):
                    if (hand_array[i, j]==1 and hand_array[i, j+1]==0 and hand_array[i, j+2]!=0 and hand_array[i, j+3]==1 and hand_array[i, j+4]!=1 and hand_array[i, j-1]==0 and hand_array[i, j-2]==0) or (hand_array[i, j]==1 and hand_array[i, j+1]==0 and hand_array[i, j+2]==1 and hand_array[i, j+3]!=0 and hand_array[i, j+4]!=1 and hand_array[i, j-1]==0 and hand_array[i, j-2]==0):
                        hand_array_else_second.append([i, j])
                # (1)235,2335,223500-(1)457,4557,445700
                for j in range(4,7):
                    if (hand_array[i, j]==1 and hand_array[i, j+1]==0 and hand_array[i, j+2]==0 and hand_array[i, j-1]==0 and hand_array[i, j-2]!=0 and hand_array[i, j-3]==1 and hand_array[i, j-4]!=1) or (hand_array[i, j]==1 and hand_array[i, j+1]==0 and hand_array[i, j+2]==0 and hand_array[i, j-1]==0 and hand_array[i, j-2]==1 and hand_array[i, j-3]!=0 and hand_array[i, j-4]!=1):
                        hand_array_else_second.append([i, j])

            # 从第三级最开始提上来 加的最后优先级对子间距1位置1 只能吃1个位置 1220,122345,133,1244,9880,988765,977,9866
            for j in range(3):
                if hand_array[j, 1] == 2 and hand_array[j, 0] == 1 and hand_array[j, 2] == 0:
                    hand_array_else_second.append([j, 0])
                if hand_array[j,0]==1 and hand_array[j,1]==2 and hand_array[j,2]==1 and hand_array[j,3]==1 and hand_array[j,4]==1:
                    hand_array_else_second.append([j, 0])
                if hand_array[j,0]==1 and hand_array[j,1]==0 and hand_array[j,2]==2:
                    hand_array_else_second.append([j, 0])
                if hand_array[j,1]==1 and hand_array[j,2]==0 and hand_array[j,3]==2 and hand_array[j,0]==1:
                    hand_array_else_second.append([j, 0])
                if hand_array[j, 7] == 2 and hand_array[j, 8] == 1 and hand_array[j, 6] == 0:
                    hand_array_else_second.append([j, 8])
                if hand_array[j,8]==1 and hand_array[j,7]==2 and hand_array[j,6]==1 and hand_array[j,5]==1 and hand_array[j,4]==1:
                    hand_array_else_second.append([j, 8])
                # 779,6689
                if hand_array[j, 8] == 1 and hand_array[j, 7] == 0 and hand_array[j, 6] == 2:
                    hand_array_else_second.append([j, 8])
                if hand_array[j, 8] == 1 and hand_array[j, 7] == 1 and hand_array[j, 6] == 0 and hand_array[j, 5] == 2:
                    hand_array_else_second.append([j, 8])

            for i in range(3):
                # 第三优先级提上来的  12230和07889打2和8
                if hand_array[i,0]==1 and hand_array[i,1]==2 and hand_array[i,2]==1 and hand_array[i,3]==0:
                    hand_array_else_second.append([i,1])
                if hand_array[i,8]==1 and hand_array[i,7]==2 and hand_array[i,6]==1 and hand_array[i,5]==0:
                    hand_array_else_second.append([i,7])

            for i in range(3):
                # 刻子旁边的单牌
                # 1222和8889单列
                if hand_array[i,0]==1 and hand_array[i,1]==3 and hand_array[i,2]!=1:
                    hand_array_else_second.append([i,0])
                if hand_array[i,8]==1 and hand_array[i,7]==3 and hand_array[i,6]!=1:
                    hand_array_else_second.append([i,8])
                # 1333和7779单列
                if hand_array[i,0]==1 and hand_array[i,1]!=1 and hand_array[i,2]==3:
                    hand_array_else_second.append([i,0])
                if hand_array[i,8]==1 and hand_array[i,7]!=1 and hand_array[i,6]==3:
                    hand_array_else_second.append([i,8])
                # 02333
                if hand_array[i,0]==0 and hand_array[i,1]==1 and hand_array[i,2]==3:
                    hand_array_else_second.append([i,1])
                # 77780
                if hand_array[i,8]==0 and hand_array[i,7]==1 and hand_array[i,6]==3:
                    hand_array_else_second.append([i,7])
            for i in range(3):
                # 003444-008999
                for j in range(2, 8):
                    if hand_array[i,j]==1 and hand_array[i,j+1]==3 and hand_array[i,j-1]==0 and hand_array[i,j-2]==0:
                            hand_array_else_second.append([i,j])
                # 111200-666700
                for j in range(1, 7):
                    if hand_array[i,j]==1 and hand_array[i,j-1]==3 and hand_array[i,j+1]==0 and hand_array[i,j+2]==0:
                            hand_array_else_second.append([i,j])
                # 020444-070999
                for j in range(1, 7):
                    if hand_array[i,j]==1 and hand_array[i,j+1]==0 and hand_array[i,j+2]==3 and hand_array[i,j-1]==0:
                            hand_array_else_second.append([i,j])
                # 111030-666080
                for j in range(2, 8):
                    if hand_array[i,j]==1 and hand_array[i,j-1]==0 and hand_array[i,j-2]==3 and hand_array[i,j+1]==0:
                        hand_array_else_second.append([i, j])

            for i in range(3):
                # 2456(0/2)-4678(0/2)
                for j in range(1,4):
                    if hand_array[i, j]==1 and hand_array[i, j+1]==0 and hand_array[i, j+2]==1 and hand_array[i, j+3]==1 and hand_array[i, j+4]==1 and hand_array[i, j+5]!=1:
                        hand_array_else_second.append([i, j])
                # 8654(0/2)-6432(0/2)
                for j in range(7,4,-1):
                    if hand_array[i, j]==1 and hand_array[i, j-1]==0 and hand_array[i, j-2]==1 and hand_array[i, j-3]==1 and hand_array[i, j-4]==1 and hand_array[i, j-5]!=1:
                        hand_array_else_second.append([i, j])

            for i in range(3):
                # 005789or123500
                if (hand_array[i,4]==1 and hand_array[i,5]==0 and hand_array[i,6]==1 and hand_array[i,7]==1 and hand_array[i,8]==1 and hand_array[i,3]==0 and hand_array[i,2]==0) or (hand_array[i,4]==1 and hand_array[i,3]==0 and hand_array[i,2]==1 and hand_array[i,1]==1 and hand_array[i,0]==1 and hand_array[i,5]==0 and hand_array[i,6]==0):
                    hand_array_else_second.append([i,5])

            for i in range(3):
                # 00356,3556,3566-00578,5778,5788
                for j in range(2,5):
                    if (hand_array[i, j]==1 and hand_array[i, j+1]==0 and hand_array[i, j+2]!=0 and hand_array[i, j+3]==1 and hand_array[i, j-1]==0 and hand_array[i, j-2]==0) or (hand_array[i, j]==1 and hand_array[i, j+1]==0 and hand_array[i, j+2]==1 and hand_array[i, j+3]!=0 and hand_array[i, j-1]==0 and hand_array[i, j-2]==0):
                        hand_array_else_second.append([i, j])
                # 235,2335,223500-457,4557,445700
                for j in range(4,7):
                    if (hand_array[i, j]==1 and hand_array[i, j+1]==0 and hand_array[i, j+2]==0 and hand_array[i, j-1]==0 and hand_array[i, j-2]!=0 and hand_array[i, j-3]==1) or (hand_array[i, j]==1 and hand_array[i, j+1]==0 and hand_array[i, j+2]==0 and hand_array[i, j-1]==0 and hand_array[i, j-2]==1 and hand_array[i, j-3]!=0):
                        hand_array_else_second.append([i, j])

            for i in range(3):
                # 0204
                if hand_array[i,1]==1 and hand_array[i,0]==0 and hand_array[i,2]==0 and hand_array[i,3]==1:
                    hand_array_else_second.append([i, 1])
                # 0806
                if hand_array[i,7]==1 and hand_array[i,8]==0 and hand_array[i,6]==0 and hand_array[i,5]==1:
                    hand_array_else_second.append([i, 7])

            for i in range(3):
                # (2)0305-(2)0709
                for j in range(2, 7):
                    if hand_array[i,j]==1 and hand_array[i,j+1]==0 and hand_array[i,j+2]==1 and hand_array[i,j-1]==0 and hand_array[i,j-2]!=2:
                        hand_array_else_second.append([i,j])
                # (2)0705-(2)0402
                for j in range(6, 3, -1):
                    if hand_array[i,j]==1 and hand_array[i,j+1]==0 and hand_array[i,j+2]!=2 and hand_array[i,j-1]==0 and hand_array[i,j-2]==1:
                        hand_array_else_second.append([i,j])

                # 023340-067780 连上面# 第三优先级提上来的  12230和07889打2和8
                # for j in range(2, 7):
                #     if hand_array[i,j]==2 and hand_array[i,j+1]==1 and hand_array[i,j+2]==0 and hand_array[i,j-1]==1 and hand_array[i,j-2]==0:
                #         hand_array_else_second.append([i, j])

            # 第三优先级 对子间距1位置0 间距2位置1  再加上最后优先级 133和122是等同优先级
            for i in range(3):
                # 加的最后优先级 11200
                if hand_array[i, 0] == 2 and hand_array[i, 1] == 1 and hand_array[i, 2] == 0 and hand_array[i,3]==0:
                    hand_array_else_third.append([i, 1])
                # 加的最后优先级 99800
                if hand_array[i, 8] == 2 and hand_array[i, 7] == 1 and hand_array[i, 6] == 0 and hand_array[i,5]==0:
                    hand_array_else_third.append([i, 7])

                # 6680
                if hand_array[i, 8] == 0 and hand_array[i, 7] == 1 and hand_array[i, 6] == 0 and hand_array[i, 5] == 2:
                    hand_array_else_third.append([i, 7])
                # 0244
                if hand_array[i,1]==1 and hand_array[i,2]==0 and hand_array[i,3]==2 and hand_array[i,0]==0:
                    hand_array_else_third.append([i, 1])

            # 0300-0700 or 0030-0070
            for x in range(3):
                for j in range(2, 7):
                    if (hand_array[x, j] == 1 and hand_array[x, j + 1] == 0 and hand_array[x, j + 2] == 0 and hand_array[x, j - 1] == 0) or (hand_array[x, j] == 1 and hand_array[x, j - 1] == 0 and hand_array[x, j - 2] == 0 and hand_array[x, j + 1] == 0):
                        hand_array_else_third.append([x, j])

            for i in range(3):
                # 0355
                if hand_array[i,2]==1 and hand_array[i,3]==0 and hand_array[i,4]==2 and hand_array[i,1]==0:
                    hand_array_else_third.append([i,2])
                # 5570
                if hand_array[i,4]==2 and hand_array[i,5]==0 and hand_array[i,6]==1 and hand_array[i,7]==0:
                    hand_array_else_third.append([i,6])
                # 0466-0799or123466-456799
                for j in range(3, 7):
                    if (hand_array[i,j]==1 and hand_array[i,j+1]==0 and hand_array[i,j+2]==2 and hand_array[i,j-1]==0) or (hand_array[i,j]==1 and hand_array[i,j+1]==0 and hand_array[i,j+2]==2 and hand_array[i,j-1]==1 and hand_array[i,j-2]==1 and hand_array[i,j-3]==1):
                            hand_array_else_third.append([i,j])
                # 1130-4460or113456-446789
                for j in range(0, 4):
                    if (hand_array[i,j]==2 and hand_array[i,j+1]==0 and hand_array[i,j+2]==1 and hand_array[i,j+3]==0) or (hand_array[i,j]==2 and hand_array[i,j+1]==0 and hand_array[i,j+2]==1 and hand_array[i,j+3]==1 and hand_array[i,j+4]==1 and hand_array[i,j+5]==1):
                            hand_array_else_third.append([i,j+2])

            for i in range(3):
                # 11230,07899
                if hand_array[i,0]==2 and hand_array[i,1]==1 and hand_array[i,2]==1 and hand_array[i,3]==0:
                    hand_array_else_third.append([i,0])
                if hand_array[i,8]==2 and hand_array[i,7]==1 and hand_array[i,6]==1 and hand_array[i,5]==0:
                    hand_array_else_third.append([i,8])
            for i in range(3):
                # 0678899 067880
                if hand_array[i,8]!=1 and hand_array[i,7]==2 and hand_array[i,6]==1 and hand_array[i,5]==1 and hand_array[i,4]==0:
                    hand_array_else_third.append([i,7])
                # 123300-567700
                for j in range(0,5):
                    if hand_array[i,j]==1 and hand_array[i,j+1]==1 and hand_array[i,j+2]==2 and hand_array[i,j+3]==0 and hand_array[i,j+4]!=1:
                        hand_array_else_third.append([i,j+2])
                # 007789-003345
                for j in range(2, 7):
                    if hand_array[i,j]==2 and hand_array[i,j+1]==1 and hand_array[i,j+2]==1 and hand_array[i,j-1]==0 and hand_array[i,j-2]!=1:
                        hand_array_else_third.append([i, j])
                # 023340-067780
                for j in range(2, 7):
                    if hand_array[i,j]==2 and hand_array[i,j+1]==1 and hand_array[i,j+2]==0 and hand_array[i,j-1]==1 and hand_array[i,j-2]==0:
                        hand_array_else_third.append([i, j])

            # 最后优先级 对子间距1位置1 对子为0178放到第三优先级
            for i in range(3):
                #  1223~7889
                for j in range(1, 8):
                    if hand_array[i,j]==2 and hand_array[i,j-1]==1 and hand_array[i,j+1]==1:
                        hand_array_else_last.append([i,j])

                # 连2 230-780
                # for j in range(2, 7):
                #     if (hand_array[i,j]==1 and hand_array[i,j+1]==1 and hand_array[i,j+2]==0) or (hand_array[i,j]==1 and hand_array[i,j-1]==1 and hand_array[i,j-2]==0):
                #         hand_array_else_last.append([i,j])

            for i in range(3):
                # 02330和07780
                if hand_array[i,0]==0 and hand_array[i,1]==1 and hand_array[i,2]==2 and hand_array[i,3]==0:
                    hand_array_else_last.append([i,1])
                if hand_array[i,5]==0 and hand_array[i,6]==2 and hand_array[i,7]==1 and hand_array[i,8]==0:
                    hand_array_else_last.append([i,7])
            for i in range(3):
                # 3440-7880or0223-0667
                for j in range(2, 7):
                    if (hand_array[i,j]==1 and hand_array[i,j+1]==2 and hand_array[i,j+2]==0) or (hand_array[i,j]==1 and hand_array[i,j-1]==2 and hand_array[i,j-2]==0):
                            hand_array_else_last.append([i,j])

            # 判断是否为空 做出出牌选择
            # 特殊牌型出牌选择 七对
            if len(hand_array_cupple) > 4:
                for i in range(3):
                    for j in range(9):
                        if hand_array[i][j]!=2 and hand_array[i][j]!=0 and discard_history[i][j]>0:
                            print("打的牌是七对" , [i,j])
                            self._conv_req_mess('Discard', self._get_card_str(i,j), '')
                            return
                for i in range(3):
                    for j in range(9):
                        if hand_array[i][j]==1 or hand_array[i][j]==3:
                            print("打的牌是七对" , [i,j])
                            self._conv_req_mess('Discard', self._get_card_str(i,j), '')
                            return

            # 判断是否听牌
            print('*'*40)
            can_ting, listener_id = self._is_ting()
            print('-'*40)
            if can_ting:
                print(listener_id)
                self._simulate_card(listener_id)

            # 四个优先级弃牌模拟胡牌次数
            times_first = []
            times_second = []
            times_third = []
            times_last = []
            if hand_array_else_first != []:
                print('第一级弃牌选择',hand_array_else_first)
                for i in range(len(hand_array_else_first)):
                    if discard_history[hand_array_else_first[i][0],hand_array_else_first[i][1]] > 0:
                        print("打的牌是第一级" , hand_array_else_first[i])
                        if can_ting:
                            # 获取第一级弃牌列表中每张牌在5次模拟听牌中胡牌次数
                            times_first = self._fire_hu(hand_array_else_first, listener_id)
                            print('第一级弃牌列表', hand_array_else_first)
                            print('第一级弃牌列表中每张牌在10次模拟听牌中胡牌次数',times_first)
                            # 若胡牌次数最少的小于？ 则弃牌 否则转入第二优先级模拟
                            if min(times_first) == 0:
                                zero_index = times_first.index(min(times_first))
                                print("打的牌是第一级中已经打过的牌(%d,%d)" %(hand_array_else_first[zero_index][0], hand_array_else_first[zero_index][1]))
                                self._conv_req_mess('Discard', self._get_card_str(hand_array_else_first[zero_index][0], hand_array_else_first[zero_index][1]), '')
                                return
                            # else 转入第二优先级 四个优先级划分为四个函数
                    # 没有打过的牌的判断模拟点炮次数
                    if can_ting:
                        # 获取第一级弃牌列表中每张牌在5次模拟听牌中胡牌次数
                        times_first = self._fire_hu(hand_array_else_first, listener_id)
                        print('第一级弃牌列表', hand_array_else_first)
                        print('第一级弃牌列表中每张牌在10次模拟听牌中胡牌次数',times_first)
                        # 若胡牌次数最少的小于？ 则弃牌 否则转入第二优先级模拟
                        if min(times_first) == 0:
                            zero_index = times_first.index(min(times_first))
                            print("打的牌是第一级中没有打过的牌(%d,%d)" %(hand_array_else_first[zero_index][0], hand_array_else_first[zero_index][1]))
                            self._conv_req_mess('Discard', self._get_card_str(hand_array_else_first[zero_index][0], hand_array_else_first[zero_index][1]), '')
                            return
            elif hand_array_else_second != []:
                print('第二级弃牌选择',hand_array_else_second)
                for i in range(len(hand_array_else_second)):
                    if discard_history[hand_array_else_second[i][0], hand_array_else_second[i][1]] > 0:
                        print("打的牌是第二级" , hand_array_else_second[i])
                        if can_ting:
                            # 获取第二级弃牌列表中每张牌在5次模拟听牌中胡牌次数
                            times_second = self._fire_hu(hand_array_else_second, listener_id)
                            print('第二级弃牌列表', hand_array_else_second)
                            print('第二级弃牌列表中每张牌在10次模拟听牌中胡牌次数',times_second)
                            # 若胡牌次数最少的小于？ 则弃牌 否则转入下一优先级模拟
                            if min(times_second) == 0:
                                zero_index = times_second.index(min(times_second))
                                print("打的牌是第二级中已经打过的牌(%d,%d)" %(hand_array_else_second[zero_index][0], hand_array_else_second[zero_index][1]))
                                self._conv_req_mess('Discard', self._get_card_str(hand_array_else_second[zero_index][0], hand_array_else_second[zero_index][1]), '')
                                return
                            # else 转入第二优先级 四个优先级划分为四个函数
                    # 没有打过的牌的判断模拟点炮次数
                    if can_ting:
                        times_second = self._fire_hu(hand_array_else_second, listener_id)
                        print('第二级弃牌列表', hand_array_else_second)
                        print('第二级弃牌列表中每张牌在10次模拟听牌中胡牌次数', times_second)
                        if min(times_second) == 0:
                            zero_index = times_second.index(min(times_second))
                            print("打的牌是第二级中没有打过的牌(%d,%d)" %(hand_array_else_second[zero_index][0], hand_array_else_second[zero_index][1]))
                            self._conv_req_mess('Discard', self._get_card_str(hand_array_else_second[zero_index][0], hand_array_else_second[zero_index][1]), '')
                            return
            elif hand_array_else_third != []:
                print('第三级弃牌选择',hand_array_else_third)
                for i in range(len(hand_array_else_third)):
                    if discard_history[hand_array_else_third[i][0], hand_array_else_third[i][1]] > 0:
                        print("打的牌是第三级" , hand_array_else_third[i])
                        if can_ting:
                            # 获取第二级弃牌列表中每张牌在5次模拟听牌中胡牌次数
                            times_third = self._fire_hu(hand_array_else_third, listener_id)
                            print('第三级弃牌列表', hand_array_else_third)
                            print('第三级弃牌列表中每张牌在10次模拟听牌中胡牌次数',times_third)
                            # 若胡牌次数最少的小于？ 则弃牌 否则转入下一优先级模拟
                            if min(times_third) == 0:
                                zero_index = times_third.index(min(times_third))
                                print("打的牌是第三级中已经打过的牌(%d,%d)" %(hand_array_else_third[zero_index][0], hand_array_else_third[zero_index][1]))
                                self._conv_req_mess('Discard', self._get_card_str(hand_array_else_third[zero_index][0], hand_array_else_third[zero_index][1]), '')
                                return
                            # else 转入第二优先级 四个优先级划分为四个函数
                    # 没有打过的牌的判断模拟点炮次数
                    if can_ting:
                        times_third = self._fire_hu(hand_array_else_third, listener_id)
                        print('第三级弃牌列表', hand_array_else_third)
                        print('第三级弃牌列表中每张牌在10次模拟听牌中胡牌次数',times_third)
                        if min(times_third) == 0:
                            zero_index = times_third.index(min(times_third))
                            print("打的牌是第三级中没有打过的牌(%d,%d)" %(hand_array_else_third[zero_index][0], hand_array_else_third[zero_index][1]))
                            self._conv_req_mess('Discard', self._get_card_str(hand_array_else_third[zero_index][0], hand_array_else_third[zero_index][1]), '')
                            return
                        self._conv_req_mess('Discard', self._get_card_str(hand_array_else_third[i][0], hand_array_else_third[i][1]), '')
                        return
            elif hand_array_else_last != []:
                print('第四级弃牌选择',hand_array_else_last)
                # 吃牌为空 寻求对对胡
                # if chow_hand_card == "":
                for i in range(len(hand_array_else_last)):
                    if discard_history[hand_array_else_last[i][0], hand_array_else_last[i][1]] > 0:
                        print("打的牌是第四级" , hand_array_else_last[i])
                        if can_ting:
                            # 获取第四级弃牌列表中每张牌在5次模拟听牌中胡牌次数
                            times_last = self._fire_hu(hand_array_else_last, listener_id)
                            print('第四级弃牌列表', hand_array_else_last)
                            print('第四级弃牌列表中每张牌在10次模拟听牌中胡牌次数',times_last)
                            # 若胡牌次数最少的小于？ 则弃牌 否则转入下一优先级模拟
                            if min(times_last) == 0:
                                zero_index = times_last.index(min(times_last))
                                print("打的牌是第四级中已经打过的牌(%d,%d)" %(hand_array_else_last[zero_index][0], hand_array_else_last[zero_index][1]))
                                self._conv_req_mess('Discard', self._get_card_str(hand_array_else_last[zero_index][0], hand_array_else_last[zero_index][1]), '')
                                return
                            # else 转入第二优先级 四个优先级划分为四个函数
                    # 没有打过的牌的判断模拟点炮次数
                    if can_ting:
                        times_last = self._fire_hu(hand_array_else_last, listener_id)
                        print('第四级弃牌列表', hand_array_else_last)
                        print('第四级弃牌列表中每张牌在10次模拟听牌中胡牌次数',times_last)
                        if min(times_last) == 0:
                            zero_index = times_last.index(min(times_last))
                            print("打的牌是第四级中没有打过的牌(%d,%d)" %(hand_array_else_last[zero_index][0], hand_array_else_last[zero_index][1]))
                            self._conv_req_mess('Discard', self._get_card_str(hand_array_else_last[zero_index][0], hand_array_else_last[zero_index][1]), '')
                            return

            # 四个弃牌列表点炮次数没有等于0选择次数最小的
            hand_array_else_sum = hand_array_else_first + hand_array_else_second + hand_array_else_third + hand_array_else_last
            times_sum = times_first + times_second + times_third + times_last
            min_index = times_sum.index(min(times_sum))
            print("没有点炮次数为0的弃牌便选择点炮次数最少的打(%d,%d)" %(hand_array_else_sum[min_index][0], hand_array_else_sum[min_index][1]))
            self._conv_req_mess('Discard', self._get_card_str(hand_array_else_sum[min_index][0], hand_array_else_sum[min_index][1]), '')
            return


            # 四个优先级弃牌
            # if hand_array_else_first != []:
            #     print('第一级弃牌选择',hand_array_else_first)
            #     for i in range(len(hand_array_else_first)):
            #         if discard_history[hand_array_else_first[i][0],hand_array_else_first[i][1]] > 0:
            #             print("打的牌是第一级" , hand_array_else_first[i])
            #             if can_ting:
            #                 # 获取第一级弃牌列表中每张牌在5次模拟听牌中胡牌次数
            #                 times = self._fire_hu(hand_array_else_first, listener_id)
            #                 print('第一级弃牌列表中每张牌在5次模拟听牌中胡牌次数',times)
            #                 # 若胡牌次数最少的小于？ 则弃牌 否则转入第二优先级模拟
            #                 if min(times) == 0:
            #                     zero_index = times.index(min(times))
            #                     self._conv_req_mess('Discard', self._get_card_str(hand_array_else_first[zero_index][0], hand_array_else_first[zero_index][1]), '')
            #                 # else 转入第二优先级 四个优先级划分为四个函数
            #             self._conv_req_mess('Discard', self._get_card_str(hand_array_else_first[i][0], hand_array_else_first[i][1]), '')
            #             return
            #     print("打的牌是第一级(%d,%d)" %(hand_array_else_first[0][0], hand_array_else_first[0][1]))
            #     self._conv_req_mess('Discard', self._get_card_str(hand_array_else_first[0][0], hand_array_else_first[0][1]), '')
            #     return
            # elif hand_array_else_second != []:
            #     print('第二级弃牌选择',hand_array_else_second)
            #     for i in range(len(hand_array_else_second)):
            #         if discard_history[hand_array_else_second[i][0], hand_array_else_second[i][1]] > 0:
            #             print("打的牌是第二级" , hand_array_else_second[i])
            #             self._conv_req_mess('Discard', self._get_card_str(hand_array_else_second[i][0], hand_array_else_second[i][1]), '')
            #             return
            #     print("打的牌是第二级(%d,%d)" %(hand_array_else_second[0][0], hand_array_else_second[0][1]))
            #     self._conv_req_mess('Discard', self._get_card_str(hand_array_else_second[0][0], hand_array_else_second[0][1]), '')
            #     return
            # elif hand_array_else_third != []:
            #     print('第三级弃牌选择',hand_array_else_third)
            #     for i in range(len(hand_array_else_third)):
            #         if discard_history[hand_array_else_third[i][0], hand_array_else_third[i][1]] > 0:
            #             print("打的牌是第三级" , hand_array_else_third[i])
            #             self._conv_req_mess('Discard', self._get_card_str(hand_array_else_third[i][0], hand_array_else_third[i][1]), '')
            #             return
            #     print("打的牌是第三级(%d,%d)" %(hand_array_else_third[0][0], hand_array_else_third[0][1]))
            #     self._conv_req_mess('Discard', self._get_card_str(hand_array_else_third[0][0], hand_array_else_third[0][1]), '')
            #     return
            # elif hand_array_else_last != []:
            #     print('第四级弃牌选择',hand_array_else_last)
            #     # 吃牌为空 寻求对对胡
            #     # if chow_hand_card == "":
            #     for i in range(len(hand_array_else_last)):
            #         if discard_history[hand_array_else_last[i][0], hand_array_else_last[i][1]] > 0:
            #             print("打的牌是第四级" , hand_array_else_last[i])
            #             self._conv_req_mess('Discard', self._get_card_str(hand_array_else_last[i][0], hand_array_else_last[i][1]), '')
            #             return
            #     print("打的牌是第四级(%d,%d)" %(hand_array_else_last[0][0], hand_array_else_last[0][1]))
            #     self._conv_req_mess('Discard', self._get_card_str(hand_array_else_last[0][0], hand_array_else_last[0][1]), '')
            #     return
            #     # else:
            #     #     if len(hand_array_cupple) > 1:
            #     #         for i in range(len(hand_array_else_last)):

            # 连牌情况
            hand_special_cupple_one = []
            hand_special_cupple_two = []
            print('所有已知牌包括自己手牌\n', self.ShowCount)
            print('自己手牌\n',hand_array)

            # 多个对子有无吃牌拆对子
            def pair_chai(self):
                sm = len(hand_array_cupple) + len(hand_array_triplet)
                if sm>2:
                    for i in range(3):
                        for j in range(9):
                            if hand_array[i][j]==2  and discard_history[i][j]>0:
                                # print([i,j])
                                hand_special_cupple_one.append([i,j])
                    print('special_one对子中已经有打出去的牌',hand_special_cupple_one)
                    for i in range(3):
                        for j in range(2,7):
                            if (hand_array[i][j]==2 and hand_array[i][j+1]==2) or (hand_array[i][j]==2 and hand_array[i][j+2]==2) or (hand_array[i][j]==2 and hand_array[i][j-1]==2) or (hand_array[i][j]==2 and hand_array[i][j-2]==2):
                                hand_special_cupple_two.append([i,j])
                            if hand_array[i][j+1]==2 and hand_array[i][j+2]==2:
                                hand_special_cupple_two.append([i,j+1])
                            if hand_array[i][j-1]==2 and hand_array[i][j-2]==2:
                                hand_special_cupple_two.append([i,j-1])
                    print('special_two对子旁边还是对子', hand_special_cupple_two)
                if hand_special_cupple_one != []:
                    for i in range(len(hand_special_cupple_one)):
                        print(hand_special_cupple_one)
                        print("拆对子一" , hand_special_cupple_one[i])
                        self._conv_req_mess('Discard', self._get_card_str(hand_special_cupple_one[i][0], hand_special_cupple_one[i][1]), '')
                        return
                elif hand_special_cupple_two != []:
                    for i in range(len(hand_special_cupple_two)):
                        print("拆对子二" , hand_special_cupple_two[i])
                        self._conv_req_mess('Discard', self._get_card_str(hand_special_cupple_two[i][0], hand_special_cupple_two[i][1]), '')
                        return

            # 四个优先级弃牌为空时弃牌考虑 吃牌为空寻求碰碰胡 不为空拆对子
            if chow_hand_card != "":
                pair_chai(self)
                """
                if len(hand_array_cupple)>2:
                    for i in range(3):
                        for j in range(9):
                            if hand_array[i][j]==2  and discard_history[i][j]>0:
                                # print([i,j])
                                hand_special_cupple_one.append([i,j])
                    print('special_one',hand_special_cupple_one)
                    for i in range(3):
                        for j in range(2,7):
                            if (hand_array[i][j]==2 and hand_array[i][j+1]==2) or (hand_array[i][j]==2 and hand_array[i][j+2]==2) or (hand_array[i][j]==2 and hand_array[i][j-1]==2) or (hand_array[i][j]==2 and hand_array[i][j-2]==2):
                                hand_special_cupple_two.append([i,j])
                            if hand_array[i][j+1]==2 and hand_array[i][j+2]==2:
                                hand_special_cupple_two.append([i,j+2])
                            if hand_array[i][j-1]==2 and hand_array[i][j-2]==2:
                                hand_special_cupple_two.append([i,j-2])
                    print('special_two', hand_special_cupple_two)
                if hand_special_cupple_one != []:
                    for i in range(len(hand_special_cupple_one)):
                        print(hand_special_cupple_one)
                        print("拆对子一" , hand_special_cupple_one[i])
                        self._conv_req_mess('Discard', self._get_card_str(hand_special_cupple_one[i][0], hand_special_cupple_one[i][1]), '')
                        return
                elif hand_special_cupple_two != []:
                    for i in range(len(hand_special_cupple_two)):
                        print("拆对子二" , hand_special_cupple_two[i])
                        self._conv_req_mess('Discard', self._get_card_str(hand_special_cupple_two[i][0], hand_special_cupple_two[i][1]), '')
                        return
                """
            # 寻求对对胡
            else:
                # print('碰牌矩阵\n',self.StateData[self.player_seat, 2])
                # print('杠牌矩阵\n',self.StateData[self.player_seat, 3])
                pon_sum = 0
                kon_sum = 0
                for i in range(3):
                    for j in range(9):
                        if self.StateData[self.player_seat, 2, i, j] == 3:
                            pon_sum += 1
                        if self.StateData[self.player_seat, 3, i, j] == 4:
                            kon_sum += 1
                print("碰牌数目为%d\n杠牌数目为%d" % (pon_sum,kon_sum))
                num_sum = pon_sum + kon_sum + len(hand_array_triplet)
                if num_sum > 4:
                    for i in range(3):
                        for j in range(9):
                            if hand_array[i][j] == 1 and discard_history[i][j]>0:
                                self._conv_req_mess('Discard', self._get_card_str(i,j), '')
                                return
                    for i in range(3):
                        for j in range(9):
                            if hand_array[i][j] == 1:
                                self._conv_req_mess('Discard', self._get_card_str(i,j), '')
                                return

                # 普通胡
                else:
                    pair_chai(self)

        except Exception as e:
            print(e)
            """
            for i in range(3):
                for j in range(9):
                    if self.StateData[self.player_seat, 0 , i, j] == 3:
                        temp_hand_array[i, j] = 0
                    if hand_array[i, j] == 2:
                        hand_array_cupple.append([i, j])
            # 判断手牌中对子个数 若多余两对 先检测顺子 否则就先处理对子
            if len(hand_array_cupple) > 1:
                for i in range(3):
                    for j in range(7):
                        if temp_hand_array[i, j] >0 and temp_hand_array[i, j+1] > 0 and temp_hand_array[i, j+2] > 0:
                            temp_hand_array[i, j] -= 1
                            temp_hand_array[i, j+1] -= 1
                            temp_hand_array[i, j+2] -= 1
            elif len(hand_array_cupple) == 1:
                temp_hand_array[i, j] = 0
            # 处理完手牌中刻子 顺子 对子后 弃牌选择根据经验优先级1,9>2,8>3,4,5,6,7和已弃牌
            else:
                for i in range(3):
                    for j in range(9):
                        if temp_hand_array[i, 1] == 1:
                            self._conv_req_mess('Discard', self._get_card_str(i, 1), '')
                            print("打牌[%d" %i,1,']')
                            return
                        elif temp_hand_array[i, 8] == 1:
                            self._conv_req_mess('Discard', self._get_card_str(i, 8), '')
                            print("打牌[%d" % i, 8, ']')
                            return
                        elif self.ShowCount[i, j] > 0 and temp_hand_array[i, j] == 1:
                            self._conv_req_mess('Discard', self._get_card_str(i, j), '')
                            print("打牌[%d %d" %(i,j),']')
                            return
                        elif temp_hand_array[i, 2] == 1:
                            self._conv_req_mess('Discard', self._get_card_str(i, 2), '')
                            print("打牌[%d" % i,2,']')
                            return
                        elif temp_hand_array[i, 7] == 1:
                            self._conv_req_mess('Discard', self._get_card_str(i, 7), '')
                            print("打牌[%d" % i, 7, ']')
                            return
                        elif temp_hand_array[i, j] == 1:
                            self._conv_req_mess('Discard', self._get_card_str(i, j), '')
                            print("打牌[%d %d" % i, j, ']')
                            return
            """
        # 打最后一张牌
        # for i in [3, 2, 1, 0]:
        #     for j in [8, 7, 6, 5, 4, 3, 2, 1, 0]:
        #         if self.StateData[self.player_seat, 0, i, j] != 0:
        #             self._conv_req_mess('Discard', self._get_card_str(i, j), '')
        #             return

    def _is_ting(self):
        discard_history = self.MessData['history']
        listen_id = [-1, -1, -1, -1]
        for i in range(len(discard_history)):
            print(discard_history[i])
            print(self.player_seat)
            if self.player_seat != int(discard_history[i][0]):
                print(discard_history[i], end='\n')
                if discard_history[i][2] == 'L':
                    print(discard_history[i])
                    listen_id[int(discard_history[i][0])] = 1
        # print('有选手停牌后的听牌列表',listen_id)
        if sum(listen_id) != -4:
            print('有选手停牌后的听牌列表', listen_id)
            return True, listen_id

    def _simulate_card(self, id):
        # 初始化牌，每张牌都有四张
        total = np.zeros(shape=(4, 9), dtype='i1')
        for i in range(3):
            for j in range(9):
                total[i][j] = 4
        # 当前未揭牌矩阵
        un_show_count = total - self.ShowCount
        print('未知牌矩阵', un_show_count)
        print('已知牌矩阵', self.ShowCount)
        un_show_sum = un_show_count.sum()
        un_show_row1 = un_show_count.sum(axis=1)[0]
        un_show_row2 = un_show_count.sum(axis=1)[1]
        un_show_row3 = un_show_count.sum(axis=1)[2]
        print('未知牌矩阵牌数总和以及每一行之和是：', un_show_sum)#un_show_row1,un_show_row2,un_show_row3
        discard_history = self.MessData['history']
        start = time.time()
        # 模拟5种听牌选手手牌
        moni_sum = 0
        for x in range(4):
            if id[x]==1:
                time_C, time_P, time_K = 0, 0, 0  # 统计吃碰杠的次数
                # 统计听牌选手吃碰杠数目得出剩余手牌个数
                for j in range(len(discard_history)):
                    if int(discard_history[j][0])==x and discard_history[j][2]=='C':
                        time_C += 1
                    if int(discard_history[j][0])==x and discard_history[j][2]=='P':
                        time_P += 1
                    if int(discard_history[j][0])==x and discard_history[j][2]=='K':
                        time_K += 1
                simulate_shou_num = 13 - time_C * 3 - time_P * 3 - time_K * 3
                print('要模拟的手牌个数是：',simulate_shou_num)
                simulate_zuhe_num = int(simulate_shou_num / 3)
                un_show_list = []
                for a in range(3):
                    for b in range(9):
                        un_show_list.append(un_show_count[a][b])
                linshi_juzhen = np.zeros(shape=(4, 9), dtype='i1')
                s = 0
                while True:
                    # 随机生成simulate_shou_num个手牌
                    random_shou = random.sample(range(0,un_show_sum), simulate_shou_num)
                    random_shou.sort()
                    print('排序后模拟生成的手牌列表是：', random_shou)

                    # 获取随机生成的牌的位置
                    for v in range(len(random_shou)):
                        list_sum = 0
                        for u in range(len(un_show_list)):
                            list_sum += un_show_list[u]
                            if list_sum >= random_shou[v]:
                                line, row = self._get_array_index(u)
                                print('随机模拟排序后生成的手牌列表对应位置是{}{}'.format(line,row))
                                self.StateData[x][0][line][row] += 1
                                moni_sum += 1
                                break
                            continue
                    can_ting, ting_result = self._check_ting(x, t_ting=True)
                    if can_ting:
                        self.simulate_random_shou[x][s] = self.StateData[x][0]
                        print('模拟第{}个听牌手牌矩阵{}'.format(s,self.simulate_random_shou[x][s]))
                        s += 1
                    self.StateData[x][0] = linshi_juzhen
                    if s == 10:
                        break
        end = time.time()
        print('模拟听牌手牌消耗时间：{}, 模拟总次数：{}'.format(end-start, moni_sum))
        file_handle = open('1.txt', mode='a+')
        file_handle.write('消耗时间'+str(end-start)+'总次数'+str(moni_sum)+'\n')

        """
        num_ke = 0
        num_shun = 0
        num_zuhe = 0
        for i in range(3):
            for j in range(9):
                if un_show_count[i][j]>2:
                    num_ke += 1
            for j in range(7):
                if un_show_count[i][j]>0 and un_show_count[i][j+1]>0 and un_show_count[i][j+2]>0:
                    num_shun += 1
        num_zuhe = num_ke + num_ke
        """
    def _fire_hu(self, qipai_list, id):
        print('听牌选手列表：',id)
        for x in range(4):
            if id[x]==1:
                fire_times_list = []
                for i in range(len(qipai_list)):
                    fire_times = 0
                    for j in range(10):
                        # print('听牌选手模拟的第{}种手牌矩阵是：'.format(j))
                        # print(self.simulate_random_shou[x][j])
                        simulate_shou = copy.deepcopy(self.simulate_random_shou[x][j])
                        simulate_shou[qipai_list[i][0]][qipai_list[i][1]] += 1
                        # self.simulate_random_shou[x][j][qipai_list[i][0]][qipai_list[i][1]] += 1
                        # 把模拟的手牌传过去，看点炮否
                        # is_hu, _ = self._check_hu(self.simulate_random_shou[x][j])
                        is_hu, _ = self._check_hu(simulate_shou)
                        if is_hu:  # 点炮去寻找下一个
                            fire_times += 1
                            print('可能点炮了，最好换一张牌出！')
                        # self.simulate_random_shou[x][j][qipai_list[i][0]][qipai_list[i][1]] -= 1
                    fire_times_list.append(fire_times)
                for j in range(10):
                    print('听牌选手模拟的第{}种手牌矩阵是：'.format(j))
                    print(self.simulate_random_shou[x][j])
                return fire_times_list

    def _del_other_out(self):
        '''
        处理对手玩家打牌
        :return:
        '''
        # self._del_ourself_drw()
        hand_array = copy.deepcopy(self.StateData[self.player_seat, 0])
        hand_array_cupple = []
        for i in range(3):
            for j in range(9):
                if hand_array[i, j] == 2:
                    hand_array_cupple.append([i, j])

        temp_hand_count = copy.deepcopy(self.StateData[self.player_seat, 0])
        line, row = self._get_card_index(self.Now_Deal)
        temp_hand_count[line, row] += 1

        is_hu, _ = self._check_hu(temp_hand_count)
        logging.debug("胡牌判断：%s", is_hu)
        if is_hu:
            self._conv_req_mess('Win', self.Now_Deal)
            return
        try:
            if len(hand_array_cupple)<5:
                can_gang, gang_count = self._check_gang(self.player_seat, is_self=False)
                if can_gang:
                    self._conv_req_mess('Kon', self._get_card_str(gang_count[0][0], gang_count[0][1]) * 4, '')
                    logging.debug(self.ReqMess)
                    return
                can_pen, pen_count = self._check_peng(self.player_seat)
                if can_pen:
                    self._conv_req_mess('Pon', self._get_card_str(pen_count[0][0], pen_count[0][1]) * 3, '')
                    return
                can_chi, chi_count,chi_count_one,chi_count_two,chi_count_three = self._check_chi(self.player_seat)
                print(chi_count)
                logging.debug(chi_count)
                now_line, now_row = self._get_card_index(self.Now_Deal)
                if can_chi:
                    for i in range(len(chi_count)):
                        # 排除1无法吃
                        if chi_count[i][1] > -1:
                            if self.StateData[self.player_seat, 0, now_line, now_row]==0:
                                if chi_count_three != "":
                                    for j in range(len(chi_count_three)):
                                        action_index = self._get_card_cod(chi_count_three[j][0], chi_count_three[j][1])
                                        logging.debug(action_index)
                                        print("第三级吃")
                                        self._conv_req_mess('Chow', index_chi[action_index], '')
                                        return
                                if chi_count_one != "":
                                    for j in range(len(chi_count_one)):
                                        if len(chi_count_one) > 1:
                                            for x in range(len(chi_count_one)):
                                                # 尽量吃789 但是不能本来没有无效牌吃过后就有了
                                                if chi_count_one[x][1] == 6:
                                                    action_index = self._get_card_cod(chi_count_one[x][0], chi_count_one[x][1])
                                                    logging.debug(action_index)
                                                    print("第一级789吃")
                                                    self._conv_req_mess('Chow', index_chi[action_index], '')
                                                    return
                                        action_index = self._get_card_cod(chi_count_one[j][0], chi_count_one[j][1])
                                        logging.debug(action_index)
                                        # if hand_array[line, row]==1 and
                                        print("第一级吃")
                                        self._conv_req_mess('Chow', index_chi[action_index], '')
                                        return
                                if chi_count_two != "":
                                    for j in range(len(chi_count_two)):
                                        if len(chi_count_two) > 1:
                                            for x in range(len(chi_count_two)):
                                                # 尽量吃789 但是不能本来没有无效牌吃过后就有了
                                                if chi_count_two[x][1] == 6:
                                                    action_index = self._get_card_cod(chi_count_two[x][0], chi_count_two[x][1])
                                                    logging.debug(action_index)
                                                    print("第二级789吃")
                                                    self._conv_req_mess('Chow', index_chi[action_index], '')
                                                    return
                                        action_index = self._get_card_cod(chi_count_two[j][0], chi_count_two[j][1])
                                        logging.debug(action_index)
                                        print("第二级吃")
                                        self._conv_req_mess('Chow', index_chi[action_index], '')
                                        return
                            elif self.StateData[self.player_seat, 0, now_line, now_row] == 1:
                                if chi_count_three != "":
                                    for j in range(len(chi_count_three)):
                                        action_index = self._get_card_cod(chi_count_three[j][0], chi_count_three[j][1])
                                        logging.debug(action_index)
                                        print("第三级吃")
                                        self._conv_req_mess('Chow', index_chi[action_index], '')
                                        return
                                if chi_count_two != "":
                                    for j in range(len(chi_count_two)):
                                        if len(chi_count_two) > 1:
                                            for x in range(len(chi_count_two)):
                                                # 尽量吃789 但是不能本来没有无效牌吃过后就有了
                                                if chi_count_two[x][1] == 6 and self.StateData[self.player_seat, 0, now_line, now_row]==0:
                                                    action_index = self._get_card_cod(chi_count_two[x][0], chi_count_two[x][1])
                                                    logging.debug(action_index)
                                                    print("第二级789吃")
                                                    self._conv_req_mess('Chow', index_chi[action_index], '')
                                                    return
                                        action_index = self._get_card_cod(chi_count_two[j][0], chi_count_two[j][1])
                                        logging.debug(action_index)
                                        print("第二级吃")
                                        self._conv_req_mess('Chow', index_chi[action_index], '')
                                        return
                                if chi_count_one != "":
                                    for j in range(len(chi_count_one)):
                                        if len(chi_count_one) > 1:
                                            for x in range(len(chi_count_one)):
                                                # 尽量吃789 但是不能本来没有无效牌吃过后就有了
                                                if chi_count_one[x][1] == 6:
                                                    action_index = self._get_card_cod(chi_count_one[x][0], chi_count_one[x][1])
                                                    logging.debug(action_index)
                                                    print("第一级789吃")
                                                    self._conv_req_mess('Chow', index_chi[action_index], '')
                                                    return
                                        action_index = self._get_card_cod(chi_count_one[j][0], chi_count_one[j][1])
                                        logging.debug(action_index)
                                        print("第一级吃")
                                        self._conv_req_mess('Chow', index_chi[action_index], '')
                                        return
                        """
                        if self.StateData[self.player_seat, 0 ,chi_count[i][0], chi_count[i][1]] == 1:
                            for j in range(len(chi_count)):
                                # if len(chi_count) > 1:
                                if chi_count[j][1] > 3 and len(chi_count) > 1:
                                    for x in range(len(chi_count)):
                                        # 尽量吃789 但是不能本来没有无效牌吃过后就有了
                                        if chi_count[x][1] == 6 and self.StateData[self.player_seat, 0, now_line, now_row]==0:
                                            action_index = self._get_card_cod(chi_count[x][0], chi_count[x][1])
                                            logging.debug(action_index)
                                            print("第一级单牌789吃并且吃的牌手牌中为0")
                                            self._conv_req_mess('Chow', index_chi[action_index], '')
                                            return
                                    # 单牌能吃就不拆对子
                                    if self.StateData[self.player_seat, 0, chi_count[j][0], chi_count[j][1]] == 1: # 5788chi6
                                        action_index = self._get_card_cod(chi_count[j][0], chi_count[j][1])
                                        logging.debug(action_index)
                                        print("第一级单牌吃并且吃牌序列手牌为1")
                                        self._conv_req_mess('Chow', index_chi[action_index], '')
                                        return
                                    action_index = self._get_card_cod(chi_count[j+1][0], chi_count[j+1][1])
                                    logging.debug(action_index)
                                    print("diyiji")
                                    self._conv_req_mess('Chow', index_chi[action_index], '')
                                    return
                                action_index = self._get_card_cod(chi_count[j][0], chi_count[j][1])
                                logging.debug(action_index)
                                print(chi_count)
                                self._conv_req_mess('Chow', index_chi[action_index], '')
                                return
                            action_index = self._get_card_cod(chi_count[i][0], chi_count[i][1])
                            logging.debug(action_index)
                            print(chi_count)
                            self._conv_req_mess('Chow', index_chi[action_index], '')
                            return
                        if self.StateData[self.player_seat, 0 ,chi_count[i][0], chi_count[i][1]] == 2:
                            for j in range(len(chi_count)):
                                if len(chi_count) > 1:
                                    action_index = self._get_card_cod(chi_count[j+1][0], chi_count[j+1][1])
                                    logging.debug(action_index)
                                    print("zhongjian")
                                    self._conv_req_mess('Chow', index_chi[action_index], '')
                                    return

                        action_index = self._get_card_cod(chi_count[i][0], chi_count[i][1])
                        logging.debug(action_index)
                        print("dierji")
                        self._conv_req_mess('Chow', index_chi[action_index], '')
                        return
                        """

                self._conv_req_mess('Pass', '', '')
                return

            self._conv_req_mess('Pass', '', '')
            return

        except:
            logging.error("消息处理失败")

if __name__ == "__main__":
    import json
    # 12345668,789 打6不打8 听牌判断位置
    # test_str = {"pon_hand":"","kon_hand":"","chow_hand":"B1B2B3","hand":"C1C2C3C4C5C6C6D7D8D9","history":["3,Discard,B9"],"dealer":3,"seat":0,"special":""}
    # 第二优先级0300-0700 0030-0070 355本该是第三优先级
    # test_str = {"pon_hand":"B1B1B1","kon_hand":"","chow_hand":"","hand":"B3B5B5C2C4C4C8C9C9D4D5","history":["3,Discard,C4"],"dealer":3,"seat":0,"special":""}
    # 多个对子有无吃牌拆对子
    # test_str = {"pon_hand":"B9B9B9,D1D1D1","kon_hand":"","chow_hand":"","hand":"B5B5C7C7C8C8D7D8","history":["0,Pon,B9B9B9","0,Pon,D1D1D1","3,Discard,D8"],"dealer":3,"seat":0,"special":""}
    # 有效听牌数
    # test_str = {"pon_hand":"B9B9B9，D8D8D8","kon_hand":"","chow_hand":"C4C5C6","hand":"B5B5C6C7C7","history":["3,Discard,C4"],"dealer":3,"seat":0,"special":""}
    # test_str = {"pon_hand":"B9B9B9，D8D8D8","kon_hand":"","chow_hand":"","hand":"B1B1B1C4C5C6C7C8","history":["3,Discard,C4"],"dealer":3,"seat":0,"special":""}
    # 对对胡与听牌有效数矛盾 以听牌有效数为准
    # test_str = {"pon_hand":"B9B9B9，D8D8D8","kon_hand":"","chow_hand":"","hand":"B1B1B1C5C5C5D7D8","history":["3,Discard,C4"],"dealer":3,"seat":0,"special":""}
    # 七对
    # test_str = {"pon_hand":"","kon_hand":"","chow_hand":"","hand":"B3B3B5B5B9B9C2C2C7C8C9C9D4D5","history":["3,Discard,C4"],"dealer":3,"seat":0,"special":""}
    # test_str = {"pon_hand":"","kon_hand":"","chow_hand":"","hand":"B2B2B3B6C2C2C3C6C6C8D1D1D2D2","history":["3,Discard,C4"],"dealer":3,"seat":0,"special":""}
    # 吃吐测试
    # test_str = {"pon_hand":"","kon_hand":"","chow_hand":"","hand":"B1B2B3C2C2C3C6C6C8D1D1D2D2","history":["3,Discard,B1"],"dealer":3,"seat":0,"special":""}
    # ++++++++++连牌中加上听牌有效数拆连牌 ？？？？？？
    # test_str = {"pon_hand":"D6D6D6","kon_hand":"D9D9D9D9","chow_hand":"","hand":"B1B1C2C3C4C5D7D8","history":["1,Discard,B9","1,Discard,D6","0,Pon,D6D6D6","1,Discard,D9","0,Kon,D9D9D9D9","3,Discard,B6"],"dealer":3,"seat":0,"special":""}

    # 用字典测试  dealer:庄家  seat:玩家座号 0,discard,B2
    test_str = {"pon_hand": "", "kon_hand": "", "chow_hand": "B1B2B3,B2B3B4", "hand": "C4C6C8D4D6D8D8D9",
                "history": ['0,Discard,B9', '1,Kon,B9B9B9B9','1,Discard,B4', '2,Discard,B6', '3,Discard,C1',
                            '0,Discard,C1', '1,Discard,B6','2,Kon,D3D3D3D3', '2,Discard,D2', '3,Discard,C8',
                            '0,Discard,C6', '1,Discard,C2', '2,Discard,B1', '3,Chow,B1B2B3', '3,Discard,C9',
                            '0,Discard,D2', '1,Discard,C5', '2,Pon,B8B8B8', '2,Discard,B3', '2,Listen,D4','3,Chow,B2B3B4'
                            ],
                "dealer": 0, "seat": 3, "special": ""}
    test = Pubilc_MahJong(json.dumps(test_str))
    # test._is_ting()
    Req_Mess = test.get_game_req()
    print(Req_Mess)