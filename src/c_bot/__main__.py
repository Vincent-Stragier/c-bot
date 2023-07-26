"""Main entry point for the c_bot application."""
from .c_bot import main

if __name__ != "__main__":
    raise RuntimeError("Only for use with the -m switch, not as a Python API")

# Run the main function
main()
