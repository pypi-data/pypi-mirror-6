""" Lazyconf: Insultingly simple configuration for python applications.

    Example usage:
    --------------
    
    ### Create an instance and load the config ###

    lazy = Lazyconf()
    lazy.load('/path/to/.lazy')

    # or

    lazy = Lazyconf()
    lazy = Lazyconf().load() # Loads from os.cwd

    # or 

    lazy = Lazyconf().load() # Shorter version.

    ### Get a specific key ###

    print lazy.get('env.domain')

    ### Set a specific key ###

    lazy.set('env.domain', 'example.com')

    ### Run through the schema file, prompt user for config. ###
    ### Uses data file for defaults. ###

    lazy.configure()
"""

from lazyconf import *
