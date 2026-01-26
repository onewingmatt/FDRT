
# Import and mount static files
from fastapi.staticfiles import StaticFiles
import os

# Mount the current directory as static files
app.mount("/static", StaticFiles(directory="."), name="static")
