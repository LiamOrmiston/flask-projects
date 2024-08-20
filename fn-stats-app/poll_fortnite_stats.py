import requests
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")  # hidden variables located in .env file not checked in

client = MongoClient(config['MONGODB_URL'])
db = client['fortnite_db']

def fetch_and_store_stats():
    params = {'name': config['USERNAME']}
    url = config['API_URL']
    response = json.loads(requests.get(url, params=params, headers={'Authorization': config['API_KEY']}).text)

    if response['status'] == 200:
        data = response['data']

        # Update each category
        for category, stats in data['stats']['all'].items():
            if category != 'trio':
                update_category(category, stats)
            else:
                print('Skipping trio')

        # Update battle pass progress
        data['battlePass']['lastModified'] = datetime.utcnow()
        current_BP_tuple = (data['battlePass']['level'], data['battlePass']['progress'])
        last_BP = db['battlePass'].find_one(sort=[("_id", -1)])
        if last_BP is None:
            db['battlePass'].insert_one(data['battlePass'])
            print(f"New data for battlePass inserted.")
        elif current_BP_tuple != (last_BP['level'], last_BP['progress']):
            db['battlePass'].insert_one(data['battlePass'])
            print(f"New data for battlePass inserted.")
        else:
            print(f"No new data to insert for battlePass.")
    else:
        print(f"Failed to fetch data: {response['status']}")

# Function to update a category collection
def update_category(category_name, new_stats):
    collection = db[category_name]
    
    # Get the last record's lastModified timestamp
    last_record = collection.find_one(sort=[("_id", -1)])
    
    if last_record is None or new_stats['lastModified'] > last_record['lastModified']:
        collection.insert_one(new_stats)
        print(f"New data for {category_name} inserted.")
    else:
        print(f"No new data to insert for {category_name}.")

# Set up scheduler
scheduler = BlockingScheduler()
scheduler.add_job(fetch_and_store_stats, 'interval', minutes=5)

if __name__ == "__main__":
    print("Starting polling script...")
    fetch_and_store_stats()  # Run once immediately
    scheduler.start()
