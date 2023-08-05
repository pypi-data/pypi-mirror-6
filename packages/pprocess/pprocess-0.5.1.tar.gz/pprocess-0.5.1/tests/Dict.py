#!/usr/bin/env python

"A simple file indexer."

import codecs
import time

class Parser:
    def __init__(self, filenames, encoding=None, delay=None):
        self.filenames = filenames
        self.encoding = encoding
        self.delay = delay

    def _get_file_content(self, filename):
        if self.encoding is None:
            f = open(filename)
        else:
            f = codecs.open(filename, encoding=self.encoding)
        s = f.read()
        f.close()
        return s

    def send_entries(self, channel):

        "Send word entries from the file."

        for filename in self.filenames:
            tokens = self._get_file_content(filename).split()
            index = {}

            words = []
            for token in tokens:
                token = self._strip(token)
                if token not in words:
                    channel.send((token, filename))
                    words.append(token)

            # Introduce a delay to simulate hard work.

            if self.delay:
                time.sleep(self.delay)

    def _strip(self, token):

        "Return the token stripped of non-alphanumeric symbols at each end."

        characters = []
        in_alphanum = 0
        for c in token:
            if not c.isalpha() and not c.isdigit():
                if in_alphanum:
                    break
            else:
                in_alphanum = 1
                characters.append(c)
        return "".join(characters)

class Indexer:
    def __init__(self):
        self.index = {}

    def get_index(self):
        return self.index

    def add_entry(self, entry):

        "Add the given word 'entry' (token, filename) to the index."

        token, filename = entry

        if not token:
            return

        slot = self.index
        for c in token:
            if not slot.has_key(c):
                slot[c] = {}, {}
            slot, words = slot[c]

        if not words.has_key(token):
            words[token] = []
        words[token].append(filename)

class Searcher:
    def __init__(self, index):
        self.index = index

    def find(self, pattern):

        "Find words beginning with the given 'pattern'."

        slot = self.index
        words = []

        for c in pattern:
            if not slot.has_key(c):
                return []
            slot, words = slot[c]

        results = {}
        results.update(words)
        results.update(self.get_all_words(slot))
        return results

    def get_all_words(self, slot):

        "Get all words under the given index 'slot'."

        all_words = {}
        keys = slot.keys()
        keys.sort()
        for c in keys:
            this_slot, words = slot[c]
            all_words.update(words)
            all_words.update(self.get_all_words(this_slot))
        return all_words

# vim: tabstop=4 expandtab shiftwidth=4
