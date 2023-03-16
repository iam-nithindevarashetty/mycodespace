import json

# JSON object representing the sample application
json_str = '''
{
    "name" : "hello-sample-app-1",
    "ad_group" : [ "strati_wce_eng" ],
    "contact" : [ "nithin.d@walmart.com" ],
    "apmId" : "APM0007940",
    "cluster_info" : "mlsChina",
    "trProductName" : "GTP-Container-WCNP",
    "fluent_config" : {
        "namespaces" : [ "hello-sample-app-1" ],
        "environments" : {
            "dev" : [ {
                "region" : "cne",
                "retention" : "14",
                "ingestionRate" : "10",
                "status" : "REQUESTED",
                "statusTracker" : "STRMLSPLAT-0000",
                "comments" : "Ingestion is in Units MB/day Retention is in Units: days"
            } ],
            "stage" : [ {
                "region" : "cne",
                "retention" : "14",
                "ingestionRate" : "10",
                "status" : "REQUESTED",
                "statusTracker" : "STRMLSPLAT-0000",
                "comments" : "Ingestion is in Units MB/day Retention is in Units: days"
            } ],
            "prod" : [ {
                "region" : "cne",
                "retention" : "14",
                "ingestionRate" : "10",
                "status" : "REQUESTED",
                "statusTracker" : "STRMLSPLAT-0000",
                "comments" : "Ingestion is in Units MB/day Retention is in Units: days"
            } ]
        }
    },
    "Indexes" : [ {
        "name" : "index-test-cn-1",
        "log_files_count" : "1",
        "daily_data_ingestion_MB" : "10",
        "retention" : "14",
        "concurrent_queries" : "1"
    } ],
    "capacity" : {
        "storage" : "210.0",
        "storage_stg" : "",
        "ingestion_kbps_stg" : "",
        "ingestion_kbps" : "0.0",
        "cores" : "1",
        "indexer_ack" : "0"
    },
    "status" : "REQUESTED",
    "trProductID" : "167",
    "trackerId" : "STRMLSPLAT-0000"
}
'''

# Load the JSON object
data = json.loads(json_str)

# Get the configuration information for the dev environment
dev_config = data["fluent_config"]["environments"]["dev"][0]

# Get the configuration information for the stage environment
stage_config = data["fluent_config"]["environments"]["stage"][0]

# Get the configuration information for the prod environment
prod_config = data["fluent_config"]["environments"]["prod"][0]

# Print the configuration information for the dev environment
print("Dev environment configuration:")
print("Region:", dev_config["region"])
print("Retention:", dev_config["retention"])
print("Ingestion rate:", dev_config["ingestionRate"])

# Print the configuration information for the stage environment
print("Stage environment configuration:")
print("Region:", stage_config["region"])
print("Retention:", stage_config["retention"])
print("Ingestion rate:", stage_config["ingestionRate"])

# Print the configuration information for the prod environment
print("prod environment configuration:")
print("Region:", prod_config["region"])
print("Retention:", prod_config["retention"])
print("Ingestion rate:", prod_config["ingestionRate"])

data = {
    "name" : "hello-sample-app-1",
    "ad_group" : [ "strati_wce_eng" ],
    "contact" : [ "nithin.d@walmart.com" ],
    "apmId" : "APM0007940",
    "cluster_info" : "mlsChina",
    "trProductName" : "GTP-Container-WCNP",
    "fluent_config" : {
        "namespaces" : [ "hello-sample-app-1" ],
        "environments" : {
            "dev" : [ {
                "region" : "cne",
                "retention" : "14",
                "ingestionRate" : "10",
                "status" : "REQUESTED",
                "statusTracker" : "STRMLSPLAT-0000",
                "comments" : "Ingestion is in Units MB/day Retention is in Units: days"
            } ],
            "stage" : [ {
                "region" : "cne",
                "retention" : "14",
                "ingestionRate" : "10",
                "status" : "REQUESTED",
                "statusTracker" : "STRMLSPLAT-0000",
                "comments" : "Ingestion is in Units MB/day Retention is in Units: days"
            } ],
            "prod" : [ {
                "region" : "cne",
                "retention" : "14",
                "ingestionRate" : "10",
                "status" : "REQUESTED",
                "statusTracker" : "STRMLSPLAT-0000",
                "comments" : "Ingestion is in Units MB/day Retention is in Units: days"
            } ]
        }
    },
    "Indexes" : [ {
        "name" : "index-test-cn-1",
        "log_files_count" : "1",
        "daily_data_ingestion_MB" : "10",
        "retention" : "14",
        "concurrent_queries" : "1"
    } ],
    "capacity" : {
        "storage" : "210.0",
        "storage_stg" : "",
        "ingestion_kbps_stg" : "",
        "ingestion_kbps" : "0.0",
        "cores" : "1",
        "indexer_ack" : "0"
    },
    "status" : "REQUESTED",
    "trProductID" : "167",
    "trackerId" : "STRMLSPLAT-0000"
}

indexes = data["Indexes"]
for index in indexes:
    print("Index name:", index["name"])
    print("Log files count:", index["log_files_count"])
    print("Daily data ingestion (MB):", index["daily_data_ingestion_MB"])
    print("Retention (days):", index["retention"])
    print("Concurrent queries:", index["concurrent_queries"])
