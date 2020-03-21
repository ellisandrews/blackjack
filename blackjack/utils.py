import os


def clear(): 
    """Clear the terminal screen (operating system dependent)."""
    # Windows 
    if os.name == 'nt':
        os.system('cls') 
    # Mac/Linux 
    else: 
        os.system('clear')
