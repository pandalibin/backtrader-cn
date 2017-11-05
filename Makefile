pip_install:
	@echo 'pip install modules ...'
	@grep -Ev '^#' requirements.txt | awk -F'# ' '{print $$1}' | xargs -n 1 -L 1 pip install

deploy: clean
	@echo "upload source code to remote server ..."
	@rsync -raPH -e ssh --delete ./ gvm-tw-backtradercn:/data/web/backtrader-cn

clean:
	@echo "make clean ..."
	@find ./ -name '*.pyc' -exec rm -rf {} \;

.PHONY: pip_install, deploy, clean
