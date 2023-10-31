import numpy as np
import random
from enum import Enum, auto
from collections import deque

class Request:
    def __init__(self, time, dest, topic):
        self.start_time = time
        self.end_time = 0

        self.dest = dest
        self.curr_position = None

        self.topic = topic
        # self.status = None

    def forward(self, t):
        # self.status = "end"
        return t - self.start_time

    def set_pos(self, node):
        self.curr_position = node

    def get_dest(self):
        return self.dest

    def get_topic(self):
        return self.topic

class Topic:    # topic = publisher
    def __init__(self, id):
        self.id = id
        self.popularity = 0
        self.connected_svr = None

    def set_popularity(self, popularity):
        self.popularity = popularity

    def get_popularity(self):
        return self.popularity

    def set_svr(self, svr):
        self.connected_svr = svr

    def get_svr(self):
        return self.connected_svr


class Broker:
    def __init__(self, id, cache_size, num_data, controller):
        self.id = id
        self.cache_size = cache_size
        self.caching_map = np.zeros(num_data, dtype=np.bool_)
        self.controller = controller
        self.sub_lst = list()
        self.topic_lst = list()
        self.neighbor_list = list()
        self.ex_output = 0
        self.ex_input = 0
        self.in_input = 0
        self.in_output = 0

        self.queues = deque()

    def print_info(self):
        print(f'Broker {self.id} has {self.topic_lst} topics')
        tmp = list()
        for sub in self.sub_lst:
            tmp.append((sub.id, sub.get_interest().id))
        print(f'Broker {self.id} has {tmp} subscribers')

    def add_topic(self,top):    # top: int
        self.topic_lst.append(top)

    def set_neighbor(self, neighbor):
        if type(neighbor) == list:
            self.neighbor_list = neighbor
        elif type(neighbor) == int:
            self.neighbor_list.append(neighbor)

    def get_neighbor(self):
        return self.neighbor_list

    def add_subscriber(self, sub):  # sub: int
        self.sub_lst.append(sub)
        #sub.connect_broker(self)

    def add_request(self, req):
        self.queues[req.dest].append(req)

    def get_load(self):
        # print(len(self.sub_lst))
        if len(self.sub_lst) == 0:
            return 0
        else:
            return len(self.sub_lst)

    # def process_req(self, top):
    #     if self.isContain(top):
    #         self.forward_msg()
    #     else:
    #         self.routing_msg()

    def isContain(self, top):
        avail = False
        if self.caching_map[top] or (top in self.topic_lst):
            avail = True
        return avail

    def make_requests(self, size):
        req_sub = [self.sub_lst[random.randrange(len(self.sub_lst))] for _ in range(size)]
        request = [sub.get_interest() for sub in req_sub]
        return request

    # def fetch(self):
    #     self.ex_input += 1
    #     # print("fetching")
    #
    # def forward(self, req):
    #     self.ex_output += 1
    #     # print("forwarding")
    #     req.change_status("end")
    #
    #
    # def routing(self, target_brk):
    #     # print("route to ", target_brk.id)
    #     target_brk.rcv_traffic(self)
    #     self.in_output += 1
    #
    #
    # def rcv_traffic(self, brk):
    #     brk.in_input += 1
    #
    #
    # def get_traffic(self):
    #     return self.ex_input, self.ex_output, self.in_input, self.in_output
    #
    # def clear(self):
    #     self.ex_output = self.ex_input = self.in_output = self.in_input = 0


class Subscriber:
    def __init__(self, id):
        self.id = id
        self.interest = None
        self.conn_brk = None

    def set_interest(self, topic):
        self.interest = topic

    def get_interest(self):
        return self.interest

    def connect_broker(self, brk):
        self.conn_brk = brk

    def get_position(self):
        return self.conn_brk