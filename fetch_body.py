import urllib.request
import urllib.error

try:
    url = "http://127.0.0.1:8000/api/v1/videos/a48b4d08-7e3c-4aa3-a801-0756875508b8/summary"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as response:
        with open(r"c:\Mukul K\vinfo1\video-search-engine\http_body.txt", "w") as f:
            f.write("200 OK\n")
            f.write(response.read().decode())
except urllib.error.HTTPError as e:
    with open(r"c:\Mukul K\vinfo1\video-search-engine\http_body.txt", "w") as f:
        f.write(f"HTTP {e.code}\n")
        f.write(e.read().decode())
except Exception as e:
    with open(r"c:\Mukul K\vinfo1\video-search-engine\http_body.txt", "w") as f:
        f.write(f"Exception: {e}\n")
