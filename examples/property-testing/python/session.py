# [impl->req~expiration~1]
def expired(last_activity, now, timeout):
    return now >= last_activity + timeout
