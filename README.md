# mahjong
2020年中国大学生计算机博弈大赛暨第十四届中国计算机博弈锦标赛下饭麻将（冠军）fanfou_mahjong基础上整合改进的完整实验
# first commit 4robot
在个人电脑上实现的完整对局，采用随机出牌算法的4个robot进行完整对局，吃碰杠策略沿用下饭麻将（fanfou_mahjong）的设计，提高游戏进程，平均每10局胡4局
# second commit 模拟 and 完整实验
麻将属于多人非完备信息博弈，考虑到麻将中点炮使己方收益最小化的问题，针对听牌对手模拟其手牌，结合先验知识即弃牌优先级的设计改进弃牌策略  
完整实验包括三大部分：  
（1）下饭麻将（fanfou_mahjong）作为fanfou_ba与改进版fanfou_op的对比实验，另外两个采用随机出牌算法robot,只考虑fanfou_ba与fanfou_op的顺序共12种排列组合方式，每种组合方式1000局  
（2）改进版fanfou_op与提升版fanfou_mc(蒙特卡罗模拟与先验知识的结合)的对比实验，另外两个采用随机出牌算法robot,只考虑fanfou_op与fanfou_mc的顺序共12种排列组合方式，每种组合方式1000局  
（3）两个fanfou_op与两个fanfou_mc的对比实验，只考虑fanfou_op与fanfou_mc的顺序共4种排列组合方式，每种组合方式5000局  
# 上述是已完成的工作，上传的文件由于近期忙于后续试验而还没有做整理直接上传的所有版本，会显得有些杂乱，后期会继续整理并上传后续试验代码，后续试验进行深度强化学习的麻将博弈研究
深度强化学习研究思路：  
（1）4个robot进行自对弈收集牌谱数据，调用神经网络进行数据抽取训练生成模型  
（2）在胜率或收益率达到目标的情况下保存模型，4个robot调用该模型，其中一个robot继续收集牌谱数据进行训练迭代式更新模型  
（3）利用最好的模型与下饭麻将的各个版本进行对比实验验证  

# 2020麻将博弈大赛规则
大众麻将规则
一、游戏规则  
牌库：只使用万，筒，条，点数分别为1至9，总共108张牌。庄家起手14张牌，其他3位起手13张牌  
打法：行牌过程，可吃、碰、杠和报听，并都可获得直接收益  
胡牌方式：点炮，自摸，抢杠胡  
二、番种介绍  
1.行牌番种  
①吃：1番X1人  
只能吃上家牌，比如上家打出4万，自己手上有56万，则可以吃，凑成456万  
吃牌成功，可以获得上家1番分数  
吃吐不得分，即吃掉某张牌后，立即打出同一张，此行为称之为吃吐，吃吐后需要退还吃牌所得收益，比如上家打出4万，自己手上有456万，吃了凑成456万再打出4万，就是吃吐  
②碰：2番X1人  
当桌其他玩家打出的牌与手牌可以构成碰牌时，则可以碰，比如玩家打出4万，自己手上有一对4万，则可以碰  
③杠：分为直杠、补杠和暗杠  
直杠：4番X1人。当玩家手里有刻子，其他玩家打出该刻子的第4张，进行开杠即为直杠  
补杠：1番X3人。当玩家碰牌后，再抓到第4张并杠牌，即为补杠；  
暗杠：3番X3人。当玩家手牌有4张一样牌张时，进行开杠即为暗杠  
特别说明：当玩家手上有刻子，其他玩家打出第4张，玩家先选择了碰牌，如果本手碰牌后再继续杠，则按直杠处理；如果玩家过了一手再杠，则按补杠处理  
④听：1番X3人  
当手牌可以下叫时，玩家可选择是否报听，报听后可以获得分数奖励  
报听后，不可再改叫，即摸什么牌就打什么牌，但在不影响下叫的情况下，有杠可以选择是否杠  
2.胡牌番种  
①如果是点炮胡，则获得番型X1人的分数，如果是自摸，则获得番型X3人的分数  
②基本胡：6番  
胡牌为全是顺子（包括吃）或者三个刻子（包括碰）加一对组成，如123,345万，567条，789筒加33筒组成的胡牌就计基本胡  
③碰碰胡：8番  
胡牌为全是刻子（三张一样的，包括碰，杠，下同）加一对将组成的胡牌，如111，444万，888,999条，22筒。  
④清一色：12番  
胡牌由三种花色牌（条，筒，万）中的一种组成的牌型，如123,234,567,888,99万  
⑤七对：12番  
胡牌的14张牌全是对子的胡牌，如11,44,66万，88,99条，22,33筒  
⑥如果出现组合牌型，则以最大番数计，比如清一色碰碰胡，则以清一色计算；并大众麻将没有带根胡  
三、对局和胡牌  
对局流程  
①4位玩家分东南西北入座，每人起手摸13张牌，由“庄家”位玩家起手按顺时针出牌，“庄家”位玩家起手多摸一张牌，共计14张。  
②行牌过程的优先级为：胡牌>杠>碰>吃  
③同一人存在多个响应时，比如可以同时响应胡和杠，则需要生成2个响应气泡以供选择，同时还需要生成1个放弃气泡，以供玩家选择过牌。  
④如果存在多人响应，则每个人都需要生成相应的响应气泡，最终的执行结果根据行牌优先级判定  
⑤当有玩家成功胡牌，则牌局结束  
胡牌阶段  
①玩家点击胡牌和听牌自动胡牌皆可，胡牌后按照番型进行积分计算  
②允许一炮多响，即多个玩家响应一个点炮  
③如果牌摸完都无人胡牌则为流局，流局不查叫  
④托管情况下，如果有叫未听牌，在可以胡牌的情况下也可以自动胡牌  

