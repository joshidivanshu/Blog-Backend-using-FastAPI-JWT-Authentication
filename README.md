# Blog FastAPI & Jwt Authentication
An api for Blog using FastAPI

## Installing Requirements

Use Virtualenv and install the packages.
```
pip install -r requirements.txt
```
## Running the Project

Go to the project dir and run the below line in the terminal.

```
uvicorn main:app --reload
```

## Interacting with the API

1. To get all blogs
```
[GET]
http://localhost:800/blog 
Authorization : Bearer token
```
2. to get a blog with id
```
[GET]
http://localhost:8000/blog/{blog_id}
Authorization : Bearer token
```
3. To create a blog
```
[POST] 
http://localhost:8000/blog
in request body pass in json
{
    "title": "title of the blog",
    "body": "body of the blog"
}
Authorization : Bearer token
```
4. To delete a blog
```
[DELETE]
http://localhost:8000/blog/{blog_id}
Authorization : Bearer token
```
5. To update a blog
``` 
[PUT]
http://localhost:8000/blog/{blog_id}
in request body pass in json
{
    "title": "title of the blog",
    "body": "body of the blog"
}
Authorization : Bearer token
```
6. To retrieve access token
``` 
[POST]
http://localhost:8000/login
in form passs
username & password
``` 
7. To create a user
``` 
[POST]
http://localhost:8000/user
Authorization : Bearer token
```

### Default Username & Password

``` 
username = divanshu
password = divanshu
```