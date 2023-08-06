from datetime import datetime, timedelta

def today():
	now = datetime.now()
	return datetime(year=now.year, month=now.month, day=now.day)


def yesterday():
	return today() + timedelta(days=-1)


def tommorrow():
	return today() + timedelta(days=1)
