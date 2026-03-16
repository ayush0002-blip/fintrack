from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.services.plaid_service import PlaidService
from app.models import PlaidItem
from app.extensions import db

plaid_bp = Blueprint('plaid', __name__)

@plaid_bp.route('/create_link_token', methods=['POST'])
@login_required
def create_link_token():
    try:
        link_token = PlaidService.get_link_token(current_user.id)
        return jsonify({'link_token': link_token})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@plaid_bp.route('/exchange_public_token', methods=['POST'])
@login_required
def exchange_public_token():
    public_token = request.json.get('public_token')
    if not public_token:
        return jsonify({'error': 'Missing public token'}), 400
    
    try:
        exchange_response = PlaidService.exchange_public_token(public_token)
        
        # Save the access token and item ID
        plaid_item = PlaidItem(
            user_id=current_user.id,
            access_token=exchange_response['access_token'],
            item_id=exchange_response['item_id'],
            institution_name=request.json.get('metadata', {}).get('institution', {}).get('name')
        )
        db.session.add(plaid_item)
        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
