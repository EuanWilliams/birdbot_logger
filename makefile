init: 
	python -m venv venv 
	. .\venv\Scripts\activate
	pip install -r requirements.txt

check: 
	flake8 ./
	pylint ./
	mypy --strict --explicit-package-bases ./

black:
	black ./ --line-length 160

test:
	python -m unittest discover tests/
