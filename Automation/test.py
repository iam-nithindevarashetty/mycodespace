import json

cluster_index_vars_mapping = "configs/cluster_index_vars_mapping.json"
temp_idxr_list = json.loads(open(cluster_index_vars_mapping,"r").read())
print(temp_idxr_list)

config_cluster = json.loads(open("configs/target_clusters_mapping.json","r").read())
#target_clusterlist = config_cluster[mlsChina].split(',')
print(config_cluster)

'''
{'mls-china-np': {'azeastcn': ['inventories/mls-china-np/group_vars/cluster_azeastcn/vars'], 'idxr_cluster': ['inventories/mls-china-np/group_vars/idxr_vars/vars']}, 'mls-china': {'azeastcn': ['inventories/mls-china/group_vars/cluster_azeastcn/vars'], 'aznorthcn': ['inventories/mls-china/group_vars/cluster_aznorthcn/vars'], 'idxr_cluster': ['inventories/mls-china/group_vars/idxr_vars/vars']}}
'''