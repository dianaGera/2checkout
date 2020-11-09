
  - `cd config`
  - `cp .env.example .env`
  
  
  - `docker-compose build`

  - `docker-compose run django python manage.py migrate`

  - `docker-compose up`

- ### Create superuser

  - `docker-compose run django python manage.py createsuperuser`


