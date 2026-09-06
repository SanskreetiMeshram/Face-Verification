@echo off
echo =========================================================
echo    Pushing FaceChain Verify to GitHub Repository
echo    https://github.com/SanskreetiMeshram/Face-Verification
echo =========================================================
echo.

git remote set-url origin https://github.com/SanskreetiMeshram/Face-Verification.git
git branch -M main
git add .
git commit -m "feat: complete Face ID + Blockchain Verification pipeline with mobile PWA, SQLite audit logs, and downloadable zip" 2>nul

echo Pushing all files, mobile PWA, and zip package to GitHub...
echo (If prompted, please log in with your GitHub account)
echo.
git push -u origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo =========================================================
    echo   SUCCESS! All files and ZIP uploaded to your repo:
    echo   https://github.com/SanskreetiMeshram/Face-Verification
    echo =========================================================
) else (
    echo =========================================================
    echo   If prompted to authenticate, please complete login
    echo   or use a GitHub Personal Access Token (PAT).
    echo =========================================================
)
echo.
pause
