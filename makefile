build: test_requirements test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install pip-tools
	pip-sync tests/requirements.txt

update_requirements:
	pip-compile --output-file tests/requirements.txt tests/requirements.in

upgrade_requirements:
	pip-compile --upgrade --output-file tests/requirements.txt tests/requirements.in

static_analysis: pep8 xenon

pep8:
	@echo "Running flake8 over codebase"
	flake8 --ignore=E501,W391,F999 zmqservices/

xenon:
	@echo "Running xenon over codebase"
	xenon --max-absolute B --max-modules B --max-average A zmqservices/

test: clean static_analysis
	py.test -rw tests --timeout=1 --cov=zmqservices $(pytest_args)

.PHONY: build clean test_requirements test static_analysis pep8 xenon update_requirements upgrade_requirements
