module Main where

import Control.Monad (unless)
import System.Exit (exitFailure)
import Test.QuickCheck

expired :: Integer -> Integer -> Integer -> Bool
expired lastActivity now ttl = now >= lastActivity + ttl

timestamp :: Gen Integer
timestamp = chooseInteger (0, 1000000000)

timeouts :: Gen Integer
timeouts = chooseInteger (1, 1000000)

-- Traceability identities and links are declared in traceability.md.
postcondition :: Property
postcondition = conjoin
  [ counterexample "expiration at the boundary" (expired 0 1 1)
  , counterexample "expiration after the boundary" (expired 0 2 1)
  , forAllShrink (chooseInteger (-1000000000, 1000000000)) shrink $ \lastActivity ->
      forAllShrink (chooseInteger (-1000000000, 1000000000)) shrink $ \now ->
      forAllShrink timeouts (filter (> 0) . shrink) $ \ttl ->
        expired lastActivity now ttl === (now - lastActivity >= ttl)
  ]

boundary :: Property
boundary = forAllShrink timestamp (filter (>= 0) . shrink) $ \lastActivity ->
  forAllShrink timeouts (filter (> 0) . shrink) $ \ttl ->
  conjoin [not (expired lastActivity (lastActivity + ttl - 1) ttl),
           expired lastActivity (lastActivity + ttl) ttl]

translation :: Property
translation = forAllShrink timestamp (filter (>= 0) . shrink) $ \lastActivity ->
  forAllShrink timestamp (filter (>= 0) . shrink) $ \now ->
  forAllShrink timeouts (filter (> 0) . shrink) $ \ttl ->
  forAllShrink timestamp (filter (>= 0) . shrink) $ \shift ->
    expired lastActivity now ttl === expired (lastActivity + shift) (now + shift) ttl

main :: IO ()
main = do
  results <- mapM (quickCheckWithResult stdArgs {maxSuccess = 100}) [postcondition, boundary, translation]
  unless (all isSuccess results) exitFailure
