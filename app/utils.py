from typing import List
def calculate_average(numbers: List[float]) -> float:
    """
    คำนวณค่าเฉลี่ยจาก list ของตัวเลข
    """
    if not numbers:
        raise ValueError("Numbers list must not be empty")
    return sum(numbers) / len(numbers)


def reverse_string(text: str) -> str:
    """
    กลับลำดับข้อความ
    """
    return text[::-1]

