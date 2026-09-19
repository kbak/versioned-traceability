# [impl~retry-growth~1->req~retry-growth~1]
def exponential(attempt):
    return 2**attempt


# [impl~retry-cap~1->req~retry-cap~1]
def cap(delay):
    return min(delay, 8)
