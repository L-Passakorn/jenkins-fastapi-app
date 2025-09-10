from fastapi import FastAPI, HTTPException, Query
from typing import List
from app.utils import calculate_average, reverse_string
import time

app = FastAPI(
    title="FastAPI Clean Code Example",
    description="Simple FastAPI app for Jenkins + Docker + SonarQube pipeline demo",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Hello from FastAPI with Jenkins & SonarQube!"}


@app.get("/average")
def get_average(numbers: List[float] = Query(..., description="List ของตัวเลข")):
    try:
        result = calculate_average(numbers)
        return {"average": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/reverse")
def get_reverse(text: str = Query(..., description="ข้อความที่ต้องการกลับ")):
    result = reverse_string(text)
    return {"reversed": result}


# Code Smells for SonarQube Testing
def unused_function():
    """This function is never called - Code Smell: Dead Code"""
    pass


@app.get("/smells")
def code_smells_example():
    """Intentional code smells for SonarQube testing"""
    
    # Code Smell: Magic Numbers
    if 5 > 3:
        x = 42
    
    # Code Smell: Duplicated String Literals
    print("This is a test")
    print("This is a test")
    print("This is a test")
    
    # Code Smell: Long Parameter List (simulated)
    def bad_function(a, b, c, d, e, f, g, h):
        return a + b + c + d + e + f + g + h
    
    # Code Smell: Unused Variable
    unused_var = "This variable is never used"
    
    # Code Smell: Complex Conditional
    if x > 10 and x < 50 and x != 25 and x != 30 and x != 35:
        result = "complex condition"
    else:
        result = "simple"
    
    # Code Smell: Sleep in code (performance)
    time.sleep(0.1)
    
    return {"message": "Code smells example", "result": result}
