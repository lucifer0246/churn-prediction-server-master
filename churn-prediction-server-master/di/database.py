from motor import motor_asyncio

from config import DB_PASSWORD, DB_URL, DB_USERNAME


db_url= DB_URL
password= DB_PASSWORD
username= DB_USERNAME

url = db_url.replace('<password>',password).replace('<username>',username)

try:
  client = motor_asyncio.AsyncIOMotorClient(url)
  print('Connected successfully')
except Exception as e:
  print(e)
  raise e

def get_db():
  return client.get_database(name='churnprediction')