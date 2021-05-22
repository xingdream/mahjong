ICGA文档
========================

## 一、ICGA麻将说明文件
------------------------

### 目录结构
    ai-demo:        一个简单的AI服务器框架，建议将其部署到自己的电脑上并实现自己的AI
        \HTTPServer.py  AI主程序
        \src            AI逻辑代码
        \README.md      说明文档
    doc             大人麻将规则以及AI接口文档
    mj.exe          主程序，模拟麻将玩法并调用AI操作
    mj_config.json  配置文件
    mj.log          日志文件
    README.md       部署说明文档


### 描述：
    1. 启动程序(mj.exe)后，系统自动开启4个玩家打麻将（位置分别为：0,1,2,3）进行大人麻将游戏，其中1号位置是AI, 该它操作的时候他会去请求AI服务器，其它3个方位的AI规则是简单的摸啥打啥。
    2. 打完一局后过5秒自动打下一局。
    3. 运行程序后会自动生成的日志文件(`mj.log`)有利于调试。


### 使用说明：
    1、先设置好配置表(同级目录下 mj_config.json 文件)，注意json的格式一定要正确
    2、启动mj.exe
    3、查看日志文件

### 配置说明：
    1. mj_config.json:
    {
        "url": "http://100.64.15.28:9002/Pubilc_MahJong",       // AI服务器地址
        "sec_thinking": 15,     // 出牌者思考时间
        "sec_attack": 15,       // 别人出牌后，非出牌者确定操作的时间(吃碰杠胡)
        "card_fixed": true	    // AI是否使用固定的牌型(可快速完成一局并走完吃碰杠胡所有流程，方便测试), false则随机发牌
    }

    2. 建议 sec_thinking、sec_attack 均设置为15秒
    3. AI请求服务器一定要在配置的时间内返回(小于sec_thinking或者sec_attack)


---

## 二、ICGA麻将AI-服务器部署文档
------------------------

***安装步骤***
> 1. 请先安装 python (3.7及其以上版本)
> 2. 在命令行窗口中运行 `pip install numpy`安装依赖库


***配置修改***
> 如果需要修改server的启动参数，打开文件 `HTTPServer.py`，  
> 修改端口: 找到 `Port = 9001`，修改则可(可不用修改，只要本机没有其它服务使用这个端口)
> 修改IP:  找到 `IP = '0.0.0.0'`，修改则可(通常情况下可不修改，表示在本机所有IP上开启服务)


***运行***
> python HTTPServer.py
> 输出类似 `Fri, 10 Apr 2020 10:53:12 HTTPServer.py[line:57] DEBUG Starting server, listen at: 0.0.0.0:9002`
> 字样表示服务开启成功


***接口说明***
> 本程序运行后以HTTP的方式提供服务，提供两个接口(见`HTTPServer.py`文件)，

1. 测试接口:
```
    def do_GET(self):
        data = {
            'result_code': '1',
            'result_desc': 'Success',
            'timestamp': '',
            'data': {'message_id': '25d55ad283aa400af464c76d713c07ad'}
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    该接口的主要作用是给访问者返回一段固定的json内容，目的是确保本服务正常工作中。
```

2. AI功能接口:
```
    def do_POST(self):
        if self.path == '/Pubilc_MahJong':
            req_datas = self.rfile.read(int(self.headers['content-length']))
            # logging.debug('收到消息：%s', req_datas.decode())
            # start = time.time()

            game_state = Pubilc_MahJong(req_datas)
            Req_Mess = game_state.get_game_req()

            # logging.debug('发送消息：%s', Req_Mess)
            # end = time.time()
            # logging.debug("消耗时间：%f", end - start)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(Req_Mess).encode('utf-8'))
    
    请求说明：
        do_POST 表示需要以POST的方式访问我们的接口
        if self.path == '/Pubilc_MahJong'  定义接口地址，访问者访问本接口的完整URL应该是 http://yourip:9002/Pubilc_MahJong

    每一次请求都会走一遍这个函数完成访问。每次请求之间都是独立的，为方便说明把上面接口分成3部分并且屏蔽了时间统计功能(#开头的行)
    第一部分：解析请求者传递过来的参数到req_datas中
    第二部分：真正的逻辑处理过程，根据输入参数(req_datas)并生成返回数据(Req_Mess)
    第三部分：将返回数据传递给请求者，完成一次AI请求。

    输入参数、输出数据需要严格符合 `ICGA大众麻将接口文档.doc` 中的要求。

    我们提供的AI Demo中只做了简单的AI处理(src目录下的两个文件)，实现者可基于它做处理，也可忽略而自由发挥，只需要最终返回的数据符合格式就可以。
```
