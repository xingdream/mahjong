# -*- coding: utf-8 -*- 
# @Time    : 2020/4/2 10:04
# @Author  : WangHong 
# @FileName: dazhong_mahjong.py
# @Software: PyCharm
from src.mahjong_no_state import *


class Pubilc_MahJong(MahJong_NO_State_Base):
    '''
    二人麻将无状态AI，第一版本
    '''

    def __init__(self, mess_data):
        super(Pubilc_MahJong, self).__init__(mess_data)
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
        elif card_num % 3 == 2:
            self._del_ourself_drw()
            return
        # 对手打牌
        elif card_num % 3 == 1:
            self._del_other_out()
        else:
            logging.error("相公")
            self._conv_req_mess('相公了', 'Self')

    def _del_ourself_drw(self):
        '''
        处理自己的摸牌动作
        :return:
        '''
        # 先判断是否可以自摸
        for i in [3, 2, 1, 0]:
            for j in [8, 7, 6, 5, 4, 3, 2, 1, 0]:
                if self.StateData[self.player_seat, 0, i, j] != 0:
                    self._conv_req_mess('Discard', self._get_card_str(i, j), '')
                    return

    def _del_other_out(self):
        '''
        处理对手玩家打牌
        :return:
        '''
        temp_hand_count = copy.deepcopy(self.StateData[self.player_seat, 0])
        line, row = self._get_card_index(self.Now_Deal)
        temp_hand_count[line, row] += 1

        is_hu, _ = self._check_hu(temp_hand_count)
        logging.debug("胡牌判断：%s", is_hu)
        if is_hu:
            self._conv_req_mess('Win', self.Now_Deal)
            return
        try:
            can_gang, gang_count = self._check_gang(self.player_seat, is_self=False)
            if can_gang:
                self._conv_req_mess('Kon', self._get_card_str(gang_count[0][0], gang_count[0][1]) * 4, '')
                logging.debug(self.ReqMess)
                return
            can_pen, pen_count = self._check_peng(self.player_seat)
            if can_pen:
                self._conv_req_mess('Pen', self._get_card_str(pen_count[0][0], pen_count[0][1]) * 3, '')
                return
            can_chi, chi_count = self._check_chi(self.player_seat)
            logging.debug(chi_count)
            if can_chi:
                action_index = self._get_card_cod(chi_count[0][0], chi_count[0][1])
                logging.debug(action_index)
                self._conv_req_mess('Chow', index_chi[action_index], '')
                return
            self._conv_req_mess('Pass', '', '')
        except:
            logging.error("消息处理失败")

if __name__ == "__main__":
    import json
    test_str = {"pon_hand":"","kon_hand":"","chow_hand":"","hand":"C1C1C1C4C5B2B2B3B3B3D5D2D3","history":["3,Discard,C6"],"dealer":3,"seat":0,"special":""}

    test = Pubilc_MahJong(json.dumps(test_str))
    Req_Mess = test.get_game_req()
    print(Req_Mess)