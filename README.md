# fb_bot
Testing out a facebook bot

Instructions for setting up the Facebook app can be found [here](https://www.twilio.com/blog/2017/12/facebook-messenger-bot-python.html)

## To start

1. Run the installer
2. Start the script

```
make init
make start_yes
OR
make start_undecided
```

Non Makefile instructions

```
pip install --upgrade pip && pip install -r requirements.txt
python start.py vote_yes
OR
python start.py
```