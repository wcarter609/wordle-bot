import string
import re
from collections import defaultdict
from english_words import english_words_lower_set
import networkx as nx

DEFAULT_WORDSET = english_words_lower_set


class FrequencyBot:

    def __init__(self, n_char=5, wordset=DEFAULT_WORDSET):
        self.n_char = n_char
        self.words = {w for w in wordset if len(w) == n_char}
        self._charsets = [set(string.ascii_lowercase)
                          for i in range(n_char + 1)]
        self._weights = FrequencyBot._calculate_weights(self.words)

    def predict(self, n=1):
        candidates = self.words.copy()
        for fltr in FrequencyBot._build_filters(self._charsets):
            candidates = {c for c in candidates if re.match(fltr, c)}

        ranked = sorted(candidates, reverse=True, key=lambda w: self._score(w))
        return [(w, self._score(w)) for w in ranked][:n]

    def update(self, word, results):
        # results should be a list of integers
        # 0 --> not in the word
        # 1 --> in the word, but a different position
        # 2 --> in the word in the exact position
        for index, char, result in zip(range(len(word)), word, results):
            if result == 2:
                self._charsets[index] = {char}
            elif result == 1:
                self._charsets[index] -= {char}
            else:
                for charset in self._charsets:
                    charset -= {char}

    def _score(self, word):
        return sum([self._weights[c] for c in set(word)])

    @staticmethod
    def _calculate_weights(words):
        weights = defaultdict(int)
        for w in words:
            for c in set(w):
                weights[c] += 1

        return weights

    @staticmethod
    def _build_filters(charsets):
        for i, charset in enumerate(charsets[:-1]):
            yield r'.'*i + f'[{"".join(charset)}]' + r'.'*(len(charsets)-2-i)

        yield f'[{"".join(charsets[-1])}]'


class CentralityBot:

    def __init__(self, n_char=5, wordset=DEFAULT_WORDSET):
        self.n_char = n_char
        self.words = {w for w in wordset if len(w) == n_char}
        self._g = CentralityBot._graph_init(self.words)

    def predict(self, n=1):
        ranks = nx.harmonic_centrality(self._g, self.words, sources=self.words)
        return sorted(ranks, reverse=True, key=lambda w: ranks[w])[:n]

    def update(self, word, results):
        # results should be a list of integers
        # 0 --> not in the word
        # 1 --> in the word, but a different position
        # 2 --> in the word in the exact position
        self._g.remove_node(word)
        for i, c, r in zip(range(self.n_char), word, results):
            to_remove = []
            if r == 2:
                to_remove = [
                    (u, v, key) for u, v, key, data in self._g.edges(keys=True, data=True)
                    if data['position'] == i and c not in {u, v}
                ]

            elif r == 1:
                to_remove = [
                    (u, v, key) for u, v, key, data in self._g.edges(keys=True, data=True)
                    if data['position'] == i and c in {u, v}
                ]

            else:
                to_remove = [e for e in self._g.edges(c, keys=True)]

            self._g.remove_edges_from(to_remove)

    @staticmethod
    def _graph_init(words):
        g = nx.MultiGraph()
        g.add_nodes_from(words, bipartite=0)
        g.add_nodes_from(set(''.join(words)), bipartite=1)
        g.add_edges_from([
            (w, c, {"position": i}) for w in words for i, c in enumerate(w)
        ])
        return g
