@echo off
setlocal EnableExtensions EnableDelayedExpansion

set python_interpreter=D:\ises-dds\APLICACIONES_ISES\Incidencias_CF_FM\venv\Scripts\python.exe
set python_file=D:\ises-dds\APLICACIONES_ISES\Incidencias_CF_FM\incidenciasNuevo.py

"%python_interpreter%" "%python_file%"

endlocal
