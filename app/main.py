from fastapi import FastAPI
from .routers import user, skills, task, application, admin
from .database import engine, Base
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
# Import models to register them with SQLAlchemy
from .models import user as user_model, volunteer_task, applications, skill, password_reset

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all,checkfirst=True)
    yield  # This allows the app to run
    # You can add cleanup tasks after `yield` if needed

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*",  # Allow all origins (use specific domains in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user.router)
app.include_router(task.router)
app.include_router(application.router)
app.include_router(skills.router)
app.include_router(admin.router)