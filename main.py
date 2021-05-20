from fastapi import FastAPI, Depends, status, Response, HTTPException
import schemas
import models
import database
from sqlalchemy.orm import Session
from typing import List
import hashing
from jose import JWTError, jwt
import myjwttoken
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


app = FastAPI()

models.database.Base.metadata.create_all(database.engine)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# the route from which the fastapi will fetch the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# def get_current_user(token: str = Depends(oauth2_scheme),  db: Session = Depends(database.get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = schemas.TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = db.query(models.User).filter(models.User.username == token_data.username).first()
#     if user is None:
#         raise credentials_exception
#     return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print("jwt decode started")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("jwt decode successfull")
        username: str = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        print("jwt error!!!")
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        print("user doesn't exist")
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post('/blog', status_code=status.HTTP_201_CREATED, response_model=schemas.ShowBlog, tags=['blog'])
async def create(request: schemas.Blog, db: Session = Depends(database.get_db),
                 current_user: schemas.User = Depends(get_current_active_user)):
    new_blog = models.Blog(title=request.title, body=request.body, user_id=1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.delete('/blog/{blog_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['blog'])
async def delete_blog(blog_id, db: Session = Depends(database.get_db),
                      current_user: schemas.User = Depends(get_current_active_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The blog with id {blog_id} doesn't exist.")   
    blog.delete(synchronize_session=False)
    db.commit()


@app.put('/blog/{blog_id}', status_code=status.HTTP_202_ACCEPTED, tags=['blog'])
async def update_blog(blog_id, request: schemas.Blog, db: Session = Depends(database.get_db),
                      current_user: schemas.User = Depends(get_current_active_user)):
    blog = db.query(models.Blog).filter(models.Blog.id==blog_id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The blog with id {blog_id} doesn't exist.")   
    # blog.update({'title':request.title,'body':request.body},
    #                             synchronize_session=False) 
    blog.update(request)                   
    db.commit()                            
    return {"Response":f"Updated the blog with id {blog_id} successfully!!"}                            


@app.get('/blog', response_model=List[schemas.ShowBlog], tags=['blog'])
async def all_blog(db: Session = Depends(database.get_db),
                   current_user: schemas.User = Depends(get_current_active_user)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get('/blog/{blog_id}', status_code=200, response_model=schemas.ShowBlog, tags=['blog'])
async def get_blog(blog_id,response: Response, db: Session = Depends(database.get_db),
                   current_user: schemas.User = Depends(get_current_active_user)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with the id {blog_id} is not available")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"detail":f"Blog with the id {blog_id} is not available"}
    return blog 


@app.post('/user', response_model=schemas.ShowUser, tags=['accounts'])
def create_user(request: schemas.User, db: Session = Depends(database.get_db)):
    new_user = models.User(username=request.username,email=request.email
                            ,password=hashing.Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get('/user', response_model=List[schemas.ShowUser], tags=['accounts'])
async def get_all_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return users


@app.get('/user/{user_id}', status_code=200, response_model=schemas.ShowUser, tags=['accounts'])
async def get_user(user_id,response: Response, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with the id {user_id} doest not exist")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"detail":f"Blog with the id {blog_id} is not available"}
    return user


#
@app.post('/login', tags=['Authentication'])
async def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User doesn't exist")
    if not hashing.Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect Password!")
    # generate a jwt token

    access_token = myjwttoken.create_access_token( data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
    return user
    




    