from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import Document, User
from app.schemas import (
    DocumentCreate,
    DocumentUpdate,
    Token,
    UserCreate,
    UserResponse,
)
from app.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.services.pdf_service import extract_text_from_pdf


app = FastAPI(
    title="DocuMind AI API"
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "DocuMind AI API is running!"
    }


# =========================================================
# AUTHENTICATION
# =========================================================

@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=201
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    # Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(
        user_data.password
    )

    # Create user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )

    # Save user
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================================================
# LOGIN
# =========================================================

@app.post(
    "/auth/login",
    response_model=Token
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Find user using email
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    # User doesn't exist
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    password_valid = verify_password(
        form_data.password,
        user.hashed_password
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT
    access_token = create_access_token(
        data={
            "sub": str(user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================================================
# USER PROFILE
# =========================================================

@app.get(
    "/users/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


# =========================================================
# CREATE DOCUMENT
# =========================================================

@app.post("/documents")
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_document = Document(
        filename=document.filename,
        content=document.content,
        owner_id=current_user.id
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


# =========================================================
# GET ALL MY DOCUMENTS
# =========================================================

@app.get("/documents")
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    documents = (
        db.query(Document)
        .filter(
            Document.owner_id == current_user.id
        )
        .all()
    )

    return documents


# =========================================================
# GET ONE DOCUMENT
# =========================================================

@app.get("/documents/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user.id
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


# =========================================================
# UPDATE DOCUMENT
# =========================================================

@app.put("/documents/{document_id}")
def update_document(
    document_id: int,
    updated_document: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user.id
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document.filename = updated_document.filename
    document.content = updated_document.content

    db.commit()
    db.refresh(document)

    return document


# =========================================================
# DELETE DOCUMENT
# =========================================================

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user.id
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # -------------------------
    # Validate file type
    # -------------------------

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # -------------------------
    # Read uploaded file
    # -------------------------

    file_bytes = await file.read()

    # -------------------------
    # Validate file is not empty
    # -------------------------

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty"
        )

    # -------------------------
    # Extract PDF text
    # -------------------------

    try:
        extracted_text = extract_text_from_pdf(
            file_bytes
        )

    except Exception as error:
        print(f"PDF extraction error: {error}")

        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF: {str(error)}"
        )

    # -------------------------
    # Validate extracted text
    # -------------------------

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text found in PDF"
        )

    # -------------------------
    # Create database document
    # -------------------------

    new_document = Document(
        filename=file.filename or "uploaded.pdf",
        content=extracted_text,
        owner_id=current_user.id
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return {
        "message": "PDF uploaded successfully",
        "document_id": new_document.id,
        "filename": new_document.filename,
        "text_length": len(extracted_text)
    }