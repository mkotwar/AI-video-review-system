import urllib.request
import urllib.error

def main():
    try:
        url = "http://127.0.0.1:8000/api/v1/videos/03301eee-50a4-4a3a-b5db-11f29b339233/summary"
        print(f"Hitting {url}...")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as response:
            print("Success:", response.status)
            print(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code}")
        print(e.read().decode())
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()
