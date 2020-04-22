import os


def header(text):
    # Intentional asymmetrical spacing due to displayed output
    return f"\n♠️  ♥️  ♣️  ♦️   {text}  ♦️  ♣️  ♥️  ♠️\n"


def clear(): 
    """Clear the terminal screen (operating system dependent)."""
    # Windows 
    if os.name == 'nt':
        os.system('cls') 
    # Mac/Linux 
    else: 
        os.system('clear')
