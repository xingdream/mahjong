import time
import copy
import random as rd
import numpy as np

class Player(object):    
    def __init__(self,pnum):
        self.nwl=0
        self.pnum=pnum
        self.chips=20000
        self.self_action=["THP","THP"]
        self.opponent_action=["THP","THP"]
        self.game_data=[]
        self.round_data=[]
    def strategy_input(self,pt):
        print("self_cards: ",end=" ")
        pt.Print_pcard(self.pnum)
        next_action=[-1,-1]
        taction=input().split(' ')
        if len(taction)==2:
            next_action[0]=taction[0]
            next_action[1]=int(taction[1])
        else:
            next_action[0]=taction[0]
            if next_action[0]!="fold":
                next_action[1]=pt.p_bet_chip[(self.pnum+1)%2]
            
        return next_action
    def strategy_random(self,pt):
        next_action=pt.Get_Next_action(self.pnum)
        return next_action[rd.randint(0, len(next_action))]
        # return next_action[0]
    def strategy_wl(self,pt):
        next_action=pt.Get_Next_action(self.pnum)
        #print(next_action)
        self.nwl=pt.win_rate[self.pnum]
        k=len(next_action)
        maxs=-pt.p_bet_chip_sum[self.pnum]
        raction=["fold",-1]
        for tk in range(1,k):
            if next_action[tk][0]!="raise":
                tmaxs=(2*self.nwl-1-next_action[tk][1]/20000)*(next_action[tk][1])
                if maxs<tmaxs:
                    maxs=tmaxs
                    raction=[next_action[tk][0],next_action[tk][1]]
            else:
                minchip=100
                if next_action[tk][1]>0:
                    minchip=next_action[tk][1]*2
                for tchip in  range(minchip,next_action[tk][2]):
                    tmaxs=(2*self.nwl-1-tchip/20000)*(tchip)
                    if maxs<tmaxs:
                        maxs=tmaxs
                        raction=[next_action[tk][0],tchip]

        return raction
    def strategy_wlc(self,pt,ave_chip,opponent_chip):
        chip_rate=(opponent_chip-ave_chip)/20000*(opponent_chip/ave_chip)
        next_action=pt.Get_Next_action(self.pnum)
        self.nwl=pt.win_rate[self.pnum]
        k=len(next_action)
        maxs=-pt.p_bet_chip_sum[self.pnum]
        raction=["fold",-1]
        minchip=100
        for tk in range(1,k):
            if next_action[tk][0]!="raise":
                tmaxs=(2*self.nwl-1-next_action[tk][1]/20000)*(next_action[tk][1])-next_action[tk][1]*(chip_rate)
                if maxs<tmaxs:
                    maxs=tmaxs
                    raction=[next_action[tk][0],next_action[tk][1]]
            else:
                if next_action[tk][1]>0:
                    minchip=next_action[tk][1]*2
                for tchip in  range(minchip,next_action[tk][2]):
                    tmaxs=(2*self.nwl-1-tchip/20000)*(tchip)-tchip*(chip_rate)
                    if maxs<tmaxs:
                        maxs=tmaxs
                        raction=[next_action[tk][0],tchip]
        if raction[0]=="raise" and self.nwl>0.7:
            k=rd.randint(0,9)
            if k<5 and minchip+ave_chip<20000:
                raction[1]=minchip+int(ave_chip)
        

        return raction
    def strategy_ave_chip_map(self,pt,ave_chip_self,ave_chip_opponent,opponent_chip):
        self_raise_chip=(20000-ave_chip_self)/(20000-ave_chip_opponent)*(opponent_chip-ave_chip_opponent)+ave_chip_self
        action=["raise",self_raise_chip]
        pt.Do_next((self.pnum+1)%2,action)
        action=self.strategy_wlc(pt,ave_chip_opponent,opponent_chip)
        if action[0]=="raise":
            action[1]=(20000-ave_chip_opponent)/(20000-ave_chip_self)*(self_raise_chip-ave_chip_self)+ave_chip_opponent
        return action

class CT:
    def __init__(self,number,amount):
        self.cn=number
        self.ca=amount

class Poker_Table:
    def Init(self):
        self.stage=0
        self.end_flag=0
        self.win_flag=-1
        self.action_sum=0
        self.small_blind=rd.randint(0,100)%2
        self.big_blind=(self.small_blind+1)%2
        self.cards=np.ones([13,4])
        self.public_card=np.zeros([5,2])
        self.p_card=np.zeros([2,2,2])
        self.p_now_chip=[20000,20000]
        self.p_bet_chip=[0,0]
        self.p_bet_chip_sum=[0,0]
        self.earnings=[0,0]
        self.win_rate=[0,0]
        self.ts=0
    
    def Set_now_chip(self,chip0,chip1):
        self.p_now_chip[0]=chip0
        self.p_now_chip[1]=chip1

    def Get_public_card(self):
        if self.stage==1:
            i=0
            c_num=0
            for i in range(4):
                c_num=self.Get_one_card_random()
                self.p_card[i//2][i%2][0]=c_num//4
                self.p_card[i//2][i%2][1]=c_num%4
        elif self.stage==2:
            i=0
            c_num=0
            for i in range(3):
                c_num=self.Get_one_card_random()
                self.public_card[i][0]=c_num//4
                self.public_card[i][1]=c_num%4
        elif self.stage==3:
            c_num=0
            c_num=self.Get_one_card_random()
            self.public_card[3][0]=c_num//4
            self.public_card[3][1]=c_num%4
        elif self.stage==4:
            c_num=0
            c_num=self.Get_one_card_random()
            self.public_card[4][0]=c_num//4
            self.public_card[4][1]=c_num%4
        return 0
    
    def Get_one_card_random(self):
        k=0
        c_num=0
        while k<1:
            c_num=rd.randint(0,51)
            if self.cards[c_num//4][c_num%4]==1:
                self.cards[c_num//4][c_num%4]=0
                k+=1

        return c_num
    
    def Start_stage(self,card_info="",pnum=-1):
        if self.stage==0:
            self.Do_next(self.small_blind,["raise",50])
            self.Do_next(self.big_blind,["raise",100])
            self.action_sum=0
            self.stage+=1
            if card_info=="":
                self.Get_public_card()
            else:
                self.Set_Card(card_info,pnum)
            self.win_rate[0]=self.Get_Winrate(0)
            self.win_rate[1]=self.Get_Winrate(1)
        elif self.stage<4:
            self.stage+=1
            if card_info=="":
                self.Get_public_card()
            else:
                self.Set_Card(card_info)
            self.p_now_chip[0] = self.p_now_chip[0] - self.p_bet_chip[0]
            self.p_now_chip[1] = self.p_now_chip[1] - self.p_bet_chip[1]
            self.p_bet_chip_sum[0] += self.p_bet_chip[0]
            self.p_bet_chip_sum[1] += self.p_bet_chip[1]
            self.p_bet_chip[0] = 0
            self.p_bet_chip[1] = 0
            self.win_rate[0]=self.Get_Winrate(0)
            self.win_rate[1]=self.Get_Winrate(1)
        elif self.stage==4:
            self.stage+=1
            self.end_flag=1
            self.p_now_chip[0] = self.p_now_chip[0] - self.p_bet_chip[0]
            self.p_now_chip[1] = self.p_now_chip[1] - self.p_bet_chip[1]
            self.p_bet_chip_sum[0] += self.p_bet_chip[0]
            self.p_bet_chip_sum[1] += self.p_bet_chip[1]
            self.p_bet_chip[0] = 0
            self.p_bet_chip[1] = 0
            self.win_rate[0]=self.Get_Winrate(0)
            self.win_rate[1]=self.Get_Winrate(1)

        return 0

    def Do_next(self,pnum,taction):
        self.action_sum+=1
        if taction[0]=="fold":
            self.end_flag=2
            self.win_flag=(pnum+1)%2
            self.p_bet_chip_sum[0]+=self.p_bet_chip[0]
            self.p_bet_chip_sum[1]+=self.p_bet_chip[1]
        elif taction[0]=="call" or taction[0]=="check":
            self.p_bet_chip[pnum]=self.p_bet_chip[(pnum+1)%2]
            if self.p_bet_chip[pnum]==self.p_now_chip[pnum]:
                while self.stage<5:
                    self.Start_stage()
        elif taction[0]=="raise":
            self.p_bet_chip[pnum]=taction[1]
            if self.p_bet_chip[(pnum+1)%2]==self.p_now_chip[(pnum+1)%2]:
                while self.stage<5:
                    self.Start_stage()
        elif taction[0]=="allin":
            self.p_bet_chip[pnum]=self.p_now_chip[pnum]
            if self.p_bet_chip[pnum] <= self.p_bet_chip[(pnum+1)%2]:
                while self.stage<5:
                    self.Start_stage()
            elif self.p_bet_chip[(pnum+1)%2] == self.p_now_chip[(pnum+1)%2]:
                while self.stage<5:
                    self.Start_stage()

        return 0
    
    def Get_Next_pnum(self,pnow):
        pnext=(pnow+1)%2
        if self.end_flag==0 and self.p_bet_chip[0]==self.p_bet_chip[1] and self.action_sum>=2:
            self.Start_stage()
            self.action_sum=0
            pnext=self.big_blind
        if self.end_flag!=0:
            if self.end_flag==1:
                self.Win_judge()
            self.Get_S()
            pnext=-1

        return pnext
    
    def Is_start_stage(self):
        if self.end_flag==0 and self.p_bet_chip[0]==self.p_bet_chip[1] and self.action_sum>=2:
            return 1
        else:
            return 0

    def Win_judge(self):
        level0,rcards0=self.Test_CW(0)
        level1,rcards1=self.Test_CW(1)
        if level0>level1:
            self.win_flag=0
        elif level1>level0:
            self.win_flag=1
        else:
            for k in range(5):
                if rcards0[k]>rcards1[k]:
                    self.win_flag=0
                    break
                elif rcards0[k]<rcards1[k]:
                    self.win_flag=1
                    break
        return 0
    def Test_CW(self,pnum):
        all_card=np.vstack((self.p_card[pnum],self.public_card))
        all_card=sorted(all_card,key=(lambda x:x[0]),reverse=True)
        level,rcards = self.Get_Level(all_card)

        return level,rcards
    def Get_Level(self,all_card):
        tcards=[]
        rcards=[]
        tamount=1
        tsum=0
        color_num=-1
        level=-1
        for k in  range(6):
            if all_card[k][0]==all_card[k+1][0]:
                tamount+=1
            else:
                ct=[all_card[k][0],tamount]
                tcards.append(ct)
                tamount=1
        ct=[all_card[k+1][0],tamount]
        tcards.append(ct)

        tamount=len(tcards)
        if tamount>=5:
            color_sum = [0, 0, 0, 0]
            color_num = -1
            for i in range(7):
                color_sum[int(all_card[i][1])]+=1
                if color_sum[int(all_card[i][1])]>=5:
                    color_num = all_card[i][1]
                    break
            for k in range(7):
                if all_card[k][1]==color_num:
                    rcards.append(all_card[k][0])
            tamount=len(rcards)
            tsum=1

            if tamount>=5:
                for k in  range(tamount-1):
                    if rcards[k]-rcards[k+1]==1 and tsum<5:
                        tsum+=1
                    else:
                        if tsum==5:
                            level=8
                            rcards=rcards[k-4:k+1]
                            break
                        else:
                            tsum=1
                if level==-1 and tsum==5:
                        level=8
                        rcards=rcards[tamount-5:tamount]
                
                if level==-1:
                    level=5
                    rcards=rcards[0:5]
            else:
                tamount=len(tcards)
                if tamount>=5:
                    for k in range(tamount-1):
                        if tcards[k][0]-tcards[k+1][0]==1 and tsum<5:
                            tsum+=1
                        else:
                            if tsum==5:
                                level=4
                                tempc=tcards[k-4:k+1]
                                rcards=[]
                                for tc in tempc:
                                    rcards.append(tc[0])
                                break
                            else:
                                tsum=1
                    if level==-1 and tsum==5:
                        level=4
                        tempc=tcards[tamount-5:tamount]
                        rcards=[]
                        for tc in tempc:
                            rcards.append(tc[0])
        if level==-1:
            tsum=0
            rcards=[]
            tcards=sorted(tcards,key=(lambda x:(x[1],x[0])),reverse=True)
            maxc=-1
            sk=len(tcards)
            if tcards[0][1]==4:
                level=7
                for k in range(1,sk):
                    if maxc<tcards[k][0]:
                        maxc=tcards[k][0]
                for k in range(4):
                    rcards.append(tcards[0][0])
                rcards.append(maxc)
            elif tcards[0][1]==3 and tcards[1][1]>=2:
                level=6
                for k in range(1,sk):
                    if maxc<tcards[k][0] and tcards[k][1]>=2:
                        maxc=tcards[k][0]
                for k in range(3):
                    rcards.append(tcards[0][0])
                for k in range(2):
                    rcards.append(maxc)
            elif tcards[0][1]==3 and tcards[1][1]==1:
                level=3
                for k in range(3):
                    rcards.append(tcards[0][0])
                for k in range(2):
                    rcards.append(tcards[k+1][0])
            elif tcards[0][1]==2 and tcards[1][1]==2:
                level=2
                if tcards[2][1]==2:
                    if tcards[2][0]<tcards[3][0]:
                        maxc=tcards[3][0]
                    else:
                        maxc=tcards[2][0]
                else:
                    maxc=tcards[2][0]
                for k in range(2):
                    rcards.append(tcards[0][0])
                for k in range(2):
                    rcards.append(tcards[1][0])
                rcards.append(maxc)
            elif tcards[0][1]==2 and tcards[1][1]==1:
                level=1
                for k in range(2):
                    rcards.append(tcards[0][0])
                for k in range(3):
                    rcards.append(tcards[k+1][0])
            elif tcards[0][1]==1:
                 level=0
                 for k in range(5):
                    rcards.append(tcards[k][0])
        return level,rcards

    def Get_S(self):
        S=[0,0]
        if self.win_flag==0:
            S[0]=self.p_bet_chip_sum[1]
            S[1]=-self.p_bet_chip_sum[1]
        elif self.win_flag==1:
            S[0]=-self.p_bet_chip_sum[0]
            S[1]=self.p_bet_chip_sum[0]

        self.earnings[0]=S[0]
        self.earnings[1]=S[1]

        return S

    def Get_Next_action(self,pnum):
        tnum=(pnum+1)%2
        taction=[]
        taction.append(["fold",-1])
        if self.p_bet_chip[tnum]==self.p_bet_chip[pnum]:
            taction.append(["check",self.p_bet_chip[tnum]])
        elif self.p_bet_chip[tnum]>self.p_bet_chip[pnum]:
            taction.append(["call",self.p_bet_chip[tnum]])
        if self.p_now_chip[pnum]>self.p_bet_chip[tnum]:
            taction.append(["raise",self.p_bet_chip[tnum],self.p_now_chip[pnum]])
        if self.p_now_chip[pnum]>self.p_bet_chip[pnum]:
            taction.append(["allin",self.p_now_chip[pnum]])
        return taction

    def Get_Winrate(self,pnum,sum=500):
        win_sum=0
        for i in range(sum):
            t=self.Get_res_random(pnum)
            if t>=0:
                win_sum+=1
        self.win_rate[pnum]=win_sum/sum
        return (win_sum/sum)
    def Get_res_random(self,pnum):
        res=0
        card_temp=copy.deepcopy(self.cards)
        public_card_temp=copy.deepcopy(self.public_card)
        p_card_temp=copy.deepcopy(self.p_card)
        for i in range(2):
            cnum=self.Simulate_one_card(card_temp)
            p_card_temp[(pnum+1)%2][i][0]=cnum//4
            p_card_temp[(pnum+1)%2][i][1]=cnum%4
        if self.stage==1:
            for i in range(5):
                cnum=self.Simulate_one_card(card_temp)
                public_card_temp[i][0]=cnum//4
                public_card_temp[i][1]=cnum%4
        elif self.stage==2:
            for i in range(3,5):
                cnum=self.Simulate_one_card(card_temp)
                public_card_temp[i][0]=cnum//4
                public_card_temp[i][1]=cnum%4
        elif self.stage==3:
            for i in range(4,5):
                cnum=self.Simulate_one_card(card_temp)
                public_card_temp[i][0]=cnum//4
                public_card_temp[i][1]=cnum%4

        all_card=np.vstack((p_card_temp[pnum],public_card_temp))
        all_card=sorted(all_card,key=(lambda x:x[0]),reverse=True)
        level_s,rcards_s = self.Get_Level(all_card)

        all_card=np.vstack((p_card_temp[(pnum+1)%2],public_card_temp))
        all_card=sorted(all_card,key=(lambda x:x[0]),reverse=True)
        level_o,rcards_o = self.Get_Level(all_card)

        if level_s>level_o:
            res=1
        elif level_o>level_s:
            res=-1
        else:
            try:
                for k in range(5):
                    if rcards_s[k]>rcards_o[k]:
                        res=1
                        break
                    elif rcards_s[k]<rcards_o[k]:
                        res=-1
                        break
            except:
                print(all_card)
                print(level_o,rcards_o)
        return res
    def Simulate_one_card(self,card_temp):
        k=0
        c_num=0
        while k<1:
            c_num=rd.randint(0,51)
            if card_temp[c_num//4][c_num%4]==1:
                card_temp[c_num//4][c_num%4]=0
                k+=1
        return c_num
    
    def Set_Card(self,card_info,pnum=-1):
        TDATA=card_info.split('#')
        if pnum!=-1:
            for i in range(2):
                c_num=TDATA[i].split('*')
                self.p_card[pnum][i%2][0]=int(c_num[0])
                self.p_card[pnum][i%2][1]=int(c_num[1])
                self.cards[int(c_num[0])][int(c_num[1])]=0
        elif self.stage==1:
            for i in range(2):
                c_num=TDATA[i].split('*')
                self.p_card[0][i%2][0]=int(c_num[0])
                self.p_card[0][i%2][1]=int(c_num[1])
                self.cards[int(c_num[0])][int(c_num[1])]=0
        elif self.stage==2:
            for i in range(3):
                c_num=TDATA[i].split('*')
                self.public_card[i][0]=int(c_num[0])
                self.public_card[i][1]=int(c_num[1])
                self.cards[int(c_num[0])][int(c_num[1])]=0
        elif self.stage==3:
            c_num=TDATA[0].split('*')
            self.public_card[3][0]=int(c_num[0])
            self.public_card[3][1]=int(c_num[1])
            self.cards[int(c_num[0])][int(c_num[1])]=0
        elif self.stage==4:
            c_num=TDATA[0].split('*')
            self.public_card[4][0]=int(c_num[0])
            self.public_card[4][1]=int(c_num[1])
            self.cards[int(c_num[0])][int(c_num[1])]=0
        return 0
    
    def Recover_Public_Card(self,stage):
        self.stage=stage
        if self.stage==1:
            for i in range(3):
                self.cards[int(self.public_card[i][0])][int(self.public_card[i][1])]=1
                self.public_card[i][0]=0
                self.public_card[i][1]=0
        elif self.stage==2:
            self.cards[int(self.public_card[3][0])][int(self.public_card[3][1])]=1
            self.public_card[3][0]=0
            self.public_card[3][1]=0
        elif self.stage==3:
            self.cards[int(self.public_card[4][0])][int(self.public_card[4][1])]=1
            self.public_card[4][0]=0
            self.public_card[4][1]=0

    def Out_pt(self):
        print("stage "+str(self.stage))
        print("p_now_chip " + str(self.p_now_chip[0]) + " " + str(self.p_now_chip[1]))
        print("p_bet_chip " + str(self.p_bet_chip[0]) + " " + str(self.p_bet_chip[1]))
        print("p_bet_chip_sum " + str(self.p_bet_chip_sum[0]) + " " + str(self.p_bet_chip_sum[1]))
        print("###########################################################################################")

    def test(self):
        act = ""
        chip = 0
        asum = 0
        pnow = 0
        self.Start_stage()
        self.Out_pt()
        while True:
            print("p" + str(pnow) + " ",end="")
            act = input()
            if act == "raise":
                chip = int(input())
            self.Do_next(pnow, [act,chip])
            asum+=1
            pnow=self.Get_Next_pnum(pnow)
            self.Out_pt()
            if pnow==-1:
                print("end " + str(self.end_flag))
                print(str(self.earnings[0]) + " " + str(self.earnings[1]))
                break
        return 0
    
    def Print_pcard(self,pnum):
        k=0
        print(self.p_card[pnum][0],end=" ")
        print(self.p_card[pnum][1],end=" ")
        if self.stage==2:
            k=3
        elif self.stage==3:
            k=4
        elif self.stage==4:
            k=5
        for i in range(k):
            print(self.public_card[i],end=" ")
        print()

poker = Poker_Table()
poker.Init()
poker.test()
