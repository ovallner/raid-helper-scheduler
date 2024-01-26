from datetime import date, datetime, timedelta
import requests
from pymongo import MongoClient
from typing import Optional
import configparser

config = configparser.ConfigParser()
config.read("discord.ini")

channel_ids = config['Channel.IDs']
TEST_CHANNEL_ID = channel_ids['test'] #test-channel
MONDAY_CHANNEL_ID = channel_ids['monday']
TUESDAY_CHANNEL_ID = channel_ids['tuesday']
WEDNESDAY_CHANNEL_ID = channel_ids['wednesday']
THURSDAY_CHANNEL_ID = channel_ids['thursday']
FRIDAY_CHANNEL_ID = channel_ids['friday']
SATURDAY_CHANNEL_ID = channel_ids['saturday']
SUNDAY_CHANNEL_ID = channel_ids['sunday']

server_ids = config['Server.IDs']
CATJAM_SERVER_ID =  server_ids['catJAM'] #catJAM

auth = config['Auth']
AUTH_HEADER = auth['auth_header']

user_ids = config['User.IDs']
MAELLIC_USER_ID = user_ids['maellic']
INVALID_USER_ID = user_ids['invalid']
WOW_TEMPLATE_ID = 2
TEST_MODE = True

client = MongoClient()
db = client.raid_planner_db
raid_resets = db.raid_resets
raid_posts = db.raid_posts

def main():
    print("Running raid-planner script...")

    should_post, next_reset_start = determine_if_should_post()

    if not should_post or next_reset_start is None:
        return

    request_headers = create_request_headers()
    for i in range(0, 3):
        response = send_create_event_request(i, next_reset_start, request_headers)
        print(f"{response.status_code:}")
        if response.status_code != 200:
            print("Request did not finish with status code 200")
            break

    insert_raid_post(3)



def determine_if_should_post() -> tuple[bool, Optional[datetime]]:
    today_datetime = datetime.utcnow()

    most_recent_post = raid_posts.find().sort({"resetId":-1}).limit(1)
    if not most_recent_post.alive:
        print("No recent posts. Please initialize with at least 1 post.")
        return (False, None)

    next_reset_id = most_recent_post[0]["resetId"] + 1

    next_reset = raid_resets.find({"resetId": next_reset_id})
    if not next_reset.alive:
        print("No future resets found")
        return (False, None)

    next_reset_start = next_reset[0]["resetStart"]
    twelve_hour_before_reset = next_reset_start - timedelta(hours=24)
    print(f"{twelve_hour_before_reset=}")
    if today_datetime > twelve_hour_before_reset:
        print(f"It is less than 12hrs until the reset")
        print(f"Signups should be posted")
        return (True, next_reset_start)
    else:
        print(f"It is more than 12hrs until the reset")
        print(f"Signups should not be posted")
        return (False, None)

def insert_raid_post(num_posts: int):
    most_recent_post = raid_posts.find().sort({"resetId":-1}).limit(1)[0]

    next_raid_post = {
        "raid": "BFD",
        "resetId": most_recent_post["resetId"] + 1,
        "num_posts": num_posts,
        "resetStart": most_recent_post["resetStart"] + timedelta(days=3),
        "resetEnd": most_recent_post["resetEnd"] + timedelta(days=3),
        "postDateTime": datetime.utcnow()
    }

    raid_posts.insert_one(next_raid_post)


def send_create_event_request(day_number: int, start_datetime: datetime, request_headers: dict) -> requests.Response:
    event_date = start_datetime + timedelta(days=day_number)
    event_json = create_event_json(day_number, event_date)
    channel_id = determine_channel(event_date)
    create_event_url = f"https://raid-helper.dev/api/v2/servers/{CATJAM_SERVER_ID}/channels/{channel_id}/event"

    return requests.post(create_event_url, json=event_json, headers=request_headers)


def determine_channel(input_datetime: datetime) -> str:
    if TEST_MODE:
        return TEST_CHANNEL_ID

    signup_channels = {
        "0": MONDAY_CHANNEL_ID, #monday-raid
        "1": TUESDAY_CHANNEL_ID, #tuesday-raid
        "2": WEDNESDAY_CHANNEL_ID, #wednesday-raid
        "3": THURSDAY_CHANNEL_ID, #thursday-raid
        "4": FRIDAY_CHANNEL_ID, #friday-raid
        "5": SATURDAY_CHANNEL_ID, #saturday-raid
        "6": SUNDAY_CHANNEL_ID #sunday-raid
    }

    return signup_channels[str(input_datetime.weekday())]


def create_event_json(day_number: int, start_date: datetime) -> dict:
    time = ''

    if start_date.weekday() in [4, 5, 6]:
        time = "8:30 PM"
    else:
        time = "7:00 PM"

    return {
        "leaderId": str(MAELLIC_USER_ID),
        "templateId": WOW_TEMPLATE_ID,
        "date": str(start_date.date()),
        "time": time,
        "title": f"BFD Reset night {day_number + 1}"
    }


def create_request_headers() -> dict:
    return {
        "Authorization": AUTH_HEADER,
        "Content-Type": "application/json; charset=utf-8"
    }

if __name__ == "__main__": main()
