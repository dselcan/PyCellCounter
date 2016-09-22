pyinstaller.exe "PyCellCounter.spec"
copy /Y dist\pyCellAnalyzer\* dist\pyCellCounter
del /Q dist\pyCellAnalyzer