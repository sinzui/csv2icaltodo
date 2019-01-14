p=test*.py
lint:
	flake8 $$(find . -name '*.py') --builtins xrange,basestring
test:
	TMPDIR=/tmp python -m unittest discover -vv . -p "$(p)"
cover:
	python -m coverage run --source="./" --omit "./tests/*" -m unittest discover -vv ./tests
	python -m coverage report
clean:
	find . -name '*.pyc' -delete
.PHONY: lint test cover clean
