# -*- coding: utf-8 -*- 
# @Time    : 2020/1/11 17:04
# @Author  : WangHong 
# @FileName: HTTPServer.py
# @Software: PyCharm
# ! /usr/bin/env python3
# -*- coding:UTF-8 -*-
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from src.dazhong_mahjong import *
import time


class Resquest(BaseHTTPRequestHandler):

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

    def do_POST(self):
        print(self.path)
        if self.path == '/Pubilc_MahJong':
            req_datas = self.rfile.read(int(self.headers['content-length']))  # 重点在此步!
            print("收到消息",req_datas)
            logging.debug('收到消息：%s', req_datas.decode())
            start = time.time()

            game_state = Pubilc_MahJong(req_datas)
            Req_Mess = game_state.get_game_req()
            print("输出Req_Mess",Req_Mess)

            logging.debug('发送消息：%s', Req_Mess)
            end = time.time()
            logging.debug("消耗时间：%f", end - start)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(Req_Mess).encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'err_msg': 'Illegal information'}).encode('utf-8'))


if __name__ == '__main__':
    IP = '0.0.0.0'
    Port = 9002
    if "BOT_AI_IP" in os.environ and "BOT_AI_PORT" in os.environ:
        IP = os.environ["BOT_AI_IP"]
        Port = int(os.environ["BOT_AI_PORT"])
    print('HTTPServer.py执行')
    host = (IP, Port)
    server = HTTPServer(host, Resquest)
    logging.debug("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
