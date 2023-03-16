#!/usr/bin/python

import json
import yaml
import os
import pprint
import collections
import copy
import logging
import logging.handlers
import sys
import math
import ruamel.yaml
import re
import subprocess
import shlex

target_cluster = ""
cluster_index_vars_mapping = "configs/cluster_index_vars_mapping.json"
customer_json = sys.argv[1]
customer_json_path = customer_json
index_cluster_dict = {}
allocate_cluster_dict = {}
base_idxr_path = ""
base_inventory_path = ""
allocate_vars_path = ""
sizeIndex_dict = {}
indexExistInCluster = {}
allocateExistInCluster = {}

temp_idxr_list = json.loads(open(cluster_index_vars_mapping,"r").read())
config_dict = {}
allocate_dict = {}
config_dict["indexes"] = []
customer_dict = {}
base_dict = {}
base_dict["indexes"] = []
logger = logging.getLogger(__name__)
logger.info("Starting Program")
logging.VERBOSE = 5
logging.addLevelName(logging.VERBOSE, "VERBOSE")
logging.Logger.verbose = lambda inst, msg, *args, **kwargs: inst.log(logging.VERBOSE, msg, *args, **kwargs)
FORMAT = "%(funcName)20s >>> %(message)s"
logging.basicConfig(level=logging.VERBOSE,format=FORMAT)

def calculate_indexers(mode='private',datacenter=None,target_cluster=None):
    base_inventory_path = "inventories/%s/hosts" %target_cluster
    logger.info("Indexers node calculation  ")
    logger.info(base_inventory_path)
    logger.info(datacenter)
    if mode == 'public':
        if datacenter == "idxr_cluster":
            command = 'cat {} | grep ansible_host | egrep -i \"idxr\" | egrep -i \"{}\" |wc -l'.format(base_inventory_path,"[a-z]")
        else:
            command = 'cat {} | grep ansible_host | egrep -i \"idxr\" | egrep -i \"{}\" |wc -l'.format(base_inventory_path,datacenter)
    else:
        command = 'cat {} | grep ansible_host | egrep -i \"idxr\" | egrep -i \"{}\" |wc -l'.format(base_inventory_path,datacenter)
    logger.info(int(subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0]))
    return int(subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0])

def hotbucket_warmdbcount(bucket=None,mode=None,datasize=None):
    if mode == 'auto':
        bucket_size = 750
    elif mode == 'auto_high_volume':
        bucket_size = 10000
    if bucket == 'hot':
        return int(math.ceil((0.15 * (datasize))/bucket_size))
    elif bucket == 'warm':
        return int(math.ceil((0.15 * (datasize))/bucket_size))

def create_stanza(target_cluster=target_cluster,outer=None,inner=None,index_yaml_load=None):
    counter = 0
    full_dict = {}
    temp_dict = {}
    for key,value in outer.items():
        full_dict[key] = value

    full_dict['misc_props'] = []
    for key, value in inner.items():
        temp_dict['attribute'] = key
        temp_dict['value'] = value
        full_dict['misc_props'].append(copy.deepcopy(temp_dict))
    if "indexes" in index_yaml_load.keys():
        for list_item in index_yaml_load['indexes']:
            if list_item['name'].lower() == full_dict['name'].lower():
                logger.info("Index already defined !! , Updating the existing configuration")
                counter = 1
                list_item.update(full_dict)
    elif "cluster_indexes" in index_yaml_load.keys():
        for list_item in index_yaml_load['cluster_indexes']:
            if list_item['name'].lower() == full_dict['name'].lower():
                logger.info("Index already defined !! , Updating the existing configuration")
                counter = 1
                list_item.update(full_dict)
    
    else:
        logger.info("no vars indexes stanza exists....")
    if counter == 0:
        logger.info("Appending Index Configuration")
        if "indexes" in index_yaml_load.keys():
            index_yaml_load['indexes'].append(full_dict)
        if "cluster_indexes" in index_yaml_load.keys():
            index_yaml_load['cluster_indexes'].append(full_dict)
        else:
            logger.info(" Skipping onboarding ----%s------ on stage "%(full_dict['name'].lower()))


def allocate_check(target_cluster,name=None,rate=None,retention=None,allocation_onboard_vars_path=None):
    mytemp_dict = dict()
    update = 0
    logger.debug("Resetting flag to 0")
    allocation = int(rate) * int(retention)
    actual_allocation = int(int(rate) * int(retention) * float(1.3))
    logger.debug("Allocation = rate * retention => {} * {}".format(int(rate),int(retention),int(rate) * int(retention)))
    logger.debug("Opening Allocation vars file {}".format(allocation_onboard_vars_path))
    logger.info(allocation_onboard_vars_path)
    allocate_dict = ruamel.yaml.load(open(allocation_onboard_vars_path,"r").read(),Loader=ruamel.yaml.RoundTripipLoader)
    if allocate_dict['allocation'] != None:
        for item in allocate_dict['allocation']:
            if name == item['name']:
                logger.debug("Already index esists")
                update = 1
            else:
                continue
        if update == 0:
            mytemp_dict.cleat()
            logger.debug("Index allocation not registered")
            mytemp_dict['name'] = name
            mytemp_dict['ingestion'] = int(rate)
            mytemp_dict['retention'] = int(retention)
            mytemp_dict['calculated_allocation'] = allocation
            if mytemp_dict['calculated_allocation'] == 0:
                mytemp_dict['actual_allocation'] == 18200
            else:
                mytemp_dict['actual_allocation'] == actual_allocation
            if mytemp_dict['actual_allocation'] < 18200:
                mytemp_dict['actual_allocation'] == 18200
            logger.debug("Appending index allocation record")
            allocate_dict['allocation'].append(copy.deepcopy(mytemp_dict))
        stream = open(allocation_onboard_vars_path,"w")
        ruamel.yaml.dump(allocate_dict,stream,Dumper=ruamel.yaml.RoundTripDumper,width=500000000000000000)
        stream.close()


def create_index(target_cluster=target_cluster,name=None,rate=None,retention=None,idxr_count=None,customer_index_onboard=None):
    index_yaml_load = {}
    for indexVarsPath in customer_index_onboard:
        index_yaml_load.clear()
        index_yaml_load = ruamel.yaml.load(open(indexVarsPath,"r").read(),Loader=ruamel.yaml.RoundTripLoader)
        logger.debug("Calculation stanza for index_name={} ingestion_rate={} retention={} idx_count={}".format(name,rate,retention,idxr_count))
        stanza_dict = {}
        misc_dict = {}
        stanza_dict['name'] = str(name)
        misc_dict['frozenTimePeriodInSecs'] = int(retention) * 86400
        misc_dict['maxTotalDataSizeMB'] = int((float(rate) * int(retention) * 1.3) / int(idxr_count))
        if misc_dict['maxTotalDataSizeMB'] < 1000:
            logger.info("The index size is lessthan 1G , I'm resetting this")
            misc_dict['maxTotalDataSizeMB'] = 1000
        misc_dict['maxHotSpanSecs'] = 604800
        if name.startswith('stg_'):
            stanza_dict['maxDataSize'] = 'auto'
            stanza_dict['maxHotBuckets'] = 1
            misc_dict['maxTotalDataSizeMB'] = 1000
            misc_dict['maxWarmDBCount'] = 1
            misc_dict['frozenTimePeriodInSecs'] = 7 * 86400
        else:
            if int(rate) > 50000:
                stanza_dict['maxDataSize'] = 'auto_high_volume'
            else:
                stanza_dict['maxDataSize'] = 'auto'
            stanza_dict['maxHotBuckets'] = hotbucket_warmdbcount(bucket='hot',mode=stanza_dict['maxDataSize'],datasize=misc_dict['maxTotalDataSizeMB'])
            misc_dict['maxWarmDBCount'] = hotbucket_warmdbcount(bucket='warm',mode=stanza_dict['maxDataSize'],datasize=misc_dict['maxTotalDataSizeMB'])
        logger.debug("Calling stanza build for index_name={} ingestion_rate={} retention={} idx_count={}".format(name,rate,retention,idxr_count))
        create_stanza(target_cluster=target_cluster,outer=stanza_dict,inner=misc_dict,index_yaml_load=index_yaml_load)
        stream = open(indexVarsPath,"w")
        ruamel.yaml.dump(index_yaml_load,stream,Dumper=ruamel.yaml.RoundTripDumper,width=500000000000000000)
        stream.close()     


def customer_index_parse(target_cluster=target_cluster,index=None,datacenter=None,customer_index_onboard=None,allocation_rate=None):
    global allocate_vars_path
    global allocateExistInCluster
    logger.info("Pulling Index name from Indexes")
    num_indexers = calculate_indexers(mode='public',datacenter=datacenter,target_cluster=target_cluster)
    index['name'] = index['name'].strip().lower()
    index['name'] = re.sub(' ','_',index['name'])
    logger.info("allocateExistInCluster")
    logger.info(allocateExistInCluster)
    logger.info(index)
    logger.info(allocateExistInCluster[target_cluster][index['name']])
    logger.info("<<<<<<<<<<<<<<<<<<")
    if 'retention' not in index.keys():
        logger.info("retention is default of 14 days")
        create_index(target_cluster=target_cluster,name=index['name'],rate=allocation_rate,retention=14,idxr_count=num_indexers,customer_index_onboard=customer_index_onboard)
        if not allocateExistInCluster[target_cluster][index['name']]:
            allocate_check(target_cluster=target_cluster,name=index['name'],rate=allocation_rate,retention=14,allocation_onboard_vars_path=allocate_vars_path)
    else:
        logger.info("retention {} days".format(index['retention']))
        create_index(target_cluster=target_cluster,name=index['name'],rate=allocation_rate,retention=index['retention'],idxr_count=num_indexers,customer_index_onboard=customer_index_onboard)
        if not allocateExistInCluster[target_cluster][index['name']]:
            allocate_check(target_cluster=target_cluster,name=index['name'],rate=allocation_rate,retention=index['retention'],allocation_onboard_vars_path=allocate_vars_path)
    logger.info("<<<<<<<<<<<<<<<<<<allocateExistInCluster<<<<<<<<<<<<<")


def checkIfindexExistInCluster(index_name,index_cluster_dict):
    global indexExistInCluster
    logger.info("validating index --- {} --- if exists".format(index_name['name'].lower()))
    temp_dict = {}
    for target_cluster in index_cluster_dict:
        if target_cluster not in indexExistInCluster.keys():
            indexExistInCluster[target_cluster]={}
        for datacenter in index_cluster_dict[target_cluster]:
            if datacenter not in indexExistInCluster[target_cluster].keys():
                indexExistInCluster[target_cluster][datacenter]={}
            if index_name['name'].lower() not in indexExistInCluster[target_cluster][datacenter].keys():
                indexExistInCluster[target_cluster][datacenter][index_name['name'].lower()] = None
            if index_name['name'].lower() in index_cluster_dict[target_cluster][datacenter]:
                indexExistInCluster[target_cluster][datacenter][index_name['name'].lower()] = True
            else:
                indexExistInCluster[target_cluster][datacenter][index_name['name'].lower()] = False
    return indexExistInCluster

def checkIfallocateExistInCluster(index_name,target_clusterlist,allocate_cluster_dict):
    global allocateExistInCluster
    logger.info("validating index --- {} --- if exists".format(index_name['name'].lower()))
    temp_dict = {}
    for target_cluster in target_clusterlist:
        if target_cluster not in allocateExistInCluster.keys():
            allocateExistInCluster[target_cluster]={}
        if index_name['name'].lower() not in allocateExistInCluster[target_cluster].keys():
            allocateExistInCluster[target_cluster][index_name['name'].lower()] = None
        if index_name['name'].lower() in index_cluster_dict[target_cluster]:
            allocateExistInCluster[target_cluster][index_name['name'].lower()] = True
        else:
            allocateExistInCluster[target_cluster][index_name['name'].lower()] = False
    return allocateExistInCluster

def buildAllocateIndexesList(target_cluster=None):
    global allocate_cluster_dict
    logger.info(target_cluster)
    varsPath = "inventories/%s/allocate_vars" %target_cluster
    tempAllocateList = []
    logger.info("buildAllocateIndexesList")
    logger.info(varsPath)
    if os.path.isfile(str(varsPath)):
        allocate_yaml_dict = ruamel.yaml.load(open(varsPath,"r").read(),Loader=ruamel.yaml.RoundTripLoader)
        if not target_cluster in allocate_dict.keys():
            allocate_cluster_dict[target_cluster]=[]
        for index in allocate_yaml_dict["allocation"]:
            tempAllocateList.append(index['name'].lower())
    allocate_cluster_dict[target_cluster] = tempAllocateList


def buildConfigIndexesList(target_cluster,datacenter,indexVarsPath):
    global config_dict
    global index_cluster_dict
    global sizeIndex_dict
    index_temp_dict=[]
    size_dict = {}
    temp_dict = {}
    if target_cluster not in index_cluster_dict.keys() and target_cluster not in sizeIndex_dict.keys():
        index_cluster_dict[target_cluster] = {}
        sizeIndex_dict[target_cluster] = {}
    if datacenter not in index_cluster_dict[target_cluster].keys() and datacenter not in sizeIndex_dict[target_cluster].keys():
        index_cluster_dict[target_cluster][datacenter] = []
        sizeIndex_dict[target_cluster][datacenter] = []
    logger.info("Loading Index Vars ------ %s" %datacenter)
    for varsPath in indexVarsPath:
        logger.info("vars ------ %s" %varsPath)
        if 'indexes' in temp_dict.keys():
            for item in temp_dict["indexes"]:
                index_temp_dict.append(item['name'].lower())
                if item['name'] not in size_dict.keys():
                    size_dict[item['name']] = ""
                for misc_props in item['misc_props']:
                    if misc_props['attribute'] == "maxTotalDataSizeMB":
                        size_dict[item['name']] = misc_props['value']
        elif 'cluster_indexes' in temp_dict.keys():
            for item in temp_dict["cluster_indexes"]:
                index_temp_dict.append(item['name'].lower())
                if item['name'] not in size_dict.keys():
                    size_dict[item['name']] = ""
                for misc_props in item['misc_props']:
                    if misc_props['attribute'] == "maxTotalDataSizeMB":
                        size_dict[item['name']] = misc_props['value']
    index_cluster_dict[target_cluster][datacenter] = index_temp_dict
    sizeIndex_dict[target_cluster][datacenter] = size_dict


def getTargetCluster(customer_dict,indexExistInCluster):
    for inventory_target_cluster in ["mls-china-np","mls-china"]:
        for index_name in customer_dict['indexes']:
            logger.info(index_name)
            for datacenter in indexExistInCluster[inventory_target_cluster].keys():
                logger.info(datacenter)
                if indexExistInCluster[inventory_target_cluster][datacenter][index_name['name']]:
                    logger.info(inventory_target_cluster)
                    return inventory_target_cluster



def main():
    global base_dict
    global index_cluster_dict
    global allocate_cluster_dict 
    global allocateExistInCluster
    temp_dict = dict()
    global customer_dict
    global config_dict
    global base_inventory_path
    global allocate_vars_path
    try:
        logger.info("Loading Main Global Index Vars to base_dict")
        customer_dict = json.loads(open(customer_json_path,"r").read())
        config_cluster = json.loads(open("configs/target_clusters_mapping.json","r").read())

        target_clusterlist = config_cluster[sys.argv[2]].split(',')
        logger.info(target_clusterlist)

        env_keys = list(customer_dict['fluent_config']['environments'].keys())

        d_s = ['dev', 'stage']
        p = ['prod']
        d_s_p = ['dev', 'stage', 'prod']

        if env_keys == d_s:
            if customer_dict['fluent_config']['environments']['dev'][0]['region'] or customer_dict['fluent_config']['environments']['stage'][0]['region'] == 'cne':
                buildConfigIndexesList(temp_idxr_list["mls-china-np"],'azeastcn', temp_idxr_list["mls-china-np"]['azeastcn'][0])
            elif customer_dict['fluent_config']['environments']['dev'][0]['region'] and customer_dict['fluent_config']['environments']['stage'][0]['region'] == '':
                buildConfigIndexesList(temp_idxr_list["mls-china-np"],'idxr_cluster', temp_idxr_list["mls-china-np"]['idxr_cluster'][0])
        elif env_keys == d_s_p:
            if (customer_dict['fluent_config']['environments']['dev'][0]['region'] or customer_dict['fluent_config']['environments']['stage'][0]['region']) or customer_dict['fluent_config']['environments']['prod'][0]['region'] == 'cne':
                buildConfigIndexesList(temp_idxr_list["mls-china-np"],'azeastcn', temp_idxr_list["mls-china-np"]['azeastcn'][0])
                buildConfigIndexesList(temp_idxr_list["mls-china"],'azeastcn', temp_idxr_list["mls-china"]['azeastcn'][0])
            elif (customer_dict['fluent_config']['environments']['dev'][0]['region'] or customer_dict['fluent_config']['environments']['stage'][0]['region']) or customer_dict['fluent_config']['environments']['prod'][0]['region'] == '':
                buildConfigIndexesList(temp_idxr_list["mls-china-np"],'idxr_cluster', temp_idxr_list["mls-china-np"]['idxr_cluster'][0])
                buildConfigIndexesList(temp_idxr_list["mls-china"],'idxr_cluster', temp_idxr_list["mls-china"]['idxr_cluster'][0])
        elif env_keys == p:
            if customer_dict['fluent_config']['environments']['prod'][0]['region'] == 'cne':
                buildConfigIndexesList(temp_idxr_list["mls-china"],'azeastcn', temp_idxr_list["mls-china"]['azeastcn'][0])
            elif customer_dict['fluent_config']['environments']['prod'][0]['region'] == 'cnn':
                buildConfigIndexesList(temp_idxr_list["mls-china"],'aznorthcn', temp_idxr_list["mls-china"]['aznorthcn'][0])
            else:
                buildConfigIndexesList(temp_idxr_list["mls-china"],'idxr_cluster', temp_idxr_list["mls-china"]['idxr_cluster'][0])
                

#        for inventory_target_cluster in target_clusterlist:
 #           if inventory_target_cluster in temp_idxr_list.keys():
  #              for datacenter in temp_idxr_list[inventory_target_cluster]:
   #                 buildConfigIndexesList(inventory_target_cluster,datacenter,temp_idxr_list[inventory_target_cluster][datacenter])
    #        buildAllocateIndexesList(target_cluster=inventory_target_cluster)

        for inventory_target_cluster in target_clusterlist:
            buildAllocateIndexesList(target_cluster=inventory_target_cluster)

        for index_name in customer_dict['indexes']:
            checkIfindexExistInCluster(index_name,target_clusterlist,allocate_cluster_dict)

    except Exception as e:
        logger.warning("Input Load Failed - %s" %e.message)
        sys.exit(1)

    logger.info(indexExistInCluster)
    logger.info(allocateExistInCluster)

    for index_name in customer_dict['indexes']:
        for target_cluster in target_clusterlist:
            logger.info("target_cluster ---------> {}".format(target_cluster))
            base_idxr_path = "inventories/%s/group_vars/idxr_cluster/vars" %target_cluster
            allocate_vars_path = "inventories/%s/allocate_vars" %target_cluster
            base_inventory_path = "inventories/%s/hosts" %target_cluster
            logger.info(base_idxr_path)
            logger.info(allocate_vars_path)
            logger.info(base_inventory_path)
            for datacenter in index_cluster_dict[target_cluster].keys():
                logger.info("---------------------------------------")
                logger.info(target_cluster)
                logger.info(datacenter)
                logger.info(index_name['name'].lower())
                if indexExistInCluster[target_cluster][datacenter][index_name['name'].lower()]:
                    logger.info("Index already exists")
                    logger.info("old_ingestion_size ={}".format(sizeIndex_dict[target_cluster][datacenter][index_name['name'].lower()]))
                    logger.info(calculate_indexers(mode='public',datacenter=datacenter,target_cluster=target_cluster))
                    new_ingestion_size=int(int(index_name['daily_data_ingestion_MB'])*1.3*int(index_name['retention']))/int(calculate_indexers(mode='public',datacenter=datacenter,target_cluster=target_cluster))
                    old_ingestion_size = int(sizeIndex_dict[target_cluster][datacenter][index_name['name'].lower()])
                    logger.info("new_ingestion_size = {}".format(new_ingestion_size))
                    if new_ingestion_size >= old_ingestion_size:
                        logger.info("New ingestion size is greater than older ingestion size")
                        customer_index_parse(target_cluster=target_cluster,index=index_name,datacenter=datacenter,customer_index_onboard=temp_idxr_list[target_cluster][datacenter],allocation_rate=index_name['daily_data_ingestion_MB'])
                    else:
                        logger.info("New ingestion size is lesser than older ingestion size value")
                
                if not indexExistInCluster[target_cluster][datacenter][index_name['name'].lower()]:
                    logger.info("\n")
                    logger.info("Running customer_index_parse")
                    customer_index_parse(target_cluster=target_cluster,index=index_name,datacenter=datacenter,customer_index_onboard=temp_idxr_list[target_cluster][datacenter],allocation_rate=index_name['daily_data_ingestion_MB'])

if __name__ == "__main__":
    main()



        


