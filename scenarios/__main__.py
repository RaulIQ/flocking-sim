from argparse import ArgumentParser
from pathlib import Path

from scenarios.catalogue import catalogue
from scenarios.trial import Trial

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="python -m scenarios",
        description="Run scripted flights and write their logs into scenarios/logs",
    )
    parser.add_argument("names", nargs="*", help="scenarios to run, or all")
    parser.add_argument("--watch", action="store_true", help="play in a window too")
    arguments = parser.parse_args()
    if not arguments.names:
        for name, scenario in catalogue().items():
            print(f"{name:14s}{scenario.story}")
    for name in catalogue() if arguments.names == ["all"] else arguments.names:
        if name not in catalogue():
            parser.error(f"There is no scenario named {name}")
        trial = Trial(name, catalogue()[name], 6)
        print("\n".join(trial.run(Path(__file__).parent / "logs").lines()[:-1]), end="\n\n")
        if arguments.watch:
            from scenarios.screening import Screening

            Screening(trial).run()
