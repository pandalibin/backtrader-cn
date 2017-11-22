.PHONY: all, pip, install-dev, deploy, test, coverage, webhook, lint, docs, clean

all: test

pip:
	@echo 'pip install Python modules ...'
	@grep -Ev '^#' requirements.txt | awk -F'# ' '{print $$1}' | xargs -n 1 -L 1 pip install

install-dev:
	@pip install -U -r dev-requirements.txt

deploy: clean
	@echo "upload source code to remote server ..."
	@rsync -raPH -e ssh --delete ./ gvm-2c8g:/data/web/backtrader-cn
	@rsync -raPH -e ssh --delete ./ gvm-4c8g:/root/web/backtrader-cn

test: clean install-dev
	pytest

coverage: clean install-dev
	coverage run --source backtradercn -m pytest -v
	coverage report

webhook:
	@echo "trigger webhooks ..."
	@curl -X POST http://35.194.246.210/hooks/travis
	@curl -X POST http://35.189.182.250/webhook

lint:
	pylint *.py backtradercn

docs: clean install-dev
	$(MAKE) -C docs html

clean:
	@echo "make clean ..."
	@find ./ -name '*.pyc' -exec rm -f {} +
	@find ./ -name '*.pyo' -exec rm -f {} +
	@find ./ -name '*~' -exec rm -f {} +
	@find ./ -name '__pycache__' -exec rm -rf {} +
