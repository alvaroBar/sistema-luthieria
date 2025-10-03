@echo off
echo --- Iniciando o processo de build limpo para o SistemaLuthier ---

echo.
echo Ativando o ambiente virtual (venv2)...
call .\venv2\Scripts\activate

echo.
echo Configurando um PATH temporario e limpo para evitar conflitos...
REM A linha abaixo prioriza o GTK que instalamos, ignorando outras versoes (como a do Tesseract)
set "PATH=C:\Program Files\GTK3-Runtime Win64\bin;%PATH%"

echo.
echo Limpando builds antigos...
rmdir /s /q build
rmdir /s /q dist

echo.
echo Executando o PyInstaller com o .spec...
pyinstaller SistemaLuthier.spec

echo.
echo --- Build Concluido! ---
echo Pressione qualquer tecla para sair.
pause