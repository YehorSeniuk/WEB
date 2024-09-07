from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from datetime import date

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, index=True)
    room_number = Column(Integer)

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Issuance(Base):
    __tablename__ = 'issuances'

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    issue_date = Column(Date)

    employee = relationship("Employee")
    item = relationship("Item")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

class EmployeeCreate(BaseModel):
    last_name: str
    room_number: int

class ItemCreate(BaseModel):
    name: str

class IssuanceCreate(BaseModel):
    employee_id: int
    item_id: int
    issue_date: date

@app.post("/employees/")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employee(last_name=employee.last_name, room_number=employee.room_number)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.post("/items/")
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/issuances/")
def create_issuance(issuance: IssuanceCreate, db: Session = Depends(get_db)):
    db_issuance = Issuance(employee_id=issuance.employee_id, item_id=issuance.item_id, issue_date=issuance.issue_date)
    db.add(db_issuance)
    db.commit()
    db.refresh(db_issuance)
    return db_issuance

@app.get("/employees/")
def read_employees(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Employee).offset(skip).limit(limit).all()

@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Item).offset(skip).limit(limit).all()

@app.get("/issuances/")
def read_issuances(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Issuance).offset(skip).limit(limit).all()

@app.get("/employees/{employee_id}")
def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Робітник не знайден")
    return db_employee

@app.get("/items/{item_id}")
def get_item_by_id(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Майно не знайдено")
    return db_item

@app.get("/issuances/{issuance_id}")
def get_issuance_by_id(issuance_id: int, db: Session = Depends(get_db)):
    db_issuance = db.query(Issuance).filter(Issuance.id == issuance_id).first()
    if db_issuance is None:
        raise HTTPException(status_code=404, detail="Запис про відповідальність не знайдено")
    return db_issuance

@app.get("/employees/")
def get_employees_by_last_name(last_name: str, db: Session = Depends(get_db)):
    db_employees = db.query(Employee).filter(Employee.last_name == last_name).all()
    if not db_employees:
        raise HTTPException(status_code=404, detail="Робітник із таким прізвищем не знайден")
    return db_employees

@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Робітник не знайден")

    db_employee.last_name = employee.last_name
    db_employee.room_number = employee.room_number
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Майно не знайдено")

    db_item.name = item.name
    db.commit()
    db.refresh(db_item)
    return db_item


@app.put("/issuances/{issuance_id}")
def update_issuance(issuance_id: int, issuance: IssuanceCreate, db: Session = Depends(get_db)):
    db_issuance = db.query(Issuance).filter(Issuance.id == issuance_id).first()
    if db_issuance is None:
        raise HTTPException(status_code=404, detail="Запис про відповідальність не знайдено")

    db_issuance.employee_id = issuance.employee_id
    db_issuance.item_id = issuance.item_id
    db_issuance.issue_date = issuance.issue_date
    db.commit()
    db.refresh(db_issuance)
    return db_issuance


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Робітник не найден")

    db.delete(db_employee)
    db.commit()
    return {"detail": "Робітник видален"}


@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Майно не знайдено")

    db.delete(db_item)
    db.commit()
    return {"detail": "Майно видалено"}


@app.delete("/issuances/{issuance_id}")
def delete_issuance(issuance_id: int, db: Session = Depends(get_db)):
    db_issuance = db.query(Issuance).filter(Issuance.id == issuance_id).first()
    if db_issuance is None:
        raise HTTPException(status_code=404, detail="Відповідальність не знайдено")

    db.delete(db_issuance)
    db.commit()
    return {"detail": "Відповідальність видалено"}