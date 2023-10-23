import argparse
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))
from modules.evaluator import EvaluatorRunner


def check_args(arg_parser: argparse.ArgumentParser, args: argparse.Namespace):
    if not os.path.isdir(args.test_suites_dir):
        arg_parser.error(f"Tests directory doesn't exist: {args.test_suites_dir}")

    if not (args.tools.endswith(".json") and os.path.isfile(args.tools)):
        arg_parser.error(f"Tools list file doesn't exist or isn't a JSON file: {args.tools}")


def parse_args(arg_list: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluator for static analysis tools")
    parser.add_argument("--test-suites", dest="test_suites_dir",
                        help="Test suites directory", required=True)
    parser.add_argument("--tools", dest="tools",
                        help="JSON formatted file where all repository URLs are written",
                        required=True)
    args = parser.parse_args(arg_list)
    check_args(parser, args)
    return args


def parse_tools_dict(tools: str) -> dict:
    with open(tools, 'r') as json_file:
        return json.load(json_file)


def main(arg_list: list):
    args = parse_args(arg_list)
    evaluator_runner = EvaluatorRunner(args.test_suites_dir)
    evaluator_runner.run_all(parse_tools_dict(args.tools))
    evaluator_runner.save()


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as err:
        print(type(err).__name__, ": ", err)
        exit(1)
