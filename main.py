from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Date, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, date
from typing import Optional

app = FastAPI()
DATABASE_URL = "sqlite:///./taskstodo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# SQLAlchemy model
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="pending")
    due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.now)
    priority = Column(String, default="medium")  # New priority field

Base.metadata.create_all(bind=engine)

# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    status: str = Field(default="pending")  
    due_date: Optional[date]
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")  # Updated to use pattern

    def validate(self):
        if self.status not in ("pending", "completed"):
            raise ValueError("Status must be 'pending' or 'completed'")
        if self.due_date and self.due_date < date.today():
            raise ValueError("Due date cannot be before today")
        if self.priority not in ("low", "medium", "high"):
            raise ValueError("Priority must be 'low', 'medium', or 'high'")

class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    due_date: Optional[date]
    priority: Optional[str]  # New priority field

@app.post("/tasks/", status_code=201)
def create_task(task: TaskCreate):
    try:
        task.validate()
        db = SessionLocal()
        new_task = Task(**task.dict())
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while creating the task.")
    finally:
        db.close()

@app.get("/tasks/")
def get_all_tasks():
    try:
        db = SessionLocal()
        tasks = db.query(Task).all()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while retrieving tasks.")
    finally:
        db.close()

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    try:
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the task.")
    finally:
        db.close()

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    try:
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        update_data = update.dict(exclude_unset=True)
        if "status" in update_data and update_data["status"] not in ("pending", "completed"):
            raise HTTPException(status_code=400, detail="Invalid status")
        if "priority" in update_data and update_data["priority"] not in ("low", "medium", "high"):
            raise HTTPException(status_code=400, detail="Invalid priority")

        for key, value in update_data.items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating the task.")
    finally:
        db.close()

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    try:
        db = SessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db.delete(task)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while deleting the task.")
    finally:
        db.close()

@app.get("/tasks/status/{status}")
def filter_by_status(status: str):
    if status not in ("pending", "completed"):
        raise HTTPException(status_code=400, detail="Invalid status")
    try:
        db = SessionLocal()
        tasks = db.query(Task).filter(Task.status == status).all()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while filtering tasks by status.")
    finally:
        db.close()

@app.get("/tasks/due/{due_date}")
def filter_by_due_date(due_date: date):
    try:
        db = SessionLocal()
        tasks = db.query(Task).filter(Task.due_date == due_date).all()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while filtering tasks by due date.")
    finally:
        db.close()

@app.get("/tasks/search/")
def search_tasks(query: str):
    try:
        db = SessionLocal()
        tasks = db.query(Task).filter(
            (Task.title.ilike(f"%{query}%")) | 
            (Task.description.ilike(f"%{query}%"))
        ).all()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while searching tasks.")
    finally:
        db.close()
