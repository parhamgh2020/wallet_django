# wallet

### how to run 

```
to install dependency:
first make virtual environment 
install dependency by: pip install -r requirement 

to make sqlite
go to project directory 
run: python3 ./manage.py makemigrations
run: python3 ./manage.py migrate

to load data
run: python3 ./manage.py loaddata data/db.json

to run project:
go to project directory 
run: python3 ./manage.py runserver 

for test: 
go to project directory 
run: python3 ./manage.py test

note : there is no need to run third party app, the app is similated in utils.py module
```
### project end points
```commandline
to find out all endpoints please check swagger in "/api/docs/" endpoint
```


