from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient()
db = client.raid_planner_db
raid_resets = db.raid_resets
raid_posts = db.raid_posts

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S%z"
RESET_START_STRING = "2024-03-05 16:00:00+00:00"
RESET_END_STRING = "2024-03-08 15:59:59+00:00"
GNOMEREGAN_END_DATE_STRING = "2024-05-01 16:00:00+00:00"
RAID_NAME = "Gnomeregan"


reset_start = datetime.strptime(RESET_START_STRING, DATETIME_FORMAT)
reset_end = datetime.strptime(RESET_END_STRING, DATETIME_FORMAT)

# already have raid posts, so don't need to initialize
'''
reset_id = 1
init_raid_post = {
    "raid": RAID_NAME,
    "resetId": reset_id,
    "num_posts": 2,
    "resetStart": reset_start,
    "resetEnd": reset_end,
    "postDateTime": datetime.utcnow()
}
raid_posts.insert_one(init_raid_post)
'''

most_recent_reset = raid_resets.find().sort({"resetId":-1}).limit(1)[0]
reset_id = 1
if len(list(most_recent_reset)) > 0:
    print(f'{most_recent_reset=}')
    reset_id = most_recent_reset["resetId"] + 1
gnomeregan_end_date = datetime.strptime(GNOMEREGAN_END_DATE_STRING, DATETIME_FORMAT)
while reset_end < gnomeregan_end_date:
    reset_obj = {
        "raid": RAID_NAME,
        "resetId": reset_id,
        "resetStart": reset_start,
        "resetEnd": reset_end,
        "numberOfDaysRaiding": 2
    }
    post_id = raid_resets.insert_one(reset_obj).inserted_id
    print(f"{post_id:}")
    reset_start = reset_start + timedelta(days=3)
    reset_end = reset_end + timedelta(days=3)
    reset_id += 1


#for reset in raid_resets.find({}):
#    print(f"{reset:}")


