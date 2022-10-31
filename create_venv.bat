python -m venv .venv
call .venv/scripts/activate.bat
if %errorlevel% neq 0 goto :error
pip install -r requirements.txt
pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113
git clone https://github.com/salesforce/BLIP scripts/BLIP
if %errorlevel% neq 0 goto :error

goto :done

:error
echo Error occurred trying to install or activate venv.
exit /b %errorlevel%

:done