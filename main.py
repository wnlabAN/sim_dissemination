from config import *
from environment import *
from genData import *
from cacheAlgo import CacheAlgo
import os.path
import pickle
import argparse


def load_file(path, name):
    with open(os.path.join(path, name), 'rb') as f:
        file = pickle.load(f)
        print("success to load the file: %s" % path+name)
    return file

def save_file(path, name, obj):
    with open(os.path.join(path, name), 'wb') as f:
        pickle.dump(obj, f)
    print("Success to generate and save the file: %s" % path+name)

def run(integrated_file):
    env = integrated_file['environment']
    env.add_algo(CacheAlgo("proposed", env, w=True))
    # env.add_algo(CacheAlgo("BP", env, w=False))

    for brk in env.brk_lst:
        brk.print_info()

    hit_result = [0 for _ in range(len(env.algo_lst))]
    delay_result = [0 for _ in range(len(env.algo_lst))]

    # proactive caching
    env.caching()

    t = 0
    while t <= end_time:
        curr_req = env.load_curr_request(t)

        for idx, algo in enumerate(env.algo_lst):
            hit_result[idx] += algo.add_req(curr_req)
            routing_control = algo.backpressure(env.link_state, dist_weight=dist_w)
            caching_control = algo.caching()
            delay_result[idx] += algo.move_packets(routing_control, caching_control, t)
        t += 1

    result = {f'total_request: {env.total_req}, hit_count: {hit_result}, total_delay: {delay_result}'}

    # result = {f'total_request: {env.total_req}, succ_request: {}, hit_count: {hit_result}, '
    #           f'total_delay: {delay_result}, avg_delay: {np.array(delay_result)/succ_req}, hit_ratio: {np.array(hit_result) / env.total_req}'}
    print(result)

if __name__ == "__main__":
    if flag == 1:
        if os.path.exists(file_path+env_name):
            env_file = load_file(file_path, env_name)
            env = env_file['environment']
            zipf = env_file['zipf']
        else:
            zipf = Zipf()
            zipf.set_env(zipf_param, num_topic)
            env = Environment(zipf)
            env_file = {'environment': env, 'zipf': zipf}
            save_file(file_path, env_name, env_file)

        if os.path.exists(file_path+req_name):
            requests = load_file(file_path, req_name)
        else:
            requests = make_request(num_broker, arrival_rate, end_time, zipf, env.top_lst, env.sub_lst, env.brk_lst)
            save_file(file_path, req_name, requests)

        env.set_requests(requests)
        integrated_file = {'requests': requests, 'environment': env}

    if flag == 0:
        if os.path.exists(file_path + file_name):
            integrated_file = load_file(file_path, file_name)

        else:
            zipf = Zipf()
            zipf.set_env(zipf_param, num_topic)
            env = Environment(zipf)
            requests = make_request(num_broker, arrival_rate, end_time, zipf, env.top_lst, env.sub_lst, env.brk_lst)
            env.set_requests(requests)

            integrated_file = {'requests': requests, 'zipf': zipf, 'environment': env}
            save_file(file_path, file_name, integrated_file)

    run(integrated_file)