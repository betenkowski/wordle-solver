import re
import urllib.request

pattern = re.compile(r'/[\w]+$')


if __name__ == '__main__':
    with urllib.request.urlopen('https://raw.githubusercontent.com/BramboraSK/slovnik-slovenskeho-jazyka/main'
                                '/opravene.txt') as f:
        lines = filter(lambda line: pattern.search(line), f.read().decode('utf-8').splitlines())
        words = map(lambda s: pattern.sub('', s), lines)
        words5l = filter(lambda s: len(s) == 5 and s.lower() == s, words)

    # TODO: cmd line param
    with open('/Users/bartek/Downloads/dict_sk.txt', 'w') as f:
        for word in words5l:
            f.write(word + '\n')
