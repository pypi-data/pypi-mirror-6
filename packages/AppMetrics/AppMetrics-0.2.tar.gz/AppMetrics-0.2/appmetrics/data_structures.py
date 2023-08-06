##  Module data_structures.py
##
##  Copyright (c) 2014 Antonio Valente <y3sman@gmail.com>
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##  http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.

import random


class SkipListNode(object):
    def __init__(self, value, level):
        self.value = value
        self.next = [None] * level

    def iterate(self, level):
        current = self
        while current is not None:
            yield current
            current = current.next[level]

    def count(self, level):
        count = 0
        current = self
        while current is not None:
            count += 1
            current = current.next[level]
        return count

    def __str__(self):
        return str(self.value)


class SkipList(object):
    def __init__(self, key=None, max_levels=16):
        self.key = key if key is not None else (lambda x: x)
        self.max_levels = max_levels
        self.levels = 0

        self.head = SkipListNode("<<HEAD>>", max_levels)

    def insert(self, value):
        height = 1
        while random.random() < 0.5 and height <= self.max_levels:
            height += 1
        if height > self.levels:
            self.levels = height

        current = self.head
        loops = 0

        new = SkipListNode(value, height)
        for l in range(height-1, -1, -1):
            while current.next[l] is not None:
                loops += 1
                if self.key(current.next[l].value) > self.key(value):
                    break
                current = current.next[l]

            if l < len(current.next):
                new.next[l] = current.next[l]
                current.next[l] = new

        return loops

    def __iter__(self):
        for node in  self.head.next[0].iterate(0):
            yield node.value

    def __str__(self):
        if not self.levels:
            return "Empty"

        # list width - level 0 contains all of the items
        width = self.head.count(0)

        out = []
        for l in range(self.levels-1, -1, -1):
            line = [""] * width
            for i, node in enumerate(self.head.iterate(l)):
                line[i] = str(self.key(node.value))

            out.append("|".join(["Level %s (%s)" % (l, i)]+line))
        return "\n".join(out)

