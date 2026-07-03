install:
	pip install -e ".[dev]"

demo:
	python -m terminal_dreamgym.cli demo

test:
	pytest -q

report:
	python -m terminal_dreamgym.cli report
