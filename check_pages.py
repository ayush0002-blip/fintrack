from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.first()
    if not user:
        print("No users found in DB!")
        exit()
    print(f"Testing with user: {user.email}")

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        # Test dashboard
        r = client.get('/dashboard/', follow_redirects=True)
        html = r.data.decode('utf-8', errors='replace')
        print(f"\n=== /dashboard/ => HTTP {r.status_code} ===")
        print(f"Has 'Net Balance': {'Net Balance' in html}")
        print(f"Has 'Traceback': {'Traceback' in html}")
        print(f"Has 'BuildError': {'BuildError' in html}")
        if 'Traceback' in html or r.status_code >= 400:
            tb_start = html.find('Traceback')
            print("\n--- ERROR ---")
            print(html[tb_start:tb_start+2000])
        
        # Test analytics
        r2 = client.get('/analytics/', follow_redirects=True)
        html2 = r2.data.decode('utf-8', errors='replace')
        print(f"\n=== /analytics/ => HTTP {r2.status_code} ===")
        print(f"Has 'analytics': {'analytics' in html2.lower()}")
        print(f"Has 'Traceback': {'Traceback' in html2}")
        if 'Traceback' in html2 or r2.status_code >= 400:
            tb_start = html2.find('Traceback')
            print("\n--- ERROR ---")
            print(html2[tb_start:tb_start+2000])
