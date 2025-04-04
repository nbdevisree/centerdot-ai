from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from typing import Optional
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# MongoDB connection details
MONGO_URI = os.getenv("MONGO_URI")

# Initialize FastAPI and MongoDB client
app = FastAPI()

# Add CORSMiddleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, for development purposes
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

client = MongoClient(MONGO_URI)
db = client['sales']  # Select the sales database
contacts_collection = db['contacts']  # Select the contacts collection

# Pydantic model to validate incoming form data
class FormData(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    phone: str
    company: str
    role: str
    message: str
    timestamp: Optional[str] = None  # Optional field for timestamp

    # Optional: Add validation for phone number format
    # You can enhance this with a regex if needed

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI is working!"}

@app.post("/submit_form")
async def submit_form(form_data: FormData):
    # Check if required fields are present
    required_fields = ["firstName", "lastName", "email", "phone", "company", "role", "message"]
    missing_fields = [field for field in required_fields if not getattr(form_data, field)]

    if missing_fields:
        raise HTTPException(status_code=400, detail=f"Missing fields: {', '.join(missing_fields)}")

    # Prepare document to insert into MongoDB
    document = {
        "firstName": form_data.firstName,
        "lastName": form_data.lastName,
        "email": form_data.email,
        "phone": form_data.phone,
        "company": form_data.company,
        "role": form_data.role,
        "message": form_data.message,
        "status": "submitted",  # Tracking the submission status
        "timestamp": form_data.timestamp or datetime.now().isoformat()  # Add current timestamp if not provided
    }

    # Insert the form data into the MongoDB collection
    result = contacts_collection.insert_one(document)

    # Return a success response with inserted ID
    return {"status": "success", "message": "Form submitted successfully", "id": str(result.inserted_id)}

