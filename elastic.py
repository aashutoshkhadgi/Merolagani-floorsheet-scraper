from datetime import datetime
from elasticsearch import Elasticsearch
import json

ELASTIC_PASSWORD = "elastic"

# Create the client instance
client = Elasticsearch(
    "http://10.10.5.17:9201",
    #ca_certs="elastic_certs/ca.txt",
    basic_auth=("elastic", ELASTIC_PASSWORD),
    request_timeout= 600
)

# Successful response!
print(client.info())




for year in range(2015, 2025):
    for month in range(1, 13):
        print(f"year {year} month {month}")
        data = []
        batch=800000
        counter = 0
        error = []
        readfile = f"floorsheet/floorsheet-{year}-{month}.json"
        print(f"indexing for {year}-{month}")
        index = f"local-floorsheet-{year}-{month}"
        client.indices.create(index=index)
        try:
            with open(readfile,"r",encoding="ascii", errors='replace') as f:
                for line in f:
                    doc = (json.loads(line)) 
                    doc["timestamp"]=doc["date"]
                    action = {"index": {"_index": index, "_id": doc['transaction_id']}}
                    data.append(action)
                    data.append(doc)
                    # client.index(index= index, id = doc['transaction_id'], document=doc)
            f.close()
        
        except Exception as e:
            print(f"Encounter Exception: {e}")

        print(len(data))
        length = len(data)
        while counter <  length:            
            try:
                print(data[counter])
                resp = client.bulk(body=data[counter:counter+batch])
            except IndexError as e:
                print("Index Does not exist")
                break
            except Exception as e:
                print(f"exception while bluking {e}")
            finally:
                counter += batch

print("finished")


