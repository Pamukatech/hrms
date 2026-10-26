from urllib.request import urlopen
try:
    r = urlopen('http://127.0.0.1:8000/', timeout=5)
    print(r.getcode())
    print(r.headers.get('Location'))
except Exception as e:
    print(type(e).__name__)
    try:
        print(e.code)
        print(e.headers.get('Location'))
    except Exception as e2:
        print(e2)
