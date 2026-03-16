import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from flask import current_app

class PlaidService:
    """
    Service for handling Plaid API integrations.
    """
    
    @staticmethod
    def get_client():
        """
        Initialize and return the Plaid API client.
        """
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox if current_app.config.get('PLAID_ENV') == 'sandbox' else 
                 plaid.Environment.Development if current_app.config.get('PLAID_ENV') == 'development' else 
                 plaid.Environment.Production,
            api_key={
                'clientId': current_app.config.get('PLAID_CLIENT_ID'),
                'secret': current_app.config.get('PLAID_SECRET'),
            }
        )
        api_client = plaid.ApiClient(configuration)
        return plaid_api.PlaidApi(api_client)

    @staticmethod
    def get_link_token(user_id):
        """
        Generate a link token for the Plaid Link flow.
        """
        client = PlaidService.get_client()
        
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
            client_name="FinTrack",
            products=[Products("transactions")],
            country_codes=[CountryCode('US')],
            language='en'
        )
        
        response = client.link_token_create(request)
        return response['link_token']

    @staticmethod
    def exchange_public_token(public_token):
        """
        Exchange a public token for an access token.
        """
        client = PlaidService.get_client()
        
        request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        
        response = client.item_public_token_exchange(request)
        return {
            'access_token': response['access_token'],
            'item_id': response['item_id']
        }

    @staticmethod
    def sync_transactions(user_id):
        """
        Sync transactions from Plaid for a specific user.
        Currently a placeholder.
        """
        # Logic to fetch from Plaid and save to Transaction model will go here
        return 0
