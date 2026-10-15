import sys

from config import copters, sortie


def main() -> None:
    words = sortie(copters()).hangar.copters()[int(sys.argv[1]) - 1].words()
    print(words[words.index('--home') + 1])
