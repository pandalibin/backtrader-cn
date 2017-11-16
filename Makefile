pip:
	@echo 'pip install Python modules ...'
	@grep -Ev '^#' requirements.txt | awk -F'# ' '{print $$1}' | xargs -n 1 -L 1 pip install

deploy: clean
	@echo "upload source code to remote server ..."
	@rsync -raPH -e ssh --delete ./ gvm-2c8g:/data/web/backtrader-cn
	@rsync -raPH -e ssh --delete ./ gvm-4c8g:/root/web/backtrader-cn

test:
	coverage erase
	nosetests --with-coverage --cover-package backtradercn

webhook:
	@echo "trigger webhooks ..."
	@curl -X POST http://35.194.246.210/hooks/travis
	@curl -X POST http://35.189.182.250/webhook

clean:
	@echo "make clean ..."
	@find ./ -name '*.pyc' -exec rm -rf {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \; 2>/dev/null

.PHONY: pip, deploy, test, webhook, clean
