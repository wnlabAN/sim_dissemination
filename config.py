import random
import math

num_topic = 90
num_sub = 1000
num_broker = 5
cache_size = 18   #message
data_size = 1   #message

update_rate = 0.1   #per seconds
arrival_rate = 10  #per seconds
zipf_param = 0.7
end_time = 100
dist_w = 0.5

gamma = 1.1

# algo_lst = ["proposed", "optimal", "random", "no_caching"]

file_path = 'save/'
file_name = 'test.bin'

flag = 0
env_name = 'test_env.bin'
req_name = 'test_env.bin'
