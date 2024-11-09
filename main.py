import server
from fastapi.middleware.cors import CORSMiddleware

# Create the app and engine
app, engine = server.get_app()

# Enable CORS on the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The app is now ready to be served!
# In production:
# uvicorn main:app --host 0.0.0.0 --port 8080