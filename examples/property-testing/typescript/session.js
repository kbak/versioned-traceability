// [impl->req~expiration~1]
export function expired(lastActivity, now, timeout) {
  return now >= lastActivity + timeout;
}
