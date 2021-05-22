# -*- coding: utf-8 -*- 
# @Time    : 2020/4/2 10:04
# @Author  : WangHong 
# @FileName: dazhong_mahjong.py
# @Software: PyCharm
import sys
import os
import numpy as np
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from src.mahjong_no_state import *

#被模拟玩家的手牌矩阵-1-3，假设当前先模仿停牌玩家的一种手牌情况，先声明为全局变量
simulate_listener_0 = np.zeros(shape=(3, 9), dtype='i1')
simulate_listener_1 = np.zeros(shape=(3, 9), dtype='i1')
simulate_listener_2 = np.zeros(shape=(3, 9), dtype='i1')
simulate_listener_3 = np.zeros(shape=(3, 9), dtype='i1')
class Pubilc_MahJong(MahJong_NO_State_Base):
    '''
    二人麻将无状态AI，第一版本
    '''

    def __init__(self, mess_data):  #mess_date 是穿过来的test_str
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
        elif card_num % 3 == 2:     #证明这里是自己接牌，才14%3=2，然后自己开始出牌
            print('开始打自己的牌...')
            self._del_ourself_drw() #处理自己的摸牌动作
            is_can_tting, ting_result = self._check_ting(self.player_seat, t_ting=False)#出牌后检查自己能否 听
            if is_can_tting:  #可以听，差一张胡牌
                for key in ting_result.keys():
                    print('我能听牌了吗：{}'.format(is_can_tting))
                    self._conv_req_mess('Listen', key, '')  #听，拿啥打啥
                    return
            return
        # 对手打牌
        elif card_num % 3 == 1:     #这里是对方出牌，自己判读是否杠、碰、吃；
            self._del_other_out()   #处理对手的出牌动作
        else:
            logging.error("相公")
            self._conv_req_mess('相公了', 'Self') #组装回复数据

    def _del_ourself_drw(self):
        self._think_and_deal()  #自己出牌

    def _get_linstener_history(self):  #获得听牌玩家所有打出去、吃、碰、杠的牌，存贮在linstener_*中；
        pass_history = self.MessData['history']
        print('历史动作是： ', pass_history)
        had_listen = 0
        listen_id = [-1, -1, -1, -1, ]  # 假设最多有三个对手听牌了，
        # 找出听牌的人，并在listen_id里面写出听牌的座位号0-3；
        for i in range(len(pass_history)):
            id = pass_history[i][0]
            if id != self.player_seat: ###
				if pass_history[i][2] == 'L':  # 该位置有听牌的
					print('{} 玩家听了'.format(pass_history[i][0]))
					if id == '0':
						listen_id[0] = 0  # 在听牌的位置上赋值
					if id == '1':
						listen_id[1] = 1  # 在听牌的位置上赋值
					if id == '2':
						listen_id[2] = 2  # 在听牌的位置上赋值
					if id == '3':
						listen_id[3] = 3  # 在听牌的位置上赋值
        listener_0 = []
        listener_1 = []
        listener_2 = []
        listener_3 = []
        listener_all = [listener_0, listener_1, listener_2,
                        listener_3, ]  # listener_all 最后会作simulate_lintener_hand(listener_hand=[])中的参数
        # 把听过牌的玩家的手牌拿出来
        for i in range(4):
            if listen_id[i] != -1:
                print('获得玩家 {} 的手牌...'.format(i)) ###
                for j in range(len(pass_history)):     #浏览json中的history，
                    if pass_history[j][0] == '0':       #把对应听牌玩家座位号0-3的打出的牌分别存储到对应的玩家手中
						listener_0.append(pass_history[j])
                    elif pass_history[j][0] == '1':
                        listener_1.append(pass_history[j])
                    elif pass_history[j][0] == '2':
                        listener_2.append(pass_history[j])
                    elif pass_history[j][0] == '3':
                        listener_3.append(pass_history[j])
        print('listener_3', listener_3)
        print('listener_0', listener_0)
        self.simulate_lintener_hand(listener_all)      #开始模拟玩家的手牌
        # simulat_listenr_hand(listen_id,un_show_count)
        # 把听牌的座位号、未知牌矩阵传过去，
        # 根据听牌者出的牌，吃、碰、杠的牌近似模拟出他的手牌*******
        # 假设模拟出10种手牌，看打出去点炮的次数*******
        # 该函数放在每一个出牌之前，判断出该牌是点炮可能性大，
        # 如果可能性小于50%，打出改牌
        # 反之，重新执行出牌判断的过程，重新找一张牌重复上面几步，找到合适的牌输出。

    #模拟玩家的手牌
    def simulate_lintener_hand(self , listener_hand=[]):  # listener_hand 里面存贮听牌玩家的所有打出的手牌历史，list = [listener1,listener2...]
        # if listener_hand != '': ### 始终不为空
            for i in range(4):  #提取某一听牌玩家的手牌 len(listener_hand)===4
                time_C , time_P ,time_K = 0,0,0  #统计吃碰杠的次数，方便计算余下的牌怎样模拟
                if listener_hand[i] != '':       #该seat玩家听牌
                    print('当前在处理{}号玩家的打出的手牌：{}'.format(i, listener_hand[i]))
                    for j in range(len(listener_hand[i])):  #开始查看该听牌玩家打牌的历史list
                        if listener_hand[i][j][2] == 'C':      #吃牌处理
                            time_C += 1                     #吃次数+1
                            c1 = listener_hand[i][j][-1]       #获得‘0,Discard,B9’中的9
                            c2 = listener_hand[i][j][-2]       #获得‘0,Discard,B9’中的D
                            card = c2 + c1                  #组装这张牌 D+9 = D9
                            print('吃的一张牌：', card)
                            line , row = self._get_card_index(card)   #获得改牌的 line row 好在下面的调用中直接去矩阵中对应位置修改
                            self._full_array_listener(self, line, row, i, 'C')  # 填充模拟听玩家的手牌矩阵
                        if listener_hand[i][2] == 'P':       #碰牌处理
                            time_P += 1                      #碰的次数+1
                            c1 = listener_hand[i][j][-1]        #获得‘0,Discard,B9’中的9
                            c2 = listener_hand[i][j][-2]        #获得‘0,Discard,B9’中的D
                            card = c2 + c1                   #组装这张牌 D+9 = D9
                            print('碰的一张牌：', card)
                            line, row = self._get_card_index(card)              #获得改牌的 line row 好在下面的调用中直接去矩阵中对应位置修改
                            self._full_array_listener(self, line, row, i, 'P')  #填充模拟听玩家的手牌矩阵
                        if listener_hand[i][2] == 'K':        #杠牌处理
                            time_K += 1                       #杠的次数+1
                            c1 = listener_hand[i][j][-1]         #获得‘0,Discard,B9’中的9
                            c2 = listener_hand[i][j][-2]         #获得‘0,Discard,B9’中的D
                            card = c2 + c1                    #组装这张牌 D+9 = D9
                            print('杠的一张牌：', card)
                            line, row = self._get_card_index(card)              #获得改牌的 line row 好在下面的调用中直接去矩阵中对应位置修改
                            self._full_array_listener(self, line, row, i, 'K')  # 填充模拟听玩家的手牌矩阵
                        if listener_hand[i][2] == 'D':  # 打牌处理，不能让这些牌再在手牌中出现，又有点难做。。。。。
                            c1 = listener_hand[i][-1]  # 获得‘0,Discard,B9’中的9
                            c2 = listener_hand[i][-2]  # 获得‘0,Discard,B9’中的D
                            card = c2 + c1  # 组装这张牌 D+9 = D9
                            print('打出的一张牌：', card)
                            line, row = self._get_card_index(card)  # 获得改牌的 line row 好在下面的调用中直接去矩阵中对应位置修改
                        #吃、碰、杠、之后看自己还应该模拟几张牌，然后进行模拟其他牌，得到最终的手牌矩阵****
                        #1.看玩家剩余的牌，
                        simulate_num = 13 - time_C*3 - time_P*3 - time_K*3  #杠也按*3来算，只为方便计算，不会对最终有影响
                        #2.根据剩余个数进行模拟
                        self._simulate_rest_card(simulate_num)
                else:
                    continue  #该seat玩家没听牌

    #模拟玩家吃碰杠之后的牌（差一张胡）
    def _simulate_rest_card(self,num):
        #得到未莫的牌的矩阵
        show_count = self.ShowCount
        print('当前以知的手牌矩阵')
        print(show_count)
        # 初始化牌，每张牌都有四张
        total = np.zeros(shape=(3, 9), dtype='i1')
        for i in range(3):
            for j in range(9):
                total[i][j] = 4
        un_show_count = total - show_count
        print('输出当前未接牌的矩阵：')
        print(un_show_count)
        if num == 4 :  #假设D1D2D3D4D5D6D7D8D9,B1B1D2D3,至少有一对，
            pass
        if num == 7 :  #假设D1D2D3D4D5D6D,B1B1D1D2D3D9D 9,可以没有对子，有顺子或者刻子，半顺或者半刻子12或者11
            pass
        if num == 10:  #可以没有对子，剩下的顺子和刻字共2个，半顺或者半刻子12或者11
            pass
        if num == 13:  #可以没有对子，剩下都是刻字和顺子，差一张拼够对子
            pass

    #获得 吃、碰、杠的牌，然后在该玩家的模拟手牌矩阵中更新
    def _full_array_listener(self, line, row , listener_seat, action):
        if listener_seat == 0:
           if action == 'C':
              #吃牌的判断，首先看row的大小，其次才决定改顺子的位置
              if row == 0 :
                  simulate_listener_0[line][row] = 1
                  simulate_listener_0[line][row+1] = 1
                  simulate_listener_0[line][row+2] = 1
              elif row > 0 and row < 8 :
                  simulate_listener_0[line][row] = 1
                  simulate_listener_0[line][row - 1] = 1
                  simulate_listener_0[line][row + 1] = 1
              elif row == 8 :
                  simulate_listener_0[line][row] = 1
                  simulate_listener_0[line][row - 1] = 1
                  simulate_listener_0[line][row - 2] = 1
           if action == 'P':
              #更新改牌 line row ,在矩阵中*3
              simulate_listener_0[line][row] = 3
           if action == 'K':
              # 更新改牌 line row ,在矩阵中*4
              simulate_listener_0[line][row] = 4
        if listener_seat == 1:
            if action == 'C':
                # 吃牌的判断，首先看row的大小，其次才决定改顺子的位置
                if row == 0:
                    simulate_listener_1[line][row] = 1
                    simulate_listener_1[line][row + 1] = 1
                    simulate_listener_1[line][row + 2] = 1
                elif row > 0 and row < 8:
                    simulate_listener_1[line][row] = 1
                    simulate_listener_1[line][row - 1] = 1
                    simulate_listener_1[line][row + 1] = 1
                elif row == 8:
                    simulate_listener_1[line][row] = 1
                    simulate_listener_1[line][row - 1] = 1
                    simulate_listener_1[line][row - 2] = 1
            if action == 'P':
                # 更新改牌 line row ,在矩阵中*3
                simulate_listener_1[line][row] = 3
            if action == 'K':
                # 更新改牌 line row ,在矩阵中*4
                simulate_listener_1[line][row] = 4
        if listener_seat == 2:
            if action == 'C':
                # 吃牌的判断，首先看row的大小，其次才决定改顺子的位置
                if row == 0:
                    simulate_listener_2[line][row] = 1
                    simulate_listener_2[line][row + 1] = 1
                    simulate_listener_2[line][row + 2] = 1
                elif row > 0 and row < 8:
                    simulate_listener_2[line][row] = 1
                    simulate_listener_2[line][row - 1] = 1
                    simulate_listener_2[line][row + 1] = 1
                elif row == 8:
                    simulate_listener_2[line][row] = 1
                    simulate_listener_2[line][row - 1] = 1
                    simulate_listener_2[line][row - 2] = 1
            if action == 'P':
                # 更新改牌 line row ,在矩阵中*3
                simulate_listener_2[line][row] = 3
            if action == 'K':
                # 更新改牌 line row ,在矩阵中*4
                simulate_listener_2[line][row] = 4
        if listener_seat == 3:
            if action == 'C':
                # 吃牌的判断，首先看row的大小，其次才决定改顺子的位置
                if row == 0:
                    simulate_listener_3[line][row] = 1
                    simulate_listener_3[line][row + 1] = 1
                    simulate_listener_3[line][row + 2] = 1
                elif row > 0 and row < 8:
                    simulate_listener_3[line][row] = 1
                    simulate_listener_3[line][row - 1] = 1
                    simulate_listener_3[line][row + 1] = 1
                elif row == 8:
                    simulate_listener_3[line][row] = 1
                    simulate_listener_3[line][row - 1] = 1
                    simulate_listener_3[line][row - 2] = 1
            if action == 'P':
                # 更新改牌 line row ,在矩阵中*3
                simulate_listener_3[line][row] = 3
            if action == 'K':
                # 更新改牌 line row ,在矩阵中*4
                simulate_listener_3[line][row] = 4


    #玩家摸牌后的或者吃碰之后的处理
    def _think_and_deal(self):
        '''
        处理自己的牌，并思考如何打什么牌
        :return:
        '''
        #获得当前的手牌
        print('自己的程序运行了。。')
        now_hand_card1 = self.MessData['hand']
        print('deal_ourself当前的手牌是啥：',now_hand_card1)
        print('上一玩家出的牌是{}'.format(self.Now_Deal))
        #print('deal_ourself_out正在处理的牌是：', self.Now_Deal)
        #当前的手牌矩阵
        now_hand_card = copy.deepcopy(self.StateData[self.player_seat, 0])
        print('deal_ourself输出当前手牌的矩阵：')
        print(now_hand_card)
        # 判断接到该牌是否胡了
        is_hu, _ = self._check_hu(now_hand_card)
        logging.debug("胡牌判断：%s", is_hu)
        if is_hu:
            #胡牌前看一下剩余牌的矩阵
            show_count = self.ShowCount
            print('当前以知的手牌矩阵')
            print(show_count)
            # 初始化牌，每张牌都有四张
            total = np.zeros(shape=(3, 9), dtype='i1')
            for i in range(3):
                for j in range(9):
                    total[i][j] = 4
            un_show_count = total - show_count
            print('输出当前未摸牌的矩阵：')
            print(un_show_count)
            self._conv_req_mess('Win', self.Now_Deal)
            return
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
        #遍历手牌矩阵，找到适合的牌输出
        for line in range(3):  #0:B, 1:C, 2:D.
            for row in range(9):
                if row == 0 and now_hand_card[line][row] == 1 and now_hand_card[line][row+1] == 0 :#判断在最左侧的牌10
                    print('打出的牌是{}'.format(self._get_card_str(line, row)))
                    print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                    self._conv_req_mess('Discard最左10', self._get_card_str(line, row), '')  # 那就直接输出
                    return
                elif row == 8 and now_hand_card[line][row] == 1 and now_hand_card[line][row-1] == 0 :#判断在最右侧的牌01
                    print('打出的牌是{}'.format(self._get_card_str(line, row)))
                    print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                    self._conv_req_mess('Discard最右01', self._get_card_str(line, row), '')  # 那就直接输出改牌
                    return
                elif now_hand_card[line][row] == 1 and now_hand_card[line][row-1] == 0 and now_hand_card[line][row+1] == 0 :#010，标准单牌
                    print('打出的牌是{}'.format(self._get_card_str(line,row)))
                    print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                    self._conv_req_mess('Discard两边010', self._get_card_str(line, row), '')#那就直接输出改牌
                    return
                #判断对子，并找对子附近得牌打出
                elif now_hand_card[line][row] == 2 :
                    if row == 0 and now_hand_card[line][row] == 2 and now_hand_card[line][row+1] == 1 \
                        and now_hand_card[line][row+2] == 0 : #112打出2
                        print('打出的牌是{}'.format(self._get_card_str(line, row+1)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row+1))
                        self._conv_req_mess('Discard双边7889', self._get_card_str(line, row+1), '')
                    elif row == 0 and now_hand_card[line][row] == 2 and now_hand_card[line][row+1] == 1 and \
                        now_hand_card[line][row+2] == 1 and now_hand_card[line][row+3] == 0 : #1123时打出 1
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                        self._conv_req_mess('Discard双边7889', self._get_card_str(line, row), '')#把1123打出去1变为123
                    elif row < 7 and row > 0 and now_hand_card[line][row] == 2 and now_hand_card[line][row-1] == 1 and now_hand_card[line][row+1] == 1 \
                      and now_hand_card[line][row+2] ==0: #双边对子1223
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                        self._conv_req_mess('Discard双边6778', self._get_card_str(line, row), '')  # 1223那就打2变为123
                        return
                    elif row ==7 and now_hand_card[line][row-1] == 0 and now_hand_card[line][row] ==2 \
                        and now_hand_card[line][row+1] ==1:  #889,打出9
                        print('打出的牌是{}'.format(self._get_card_str(line, row+1)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row+1))
                        self._conv_req_mess('Discard双边6678', self._get_card_str(line, row+1), '')  # 889打出9
                        return
                    elif row == 7 and now_hand_card[line][row-2] == 0 and now_hand_card[line][row-1] == 1 and \
                        now_hand_card[line][row] == 2 and now_hand_card[line][row+1] == 1:
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                        self._conv_req_mess('Discard双边6678', self._get_card_str(line, row), '')  # 7889打出8变为789
                        return
                    elif row == 8 and now_hand_card[line][row-1] == 1 and now_hand_card[line][row] ==2 and \
                            now_hand_card[line][row-2] == 0 :  #899,打出9
                        print('打出的牌是{}'.format(self._get_card_str(line, row-1)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row-1))
                        self._conv_req_mess('Discard双边6678', self._get_card_str(line, row-1), '')  # 889打出9
                        return
                    elif row == 8 and now_hand_card[line][row-3] == 0 and now_hand_card[line][row-2] == 1 and \
                        now_hand_card[line][row-1] ==1 and now_hand_card[line][row] == 2 : #7899,打出9
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的行列是：line = {}, row = {}'.format(line, row))
                        self._conv_req_mess('Discard双边6678', self._get_card_str(line, row), '')  # 7899打出9
                        return
                elif row == 0 and now_hand_card[line][row] == 1 and now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 1 \
                    and now_hand_card[line][row+3] == 1 and now_hand_card[line][row+4] == 1 and now_hand_card[line][row+5] ==0 : #4连1234，再接一张5，打出5
                    print('打出的牌是{}'.format(self._get_card_str(line, row+4)))
                    print('4+1,打1；；打出牌的位置是lin={},ro={}'.format(line, row+4))
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row+4), '')  #12345没6接5，打5
                    return
                elif row ==1 and now_hand_card[line][row-1]==1 and now_hand_card[line][row] == 1 and now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 1 \
                    and now_hand_card[line][row+3] == 1 and now_hand_card[line][row+4] == 1 and now_hand_card[line][row+5] ==0 : #4连2345，再接一张1，没6打出1
                    print('打出的牌是{}'.format(self._get_card_str(line, row-1)))
                    print('4+1,打1；；打出牌的位置是lin={},ro={}'.format(line, row-1))
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row-1), '')  #2345没6接1，打1
                    return
                elif row >=1 and row <= 3 and now_hand_card[line][row] == 1 and now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 1 \
                    and now_hand_card[line][row+3] == 1 and now_hand_card[line][row+4] == 1 and now_hand_card[line][row+5] == 0: #4连2345，再接一张5，打出5
                    print('打出的牌是{}'.format(self._get_card_str(line, row+4)))
                    print('4+1,打5；；打出牌的位置是lin={},ro={}'.format(line, row+4))
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row+4), '')  # 那就直接输出改牌
                    return
                elif row == 4 and now_hand_card[line][row-1] == 0 and now_hand_card[line][row] == 1 and now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 1 \
                    and now_hand_card[line][row+3] == 1 and now_hand_card[line][row+4] == 1: #4连5678没4，再接一张9，打出5
                    print('打出的牌是{}'.format(self._get_card_str(line, row)))
                    print('4+1,打5；；打出牌的位置是lin={},ro={}'.format(line, row))
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row), '')  #5678，没4接9，打5
                    return
                elif row == 4 and now_hand_card[line][row-2]==0 and now_hand_card[line][row-1] == 1 and now_hand_card[line][row] == 1  and now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 1 \
                    and now_hand_card[line][row+3] == 1 and now_hand_card[line][row+4] == 0 : #4连5678，没9，没3再接一张4，打出8
                    print('打出的牌是{}'.format(self._get_card_str(line, row+3)))
                    print('4+1,打5；；打出牌的位置是lin={},ro={}'.format(line, row+3))
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row+3), '')  # 5678，没4，接4.打8
                    return
                elif row == 5 and now_hand_card[line][row-2] ==0 and now_hand_card[line][row-1] ==1 and now_hand_card[line][row] ==1 and now_hand_card[line][row+1] ==1 and \
                    now_hand_card[line][row+2] == 1 and now_hand_card[line][row+3] == 1 : #6789,没4，接5，打5
                    print('打出的牌是{}'.format(self._get_card_str(line, row-1)))
                    print('4+1,打5；；打出牌的位置是lin={},ro={}'.format(line, row-1))
                    self._conv_req_mess('Discard4连+1', self._get_card_str(line, row-1), '')  # 5678，没4，接4.打8
                    return
                elif row < 6 and now_hand_card[line][row] == 1 and now_hand_card[line][row+3] == 1:#手牌1234
                    if now_hand_card[line][row+1] == 2 and now_hand_card[line][row+2] == 1:#手牌1234，接到2，打出1
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        self._conv_req_mess('Discard4连（1234）接2', self._get_card_str(line, row), '')
                        return
                    elif now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 2 and now_hand_card[line][row+3] == 0:#手牌1234，接到3，打出4
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 3))) #1234,没5，接3打4
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        self._conv_req_mess('Discard4连（1234）接3', self._get_card_str(line, row + 3), '')
                        return
                elif row < 2 and now_hand_card[line][row] == 1 and now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 1 and \
                    now_hand_card[line][row+3] == 1 and now_hand_card[line][row+4] == 1 and now_hand_card[line][row+5] == 1 and \
                    now_hand_card[line][row+6] == 1 :
                    if now_hand_card[line][row+7] == 1:   #测试这里B2B3B3B4B4B8B9B9
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 7)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 7), '')#手牌1234567，接到一张8，打出8
                        return
                elif row < 3 and now_hand_card[line][row] == 1 and now_hand_card[line][row+3] == 1 and now_hand_card[line][row+6] == 1 :#7连1234567
                    if now_hand_card[line][row+1] == 2 and now_hand_card[line][row+2] == 1 and now_hand_card[line][row+4] == 1 \
                     and now_hand_card[line][row+5] == 1 :
                        print('打出的牌是{}'.format(self._get_card_str(line, row)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        self._conv_req_mess('Discard', self._get_card_str(line, row), '')  # 手牌1234567，接到一张2，打出1
                        return
                    elif now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 2 and now_hand_card[line][row+4] == 1 \
                     and now_hand_card[line][row+5] == 1 :
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 3)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        self._conv_req_mess('Discard', self._get_card_str(line, row+3), '')  # 手牌1234567，接到一张3，打出4
                        return
                    elif now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 1 and now_hand_card[line][row+4] == 2 \
                     and now_hand_card[line][row+5] == 1 :
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 3)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 3), '')  # 手牌1234567，接到一张5，打出4
                        return
                    elif now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 1 and now_hand_card[line][row+4] == 1 \
                     and now_hand_card[line][row+5] == 2 :
                        print('打出牌的位置是lin={},ro={}'.format(line, row))
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 6)))
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 6), '')  # 手牌1234567，接到一张6，打出7
                        return
                elif now_hand_card[line][row] == 3 :       #打出刻子31旁边的1这章单牌
                    if row == 0 and now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 0 :#1112打出2
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row+1))
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 1), '')  # 手牌2223打出2
                        return
                    elif row < 7 and row > 0 and now_hand_card[line][row+1] ==1 and now_hand_card[line][row+2] == 0: #122
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row+1))
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 1), '')  # 手牌2223打出3
                        return
                    elif row == 1 and now_hand_card[line][row-1] == 1 : #1222,打出1
                        print('打出的牌是{}'.format(self._get_card_str(line, row -1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row-1))
                        self._conv_req_mess('Discard', self._get_card_str(line, row -1), '')  # 手牌1222打出3
                        return
                    elif row == 1 and now_hand_card[line][row+1] == 1 and now_hand_card[line][row+2] == 0 :
                        print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row+1))
                        self._conv_req_mess('Discard', self._get_card_str(line, row + 1), '')  # 手牌1222打出3
                        return
                    elif row < 7 and row > 1 and now_hand_card[line][row+1] == 0 and now_hand_card[line][row-1] == 1\
                            and now_hand_card[line][row-2] ==0: #2333
                        print('打出的牌是{}'.format(self._get_card_str(line, row -1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row-1))
                        self._conv_req_mess('Discard', self._get_card_str(line, row -1), '')  # 手牌#2333打出2
                        return
                    elif row == 7 :  #手牌7888，8889打出7 或者9  /  8999 打出8
                        if now_hand_card[line][row-2] == 0 and now_hand_card[line][row-1] == 1 :
                          print('打出的牌是{}'.format(self._get_card_str(line, row - 1)))
                          print('打出牌的位置是lin={},ro={}'.format(line, row-1))
                          self._conv_req_mess('Discard', self._get_card_str(line, row-1), '')  # 手牌8999打出8
                          return
                        elif now_hand_card[line][row-2] == 0 and now_hand_card[line][row+1] == 1 :
                          print('打出的牌是{}'.format(self._get_card_str(line, row + 1)))
                          print('打出牌的位置是lin={},ro={}'.format(line, row+1))
                          self._conv_req_mess('Discard', self._get_card_str(line, row + 1), '')  # 手牌8889打出9
                          return
                    elif row == 8 and now_hand_card[line][row-2] == 0 and now_hand_card[line][row-1] == 1: #8999打出8
                        print('打出的牌是{}'.format(self._get_card_str(line, row - 1)))
                        print('打出牌的位置是lin={},ro={}'.format(line, row-1))
                        self._conv_req_mess('Discard', self._get_card_str(line, row - 1), '')  # 手牌8889打出9
                        return
                #如果这些都没有那就得在补充了


    def _del_other_out(self):
        '''
        处理对手玩家打牌
        :return:
        '''
        temp_hand_count = copy.deepcopy(self.StateData[self.player_seat, 0])
        #print('deal_other_out输出当前手牌的矩阵：')
        #print( temp_hand_count)
        line, row = self._get_card_index(self.Now_Deal)
        print('Now_Deal: line = {},row = {}'.format(line,row))
        #print('输出下line ={},row={}'.format(line,row))
        temp_hand_count[line, row] += 1
        print('line row 位置上的值是：',temp_hand_count[line][row])
        print(temp_hand_count)
        print('deal_outher_out正在处理的牌是：',self.Now_Deal)
        is_hu, _ = self._check_hu(temp_hand_count)
        logging.debug("胡牌判断：%s", is_hu)
        if is_hu:
            self._conv_req_mess('Win', self.Now_Deal)
            return
        try:
            can_gang, gang_count = self._check_gang(self.player_seat, is_self=False)
            if can_gang:  #补扛
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
                #对子  刻子 旁边不吃  分别判断三个位置，
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
    #用字典测试  dealer:庄家  seat:玩家座号 0,discard,B2
    test_str = {"pon_hand":"","kon_hand":"","chow_hand":"","hand":"C1C1C1C6C6C6D4D4D4B2B2B5B5B8","history":[""],"dealer":0,"seat":0,"special":""}
    test = Pubilc_MahJong(json.dumps(test_str))
    Req_Mess = test.get_game_req()
    print('看下Req_Mess是啥：',Req_Mess)
