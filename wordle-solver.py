import argparse
from dataclasses import dataclass
from math import inf
import random


@dataclass
class Report:
    absent: set
    exact: dict
    present_not_on: dict


def is_possible(kb, word):
    for report in kb:
        if any(ch in report.absent for ch in word):
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


def add_to_set(d, key, value):
    values = d.setdefault(key, set())
    values.add(value)


def report_for_words(word, solution):
    absent = set(w for w in word if w not in solution)
    exact = {}
    present_not_on = {}
    for i, (wch, sch) in enumerate(zip(word, solution)):
        if wch == sch:
            add_to_set(exact, wch, i)

    for i, wch in enumerate(word):
        if wch in solution and i not in exact.get(wch, set()):
            add_to_set(present_not_on, wch, i)

    return Report(absent, exact, present_not_on)


def report_for_feedback(word, feedback):
    absent = set()
    exact = {}
    present_not_on = {}
    for i, (wch, fch) in enumerate(zip(word, feedback)):
        if fch == '.':
            absent.add(wch)
        elif fch == '!':
            add_to_set(exact, wch, i)
        elif fch == '?':
            add_to_set(present_not_on, wch, i)

    for ch, s in present_not_on.items():
        s.update(exact.get(ch, set()))

    return Report(absent, exact, present_not_on)


def propose(words, knowledge):
    possible = list(filter(lambda w: is_possible(knowledge, w), words))
    pos_count = len(possible)
    print(f'{pos_count} possible words found')
    max_possible = 100
    solution_found_on = 5
    if pos_count < solution_found_on:
        print(f"Solutions found: {possible}")
    if pos_count > max_possible:
        print(f'Sampling {max_possible} words')
        possible = random.sample(possible, max_possible)
    score = inf
    prop = ''
    for word in words:
        candidate_score = 0
        for solution in possible:
            knowledge.append(report_for_words(word, solution))
            candidate_score += sum(1 for w in possible if is_possible(knowledge, w))
            knowledge.pop()
        if word in possible:
            candidate_score *= 1.2  # a slight preference of possible words
        if candidate_score < score:
            prop = word
            score = candidate_score
    return prop


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Solve Wordle!')
    parser.add_argument('--dictionary', type=str, required=True)
    args = parser.parse_args()

    with open(f'dictionaries/{args.dictionary}.txt', 'r') as f:
        words = f.read().splitlines()

    knowledge = []
    while True:
        proposal = propose(words, knowledge)
        feedback = input(f'Proposal: {proposal}, feedback: ')
        if feedback == 'end':
            break
        knowledge.append(report_for_feedback(proposal, feedback))
