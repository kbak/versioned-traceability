# [impl->req~session-expiration~1]
def expired(inactive_seconds):
    return inactive_seconds >= 30 * 60
