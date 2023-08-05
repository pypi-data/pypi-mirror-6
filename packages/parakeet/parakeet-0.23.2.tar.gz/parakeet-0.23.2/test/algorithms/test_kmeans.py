import numpy as np
import time

import parakeet
from parakeet import allpairs, each
from parakeet.testing_helpers import eq, run_local_tests

def python_update_assignments(X, centroids):
  dists = [[np.sum( (x-y) ** 2) for y in centroids] for x in X]
  return np.argmin(dists, 1)

def python_update_centroids(X, assignments, k):
  d = X.shape[1]
  new_centroids = np.zeros((k,d), dtype=X.dtype)
  for i in xrange(k):
    mask = assignments == i
    count = np.sum(mask)
    assigned_data = X[mask]
    if count > 1:
      new_centroids[i, :] = np.mean(assigned_data)
    elif count == 1:
      new_centroids[i,:] = assigned_data[0]

  return new_centroids

def python_kmeans(X, k, maxiters = 100, initial_assignments = None):
  n = X.shape[0]
  if initial_assignments is None:
    assignments = np.random.randint(0, k, size=n)
  else:
    assignments = initial_assignments
  centroids = python_update_centroids(X, assignments, k)
  for _ in xrange(maxiters):
    old_assignments = assignments

    assignments = python_update_assignments(X, centroids)

    if all(old_assignments == assignments):
      break
    centroids = python_update_centroids(X, assignments, k)

  return centroids

def sqr_dist(x,y):
  return sum((x-y) ** 2)

def parakeet_update_assignments(X, centroids):
  dists = allpairs(sqr_dist, X, centroids)

  return np.argmin(dists, 1)

def mean(X):
  return sum(X) / len(X)

def parakeet_update_centroids(X, assignments, k):
  d = X.shape[1]

  new_centroids = np.zeros((k,d), dtype=X.dtype)
  for i in xrange(k):
    mask = (assignments == i)
    count = np.sum(mask)
    assigned_data = X[mask]
    if count == 1:
      new_centroids[i, :] = assigned_data[0]
    elif count > 1:
      new_centroids[i,:] = parakeet.mean(assigned_data)
  return new_centroids

def parakeet_kmeans(X, k, maxiters = 100, initial_assignments = None):
  n = X.shape[0]
  if initial_assignments is None:
    assignments = np.random.randint(0, k, size = n)
  else:
    assignments = initial_assignments

  centroids = python_update_centroids(X, assignments, k)
  for _ in xrange(maxiters):
    old_assignments = assignments
    assignments = parakeet_update_assignments(X, centroids)
    if all(old_assignments == assignments):
      break
    centroids = python_update_centroids(X, assignments, k)

  return centroids

def test_kmeans():
  n = 200
  d = 4
  X = np.random.randn(n*d).reshape(n,d)
  k = 2
  niters = 10
  assignments = np.random.randint(0, k, size = n)
  parakeet_C = parakeet_kmeans(X, k, niters, assignments)
  python_C = python_kmeans(X, k, niters, assignments)
  assert eq(parakeet_C.shape, python_C.shape), \
      "Got back wrong shape, expect %s but got %s" % \
      (python_C.shape, parakeet_C.shape)
  assert eq(parakeet_C, python_C), \
      "Expected %s but got %s" % (python_C, parakeet_C)


if __name__ == '__main__':
  run_local_tests()
