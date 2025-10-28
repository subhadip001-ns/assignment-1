from langchain_core.tools import tool


@tool
def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers together.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        The sum of the two numbers
    """
    return a + b
