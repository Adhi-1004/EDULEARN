"""
Simple Test Endpoint
For debugging API issues
"""
from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Test endpoint working", "status": "success"}

@router.get("/simple")
async def simple_test():
    """Very simple test"""
    return "Hello World"
