import argparse
from dataclasses import dataclass
from math import inf
import random
from enum import Enum
from itertools import chain


class Count(Enum):
    Min = 1
    Exact = 2


@dataclass
class Knowledge:
    present_on: dict
    absent_on: dict
    counts: dict  # character → (Min|Exact, count)

    def is_possible(self, word):
        for ch, positions in self.present_on.items():
            if any(word[position] != ch for position in positions):
                return False

        for ch, positions in self.absent_on.items():
            if any(word[position] == ch for position in positions):
                return False

        for ch, (t, count) in self.counts.items():
            cnt = word.count(ch)
            if t == Count.Min and cnt < count:
                return False
            elif t == Count.Exact and cnt != count:
                return False

        return True

    def merged_with(self, other):
        present_on = self.present_on.copy()
        absent_on = self.absent_on.copy()
        counts = self.counts.copy()

        for ch, pos in other.present_on:
            present_on[ch] = present_on.get(ch, set()) | pos

        for ch, pos in other.absent_on:
            absent_on[ch] = absent_on.get(ch, set()) | pos

        for ch, (t, cnt) in other.counts:
            ct, ccnt = counts.get(ch, (Count.Min, 0))
            if ct == Count.Min:
                if t == Count.Exact:
                    counts[ch] = (Count.Exact, cnt)
                else:
                    counts[ch] = (Count.Min, max(cnt, ccnt))

        Knowledge(present_on, absent_on, counts)

    @staticmethod
    def build_for_words(word, solution):
        present_on = {}
        absent_on = {}
        counts = {}

        for i, (wch, sch) in enumerate(zip(word, solution)):
            if wch == sch:
                add_to_set(present_on, wch, i)
            else:
                add_to_set(absent_on, wch, i)

        for wch in word:
            if wch in counts:
                continue
            word_count = word.count(wch)
            solution_count = solution.count(wch)
            counts[wch] = (Count.Exact if word_count > solution_count else Count.Min, min(word_count, solution_count))

        return Knowledge(present_on, absent_on, counts)

    @staticmethod
    def build_for_feedback(word, feedback):
        present_on = {}
        absent_on = {}
        counts = {}
        grays = set()

        for i, (wch, fch) in enumerate(zip(word, feedback)):
            if fch == '!':
                add_to_set(present_on, wch, i)
                add_one(counts, wch)
            elif fch == '?':
                add_to_set(absent_on, wch, i)
                add_one(counts, wch)
            elif fch == '.':
                add_to_set(absent_on, wch, i)
                counts.setdefault(wch, 0)
                grays.add(wch)

        counts = {ch: (Count.Exact if ch in grays else Count.Min, cnt) for ch, cnt in counts.items()}

        return Knowledge(present_on, absent_on, counts)


@dataclass
class Report:
    absent: dict
    exact: dict
    present_not_on: dict

    def __post_init__(self):
        self.cache = {}


def is_possible_single(report, word):
    if word in report.cache:
        return report.cache[word]

    def impl():
        for ch, positions in report.absent.items():
            e = report.exact.get(ch, set())
            p = report.present_not_on.get(ch, set())
            if not e and not p:
                if ch in word:
                    return False
            else:
                if word.count(ch) != len(e) + len(p):
                    return False
                if any(word[i] == ch for i in positions):
                    return False

        for ch, positions in report.exact.items():
            if any(word[pos] != ch for pos in positions):
                return False

        for ch, positions in report.present_not_on.items():
            found = False
            for i, wch in enumerate(word):
                if wch == ch and i not in positions:
                    found = True
            if not found:
                return False

        return True

    ret = impl()
    report.cache[word] = ret
    return ret


def is_possible(kb, word):
    for report in kb:
        if not is_possible_single(report, word):
            return False
    return True


def add_to_set(d, key, value):
    values = d.setdefault(key, set())
    values.add(value)


def add_one(d, key):
    value = d.setdefault(key, 0)
    d[key] = value + 1


def report_for_words(word, solution):
    absent = {}
    exact = {}
    present_not_on = {}
    analyzed = {}
    for i, (wch, sch) in enumerate(zip(word, solution)):
        if wch == sch:
            add_to_set(exact, wch, i)
            add_one(analyzed, wch)

    for i, (wch, sch) in enumerate(zip(word, solution)):
        if wch != sch:
            if wch in solution \
                    and i not in exact.get(wch, set()) \
                    and analyzed.get(wch, 0) < solution.count(wch):
                add_to_set(present_not_on, wch, i)
                add_one(analyzed, wch)
            else:
                add_to_set(absent, wch, i)

    return Report(absent, exact, present_not_on)


def report_for_feedback(word, feedback):
    absent = {}
    exact = {}
    present_not_on = {}
    for i, (wch, fch) in enumerate(zip(word, feedback)):
        if fch == '.':
            add_to_set(absent, wch, i)
        elif fch == '!':
            add_to_set(exact, wch, i)
        elif fch == '?':
            add_to_set(present_not_on, wch, i)

    return Report(absent, exact, present_not_on)


def propose(words, knowledge):
    possible = list(filter(lambda w: is_possible(knowledge, w), words))
    pos_count = len(possible)
    print(f'{pos_count} possible words found')

    max_possible = 75
    max_complexity = 16875000 * 2
    effective_pos = min(pos_count, max_possible)

    candidates = words
    if len(words) * pos_count * pos_count > max_complexity:
        cnt = int(max_complexity / (effective_pos * effective_pos))
        if cnt < len(words):
            print(f'Sampling {cnt} words')
            candidates = random.sample(words, cnt)

    solution_found_on = 5
    if pos_count < solution_found_on:
        print(f"Solutions found: {possible}")
    if pos_count > max_possible:
        print(f'Sampling {max_possible} possible words')
        possible = random.sample(possible, max_possible)
    score = inf
    prop = ''
    for word in candidates:
        candidate_score = 0
        norm = 1.2 if is_possible(knowledge, word) else 1  # a slight preference of possible words
        for solution in possible:
            knowledge.append(report_for_words(word, solution))
            candidate_score += sum(1 for w in possible if is_possible(knowledge, w)) / norm
            knowledge.pop()
            if candidate_score > score:
                break
        if candidate_score < score:
            prop = word
            score = candidate_score
    return prop


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Solve Wordle!')
    parser.add_argument('--dictionary', type=str, required=True)
    args = parser.parse_args()

    with open(f'dictionaries/{args.dictionary}.txt', 'r') as f:
        words = list(filter(lambda w: len(w) == 5, f.read().splitlines()))

    knowledge = []
    while True:
        proposal = propose(words, knowledge)
        feedback = input(f'Proposal: {proposal}, feedback: ')
        if feedback == 'end' or feedback == '!!!!!':
            break
        knowledge.append(report_for_feedback(proposal, feedback))
