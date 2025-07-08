from datetime import datetime


def calculate_nowtime_foldername():
    now = datetime.now()
    return now.strftime("%Y_%m%B_%d")