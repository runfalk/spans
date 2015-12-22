clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +

doc:
	make -C doc/ html

test:
	make -C doc doctest
	tox

sdist:
	python setup.py sdist
	rm -rf *.egg-info

preview-readme:
	python -c 'import setup; print(setup.long_desc)' > README.preview.rst
	retext README.preview.rst
	rm README.preview.rst

.PHONY : clean-pyc doc test sdist preview-readme
