import subprocess
import webbrowser

process = subprocess.Popen("py -m http.server 9000 --directory data_html", shell=True)
webbrowser.open("http://localhost:9000/en/index.html")
process.wait()