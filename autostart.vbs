
' autostart.vbs - Queens Cafe POS auto-start
' Starts the Flask server silently then opens the browser
Set WshShell = CreateObject("WScript.Shell")
Dim cafeDir
cafeDir = WshShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\Desktop\CAFE"

' Start the server hidden (no console window)
WshShell.Run "cmd /c cd /d """ & cafeDir & """ && python web.py > """ & cafeDir & "\server.log"" 2>&1", 0, False

' Wait 4 seconds for Flask to start
WScript.Sleep 4000

' Open browser
WshShell.Run "http://localhost:5000", 1, False
