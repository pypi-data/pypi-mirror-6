PROJECTNAME = 'OneTimeTokenPAS'

# Set to False in a production environment
DEBUG=False

PLUGIN_ID = 'onetimetoken_pas_plugin'

class TokenError(Exception):
    """Base exception for Token errors"""
    pass
