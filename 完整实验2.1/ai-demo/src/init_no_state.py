# -*- coding: utf-8 -*- 
# @Time    : 2020/3/5 10:40
# @Author  : WangHong 
# @FileName: mahjong_no_state.py
# @Software: PyCharm


import json
import re
import numpy as np
import copy
from config.game_config import *
from config.log_config import *


class MahJong_NO_State_Base():
    '''
    麻将无状态AI基类
    '''

    def __init__(self, mess_data):
        # 解析出来的消息字典
        self.MessData = json.loads(mess_data)
        # 返回的消息字典，需要转化为json
        self.__init_state()

    def __init_state(self):
        '''
        初始化当前的状态
        :return:
        '''
        # 返回的数据
        self.ReqMess = {}
        # 存储游戏玩家所有的状态数据
        self.StateData = np.zeros(shape=(4, 7, 4, 9), dtype=np.int8)
        # 游戏当前的特殊牌
        self.Game_Special = ''
        # 游戏玩家当前处理的牌
        self.Now_Deal = ''
        # 自己杠牌分组的统计
        self.gang_count = 0
        # 判断是否是天听
        self.is_tting = True
        # 暗杠牌的统计
        self.gang_count_an = 0
        # 所有已知牌的统计
        self.ShowCount = np.zeros(shape=(4, 9), dtype=np.int8)
        # 当前决策者的座位号
        self.player_seat = -1
        # 用于存储合法动作序列
        self.legal_action = {}
        # 分析提取数据
        self._analyze_game_data()
        # logging.debug(self.ShowCount)

    def _analyze_game_data(self):
        '''
        提取分析游戏的状态数据
        :return:
        '''
        # 提取当前玩家手中的牌
        self.player_seat = int(self.MessData['seat'])
        self._full_array(self.player_seat, 0, self._cut_string(self.MessData['hand'], 2))
        self.Game_Special = self.MessData['special']
        # 去除空的历史动作
        self.MessData['history'] = [i for i in self.MessData['history'] if i != '']
        # 根据历史动作填充数据
        if len(self.MessData['history']) != 0:
            self.is_tting = False
            for i in range(len(self.MessData['history'])):
                one_action = self.MessData['history'][i].split(",")
                self._del_one_history(one_action, i)
            last_action = self.MessData['history'][-1].split(",")
            self.Now_Deal = self._cut_string(last_action[2], 2)[0]
        else:
            self.Now_Deal = '-1'

    def _del_one_history(self, one_history, index):
        '''
         处理一条历史动作
         :param one_history:
         :return:
         '''
        action_seat = int(one_history[0])
        card_list = self._cut_string(one_history[2], 2)
        self._check_card_legal(card_list)

        if one_history[1] == 'Chow':
            self._del_history_chow(action_seat, card_list, index)
        elif one_history[1] == 'Pon':
            self._del_history_pon(action_seat, card_list)
        elif one_history[1] == 'Kon':
            self._del_history_kon(action_seat, card_list, index)
        elif one_history[1] == 'Discard':
            self._del_history_dis(action_seat, card_list)
        elif one_history[1] == 'Listen':
            self._del_history_listen(action_seat, card_list)
        elif one_history[1] == 'Win':
            self._del_history_win(action_seat, card_list)

    def _del_history_chow(self, seat, chow_str, index):
        '''
        处理历史动作中的吃牌动作
        :param seat:
        :param chow_str:
        :return:
        '''
        card_index = []
        card_lable = ''
        dis_action = self.MessData['history'][index - 1].split(",")
        for card in chow_str:
            if card != dis_action[2]:
                line, row = self._get_card_index(card)
                self.ShowCount[line, row] += 1
            temp_card = self._cut_string(card, 1)
            card_index.append(int(temp_card[1]))
            card_lable = temp_card[0]
        min_index = min(card_index)
        if card_lable == 'B':
            self.StateData[seat, 1, 0, min_index - 1] += 1
        elif card_lable == 'C':
            self.StateData[seat, 1, 1, min_index - 1] += 1
        elif card_lable == 'D':
            self.StateData[seat, 1, 2, min_index - 1] += 1
        else:
            logging.error("吃牌数据不合法")

    def _del_history_pon(self, seat, pon_list):
        '''
        处理历史动作中的碰牌动作
        :param seat:
        :param pon_list:
        :return:
        '''
        self._full_array(seat, 2, pon_list)
        line, row = self._get_card_index(pon_list[0])
        self.ShowCount[line, row] += 2

    def _del_history_kon(self, seat, kon_list, index):
        '''
         处理历史动作中的杆牌动作
        :param seat:
        :param kon_list:
        :return:
        '''
        if kon_list[0] == 'UN':
            return
        self.gang_count += 1
        line, row = self._get_card_index(kon_list[0])
        self.StateData[seat, 3, line, row] = 4
        self.ShowCount[line, row] = 4
        dis_action = self.MessData['history'][index - 1].split(",")
        if kon_list[0] != dis_action[2]:
            self.gang_count_an += 1

    def _del_history_dis(self, seat, dis_card):
        line, row = self._get_card_index(dis_card[0])
        self.ShowCount[line, row] += 1
        if self.StateData[seat, 6, 0, 0] == 0:
            self._full_array(seat, 4, dis_card)
        else:
            self._full_array(seat, 5, dis_card)

    def _del_history_listen(self, seat, lis_card):
        '''
        处理历史动作中的听牌动作
        :param seat:
        :param lis_card:
        :return:
        '''
        line, row = self._get_card_index(lis_card[0])
        self.ShowCount[line, row] += 1
        self.StateData[seat, 6] = 1
        self._full_array(seat, 5, lis_card)

    def _del_history_win(self, seat, win_card):
        '''
        处理历史动作中的赢牌动作
        :param seat:
        :param win_card:
        :return:
        '''
        # TODO
        pass

    def _check_card_legal(self, card_list):
        '''
        判断列表中的牌字符串是否合法
        :param card_list:
        :return:
        '''
        for card in card_list:
            if card not in card_set:
                logging.error("牌表示出错:%s", card)
                exit()

    def _get_card_index(self, card):
        '''
        获得字符串形式牌的索引
        :param card:
        :return:
        '''
        if card == 'UN':
            logging.error('UN')
        line = -1
        row = -1
        card_str = self._cut_string(card, 1)
        if card_str[0] == 'C' or card_str[0] == 'B' or card_str[0] == 'D':
            row = int(card_str[1]) - 1
            if row > 9:
                logging.error('牌的编码错误')
                exit()
            if card_str[0] == 'B':
                line = 0
            elif card_str[0] == 'C':
                line = 1
            elif card_str[0] == 'D':
                line = 2
        elif card_str[0] == 'W' or card_str[0] == 'A':
            line = 3
            if card_str[1] == 'E':
                row = 0
            elif card_str[1] == 'W':
                row = 1
            elif card_str[1] == 'S':
                row = 2
            elif card_str[1] == 'N':
                row = 3
            elif card_str[1] == 'C':
                row = 4
            elif card_str[1] == 'F':
                row = 5
            elif card_str[1] == 'B':
                row = 6
        else:
            print("牌的编码为",card_str)
            logging.error('牌的编码错误')
            exit()
        return line, row

    def _full_array(self, seat, feature_index, str_list):
        '''
        填充数据矩阵
        :param seat: 要填充的玩家座位0~3
        :param feature_index: 要填充的特征0~6
        :param str_list: 要填充的牌的字符串列表
        :return:
        '''
        for card in str_list:
            line, row = self._get_card_index(card)
            if feature_index == 0:
                self.ShowCount[line, row] += 1
            self.StateData[seat, feature_index, line, row] += 1

    def _cut_string(self, text, lenth):
        '''
        按照指定长度分割字符串
        :param text: 字符串
        :param lenth: 分割长度
        :return:
        '''
        textArr = re.findall(r'.{' + str(lenth) + '}', text)
        if text[(len(textArr) * lenth):] != "":
            textArr.append(text[(len(textArr) * lenth):])
        return textArr

    def _get_card_str(self, line, row):
        '''
        根据牌的行列，得到牌的字符串表示
        :param line:
        :param row:
        :return:
        '''
        card_str = ''
        if line == 0:
            card_str += 'B'
            card_str += str(row + 1)
        elif line == 1:
            card_str += 'C'
            card_str += str(row + 1)
        elif line == 2:
            card_str += 'D'
            card_str += str(row + 1)
        elif line == 3:
            if row == 0:
                card_str = 'WE'
            elif row == 1:
                card_str = 'WW'
            elif row == 1:
                card_str = 'WS'
            elif row == 1:
                card_str = 'WN'
            elif row == 1:
                card_str = 'AC'
            elif row == 1:
                card_str = 'AF'
            elif row == 1:
                card_str = 'AB'

        return card_str

    def _get_array_index(self, index):
        '''
        根据牌的编码索引，获取牌在矩阵中的位置， 0~34
        :param index:
        :return:
        '''
        line = index // 9
        row = index % 9
        return line, row

    def _get_card_cod(self, line, row):
        '''
        根据矩阵中的索引，得到牌的编码
        :param line:
        :param row:
        :return:
        '''
        index = line * 9 + row
        return index

    def _check_gang(self, seat, is_self=True):
        '''
        判断玩家是否可以杠牌
        :param seat:
        :param is_self:
        :return:
        '''
        gang_count = []
        check_count = 0
        if is_self:
            for line in range(4):
                for row in range(9):
                    check_count += 1
                    if self.StateData[seat, 0, line, row] == 4:
                        gang_count.append([line, row])
                    if self.StateData[seat, 0, line, row] == 1 and self.StateData[seat, 2, line, row] == 1:
                        gang_count.append([line, row])
        else:
            if self.Now_Deal == '-1':
                logging.error('动作序列判断错误')
                exit()
            now_line, now_row = self._get_card_index(self.Now_Deal)
            if self.StateData[seat, 0, now_line, now_row] == 3:
                gang_count.append([now_line, now_row])

        if len(gang_count) == 0:
            return False, None
        else:
            return True, gang_count

    def _check_peng(self, seat):
        '''
        判断碰牌
        :param seat:
        :return:
        '''
        peng_count = []
        now_line, now_row = self._get_card_index(self.Now_Deal)
        if self.StateData[seat, 0, now_line, now_row] >= 2:
            peng_count.append([now_line, now_row])
        if len(peng_count) == 0:
            return False, None
        else:
            return True, peng_count

    def _check_chi(self, seat):
        '''
        判断吃牌
        :param seat:
        :return:
        '''
        chi_count = []
        now_line, now_row = self._get_card_index(self.Now_Deal)
        if now_line == 3:
            return False, None
        anRelateIndex = [-1, -1, -1, -1]
        if now_row - 2 >= 0:
            anRelateIndex[0] = self.StateData[seat, 0, now_line, now_row - 2]
        if now_row - 1 >= 0:
            anRelateIndex[1] = self.StateData[seat, 0, now_line, now_row - 1]
        if now_row + 1 <= 8:
            anRelateIndex[2] = self.StateData[seat, 0, now_line, now_row + 1]
        if now_row + 2 <= 8:
            anRelateIndex[3] = self.StateData[seat, 0, now_line, now_row + 2]
        for i in range(3):
            if anRelateIndex[i] != 0 and anRelateIndex[i + 1] != 0:
                if i == 0:
                    chi_count.append([now_line, now_row - 2])
                elif i == 1:
                    chi_count.append([now_line, now_row - 1])
                elif i == 2:
                    chi_count.append([now_line, now_row])
        if len(chi_count) == 0:
            return False, None
        else:
            return True, chi_count

    def _check_ting(self, seat, t_ting=False):
        '''
        通用检查玩家是否可以听
        :param seat:
        :param t_ting:
        :return:
        '''
        ting_count = {}
        hand_array = copy.deepcopy(self.StateData[seat, 0])
        if t_ting:
            ting_count[-1] = []
            for i in range(card_kind):
                line, row = self._get_array_index(i)
                hand_array = copy.deepcopy(self.StateData[seat, 0])
                hand_array[line, row] += 1
                is_hu, hu_value = self._check_hu(hand_array)
                if is_hu:
                    ting_count[-1].append(dict_index[i])
            if len(ting_count[-1]) == 0:
                ting_count.pop(-1)
        else:
            for i in range(card_kind):
                line, row = self._get_array_index(i)
                if hand_array[line, row] == 0:
                    continue
                temp_hand_array = copy.deepcopy(self.StateData[seat, 0])
                temp_hand_array[line, row] -= 1
                ting_count[dict_index[i]] = []
                for j in range(card_kind):
                    temp_hand = copy.deepcopy(temp_hand_array)
                    now_line, mow_row = self._get_array_index(j)
                    temp_hand[now_line, mow_row] += 1
                    is_hu, _ = self._check_hu(temp_hand)
                    if is_hu:
                        ting_count[dict_index[i]].append(dict_index[j])
                if len(ting_count[dict_index[i]]) == 0:
                    ting_count.pop(dict_index[i])
        if len(ting_count) == 0:
            return False, None
        return True, ting_count

        # 以下函数需要子类继承实现的函数

    def _check_hu(self, hand_array):
        '''
        通用判断胡牌
        :param seat:
        :return:
        '''
        hand_group = self._cont_hu_list(hand_array)
        hu_key = self._call_key(hand_group)
        if hu_key in HuTable.keys():
            return True, HuTable[hu_key]
        return False, None

    def _cont_hu_list(self, hand_array):
        '''
        将手牌的统计，装换为，可以计算key的形式的列表
        :param seat:
        :return:
        '''
        group = []
        result = []
        for line in range(3):
            for row in range(9):
                if hand_array[line, row] != 0:
                    group.append(hand_array[line, row])
                else:
                    if len(group) != 0:
                        result.append(group)
                    group = []
        for row in range(7):
            if hand_array[3, row] != 0:
                result.append([hand_array[3, row]])
        return result

    def _call_key(self, DowList):
        '''
        计算牌型的key值
        :return:
        '''
        index = -1
        ret = 0
        for _, b in enumerate(DowList):
            for _, v in enumerate(b):
                index += 1
                if v == 2:
                    ret |= 0x3 << index
                    index += 2
                elif v == 3:
                    ret |= 0xF << index
                    index += 4
                elif v == 4:
                    ret |= 0x3F << index
                    index += 6
            ret |= 0x1 << index
            index += 1
        return ret

    def _conv_req_mess(self, action_type, action_content='', note=''):
        '''
        组装回复数据
        :param action:
        :return:
        '''
        self.ReqMess['action_type'] = action_type
        self.ReqMess['action_content'] = action_content
        self.ReqMess['note'] = note

    def get_game_req(self):
        '''
        返回游戏的消息
        :return:
        '''
        return self.ReqMess

    # 以下为子类实现的函数

    def _ai_del_logic(self):
        '''
        ai的处理逻辑
        :return:
        '''
        raise NotImplementedError

    def _del_ourself_drw(self):
        '''
        处理自己摸牌
        :return:
        '''
        raise NotImplementedError

    def _del_other_out(self):
        '''
        处理对手玩家打牌
        :return:
        '''
        raise NotImplementedError
