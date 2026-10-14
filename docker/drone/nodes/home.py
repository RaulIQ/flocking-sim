import sys

from config import copters, sortie

if __name__ == "__main__":
    words = sortie(copters()).hangar.copters()[int(sys.argv[1]) - 1].words()
    print(words[words.index("--home") + 1])
