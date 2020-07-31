import requests
url = 'http://121.36.68.53/WEB/MagicMirror/upload_file.php'
filename = '123.png'
filepath = '123.png'

files = {"file": (filename, open(filepath, "rb"), "image/png")}
html = requests.post(url, files=files)
print(html.text)








