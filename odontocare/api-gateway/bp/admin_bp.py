"""
Docstring for odontocare.api-gateway.bp.admin_bp
"""

from flask import Blueprint, request

admin_bp = Blueprint('admin_bp',__name__)


@admin_bp.route('/users', methods=['POST'])
def create_user():
    pass

@admin_bp.route('/doctor', methods=['POST'])
def create_doctor():
    pass

@admin_bp.route('/patient', methods=['POST'])
def create_patient():
    pass

@admin_bp.route('/clinic', methods=['POST']):
def create_clinic():
    pass

@admin_bp.route('/users', methods=['GET']):
def get_users():
    pass