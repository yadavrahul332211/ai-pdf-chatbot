from fastapi import FastAPI
from database import Base, engine
from auth import router as auth_router
from chatbot import router as chat_router

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include both routers
app.include_router(auth_router)
app.include_router(chat_router)

