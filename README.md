# DonorsKG-Website

# Setup

#### Local

`python -m venv forSite`

`.\forSite\Scripts\activate`

`pip install -r requirements.txt`

`python manage.py migrate`

`python manage.py runserver`

#### Docker

`docker build --tag kg-site .`

`docker run -p 8000:8000 --name querygenerator -d kg-site`
