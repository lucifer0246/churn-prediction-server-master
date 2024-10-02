from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from routes import predict, train, auth
from controller.auth import oauth2_scheme


app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(train.router)
app.include_router(auth.router)
@app.get('/')
def main():
  return {'status':'success','message':'Hello World'}