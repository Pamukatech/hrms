from urllib.request import urlopen, Request
try:
    req = Request('http://127.0.0.1:8000/login')
    r = urlopen(req, timeout=5)
    print(r.getcode())
    data = r.read(80)
    print(data[:50])
except Exception as e:
    print(e)
    try:
        print(e.code)
    except:
        pass
