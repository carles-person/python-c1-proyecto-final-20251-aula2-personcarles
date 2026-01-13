"""
OdontoCare Tools Module;
This module contains wrappers for authorization and authentication and also json error support functions
"""

from .errors import json_error, json_message, HTTPStatus, OCERR
from .wrappers import token_required, role_required, login_required
from .ocenums import OCENT, OCROL