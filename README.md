# mahjong
2020第十四届中国计算机博弈锦标赛下饭麻将（fanfou_mahjong）基础上整合改进的完整实验
# first commit 4robot
在个人电脑上实现的完整对局，采用随机出牌算法的4个robot进行完整对局，吃碰杠策略沿用下饭麻将（fanfou_mahjong）的设计，提高游戏进程，平均每10局胡4局
# second commit 模拟 and 完整实验
麻将属于多人非完备信息博弈，考虑到麻将中点炮使己方收益最小化的问题，针对听牌对手模拟其手牌，结合先验知识即弃牌优先级的设计改进弃牌策略
完整实验包括三大部分：
（1）下饭麻将（fanfou_mahjong）作为fanfou_ba与改进版fanfou_op的对比实验，另外两个采用随机出牌算法robot,只考虑fanfou_ba与fanfou_op的顺序共12种排列组合方式，每种组合方式1000局
（2）改进版fanfou_op与提升版fanfou_mc(蒙特卡罗模拟与先验知识的结合)的对比实验，另外两个采用随机出牌算法robot,只考虑fanfou_op与fanfou_mc的顺序共12种排列组合方式，每种组合方式1000局
（3）两个fanfou_op与两个fanfou_mc的对比实验，只考虑fanfou_op与fanfou_mc的顺序共4种排列组合方式，每种组合方式5000局
上述是已完成的工作，上传的文件由于近期忙于后续试验而还没有做整理直接上传的所有版本，会显得有些杂乱，后期会继续整理并上传后续试验代码，后续试验进行深度强化学习的麻将博弈研究
深度强化学习研究思路：
（1）4个robot进行自对弈收集牌谱数据，调用神经网络进行数据抽取训练生成模型
（2）在胜率或收益率达到目标的情况下保存模型，4个robot调用该模型，其中一个robot继续收集牌谱数据进行训练迭代式更新模型
（3）利用最好的模型与下饭麻将的各个版本进行对比实验验证
