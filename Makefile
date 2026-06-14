.PHONY: test smoke demo status e2e

test:
	pytest

smoke:
	python scripts/smoke_test.py

demo:
	python scripts/integration_demo.py

status:
	python scripts/dev_status.py

e2e:
	python scripts/e2e_compare.py --pretty
