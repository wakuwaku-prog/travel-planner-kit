@echo off
rem 双击运行：调用 Git Bash 执行 deploy-site.sh（自动定位 kit 目录，兼容中文路径）
rem 用法：deploy-site.cmd <slug> [commit标题]   例：deploy-site.cmd dongji "东极岛行程更新"
setlocal
if "%~1"=="" (
  echo 用法: deploy-site.cmd ^<slug^> [commit标题]
  echo   例: deploy-site.cmd dongji "东极岛行程更新"
  pause
  exit /b 1
)
for /d %%D in ("C:\Users\epiph\Documents\DSH*") do if exist "%%D\travel-planner-kit\deploy-site.sh" (
  "C:\Program Files\Git\bin\bash.exe" -c "cd \"$(cygpath -u '%%D')/travel-planner-kit\" && bash deploy-site.sh '%~1' '%~2'"
  goto :done
)
echo [X] 未找到 travel-planner-kit 目录
:done
pause
