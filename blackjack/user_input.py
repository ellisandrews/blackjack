INVALID_RESPONSE = 'invalid'


# Response parsing/validating/casting functions

def yes_no_response(response):
    """Check whether user's keyboard input is a valid yes or no, and return a boolean."""
    response = response.lower()
    if response in ('y', 'yes'):
        return True
    elif response in ('n', 'no'):
        return False
    else:
        return INVALID_RESPONSE


def float_response(response):
    """Check whether a user's keyboard input is a valid float, and cast it as such."""
    try:
        return float(response)
    except ValueError:
        return INVALID_RESPONSE


def int_response(response):
    """Check whether a user's keyboard input is a valid integer, and cast it as such."""
    try:
        return int(response)
    except ValueError:
        return INVALID_RESPONSE


def choice_response(response, choices):
    """Check whether user's keyboard input is a valid choice from a collection."""
    response = response.lower()
    if response not in choices:
        return INVALID_RESPONSE
    else:
        return response

# Customizable user input function

def get_user_input(prompt, parsing_func, retries=3):
    """Get raw input from the user, and ensure it's valid."""

    attempts = 0
    response = INVALID_RESPONSE
    
    while response == INVALID_RESPONSE and attempts < retries:
        if attempts > 0:
            print('Invalid response. Please try again.')
        response = parsing_func(input(prompt))
        attempts += 1

    # If they've unsuccessfullly tried to enter input the maximum number of times, exit the program
    if attempts == retries and response == INVALID_RESPONSE:
        max_retries_exit()

    return response


# Function for quiting the program due to user input retries limit

def max_retries_exit():
    """Exit the program due to hitting the maximum number of retries for user input."""
    print('Maximum retries reached. Exiting...')
    exit(1)
