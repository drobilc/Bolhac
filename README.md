# Bolhač
Bolhač is your personal private detective for stolen goods. Name the item (bicycle for example) 
that was stolen and some of its specifics (males, mountain,.. for example). Bolhač will then
do the job that men in blue don't have time to do. It will search trough the internet
and e-mail you all the ads, that were added since your item was stolen and that matches your
description of it. 
Let's make theft meaningless.

## Installation
To install run following commands. You need Python 3 to run it.
```bash
sudo apt-get install python-pip python-dev libmysqlclient-dev
git clone https://github.com/drobilc/Bolhac.git
cd Bolhac
pip install -r requirements.txt
```

## Configuration
To configure server you have to copy `example-config.json` to `config.json` and set the following parameters:
* `secret_key` - key for secure storage of cookies
* `email` - configuration for sending emails to users
  * `server` - email server (e.g. `smtp.live.com`)
  * `port` - port of email server (usually 587 for SMPT)
  * `username` - email from which you want to send emails to users
  * `password` - password for your email account
* `plugins` - array of plugin options (default is `[]`)

## Running
You can run the server by typing
```bash
python server.py
```

After the server is running in development mode, you can access the website at `http://localhost:3000/`.