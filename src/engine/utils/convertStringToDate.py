import re


def convert_stringTo_time(s):
    s = "random 4 hours 4 min ago"
    number = re.findall(r"\d+", s)
    result = number[0] if number else ""
    return result

