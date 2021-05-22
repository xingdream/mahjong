import random as rd
import copy
import math
import numpy as np
import os
import time 
import multiprocessing
from THP_Poker_Table import Poker_Table as TPT
from THP_Poker_Table import Player

class Tnode(object):
    def __init__(self,stage,node_type,node_num):
        self.node_num=node_num
        self.node_type=node_type # -1:根节点 0:叶子节点_己方弃牌  1:叶子节点_对方弃牌  2:叶子节点_比牌  3:分支节点
        self.stage=stage
        self.relative_ratio=0
        self.winrate=0.5
        self.fold_sum=0
        self.action_vq=np.array([[0,0,0,0,0],[0,0,0,0,0]]) # 0:self/1:opponent
        self.cards=[[],[]] # 0:self/1:opponent/无公共信息概念 公共信息分别和双方隐藏信息结合为整体看待
        self.fa_node=None
        self.child_leaf_node=[[],[]]
        self.child_branch_node=[]


class THP_DT(object):
    """description of class"""
    def __init__(self):
        self.vq_seq_seq_Record=[]
        self.vq_seq_RT=[]
        self.node_sum=3
        self.root=Tnode(-1,-1,0)
        tnode=Tnode(0,3,1)
        tnode.action_vq=np.array([[50,0,0,0,0],[100,0,0,0,0]])
        tnode.fa_node=self.root
        self.root.child_branch_node.append(tnode)
        tnode=Tnode(0,3,2)
        tnode.action_vq=np.array([[100,0,0,0,0],[50,0,0,0,0]])
        tnode.fa_node=self.root
        self.root.child_branch_node.append(tnode)
    def get_seq_text_record_0(self,text_file):
        seq=[]
        with open(text_file, "r") as f:  
            data = f.read() 
            data=data.split(';')
            for i in range(len(data)-1):
                vq_seq=[]
                tvq=[]
                stage=0
                tdata=data[i].split(':')
                pname=tdata[5].split('|')
                if pname[0]=="THPZZ":
                    tvq=np.array([[100,0,0,0,0],[50,0,0,0,0]])
                    vq_seq.append(tvq)
                    tvq,stage=self.get_action_vq_text(tdata[2],2)
                else:
                    tvq=np.array([[50,0,0,0,0],[100,0,0,0,0]])
                    vq_seq.append(tvq)
                    tvq,stage=self.get_action_vq_text(tdata[2],12)
                vq_seq.insert(0,stage)
                for ttvq in tvq:
                    vq_seq.append(np.array(ttvq))
                if stage==4 and pname[0]=="THPZZ":
                    tvq,stage=self.get_action_vq_text(tdata[3],3)
                    vq_seq.append(np.array(tvq))
                elif stage==4 and pname[0]!="THPZZ":
                    tvq,stage=self.get_action_vq_text(tdata[3],13)
                    vq_seq.append(np.array(tvq))
                else:
                    pass
                seq.append(vq_seq)
        return seq
    def get_action_vq_text(self,text,flag):
        avq=[]
        stage=0
        if flag==2 or flag==12:
            tvq=[[],[]]
            tvq_i=(int(flag/12)+1)%2
            chip=100
            rchip=0
            text+="/"
            L=len(text)
            for i in range(L):
                if text[i]=='r':
                    i+=1
                    while text[i]>='0' and text[i] <='9':
                        rchip=rchip*10+int(text[i])
                        i+=1
                    i-=1
                    tvq[tvq_i].append(rchip)
                    tvq_i=(tvq_i+1)%2
                    chip=rchip
                    rchip=0
                elif text[i]=='c':
                    tvq[tvq_i].append(chip)
                    tvq_i=(tvq_i+1)%2
                elif text[i]=='f':
                    tvq[0].extend([0]*(5-len(tvq[0])))
                    tvq[1].extend([0]*(5-len(tvq[1])))
                    avq.append(tvq)
                    if tvq_i==0:
                        tvq=[-1,1]
                    elif tvq_i==1:
                        tvq=[1,-1]
                    avq.append(tvq)
                    break
                elif text[i]=='/':
                    tvq[0].extend([0]*(5-len(tvq[0])))
                    tvq[1].extend([0]*(5-len(tvq[1])))
                    avq.append(tvq)
                    tvq_i=0
                    chip=0
                    stage+=1
                    tvq=[[],[]]
        elif flag==3 or flag==13:
            tvq_i=int(flag/13)
            tvq=[[],[]]
            data=text.split('/')
            tdata=data[0].split('|')
            tvq[tvq_i]=self.get_card_text(tdata[0])
            tvq[(tvq_i+1)%2]=self.get_card_text(tdata[1])
            ct=self.get_card_text(data[1])
            for tct in ct:
                tvq[0].append(tct)
                tvq[1].append(tct)
            ct=self.get_card_text(data[2])
            for tct in ct:
                tvq[0].append(tct)
                tvq[1].append(tct)
            ct=self.get_card_text(data[3])
            for tct in ct:
                tvq[0].append(tct)
                tvq[1].append(tct)
            avq=tvq
        return avq,stage
    def get_card_text(self,text):
        L=len(text)
        cards=[]
        for i in range(0,L,2):
            tcard=[-1,-1]
            if text[i]=='T':
                tcard[0]=8
            elif text[i]=='J':
                tcard[0]=9
            elif text[i]=='Q':
                tcard[0]=10
            elif text[i]=='K':
                tcard[0]=11
            elif text[i]=='A':
                tcard[0]=12
            else:
                tcard[0]=int(text[i])-2
            if text[i+1]=='h':
                tcard[1]=0
            elif text[i+1]=='s':
                tcard[1]=1
            elif text[i+1]=='d':
                tcard[1]=2
            elif text[i+1]=='c':
                tcard[1]=3
            cards.append(tcard)
            i+=1
        return cards
    
    def bulit_DT(self):
        seq=self.get_seq_text_record_0("paths.txt")
        for tvq_seq in seq:
            self.add_vq_seq(self.root,tvq_seq)
    def add_vq_seq(self,root,vq_seq):
        node_type=3
        next_root=root
        for i in range(0,vq_seq[0]+1):
            next_root=self.add_vq(next_root,vq_seq[i+1],i,node_type)
        if vq_seq[0]==4:
            node_type=2
            next_root=self.add_vq(next_root,vq_seq[vq_seq[0]+2],5,node_type)
        else:
            next_root=self.add_vq(next_root,vq_seq[vq_seq[0]+2],vq_seq[0]+1,node_type)
            try:
                if vq_seq[vq_seq[0]+3][0]==-1:
                    node_type=0
                elif vq_seq[vq_seq[0]+3][1]==-1:
                    node_type=1
            except:
                print("###################")
                print(vq_seq)
                x=input("ERROR!")
            next_root=self.add_vq(next_root,vq_seq[vq_seq[0]+3],5,node_type)        
    def add_vq(self,root,vq,stage,node_type):
        node_insert=None
        if node_type==3:
            dissimi_min=[-1,-1]
            i_min=-1
            sum=len(root.child_branch_node)
            for i in range(sum):
                dissimi=self.get_2vq_dissimilarity(root.child_branch_node[i].action_vq,vq)
                if dissimi_min[0]>dissimi[0] or dissimi_min[0]==-1:
                    dissimi_min=dissimi
                    i_min=i
                    if dissimi_min[0]==0:
                        break
            if dissimi_min[0]>0 or dissimi_min[0]==-1:
                tnode=Tnode(stage,node_type,self.node_sum)
                self.node_sum+=1
                tnode.fa_node=root
                tnode.action_vq=vq
                if dissimi_min[1]>0 or i_min==-1:
                    root.child_branch_node.insert(i_min+1,tnode)
                else:
                    root.child_branch_node.insert(i_min,tnode)
                node_insert=tnode
            elif dissimi_min[0]==0:
                node_insert=root.child_branch_node[i_min]
                root.child_branch_node[i_min].relative_ratio+=1        
        elif node_type==2:
            tnode=Tnode(stage,node_type,self.node_sum)
            self.node_sum+=1
            tnode.fa_node=root
            tnode.cards=vq
            root.child_leaf_node.append(tnode)
            node_insert=tnode

            pt=TPT()
            pt.Init()
            card_info=""
            card_info=str(vq[1][0][0])+"*"+str(vq[1][0][1])+"#"
            card_info+=str(vq[1][1][0])+"*"+str(vq[1][1][1])
            pt.Set_Card(card_info,1)

            card_info=""
            card_info=str(vq[1][2][0])+"*"+str(vq[1][2][1])+"#"
            card_info+=str(vq[1][3][0])+"*"+str(vq[1][3][1])+"#"
            card_info+=str(vq[1][4][0])+"*"+str(vq[1][4][1])
            pt.stage=2
            pt.Set_Card(card_info)

            card_info=""
            card_info=str(vq[1][5][0])+"*"+str(vq[1][5][1])
            pt.stage=3
            pt.Set_Card(card_info)

            card_info=""
            card_info=str(vq[1][6][0])+"*"+str(vq[1][6][1])
            pt.stage=4
            pt.Set_Card(card_info)

            while tnode.stage>0:
                if tnode.stage==5:
                    pt.Get_Winrate(1)
                    tnode.winrate=pt.win_rate[1]
                elif tnode.stage==4:
                    tnode.winrate=(tnode.winrate*tnode.relative_ratio+pt.win_rate[1])/(tnode.relative_ratio+1)
                    tnode.relative_ratio+=1
                elif tnode.stage==3:
                    pt.Recover_Public_Card(tnode.stage)
                    pt.Get_Winrate(1)
                    tnode.winrate=(tnode.winrate*tnode.relative_ratio+pt.win_rate[1])/(tnode.relative_ratio+1)
                    tnode.relative_ratio+=1
                elif tnode.stage==2:
                    pt.Recover_Public_Card(tnode.stage)
                    pt.Get_Winrate(1)
                    tnode.winrate=(tnode.winrate*tnode.relative_ratio+pt.win_rate[1])/(tnode.relative_ratio+1)
                    tnode.relative_ratio+=1
                elif tnode.stage==1:
                    pt.Recover_Public_Card(tnode.stage)
                    pt.Get_Winrate(1)
                    tnode.winrate=(tnode.winrate*tnode.relative_ratio+pt.win_rate[1])/(tnode.relative_ratio+1)
                    tnode.relative_ratio+=1
                tnode=tnode.fa_node
        elif node_type==1:
            if root.child_leaf_node[1]:
                root.child_leaf_node[1].relative_ratio+=1
            else:
                tnode=Tnode(stage,node_type,self.node_sum)
                self.node_sum+=1
                tnode.fa_node=root
                tnode.cards=vq
                root.child_leaf_node[1]=tnode
            tnode=root.child_leaf_node[1]
            while tnode.stage>=0:
                tnode=tnode.fa_node
                tnode.fold_sum+=1
            node_insert=root.child_leaf_node[1]
        elif node_type==0:
            if root.child_leaf_node[0]:
                root.child_leaf_node[0].relative_ratio+=1
            else:
                tnode=Tnode(stage,node_type,self.node_sum)
                self.node_sum+=1
                tnode.fa_node=root
                tnode.cards=vq
                root.child_leaf_node[0]=tnode
            node_insert=root.child_leaf_node[0]
        return node_insert
    def get_2vq_dissimilarity(self,vq_0,vq_1):
        dissimi=[-1,-1]
        try:
            dissimi_vq=np.abs(np.sum(vq_0-vq_1,1))+np.sum(np.abs(vq_0-vq_1),1)
            dissimi=[int(np.sqrt(np.sum(dissimi_vq**2))),np.sum(np.sum(vq_0-vq_1,1))]
        except:
            print("DERROR!")
            print(vq_0)
            print(vq_1)
            print(dissimi_vq)
            x=input()
            
        return dissimi

    def get_strategy(self,root,vq):
        pass

    def get_expect_return(self,root,vq):
        pass
    
    def get_opponent_winrate(self,vq_seq_RT):
        winrate=0
        index=1
        node_seleced=self.root
        winrate=self.get_winrate_weight(node_seleced,vq_seq_RT,index)

        return winrate

    def select_node(self,root,vq):
        node_seleced=[]
        if root.node_type==3 or root.node_type==-1:
            i_min=-1
            dissimi_min=[-1,-1]
            node_seleced=[]
            sum=len(root.child_branch_node)
            for i in range(sum):
                dissimi=self.get_2vq_dissimilarity(root.child_branch_node[i].action_vq,vq)
                if dissimi_min[0]>dissimi[0] or dissimi_min[0]==-1:
                    dissimi_min=dissimi
                    i_min=i
                    if dissimi_min[0]==0:
                        break
            if dissimi_min[0]>0:
                if dissimi_min[1]>0 and i_min<(sum-1):
                    node_seleced.append(root.child_branch_node[i_min])
                    node_seleced.append(root.child_branch_node[i_min+1])
                elif dissimi_min[1]>0 and i_min==(sum-1):
                    node_seleced.append(root.child_branch_node[i_min])
                elif dissimi_min[1]<=0 and i_min>0:
                    node_seleced.append(root.child_branch_node[i_min-1])
                    node_seleced.append(root.child_branch_node[i_min])
                elif dissimi_min[1]<=0 and i_min==0:
                    node_seleced.append(root.child_branch_node[i_min])
            elif dissimi_min[0]==0:
                node_seleced.append(root.child_branch_node[i_min])
        return node_seleced

    def get_winrate_weight(self,node_seleced,vq_seq_RT,index):
        winrate=winrate=node_seleced.winrate
        wr0=0
        wr1=0
        node_seleced=self.select_node(node_seleced,vq_seq_RT[index])
        if len(node_seleced)==2:
            dissimi_0=self.get_2vq_dissimilarity(node_seleced[0].action_vq,vq_seq_RT[index])
            dissimi_1=self.get_2vq_dissimilarity(node_seleced[1].action_vq,vq_seq_RT[index])
            if index+1<len(vq_seq_RT):
                wr0=self.get_winrate_weight(node_seleced[0],vq_seq_RT,index+1)
                wr1=self.get_winrate_weight(node_seleced[1],vq_seq_RT,index+1)
            else:
                wr0=node_seleced[0].winrate
                wr1=node_seleced[1].winrate
            winrate=(wr0*dissimi_1[0]+wr1*dissimi_0[0])/(dissimi_0[0]+dissimi_1[0])
        elif len(node_seleced)==1:
            if index+1<len(vq_seq_RT):
                winrate=self.get_winrate_weight(node_seleced[0],vq_seq_RT,index+1)
            else:
                winrate=node_seleced[0].winrate
        
        return winrate
    
    def print_DT(self):
        all_node=[]
        all_node.append(self.root)
        while all_node:
            n_node=all_node.pop(0)
            if n_node:
                for tnode in n_node.child_branch_node:
                    all_node.append(tnode)
                for tnode in n_node.child_leaf_node:
                    all_node.append(tnode)
                if n_node.fa_node!=None:
                    print(n_node.fa_node.node_num,end=" # ")
                else:
                    print(-1,end=" # ")
                print(n_node.node_num,end=" @ ")
                print(n_node.winrate,end=" ")
                if n_node.node_type==3:
                    print(n_node.action_vq)
                else:
                    print(n_node.cards)


    def save_DT_text_dfs(self,root,path=[]):
        fname="test_res.txt"
        tinfo=""
        f = open(fname,'a')
        for tnode in root.child_leaf_node:
            if tnode:
                tinfo=str(tnode.winrate)+" "+str(tnode.relative_ratio)+" "+str(tnode.fold_sum)+" "+str(tnode.cards)
                f.write(str(path)+str(tinfo)+"\n")
        f.close()
        for tnode in root.child_branch_node:
            tinfo=str(tnode.winrate)+" "+str(tnode.relative_ratio)+" "+str(tnode.fold_sum)#+" "+str(tnode.action_vq)
            path.append(tinfo)
            path.append("#")
            self.save_DT_text_dfs(tnode,path)
            path.pop()
            path.pop()
        

def Test_DT_Winrate():
    Play_DT=Player(0)
    Assist_DT=THP_DT()
    Play_Test=Player(1)
    pt=TPT()
    tvq=[]
    wf=0
    resf=open("res_dt.txt",'w')
    for i in range(2009):
        if i>=1000:
            print(i,"##########")
        if wf==1:
            wf=0
            resf.write("\r\n")
        pt.Init()
        pt.Start_stage()
        pnow=pt.small_blind
        Assist_DT.vq_seq_RT=[]
        Assist_DT.vq_seq_RT.append(pt.stage-1)
        if Play_DT.pnum==pt.small_blind:
            tvq=np.array([[50,0,0,0,0],[100,0,0,0,0]],np.int64)
        else:
            tvq=np.array([[100,0,0,0,0],[50,0,0,0,0]],np.int64)
        Assist_DT.vq_seq_RT.append(tvq)
        tvq=[[],[]]
        while True:
            act=[]
            if Play_DT.pnum==pnow:
                #act=Play_DT.strategy_input(pt)
                act=Play_DT.strategy_wl(pt)
                #print("Play_DT: ",act)
                tvq[0].append(act[1])
            else:
                #print("Play_Test: ",end="")
                #act=Play_Test.strategy_input(pt)
                act=Play_Test.strategy_wl(pt)
                #print("Play_Test: ",act)
                tvq[1].append(act[1])
            
            pt.Do_next(pnow,act)
            pnow=pt.Get_Next_pnum(pnow)
            if pt.stage-Assist_DT.vq_seq_RT[0]==2:
                Assist_DT.vq_seq_RT[0]+=1
                tvq[0].extend([0]*(5-len(tvq[0])))
                tvq[1].extend([0]*(5-len(tvq[1])))
                Assist_DT.vq_seq_RT.append(np.array(tvq,np.int64))
                tvq=[[],[]]
                if i>=1000:
                    wf=1
                    predwinrate=Assist_DT.get_opponent_winrate(Assist_DT.vq_seq_RT)
                    print("p_Test ",format(predwinrate, '.3f'),end=" ")
                    print("s_Test ",format(pt.win_rate[Play_Test.pnum],'.3f'),end=" ")
                    print("s_DT ",format(pt.win_rate[Play_DT.pnum],'.3f'))
                    resf.write(str(format(predwinrate, '.3f'))+" "+str(format(pt.win_rate[Play_Test.pnum],'.3f'))+" "+str(format(pt.win_rate[Play_DT.pnum],'.3f'))+"    ")
            elif pt.stage==5:
                Assist_DT.vq_seq_RT[0]+=1
                tvq[0].extend([0]*(5-len(tvq[0])))
                tvq[1].extend([0]*(5-len(tvq[1])))
                Assist_DT.vq_seq_RT.append(np.array(tvq,np.int64))
                tvq=[[],[]]
                while Assist_DT.vq_seq_RT[0]<4:
                    Assist_DT.vq_seq_RT[0]+=1
                    tvq=[[20000,0,0,0,0],[20000,0,0,0,0]]
                    Assist_DT.vq_seq_RT.append(np.array(tvq,np.int64))
                pass
            if pnow==-1:
                if pt.end_flag==2:
                    tvq[0].extend([0]*(5-len(tvq[0])))
                    tvq[1].extend([0]*(5-len(tvq[1])))
                    Assist_DT.vq_seq_RT.append(np.array(tvq,np.int64))
                    if pt.win_flag==0:
                        tvq=[1,-1]
                    else:
                        tvq=[-1,1]
                    Assist_DT.vq_seq_RT.append(tvq)
                elif pt.end_flag==1:
                    #tvq[0].extend([0]*(5-len(tvq[0])))
                    #tvq[1].extend([0]*(5-len(tvq[1])))
                    #Assist_DT.vq_seq_RT.append(np.array(tvq))
                    tvq=[[],[]]
                    tvq[0].append([int(pt.p_card[0][0][0]),int(pt.p_card[0][0][1])])
                    tvq[0].append([int(pt.p_card[0][1][0]),int(pt.p_card[0][1][1])])
                    tvq[1].append([int(pt.p_card[1][0][0]),int(pt.p_card[1][0][1])])
                    tvq[1].append([int(pt.p_card[1][1][0]),int(pt.p_card[1][1][1])])
                    for ci in range(5):
                        tvq[0].append([int(pt.public_card[ci][0]),int(pt.public_card[ci][1])])
                        tvq[1].append([int(pt.public_card[ci][0]),int(pt.public_card[ci][1])])
                    Assist_DT.vq_seq_RT.append(tvq)
                tvq=[[],[]]
                if pt.stage==5:
                    Assist_DT.vq_seq_seq_Record.append(Assist_DT.vq_seq_RT)
                
                #print("###############################")
                #for trc in Assist_DT.vq_seq_RT:
                #    print(trc)
                Assist_DT.vq_seq_RT=[]
                #print("end " + str(pt.end_flag))

                #print(str(pt.earnings[0]) + " " + str(pt.earnings[1]))
                break
        if (i+1)%100==0:
            print("# ",i+1)
            for tvs in Assist_DT.vq_seq_seq_Record:
                Assist_DT.add_vq_seq(Assist_DT.root,tvs)
            Assist_DT.vq_seq_seq_Record=[]
            #Assist_DT.print_DT()
            #x=input()
    
    resf.close()



if __name__=="__main__":
    Test_DT_Winrate()
