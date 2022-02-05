import argparse
import random
from dataclasses import dataclass
from enum import Enum
from math import inf


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

        for ch, pos in other.present_on.items():
            present_on[ch] = present_on.get(ch, set()) | pos

        for ch, pos in other.absent_on.items():
            absent_on[ch] = absent_on.get(ch, set()) | pos

        for ch, (t, cnt) in other.counts.items():
            ct, ccnt = counts.get(ch, (Count.Min, 0))
            if ct == Count.Min:
                if t == Count.Exact:
                    counts[ch] = (Count.Exact, cnt)
                else:
                    counts[ch] = (Count.Min, max(cnt, ccnt))

        return Knowledge(present_on, absent_on, counts)

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

    @staticmethod
    def empty():
        return Knowledge({}, {}, {})


def add_to_set(d, key, value):
    values = d.setdefault(key, set())
    values.add(value)


def add_one(d, key):
    value = d.setdefault(key, 0)
    d[key] = value + 1


def propose(words, knowledge):
    possible = list(filter(knowledge.is_possible, words))
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
        norm = 1.2 if knowledge.is_possible(word) else 1  # a slight preference of possible words
        for solution in possible:
            updated_kb = knowledge.merged_with(Knowledge.build_for_words(word, solution))
            candidate_score += sum(1 for w in possible if updated_kb.is_possible(w)) / norm
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

    knowledge = Knowledge.empty()
    while True:
        proposal = propose(words, knowledge)
        feedback = input(f'Proposal: {proposal}, feedback: ')
        if feedback == 'end' or feedback == '!!!!!':
            break
        knowledge = knowledge.merged_with(Knowledge.build_for_feedback(proposal, feedback))
