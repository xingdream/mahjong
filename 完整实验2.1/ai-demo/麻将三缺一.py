import random
import easygui as g
import copy

#麻将牌
majiang = 4*['东','南','西','北','中','发','1万','2万','3万','4万','5万'\
             ,'6万','7万','8万','9万','1条','2条','3条','4条','5条','6条'\
             ,'7条','8条','9条','1饼','2饼','3饼','4饼','5饼','6饼','7饼'\
             ,'8饼','9饼','白板']
feng = ['东','南','西','北','中','发','白板']
wan = ['1万','2万','3万','4万','5万','6万','7万','8万','9万']
tiao = ['1条','2条','3条','4条','5条','6条','7条','8条','9条']
bing = ['1饼','2饼','3饼','4饼','5饼','6饼','7饼','8饼','9饼']

#电脑类
class Gamer:
    def __init__(self,name,majiang_own):
        self.name = name
        self.majiang = majiang_own
        self.peng_majiang = []
        self.angang_majiang = []
    #整理牌面
    def organize(self):
        def each_organize(each_type):
            result = []
            
            for each_majiang in self.majiang:
                if each_majiang in each_type:
                    result.append(each_majiang)
            return result
        self.feng = sorted(each_organize(feng))
        self.wan = sorted(each_organize(wan))
        self.tiao = sorted(each_organize(tiao))
        self.bing = sorted(each_organize(bing))
        self.majiang_set = set(self.majiang)
        self.majiang_type = [self.feng,self.wan,self.tiao,self.bing]
    #检查杠
    def check_AAAA(self):
        self.gangflag = 0
        for i in range(4):
            for each_majiang in self.majiang_type[i]:
                if self.majiang_type[i].count(each_majiang) == 4 or \
                    each_majiang in self.peng_majiang:
                    self.angang_majiang.append(each_majiang)
                    self.gangflag = 1
                    try:
                        for j in range(4):
                            self.majiang.remove(each_majiang)
                            self.majiang_type[i].remove(each_majiang)
                    except ValueError:
                        pass
    #验胡并得到要打的麻将
    def check_win(self):
        self.common_type = [self.wan,self.tiao,self.bing]
        self.str_commontype = ['万','条','饼']
        self.majiang_else = {'风':[],'万':[],'条':[],'饼':[]}#记录多余待打麻将
        self.winflag = {'风':[],'万':[],'条':[],'饼':[]}#记录各个花色是否可赢
        self.cupple = {'风':[],'万':[],'条':[],'饼':[]}#记录单出来的对子
        #验风
        def check_feng(self):
            self.dic_feng = dict()
            feng_set = set(self.feng)
            self.winflag['风'] = 1
            for each in feng_set:
                self.dic_feng.setdefault(each,self.feng.count(each))
            for each in self.dic_feng:
                if self.dic_feng[each] == 1:
                    self.majiang_else['风'].append(each)
                    self.winflag['风'] = 0 
                elif self.dic_feng[each] == 2:
                    self.cupple['风'].append(each)
        #验万条饼
        def check_each_type(self,type_list,str_typelist):
            digit_list= [] #便于计算的牌面纯数字序列
            result_else = [] #存储该花色待打牌
            result_else.clear()
            for each in type_list:
                digit_list.append(int(each[0]))
            self.digit_list_copy = digit_list.copy()
            #检测顺子函数
            def check_ABC(self):
                for i in range(1,8):
                    if i in self.digit_list_copy and i+1 \
                       in self.digit_list_copy and i+2 in self.digit_list_copy:
                        self.digit_list_copy.remove(i)
                        self.digit_list_copy.remove(i+1)
                        self.digit_list_copy.remove(i+2)
            #检测三个一样的
            def check_AAA(self):
                for i in range(1,10):
                    if self.digit_list_copy.count(i) == 3:
                        self.digit_list_copy = [each for each in \
                                        self.digit_list_copy if each != i]
            #检测两个一样的
            def check_AA(self,str_type):
                for i in range(1,10):
                    if self.digit_list_copy.count(i) == 2:
                        self.cupple[str_type].append(i)
                        self.digit_list_copy = [each for each in \
                                self.digit_list_copy if each!= i]
            check_AAA(self)
            check_AA(self,str_typelist)
            check_ABC(self)
            if self.digit_list_copy == [] :
                self.winflag[str_typelist] = 1
            else:
                result_else.append(self.digit_list_copy)
                self.digit_list_copy = digit_list.copy()
                self.cupple[str_typelist].clear()
                check_AAA(self)
                check_ABC(self)
                check_AA(self,str_typelist)
                if self.digit_list_copy == []:
                    self.winflag[str_typelist] = 1
                else:
                    result_else.append(self.digit_list_copy)
                    self.digit_list_copy = digit_list.copy()
                    self.cupple[str_typelist].clear()
                    check_ABC(self)
                    check_AA(self,str_typelist)
                    check_AAA(self)
                    if self.digit_list_copy == [] :
                        self.winflag[str_typelist] = 1
                    else:
                        result_else.append(self.digit_list_copy)
            try:
                self.result_min = min(len(each) for each in result_else)
                result_else_f= [each for each in result_else \
                           if(len(each))==self.result_min]
                cupple_num = result_else.index(result_else_f[0])
                if cupple_num == 0:
                    check_AAA(self)
                    check_AA(self,str_typelist)
                    check_ABC(self)
                elif cupple_num == 1 :
                    check_AAA(self)
                    check_ABC(self)
                    check_AA(self,str_typelist)
            except ValueError:
                result_else_f = [[]]
            finally:
                self.majiang_else[str_typelist].extend(result_else_f[0])
        #整体验胡
        for i in range(3):
            check_each_type(self,self.common_type[i],\
                            self.str_commontype[i])
        check_feng(self)
    #胡了！
    def win(self):
        if list(self.winflag.values()) == [1,1,1,1] and \
           sum([len(self.cupple[each]) for each in self.cupple]) == 1:
            g.msgbox('玩家%s胡了！\n%s' % (self.name,str(self.majiang_type)+\
                    3*str(self.peng_majiang) + 4*str(self.angang_majiang)))
            exit()
    #接牌
    def get_majiang(self,new_majiang):
        self.majiang.append(new_majiang)
        self.organize()
        self.check_AAAA()
        self.check_win()
        self.win()
        return self.put_majiang()
    #打牌
    def put_majiang(self):
        self.majiangelse_copy = copy.deepcopy(self.majiang_else)
        if self.majiang_else['风'] == []:
            self.else_gap = {'风':[],'万':[],'条':[],'饼':[]}
            for each in self.else_gap.keys():
                for i in range(len(self.majiang_else[each])-1):
                    self.else_gap[each].append(self.majiang_else[each][i+1] - \
                                               self.majiang_else[each][i])
            for each in self.else_gap:
                for i in range(len(self.else_gap[each])):
                    if self.else_gap[each][i] == 1 :
                        del self.majiangelse_copy[each][i:i+2]
            temp = [len(each) for each in self.majiangelse_copy.values()]
            temp = [each for each in temp if each != 0] #除去[]项
            try:
                putresult1 = [each for each in self.majiangelse_copy.values()\
                              if len(each) == min(temp)]
                putresult2 = [each for each in self.majiangelse_copy.keys()\
                          if len(self.majiangelse_copy[each]) == min(temp)]
                putresult = str(putresult1[0][0]) + str(putresult2[0])
            except ValueError:
                for each in self.majiang_else:
                    if self.majiang_else[each] != []:
                        putresult = str(self.majiang_else[each][0])+each
                        break
        else:
            putresult = self.majiang_else['风'][0]
        try:
            g.msgbox('玩家%s打了%s' % (self.name,putresult))
        except UnboundLocalError:
            for eachkey in self.cupple:
                if self.cupple[eachkey] != []:
                    putresult = str(self.cupple[eachkey][0]) + eachkey
                    g.msgbox('玩家%s打了%s' % (self.name,putresult))
                    break
        self.majiang.remove(putresult)
        return putresult
    #看牌
    def watch_majiang(self,watchmajiang):
        self.watchmajiang = watchmajiang
    #碰牌
    def peng(self):
        self.pengflag = 0
        try:
            if sum(len(self.cupple[each]) for each in self.cupple) != 1:
                if self.watchmajiang in feng:
                    if self.watchmajiang in self.cupple['风']:
                        self.majiang.remove(self.watchmajiang)
                        self.majiang.remove(self.watchmajiang)
                        g.msgbox('玩家%s碰了%s!' % \
                                 (self.name,self.watchmajiang))
                        self.pengflag = 1
                        self.peng_majiang.append(self.watchmajiang)
                elif self.watchmajiang[0] in self.cupple[self.watchmajiang[1]]:
                    for i in range(2):
                        self.majiang.remove(self.watchmajiang)
                    g.msgbox('玩家%s碰了%s!' % (self.name,self.watchmajiang))
                    self.pengflag = 1
                    self.peng_majiang.append(self.watchmajiang)
        except TypeError:
            pass
    #炮胡
    def pao_win(self):
        self.majiang.append(self.watchmajiang)
        self.organize()
        self.check_AAAA()
        self.check_win()
        self.win()
        try:
            self.majiang.remove(self.watchmajiang)
        except ValueError:
            pass
        self.organize()
        self.check_AAAA()
        self.check_win()
#玩家类
class Me(Gamer):
    def __init__(self,majiang_own):
        g.msgbox('欢迎进入麻将三缺一！')
        self.majiang = majiang_own
        self.angang_majiang = []
        self.peng_majiang = []
    def get_majiang(self,new_majiang):
        g.msgbox('您获得了%s' % new_majiang)
        super().get_majiang(new_majiang)
    def put_majiang(self):
            self.putresult = g.choicebox(\
            '您的麻将是:\n%s\n%s\n%s\n%s\n碰：%s\n杠：%s\n请选择要打的麻将' % \
            (str(self.feng),str(self.wan),str(self.tiao),str(self.bing),\
             str(self.peng_majiang),str(self.angang_majiang)),'打麻将',\
            self.majiang)
            self.majiang.remove(self.putresult)
    def win(self):
        if list(self.winflag.values()) == [1,1,1,1] and \
           sum([len(self.cupple[each]) for each in self.cupple]) == 1:
            g.msgbox('恭喜，你赢了！\n%s\n%s\n%s\n%s\n%s\n%s' % (\
                str(self.feng),str(self.wan),str(self.tiao),str(self.bing),\
                3*str(self.peng_majiang),4*str(self.angang_majiang)))
            exit()
    def peng(self):
        self.pengflag = 0
        if self.majiang.count(self.watchmajiang) >1:
            ynpeng = g.ynbox('是否碰%s？\n您的牌面是\n%s\n%s\n%s\n%s'\
                             % (self.watchmajiang,str(self.feng),\
                                str(self.wan),str(self.tiao),str(self.bing)))
            if ynpeng:
                for i in range(2):
                    self.majiang.remove(self.watchmajiang)
                self.organize()
                if self.peng:
                    self.peng_majiang.append(self.watchmajiang)
                self.pengflag = 1
    def check_AAAA(self):
        self.gangflag = 0
        for i in range(4):
            for each_majiang in self.majiang_type[i]:
                if self.majiang_type[i].count(each_majiang) == 4 or \
                    each_majiang in self.peng_majiang:
                    yngang = g.ynbox('是否杠%s？' % each_majiang)
                    if yngang:
                        self.angang_majiang.append(each_majiang)
                        self.gangflag = 1
                        try:
                            for j in range(4):
                                self.majiang.remove(each_majiang)
                                self.majiang_type[i].remove(each_majiang)
                        except ValueError:
                            pass
def start():
	random.shuffle(majiang)
	majiang_split= []
	for i in range(0,52,13):
		majiang_split.append(majiang[i:i+13])
	return majiang_split
majiang_split = start()
gamer1,gamer2,gamer3= [Gamer(name = 'gamer '+ str(i+1)\
			,majiang_own = majiang_split[i] )\
                           for i in range(3)]
me = Me(majiang_split[3])
majiang = majiang[52:]
gamerlist = [me,gamer1,gamer2,gamer3]
i = 0
while majiang != []:
    while i < 4:
        gang_flag = 0
        try:
            put = gamerlist[i].get_majiang(majiang[0])
            del majiang[0]
        except IndexError:
            g.msgbox('黄了！','麻将三缺一')
        def watch():
            global put
            global i
            global gang_flag
            global majiang
            watchlist = gamerlist[i+1:]
            watchlist.extend(gamerlist[:i])
            for each_othergamer in watchlist:
                each_othergamer.watch_majiang(put)
                each_othergamer.pao_win()
                each_othergamer.peng()
                if each_othergamer.pengflag == 1:
                    i = gamerlist.index(each_othergamer)
                    put = each_othergamer.put_majiang()
                    watch()
                if each_othergamer.gangflag == 1:
                    i = gamerlist.index(each_othergamer)
                    gang_flag = 1
                    break
        watch()
        if gang_flag == 0:
            if i == 3:
                i = 0
            else:
                i += 1

        
            
