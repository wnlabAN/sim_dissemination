import numpy as np
import random
from element import Broker, Subscriber, Topic
import math
from config import *
import networkx as nx
from itertools import combinations


class Environment:   # load balancer
    def __init__(self, zipf):
        self.top_lst = list()
        self.brk_lst = list()
        self.sub_lst = list()
        self.algo_lst = list()
        self.zipf = zipf

        self.asso_map = np.zeros((num_broker, num_topic), dtype=np.bool_)
        self.lambda_map = np.zeros(num_topic, dtype=np.float_)
        self.total_load = 0
        self.total_req = 0
        self.graph = None
        self.rtt_map = np.zeros((num_broker, num_broker), dtype=np.float_)
        self.link_state = np.zeros((num_broker, num_broker), dtype=np.bool_)
        self.link_set = list()

        self.curr_t = 0
        self.requests = None
        self.curr_req = list()

        self.create_env(cache_size)

    def create_env(self, cache_size):
        print("create environment..")
        # generate topics, subscribers, brokers
        self.top_lst = self.make_topic(num_topic, self.zipf)
        print("generate topics")

        self.sub_lst = self.make_subsriber(num_sub, self.top_lst, self.zipf)
        print("generate subscribers")

        g = nx.Graph()
        for i in range(num_broker):
            broker = Broker(i, cache_size, len(self.top_lst), self)
            self.brk_lst.append(broker)
            g.add_node(i)

        # create links between nodes
        p = 0.5
        for u, v in combinations(g, 2):
            if self.link_state[u, v] is not True:
                if random.random() < p:
                    g.add_edge(u, v, rtt=random.uniform(0, 1)*0.001+0.001)
                    self.link_state[u, v] = True
                    self.link_state[v, u] = True
                    self.link_set.append((u, v))
                    self.link_set.append((v, u))
                    self.brk_lst[u].set_neighbor(v)
                    self.brk_lst[v].set_neighbor(u)
        self.graph = g

        # assign a topic(publisher) to a broker
        self.assign_top()

        # assign the subscribers to the brokers
        self.match_sub_broker(self.sub_lst)

        for top in self.top_lst:
            self.lambda_map[top.id] = arrival_rate * top.popularity

    def rtt_mapping(self, edge_key=None):
        for i in range(num_broker):
            for j in range(i + 1, num_broker):
                try:
                    length = nx.shortest_path_length(self.graph, i, j, weight=edge_key)
                    self.rtt_map[i, j] = length
                    self.rtt_map[j, i] = length
                except:
                    self.rtt_map[i, j] = 0
                    self.rtt_map[j, i] = 0
        print(self.rtt_map)

    def has_path(self, start, end, dest):
        paths = nx.all_simple_paths(self.graph, source=start, target=dest)
        has_path = False
        for path in map(nx.utils.pairwise, paths):
            if (start, end) in path:
                has_path = True
                break
        return has_path

    def find_nearest_node(self, target, node_lst):
        min_dist = None
        min_node = None
        for node in node_lst:
            dist = nx.shortest_path_length(target, node)
            if (min_dist == None) or (dist < min_dist):
                min_dist = dist
                min_node = node
        return min_node

    def make_topic(self, num_top, zipf):
        topic_lst = list()
        for k in range(num_top):
            topic = Topic(k)
            topic_lst.append(topic)
            topic.set_popularity(zipf.pdf[k])
        return topic_lst

    def make_subsriber(self, num_sub, top_lst, zipf):
        sub_list = [Subscriber(i) for i in range(num_sub)]
        interest_lst = [top_lst[i] for i in (zipf.get_sample(size=num_sub))]
        for sub in sub_list:
            sub.set_interest(interest_lst[sub.id])
        return sub_list

    def assign_top(self):
        assign_lst = np.random.uniform(0, num_broker, size=num_topic)
        for top, brk in enumerate(assign_lst):
            brk = math.trunc(brk)
            self.brk_lst[brk].add_topic(top)
            self.asso_map[brk][top] = True
            self.top_lst[top].set_svr(self.brk_lst[brk])


    def match_sub_broker(self, sub):
        for s in sub:
            brk = self.brk_lst[random.randrange(num_broker)]
            self.total_load += 1
            if self.check_load(brk):
                brk.add_subscriber(s)


    def check_load(self, brk):
        return brk.get_load() < gamma * (self.total_load / num_broker)


    def set_requests(self, requests):
        self.requests = requests


    def get_position(self, topic_idx):
        return self.top_lst[topic_idx].get_svr()


    def add_algo(self, algo):
        if type(algo).__name__ == 'CacheAlgo':
            self.algo_lst.append(algo)
            print(f'Success to add algorithm: {algo.name}')
        else:
            print("wrong algo class")


    def load_curr_request(self, t):
        self.curr_req.clear()
        self.curr_t = t
        for r in self.requests:
            if r.time != t:
                break
            self.curr_req.append(r)
        return self.curr_req

    def request(self):
        ex_input_lst = [0 for _ in range(len(self.algo_lst))]
        ex_output_lst = [0 for _ in range(len(self.algo_lst))]
        in_input_lst = [0 for _ in range(len(self.algo_lst))]
        in_output_lst = [0 for _ in range(len(self.algo_lst))]
        hit_lst = [0 for _ in range(len(self.algo_lst))]
        delay_lst = [0 for _ in range(len(self.algo_lst))]

        while self.curr_req:
            req = self.curr_req.pop(0)  # (t, svr_id, requested_top)
            # self.brk_lst[req[1]].process_req(req[2])
            self.total_req += 1
            for idx, algo in enumerate(self.algo_lst):
                ex_input, ex_output, in_input, in_output, hit, delay = algo.process_req(req)
                ex_input_lst[idx] += ex_input
                ex_output_lst[idx] += ex_output
                in_input_lst[idx] += in_input
                in_output_lst[idx] += in_output
                hit_lst[idx] += hit
                # delay_lst[idx] += delay
        return ex_input_lst, ex_output_lst, in_input_lst, in_output_lst, hit_lst, delay_lst


    def caching(self):
        for algo in self.algo_lst:
            # algo.clear()
            algo.caching()