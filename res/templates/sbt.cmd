@echo off

set "APP_DIR={app_dir}"
set "APP_PATH={app_path}"

cd /d "%APP_DIR%" || exit /b 1

"%APP_PATH%" %*
exit /b %ERRORLEVEL%
