# core/middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.db.models import Log, get_db
import json
import time

class LogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Get request details
        path = request.url.path
        method = request.method
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Try to get request body
        try:
            request_body = await request.body()
            request_body_str = request_body.decode("utf-8")
        except Exception:
            request_body_str = None
            
        # Get response
        response = await call_next(request)
        
        # Calculate process time
        process_time = time.time() - start_time
        
        # Skip logging for health checks or static files
        if path.startswith("/health") or path.startswith("/static"):
            return response
            
        # Log the request/response
        try:
            # Get DB session
            db = next(get_db())
            
            # Create log entry
            log_entry = Log(
                request_path=path,
                request_method=method,
                request_body=request_body_str if request_body_str else None,
                response_status=response.status_code,
                client_ip=client_ip,
                user_agent=user_agent,
                metadata={
                    "process_time_ms": round(process_time * 1000),
                }
            )
            
            # Add to DB
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            print(f"Error logging request: {str(e)}")
            
        return response