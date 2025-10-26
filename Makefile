SHELL := /usr/bin/env bash
.ONESHELL:

SCRIPT_DIR := $(CURDIR)/scripts
ARGS ?=

.PHONY: bootstrap dev lint fmt typecheck test e2e coverage build package release update-deps security-scan sbom gen-docs migrate clean check

bootstrap:
	$(SCRIPT_DIR)/bootstrap $(ARGS)

dev:
	$(SCRIPT_DIR)/dev $(ARGS)

lint:
	$(SCRIPT_DIR)/lint $(ARGS)

fmt:
	$(SCRIPT_DIR)/fmt $(ARGS)

typecheck:
	$(SCRIPT_DIR)/typecheck $(ARGS)

test:
	$(SCRIPT_DIR)/test $(ARGS)

e2e:
	$(SCRIPT_DIR)/e2e $(ARGS)

coverage:
	$(SCRIPT_DIR)/coverage $(ARGS)

build:
	$(SCRIPT_DIR)/build $(ARGS)

package:
	$(SCRIPT_DIR)/package $(ARGS)

release:
	$(SCRIPT_DIR)/release $(ARGS)

update-deps:
	$(SCRIPT_DIR)/update-deps $(ARGS)

security-scan:
	$(SCRIPT_DIR)/security-scan $(ARGS)

sbom:
	$(SCRIPT_DIR)/sbom $(ARGS)

gen-docs:
	$(SCRIPT_DIR)/gen-docs $(ARGS)

migrate:
	$(SCRIPT_DIR)/migrate $(ARGS)

clean:
	$(SCRIPT_DIR)/clean $(ARGS)

check:
	$(SCRIPT_DIR)/check $(ARGS)
