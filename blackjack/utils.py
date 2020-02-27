
INVALID_RESPONSE = 'invalid'


# Response parsing/validating/casting functions

def yes_no_response(response):
    """Check whether user's keyboard input is a valid yes or no."""
    response = response.lower()
    if response in ('y', 'yes'):
        return 'yes'
    elif response in ('n', 'no'):
        return 'no'
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


# Customizable user input function

def get_user_input(prompt, parsing_func, invalid_msg='Invalid response. Please try again.', retries=3):
    """Get raw input from the user, and ensure it's valid."""

    attempts = 0
    response = INVALID_RESPONSE
    
    while response == INVALID_RESPONSE and attempts < retries:
        if attempts > 0:
            print(invalid_msg)
        response = parsing_func(input(prompt))
        attempts += 1

    if attempts == retries:
        print('Maximum retries hit. Exiting...')
        exit(1)

    return response
