from pymongo.database import Database as MongoDatabase
from datetime import datetime, date
from typing import Union, Optional
from dateutil import parser as dateutil_parser

import os

def save_discussion_topic(topic: str, author: str, date: datetime, channel_id: int):
    topic = topic.strip().upper()
    author = author.strip().upper()

    if not os.path.exists('C:\\Users\\Public\\discussion_topics'):
        os.makedirs('C:\\Users\\Public\\discussion_topics')

    with open(f'C:\\Users\\Public\\discussion_topics\\{channel_id}.txt', 'a') as file:
        file.write(f"{topic}~{author}~{date.strftime('%Y-%m-%d %H:%M:%S')}\n")
    return


def load_discussion_topics(channel_id: int):
    with open(f'C:\\Users\\Public\\discussion_topics\\{channel_id}.txt', 'r') as file:
        topics = file.readlines()
    return [line.strip().split('~') for line in topics if line.strip()]


def delete_discussion_topic(channel_id: int, topic: str):
    topic = topic.strip().upper()
    topics = load_discussion_topics(channel_id)

    with open(f'C:\\Users\\Public\\discussion_topics\\{channel_id}.txt', 'w') as file:
        for line in topics:
            if not line.startswith(topic):
                file.write(line + '\n')
            else:
                file.write(f"%%"+ line + '\n')
    return


def parse_datetime(date_str: str) -> Optional[Union[datetime, date]]:
    now = datetime.now()
    delimiters = ['/', '-', ' ']
    date_parts = [
        ("%m{d}%d{d}%Y", date),
        ("%m{d}%d", date),
    ]
    time_parts = [
        ("%H:%M", datetime),
        ("%I:%M %p", datetime),
    ]
    tz_parts = ["", " %z", " %Z"]

    # Try all combinations of date, time, tz, and delimiter
    candidates = []
    for delim in delimiters:
        for base_fmt, return_type in date_parts:
            fmt = base_fmt.format(d=delim)
            candidates.append((fmt, return_type))
            for time_fmt, _ in time_parts:
                for tz_fmt in tz_parts:
                    full_fmt = f"{fmt} {time_fmt}{tz_fmt}".strip()
                    candidates.append((full_fmt, datetime))

    for fmt, return_type in candidates:
        try:
            parsed = datetime.strptime(date_str, fmt)
            if '%Y' not in fmt:
                parsed = parsed.replace(year=now.year)
                print(dateutil_parser.parse(date_str))
                return parsed if return_type is datetime else datetime.combine(parsed.date(), datetime.min.time())
        except ValueError:
            continue

    # Fallback to dateutil.parser for flexible parsing, including timezones
    try:
        parsed = dateutil_parser.parse(date_str)
        return parsed
    except (ValueError, OverflowError):
        return None 

def schedule_single_event(db: MongoDatabase, name: str, author: str, start_datetime: str, end_datetime:  str, description: str=None, location: str=None, attendees: str=None):
    # Validate inputs
    name = name.strip().upper()
    author = author.strip().upper()
    start_time = parse_datetime(start_datetime)
    end_time = parse_datetime(end_datetime)

    if start_time >= end_time:
        raise ValueError(f"Start time ({start_time}) must be before end time ({end_time}).")

    if isinstance(start_time, date) and isinstance(end_time, date):
        is_all_day = True
    else:
        is_all_day = False

    post = {
        "name": name,
        "author": author,
        "start": start_time,
        "end": end_time,
        "is_all_day": is_all_day,
        "description": description,
        "location": location,
        "attendees": attendees
    }

    post_id = db.calendar.insert_one(post)
    return post_id
