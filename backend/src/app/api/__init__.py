from fastapi import APIRouter
from src.app.api.v1 import auth, users, games, parties, party_members, messages, audit

api_router = APIRouter()

api_router.include_router(auth.router,           prefix="/auth",          tags=["Auth"])
api_router.include_router(users.router,          prefix="/users",         tags=["Users"])
api_router.include_router(games.router,          prefix="/games",         tags=["Games"])
api_router.include_router(parties.router,        prefix="/parties",       tags=["Parties"])
api_router.include_router(party_members.router,  prefix="/parties",       tags=["Party Members"])
api_router.include_router(messages.router,       prefix="/parties",       tags=["Messages"])
api_router.include_router(audit.router,          prefix="/audit",         tags=["Audit"])