import logging
import time
from typing import Any, Callable, Optional, Tuple, Type, TypeVar

from archipy.models.exceptions import ResourceExhaustedException

# Define a type variable for the return type of the decorated function
F = TypeVar("F", bound=Callable[..., Any])


def retry_decorator(
    max_retries: int = 3,
    delay: float = 1,
    retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    ignore: Optional[Tuple[Type[Exception], ...]] = None,
    resource_type: Optional[str] = None,
    lang: str = "fa",
) -> Callable[[F], F]:
    """
    A decorator that retries a function when it raises an exception.

    Args:
        max_retries (int): The maximum number of retry attempts. Defaults to 3.
        delay (float): The delay (in seconds) between retries. Defaults to 1.
        retry_on (Optional[Tuple[Type[Exception], ...]]): A tuple of exceptions to retry on.
            If None, retries on all exceptions. Defaults to None.
        ignore (Optional[Tuple[Type[Exception], ...]]): A tuple of exceptions to ignore (not retry on).
            If None, no exceptions are ignored. Defaults to None.
        resource_type (Optional[str]): The type of resource being exhausted. Defaults to None.
        lang (str): The language for the error message (default: "fa").

    Returns:
        Callable: The decorated function with retry logic.

    Example:
        To use this decorator, apply it to a function:

        ```python
        @retry_decorator(max_retries=3, delay=1, retry_on=(ValueError,), ignore=(TypeError,), resource_type="API")
        def unreliable_function():
            if random.random() < 0.5:
                raise ValueError("Temporary failure")
            return "Success"

        result = unreliable_function()
        ```

        Output:
        ```
        2023-10-10 12:00:00,000 - WARNING - Attempt 1 failed: Temporary failure
        2023-10-10 12:00:01,000 - INFO - Attempt 2 succeeded.
        Success
        ```
    """

    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            while retries < max_retries:
                try:
                    result = func(*args, **kwargs)
                    if retries > 0:
                        logging.info(f"Attempt {retries + 1} succeeded.")
                    return result
                except Exception as e:
                    retries += 1
                    # Check if the exception should be ignored
                    if ignore and isinstance(e, ignore):
                        raise e
                    # Check if the exception should be retried
                    if retry_on and not isinstance(e, retry_on):
                        raise e
                    logging.warning(f"Attempt {retries} failed: {e}")
                    if retries < max_retries:
                        time.sleep(delay)
            raise ResourceExhaustedException(resource_type=resource_type, lang=lang)

        return wrapper

    return decorator
