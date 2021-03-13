init:
	pip install --upgrade pip && pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

start_yes:
	python start.py vote_yes

start_undecided:
	python start.py