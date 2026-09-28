<b>POWERSHELL<br>
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 --user-data-dir="$env:LOCALAPPDATA\Chrome-Scraping" --proxy-server="http://100.126.54.51:8888"
<br> 
<br><b>CMD<br>
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 --user-data-dir="%LOCALAPPDATA%\Chrome-Scraping" --proxy-server="http://100.126.54.51:8888"
<br><br>Запуск панели
uv run python run.py