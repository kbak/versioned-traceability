# [impl->req~session-expiration~1]
def expired(seconds):
    return seconds >= 30 * 60
