# Chessbot
Play chess with a line message bot! Inspired by [fbchess](https://www.facebook.com/fbchess/).
![](https://raw.githubusercontent.com/blueskyson/line-bot/master/images/1.png )

## FSM

A finite state machine that shows the operation flow of chessbot. Each position is specified as a **state**, and each move will trigger a **transition** that change the state of chessbot.
![](https://raw.githubusercontent.com/blueskyson/line-bot/master/images/fsm.png)

## How to Build
#### Build on your ubuntu machine and test via [ngrok](https://ngrok.com/)
set up environment variables
```
$ ngrok http 8000
$ export LINE_CHANNEL_SECRET=         [your channel secret]
$ export LINE_CHANNEL_ACCESS_TOKEN=   [your channel access token]
$ export DOMAIN=                      [ngrok url]
$ export PORT=                        8000
```
install dependancies and run
```
$ sudo apt install graphviz libgraphviz-dev pkg-config
$ pip3 install -r requirements.txt
$ python src/app.py
```
use "[ngrok url]/callback" as **webhook settings** on your line bot messaging API panel

#### Build on [heroku](https://www.heroku.com)
```
$ heroku git:remote -a [your app name]
$ heroku buildpacks:set heroku/python
$ heroku buildpacks:add --index 1 heroku-community/apt
$ heroku config:set LINE_CHANNEL_SECRET=         [your channel secret]
$ heroku config:set LINE_CHANNEL_ACCESS_TOKEN=   [your channel access token]
$ heroku config:set DOMAIN=                      [heroku app url]
$ heroku config:set PORT=                        8000
$ git push heroku master
```

use "[heroku app url]/callback" as **webhook settings** on your line bot messaging API panel

## How to Play

Type "help" to in chat room will show commands.

![](https://raw.githubusercontent.com/blueskyson/line-bot/master/images/2.png)
