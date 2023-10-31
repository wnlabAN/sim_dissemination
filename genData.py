from element import Topic, Subscriber, Request
import numpy as np
import random

# def make_topic(num_top, zipf):
#     topic_lst = list()
#
#     for k in range(num_top):
#         topic = Topic(k)
#         topic_lst.append(topic)
#         topic.set_popularity(zipf.pdf[k])
#
#     return topic_lst
#
# def make_subsriber(num_sub, top_lst, zipf):
#     sub_list = [Subscriber(i) for i in range(num_sub)]
#     interest_lst = top_lst[zipf.get_sample(size=num_sub)]
#     for sub in sub_list:
#         sub.set_interest(interest_lst[sub.id])
#
#     return sub_list

def make_request(num_brk, arrival, end_time, zipf, top_lst, sub_lst, brk_lst):
    requests = list()
    t = 0
    while t < end_time:
        req_num = np.random.poisson(arrival, size=num_brk)  #broker마다의 request number setting
        for brk_idx in range(num_brk):
            if req_num[brk_idx] != 0:
                req = brk_lst[brk_idx].make_requests(size=req_num[brk_idx])
                for r in req:
                    requests.append(Request(t, brk_lst[brk_idx], r))
        t += 1
    #requests.sort(key=lambda x: x[0])  #time
    return requests


class Zipf:
    def __init__(self):
        self.pdf = None
        self.cdf = None

    def set_env(self, expn, num_contents):
        temp = np.power(np.arange(1, num_contents + 1), -expn)
        zeta = np.r_[0.0, np.cumsum(temp)]
        # zeta = np.r_[0.0, temp]
        self.pdf = [x / zeta[-1] for x in temp]
        self.cdf = [x / zeta[-1] for x in zeta]

    def get_sample(self, size=None):
        if size is None:
            f = random.random()
        else:
            f = np.random.random(size)
        return np.searchsorted(self.cdf, f) - 1