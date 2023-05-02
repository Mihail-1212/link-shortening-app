# Link shortening application backend

Backend application of link shortening service

Requirements:
- Python (v 3.8.1)
- pip (v 19.2.3)
- Flask (v 2.3.1)


### Quick start

Install pip libs:

```commandline
pip install -r requirements.txt
```


Create .env file (see .env.example).

Available .env vars:
- DEBUG (req) - bool variable to run app debug mode
- SECRET_KEY (req) - secret key for Flask application
- HOST (req) - host of flask application server
- PORT (req) - port of flask application server

Create database.ini file (see database.ini.example) with database variables

Migrate to database (create table):

```commandline
python main.py --migrate=True
```

Then start application:

```commandline
python main.py
```

Endpoints description:
- getAllShortLinks [GET] - return list of all short link instances
- generateShortLinkFromUrl [POST] (title, url) - generate NEW short link and return it 
- changeShortLinkInfo [PUT] (hash, title) - change info (title) of short link object
- deleteShortLink [DELETE] (hash) - remove short link instance from app
- getShortLinkByHash [POST] (hash) - getting short link by hash