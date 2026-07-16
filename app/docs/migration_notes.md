# To wipe and restart the database:

* Delete the database file in \instance
* Delete the migrations folder completely
* Run these three commands one after the other:

```
py -m flask --app run db init
py -m flask --app run db migrate -m "Initial schema"
py -m flask --app run db upgrade
```
