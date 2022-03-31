import string
import re
from collections import defaultdict
from english_words import english_words_lower_set


DEFAULT_WORDSET = english_words_lower_set


class FrequencyBot:

  def __init__(self, n_char=5, wordset=DEFAULT_WORDSET):
    self.n_char = n_char
    self.words = {w for w in wordset if len(w) == n_char}
    self.charsets = [set(string.ascii_lowercase) for i in range(n_char + 1)]
    self.weights = FrequencyBot._calculate_weights(self.words)

  def predict(self, n=1):
    candidates = self.words.copy()
    for fltr in FrequencyBot._build_filters(self.charsets):
      candidates = {c for c in candidates if re.match(fltr, c)}

    ranked = sorted(candidates, reverse=True, key=lambda w: self._score(w))
    return [(w,self._score(w)) for w in ranked][:n]
    
  def update(self, word, results):
    # results should be a list of integers
    # 0 --> not in the word
    # 1 --> in the word, but a different position
    # 2 --> in the word in the exact position
    for index, char, result in zip(range(len(word)), word, results):
      if result == 2:
        self.charsets[index] = {char}
      elif result == 1:
        self.charsets[index] -= {char}
      else:
        for charset in self.charsets:
          charset -= {char}
      
  def _score(self, word):
    return sum([self.weights[c] for c in set(word)])

  @staticmethod
  def _calculate_weights(words):
    weights = defaultdict(int)
    for w in words:
      for c in set(w):
        weights[c] += 1

    return weights

  @staticmethod
  def _build_filters(charsets):
    for i,charset in enumerate(charsets[:-1]):
      yield r'.'*i + f'[{"".join(charset)}]' + r'.'*(len(charsets)-2-i)
    
    yield f'[{"".join(charsets[-1])}]'
    