# LabServer
Some application or dockerfiles run on server

## How to Build
see BuildIt

## Add
By adminpage, if you are admin.
go to `your.domain.name/adminpage`

Add user and container automatically or by hand
`cd LabServer/LoginServer`
`docker run -it --rm -v $(pwd):/app/LoginWeb -v $(pwd)/database.db:/app/database.db linnil1/tzfserver python3`

and run 
``` python3
from tzfserver import start;
start.add(); # add user and conatiner by std
start.std_add_user() # add user by std
start.add_user(name, passwd, time=0, admin=0)
start.std_add_token(user) add token by std
start.add_token(user, tokenname, realtoken="")
```

## git
you can use
`git add -p xx`
to add modified things
