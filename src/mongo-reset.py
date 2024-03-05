from pymongo import MongoClient

client = MongoClient()
db = client.raid_planner_db
raid_resets = db.raid_resets
raid_resets.drop()
raid_posts = db.raid_posts
raid_posts.drop()
