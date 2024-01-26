from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient()
db = client.raid_planner_db
raid_resets = db.raid_resets
raid_resets.drop()
raid_posts = db.raid_posts
raid_posts.drop()

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S%z"
RESET_START_STRING = "2024-01-23 16:00:00+00:00"
RESET_END_STRING = "2024-01-26 15:59:59+00:00"
BFD_END_DATE_STRING = "2024-02-08 16:00:00+00:00"


reset_start = datetime.strptime(RESET_START_STRING, DATETIME_FORMAT)
reset_end = datetime.strptime(RESET_END_STRING, DATETIME_FORMAT)
reset_id = 1


init_raid_post = {
    "raid": "BFD",
    "resetId": reset_id,
    "num_posts": 3,
    "resetStart": reset_start,
    "resetEnd": reset_end,
    "postDateTime": datetime.utcnow()
}
raid_posts.insert_one(init_raid_post)

bfd_end_date = datetime.strptime(BFD_END_DATE_STRING, DATETIME_FORMAT)
while reset_end < bfd_end_date:
    reset_obj = {
        "raid": "BFD",
        "resetId": reset_id,
        "resetStart": reset_start,
        "resetEnd": reset_end
    }
    post_id = raid_resets.insert_one(reset_obj).inserted_id
    print(f"{post_id:}")
    reset_start = reset_start + timedelta(days=3)
    reset_end = reset_end + timedelta(days=3)
    reset_id += 1


for reset in raid_resets.find({}):
    print(f"{reset:}")


