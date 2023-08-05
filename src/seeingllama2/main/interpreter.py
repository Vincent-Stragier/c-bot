# -*- coding: utf-8 -*-
"""This module is used to interpret the function call of the LLMs."""
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler
handler = logging.FileHandler("interpreter.log")
handler.setLevel(logging.DEBUG)

AUTHORIZED_COMMANDS = [
    "detect",
    "color",
    "colors",
    "navigation",
    "position",
    "add",
    "remove",
    "look_for",
    "enumerate_individuals",
    "age_estimation",
    "emotion_estimation",
    "ocr",
    "money",
    "environment",
    "environment_question",
]


def detect(object_to_detect: str | None = None) -> bool | list:
    """Detect the visible object using a model such as YOLOv8.

    Args:
        object_to_detect (str | None, optional): The object to detect.
        Defaults to None.

    Returns:
        bool|list: True or False if the object is detected,
        else a list of objects.
    """
    # Detect all the objects here
    detected_objects = ["chair", "mocked module"]
    logger.debug("detected_objects: %s", detected_objects)
    logger.info("mocked detect")

    if object_to_detect is None:
        return detected_objects

    if isinstance(object_to_detect, str):
        return object_to_detect in detected_objects

    raise ValueError("`object_to_detect` should be None, or a string.")


def color(object_name: str | None = None) -> tuple:
    """Pick the dominant color of the mentioned object or of the environment.

    Args:
        object_name (str | None, optional): The name of the object.
        Defaults to None.

    Returns:
        tuple: The color in RGB
    """
    logger.info("mocked color")

    if object_name is None:
        # Compute the mean color of the input frame
        return (
            0,
            0,
            255,
        )

    if isinstance(object_name, str):
        # Detect object and realize mean on the area of the bounding box
        # or on the segmented area ???
        return (
            255,
            0,
            0,
        )

    raise ValueError("`object_to_detect` should be None, or a string.")


def colors() -> tuple:
    """Pick the dominant color of the environment.

    Returns:
        tuple: The color in RGB
    """
    logger.info("mocked colors")
    return (
        0,
        255,
        0,
    )


def navigation(destination: str) -> str:
    """Navigate to the given destination.

    Args:
        destination (str): The destination to reach.

    Returns:
        str: The status of the navigation.
    """
    logger.info("mocked navigation")
    return f"You have reached your {destination}."


def position() -> dict:
    """Get the current position of the user.

    Returns:
        tuple: The position of the user
    """
    logger.info("mocked position")
    return {"latitude": 25, "longitude": 65, "altitude": 9}


def add() -> str:
    """Add a face to the face recognition database.

    Returns:
        str: The status of the addition.
    """
    logger.info("mocked add")
    return "Face successfully added."


def remove() -> str:
    """Remove a face from the face recognition database.

    Returns:
        str: The status of the removal.
    """
    logger.info("mocked remove")
    return "Face successfully removed."


def look_for(name: str) -> str:
    """Look for the given person in the face recognition database
    and return the status of the search.

    Args:
        name (str): The name of the person to look for.

    Returns:
        str: The status of the search.
    """
    logger.info("mocked look_for(%s)", name)
    return "True"


def enumerate_individuals() -> list:
    """Enumerate all the individuals in the environment.

    Returns:
        list: The list of the individuals.
    """
    logger.info("mocked enumerate_individuals")
    return [
        "individual1",
        "individual2",
        "jhon doe",
        "jane doe",
        "mocked individual",
    ]


def age_estimation(name: str) -> int:
    """Estimate the age of the given person.

    Args:
        name (str): The name of the person.

    Returns:
        int: The estimated age.
    """
    logger.info("mocked age_estimation of %s", name)
    return 25


def emotion_estimation(name: str) -> str:
    """Estimate the emotion of the given person.

    Args:
        name (str): The name of the person.

    Returns:
        str: The estimated emotion.
    """
    logger.info("mocked emotion_estimation of %s", name)
    return "neutral"


def ocr(object_name: str | None = None) -> str:
    """Read the text on the mentioned object or on the every object.

    Args:
        object_name (str | None, optional): The name of the object.
        Defaults to None.

    Returns:
        str: The text read.
    """
    logger.info("mocked ocr")

    if object_name is None:
        # Read the text on the whole image
        return "mocked text on the whole image"

    if isinstance(object_name, str):
        # Detect object and read the text on the area of the bounding box
        return "mocked text on the object"

    raise ValueError("`object_to_detect` should be None, or a string.")


def money() -> dict:
    """Count the money in the wallet.

    Returns:
        int: The amount of money.
    """
    logger.info("mocked money")
    return {"total_amount": 25, "currency": "EUR", "details": (5, 10, 10)}


def environment() -> str:
    """Describe the environment.

    Returns:
        str: The description of the environment.
    """
    logger.info("mocked environment")
    return "mocked environment description"


def environment_question(question: str) -> str:
    """Answer the given question about the environment.

    Args:
        question (str): The question to answer.

    Returns:
        str: The answer to the question.
    """
    logger.info("mocked environment_question: %s", question)
    return "mocked answer to the question"


def extract_parameters(parameters_string: str) -> list:
    """Extract the parameters from the parameters string.

    Args:
        parameters_string (str): the parameters string.

    Returns:
        list: the parameters
    """
    separator = ","
    quotes = ["'", '"']
    escape = "\\"

    inhibited = False
    parameters = []
    accumulator = ""

    parameters_string = parameters_string.strip()

    # Go through the string and extract the parameters
    for index, char in enumerate(parameters_string):
        accumulator += char

        # Check if the character is in quotes and if it is not escaped.
        if char in quotes and parameters_string[index - 1] != escape:
            inhibited = not inhibited

        if char == separator:
            # If the character is a separator and it is not in quotes
            if not inhibited:
                # Add the parameter to the list
                parameters.append(accumulator[:-1].strip())

                # Reset the accumulator
                accumulator = ""

    return parameters + [accumulator.strip()]


def extract_command(command: str):
    """Extract the command name and parameters from the command string.

    Args:
        command (str): the command to interpret

    Returns:
        tuple: the command name and the parameters
    """
    # Extract the command name
    re_command = r"^([a-zA-Z_.][a-zA-Z0-9_.]+)\("
    command_name = re.findall(re_command, command)[0]

    # Extract the parameters
    re_parameters = r"\((.*)\)$"
    parameters = re.findall(re_parameters, command)[0].strip()

    parameters = extract_parameters(parameters)

    # Convert the parameters to the correct type without using eval
    for index, parameter in enumerate(parameters):
        try:
            parameters[index] = int(parameter)
        except ValueError:
            try:
                parameters[index] = float(parameter)
            except ValueError:
                if parameter.startswith(('b"', "b'")):
                    parameters[index] = parameter[2:-1].encode()

                elif parameter.startswith(("0x", "0X")):
                    parameters[index] = int(parameter, 16)

                elif parameter.startswith(("0b", "0B")):
                    parameters[index] = int(parameter, 2)

                elif parameter == "True":
                    parameters[index] = True

                elif parameter == "False":
                    parameters[index] = False

                elif parameter == "None":
                    parameters[index] = None

                elif parameter.startswith('"') and parameter.endswith('"'):
                    parameters[index] = parameter[1:-1].replace("\\", "")

                elif parameter.startswith("'") and parameter.endswith("'"):
                    parameters[index] = parameter[1:-1].replace("\\", "")

    return command_name, parameters


def interpreter(command: str, run: bool = False):
    """Interpret the given command and run it if asked to.

    The interpreter is based on the following grammar:

    command = command_name '(' parameters ')'
    parameters = parameter (',' parameter)*
    parameter = string | number | boolean | None | bytes

    It is not perfect and can be improved.
    Variables are not supported and are passed as strings.
    Keywords arguments are not supported either.

    Args:
        command (str): the command to interpret
        run (bool, optional): Whether to run or not the command.
        Defaults to False.

    Returns:
        functor, parameters or return of the running function: the functor and
        the parameters or the return of the running function
    """
    # Extract the command name and parameters
    command_name, parameters = extract_command(command)

    # Get the function to run
    if command_name in AUTHORIZED_COMMANDS:
        functor = globals()[command_name]
    else:
        raise ValueError(f"`{command_name}` is not an authorized command.")

    # Run the function if asked to
    if run:
        return functor(*parameters)

    return functor, parameters


if __name__ == "__main__":
    # interpreter('detect( "chair 25\\"", \'jf\', 25, 2.5, b"test,test",
    # 0x25, 0b01, True, False, None, "test", your_age=25)', run=True)
    print(interpreter("detect(None)", run=True))
    print(interpreter("detect( )", run=True))
    print(interpreter("ocr()", run=True))
