SHELL := /bin/bash

.PHONY: run_unit_tests run_integration_tests

run_unit_tests:
	source .venv/bin/activate && pytest -m "not integration_test and not end2end_test"

run_integration_tests:
	ENVIRONMENT="test"
	source .venv/bin/activate && pytest -m integration_test -vv
	unset ENVIRONMENT

run_coverage:
	coverage run --source=. --omit="./tests/*,./database/*" -m pytest && coverage report -m
	coverage html

