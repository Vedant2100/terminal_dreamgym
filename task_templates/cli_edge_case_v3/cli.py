import argparse
from pathlib import Path


def process_input(text: str) -> str:
    if text == "":
        raise ValueError("empty input")
    if text.startswith("!"):
        raise ValueError("bad input")
    return text.upper()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="")
    parser.add_argument("--file")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    data = Path(args.file).read_text(encoding="utf-8") if args.file else args.input
    try:
        result = process_input(data)
    except Exception as exc:
        print(str(exc))
        return 1
    if args.as_json:
        print("{result: " + result + "}")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
