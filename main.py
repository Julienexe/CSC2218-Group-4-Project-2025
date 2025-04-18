import uvicorn

def run_api():
    """Run the FastAPI application"""
    # Use a dot notation that doesn't rely on the hyphenated folder name
    uvicorn.run(
        "banking_system.presentation_layer.api_endpoints:app"
, 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )

if __name__ == "__main__":
    run_api()
   
