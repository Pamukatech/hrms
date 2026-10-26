from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
r = client.get('/', follow_redirects=False)
print(r.status_code, r.headers.get('location'))
