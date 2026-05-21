@echo off
REM Compile NM-RAG Paper to PDF
REM Requires: MiKTeX or TeX Live installed

echo ====================================
echo Compiling NM-RAG IEEE Paper
echo ====================================
echo.

REM Check if pdflatex is available
where pdflatex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pdflatex not found!
    echo.
    echo Please install MiKTeX or TeX Live, or use Overleaf instead.
    echo See COMPILATION_GUIDE.md for instructions.
    pause
    exit /b 1
)

echo [1/4] First pdflatex pass...
pdflatex -interaction=nonstopmode NM_RAG_Paper.tex
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: First compilation failed. Check the .log file.
    pause
    exit /b 1
)

echo [2/4] Processing bibliography...
bibtex NM_RAG_Paper
REM Note: bibtex might fail if .bib file doesn't exist, but we can continue

echo [3/4] Second pdflatex pass...
pdflatex -interaction=nonstopmode NM_RAG_Paper.tex

echo [4/4] Final pdflatex pass...
pdflatex -interaction=nonstopmode NM_RAG_Paper.tex

echo.
echo ====================================
echo Compilation complete!
echo ====================================
echo.
echo Output: NM_RAG_Paper.pdf
echo.

REM Check if PDF was created
if exist NM_RAG_Paper.pdf (
    echo SUCCESS: PDF generated successfully
    echo Opening PDF...
    start NM_RAG_Paper.pdf
) else (
    echo WARNING: PDF not found. Check for errors in the .log file.
)

echo.
pause
