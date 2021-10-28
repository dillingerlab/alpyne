SHELL := /bin/bash

.DEFAULT_GOAL := help
VENV=$(CURDIR)/.venv/bin/activate

$(VENV)::$(CURDIR)/requirements.txt
	python3 -m venv $(CURDIR)/.venv
	chmod 700 $(CURDIR)/.venv/bin/activate
	( \
	   source $(CURDIR)/.venv/bin/activate; \
	   pip install wheel; \
	   pip install -r $(CURDIR)/requirements.txt; \
	)


dev:
	$(MAKE) $(VENV)

lint:
	$(MAKE) $(VENV)
	flake8 || exit
	black ${CURDIR} || exit


.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
