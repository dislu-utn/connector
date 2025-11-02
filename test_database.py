from database.database import Database


db = Database()


col = db.client.collections()
for c in col:
    print(c)
