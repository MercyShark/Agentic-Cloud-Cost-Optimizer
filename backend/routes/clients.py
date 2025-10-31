from fastapi import APIRouter, HTTPException
from typing import List
from models import CloudClient
from database import db

router = APIRouter(prefix="/api/clients", tags=["clients"])

@router.post("", response_model=CloudClient)
async def create_client(client: CloudClient):
    return await db.create_client(client)

@router.get("", response_model=List[CloudClient])
async def get_clients():
    return await db.get_all_clients()

@router.get("/{client_id}", response_model=CloudClient)
async def get_client(client_id: str):
    client = await db.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/{client_id}", response_model=CloudClient)
async def update_client(client_id: str, client: CloudClient):
    existing = await db.get_client(client_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Client not found")
    return await db.update_client(client_id, client)

@router.delete("/{client_id}")
async def delete_client(client_id: str):
    success = await db.delete_client(client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}
