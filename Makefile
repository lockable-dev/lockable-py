VENV_NAME?=venv
PYTHON?=python3.7
include .env.local

venv: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: setup.cfg
	virtualenv --python "$(which $(PYTHON))" --clear $(VENV_NAME)
	$(VENV_NAME)/bin/pip install pip==22.1
	$(VENV_NAME)/bin/pip install -r requirements-dev.txt
	$(VENV_NAME)/bin/pip install -e .

build: venv
	$(VENV_NAME)/bin/python -m build

test-publish: clean venv build
	@$(VENV_NAME)/bin/python -m twine upload \
		dist/* \
		--repository testpypi \
		-u $(TEST_PIPY_USERNAME) \
		-p $(TEST_PIPY_PASSWORD) \
		--verbose

lint: venv
	$(VENV_NAME)/bin/black src/lockable
	$(VENV_NAME)/bin/isort src/lockable
	$(VENV_NAME)/bin/flake8 src/lockable

clean:
	rm -rf $(VENV_NAME) dist/


.PHONY: venv build test-publish lint clean
