pyinstaller.exe "PyCellCounter.spec"
copy /Y dist\pyCellAnalyzer\* dist\pyCellCounter
rmdir /s /q dist\pyCellAnalyzer\