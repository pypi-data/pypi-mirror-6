"""This module contains a small set of utility functions,
   created for learning purposes."""

def PrintList( li, indent = False, initialTab = 0 ):
    """Recursively prints an indented list, takes
       list, boolean and int as arguments."""
    for item in li:
        if isinstance( item, list ):
            PrintList(item, indent, initialTab+1)
        else:
            if indent and initialTab > 0:
                print( "  "*initialTab + item )
            else:
                print( item )
