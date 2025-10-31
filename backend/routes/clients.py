from fastapi import APIRouter, HTTPException
from typing import List
from models import CloudClient
from database import cloud_clients

router = APIRouter(prefix="/api/clients", tags=["clients"])

@router.post("", response_model=CloudClient)
async def create_client(client: CloudClient):
    cloud_clients[client.id] = client
    return client

@router.get("", response_model=List[CloudClient])
async def get_clients():
    return list(cloud_clients.values())

@router.get("/{client_id}", response_model=CloudClient)
async def get_client(client_id: str):
    if client_id not in cloud_clients:
        raise HTTPException(status_code=404, detail="Client not found")
    return cloud_clients[client_id]

@router.put("/{client_id}", response_model=CloudClient)
async def update_client(client_id: str, client: CloudClient):
    if client_id not in cloud_clients:
        raise HTTPException(status_code=404, detail="Client not found")
    cloud_clients[client_id] = client
    return client

@router.delete("/{client_id}")
async def delete_client(client_id: str):
    if client_id not in cloud_clients:
        raise HTTPException(status_code=404, detail="Client not found")
    del cloud_clients[client_id]
    return {"message": "Client deleted successfully"}
