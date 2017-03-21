build: test doc sdist wheel

clean: clean-pyc clean-build
	rm -rf .cache/
	rm .coverage

clean-build:
	rm -rf build/
	rm -rf *.egg-info/
	make -C doc/ clean

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -type d -name '__pycache__' -exec rmdir {} +

doc:
	make -C doc/ html

test:
	make -C doc/ doctest
	pytest

sdist:
	python setup.py sdist

wheel:
	python setup.py bdist_wheel

preview-readme:
	python -c 'import setup; print(setup.long_desc)' > README.preview.rst
	retext README.preview.rst
	rm README.preview.rst


.PHONY : build clean clean-build clean-pyc doc test sdist wheel preview-readme upload
