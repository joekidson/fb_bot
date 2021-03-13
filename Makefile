init:
	pip install --upgrade pip && pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

ngrok:
	ngrok http 5000

start:
	python3 app.py