"""
First module to be posted on pypi
"""

def nester(data):
    """
    this function prints all the items in the list
    """
    for item in data:
        if isinstance(item, list):
            nester(item)
        else:
            print(item)
