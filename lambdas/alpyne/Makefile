SHELL := /bin/bash

.DEFAULT_GOAL := help
VENV=$(CURDIR)/.venv/bin/activate

$(VENV)::$(CURDIR)/requirements.txt
	python3 -m venv $(CURDIR)/.venv
	$(CURDIR)/.venv/bin/pip install --upgrade pip
	$(CURDIR)/.venv/bin/pip install wheel
	$(CURDIR)/.venv/bin/pip install -r $(CURDIR)/requirements.txt


dev:
	$(MAKE) $(VENV)


lint:
	$(MAKE) $(VENV)
	$(CURDIR)/.venv/bin/flake8
	$(CURDIR)/.venv/bin/bandit $(CURDIR)/main.py.
	$(CURDIR)/.venv/bin/black --check .


clean:
	rm -rf $(CURDIR)/.venv


.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
