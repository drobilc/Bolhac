# Bolhač

## Installation
To install run following commands.
```bash
git clone https://github.com/drobilc/Bolhac.git
cd Bolhac
pip install -r requirements.txt
```

## Configuration
To configure server you have to copy `example-config.json` to `config.json` and set the following parameters:
* `email` - configuration for sending emails to users
  * `server` - email server (e.g. `smtp.live.com`)
  * `port` - port of email server (usually 587 for SMPT)
  * `username` - email from which you want to send emails to users
  * `password` - password for your email account
* `database` - configuration for MySQL database
  * `host` - database host, if you are running it locally use `localhost`
  * `username` - user for your database (please do not use root)
  * `password` - password for your user account
  * `database` - name of the database you want to use (`bolhac`)

## Running
You can run the server by typing
```bash
python server.py
```

After the server is running in development mode, you can access the website at `http://localhost:3000/`.