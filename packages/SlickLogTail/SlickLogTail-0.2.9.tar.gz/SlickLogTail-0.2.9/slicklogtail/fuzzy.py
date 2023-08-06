# Copyright (c) 2013. SlickLog.
__author__ = 'Torindo Nesci'

from math import sqrt

from slicklog.util import u


def levenshtein_distance(s1, s2):
  s1 = u(s1)
  s2 = u(s2)

  v1 = range(len(s1) + 1)
  v2 = range(len(s1) + 1)
  for j in range(len(s2)):
    v2[0] = j + 1
    for i in range(1, len(s1) + 1):
      if s2[j] == s1[i - 1]:
        v2[i] = v1[i - 1]
      else:
        v2[i] = 1 + min(v2[i - 1], v1[i - 1], v1[i])
    tmp = v1
    v1 = v2
    v2 = tmp
  return v1[len(s1)]


def to_vect(s):
  s = u(s)
  chars = dict()
  for c in s:
    count = chars.get(c)
    if count is None:
      count = 0
    count += 1
    chars[c] = count
  m = 0
  for k, v in chars.iteritems():
    m += v * v
  m = sqrt(m)
  return chars, m


def _smaller(chars1, chars2):
  if len(chars1) < len(chars2):
    return chars1, chars2
  return chars2, chars1


def cos_similarity(chars, mod, s):
  s_chars, s_mod = to_vect(s)
  n = 0
  chars1, chars2 = _smaller(chars, s_chars)
  for k1, v1 in chars1.iteritems():
    if k1 in chars2:
      n += v1 * s_chars.get(k1)
  if n == 0:
    return 0
  return n / (mod * s_mod)
