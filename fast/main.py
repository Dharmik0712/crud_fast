from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import SessionLocal, engine
from models import Book as BookModel
from database import Base
Base.metadata.create_all(bind=engine)

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str
    publication_year: int
    ISBN: str

    class Config:
        orm_mode = True


# DB Dependency (session manager)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE
@app.post("/books/", response_model=Book)
async def create_book(book: Book, db: Session = Depends(get_db)):
    db_book = BookModel(
        title=book.title,
        author=book.author,
        publication_year=book.publication_year,
        ISBN=book.ISBN,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


# READ (ALL)
@app.get("/books/", response_model=List[Book])
async def get_books(db: Session = Depends(get_db)):
    return db.query(BookModel).all()


# READ (ONE)
@app.get("/books/{ISBN}", response_model=Book)
async def get_book(ISBN: str, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.ISBN == ISBN).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# UPDATE
@app.put("/books/{ISBN}", response_model=Book)
async def update_book(ISBN: str, updated_book: Book, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.ISBN == ISBN).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.title = updated_book.title
    book.author = updated_book.author
    book.publication_year = updated_book.publication_year

    db.commit()
    db.refresh(book)
    return book


# DELETE
@app.delete("/books/{ISBN}", response_model=Book)
async def delete_book(ISBN: str, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.ISBN == ISBN).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return book


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
