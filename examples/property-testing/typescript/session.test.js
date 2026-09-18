import assert from "node:assert/strict";
import test from "node:test";
import fc from "fast-check";
import { expired } from "./session.js";

const timestamp = fc.integer({ min: 0, max: 1_000_000_000 });
const timeout = fc.integer({ min: 1, max: 1_000_000 });

// [utest~expiration-boundary~1->req~expiration~1]
test("expiration includes equality", () => {
  fc.assert(fc.property(timestamp, timeout, (last, ttl) => {
    assert.equal(expired(last, last + ttl - 1, ttl), false);
    assert.equal(expired(last, last + ttl, ttl), true);
  }), { numRuns: 100 });
});

// [utest~expiration-shift~1->req~expiration~1]
test("translation preserves expiration", () => {
  fc.assert(fc.property(timestamp, timestamp, timeout, timestamp, (last, now, ttl, shift) => {
    assert.equal(expired(last, now, ttl), expired(last + shift, now + shift, ttl));
  }), { numRuns: 100 });
});
