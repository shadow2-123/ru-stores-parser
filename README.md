<b>POWERSHELL<br>
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 --user-data-dir="$env:LOCALAPPDATA\Chrome-Scraping"<br>
<br><b>CMD<br>
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 --user-data-dir="%LOCALAPPDATA%\Chrome-Scraping"
<br><br>Запуск панели
uv run python run.py