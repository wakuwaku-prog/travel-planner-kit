@echo off
rem 双击运行：调用 Git Bash 执行 deploy-site.sh（自动定位 kit 目录，兼容中文路径）
setlocal
for /d %%D in ("C:\Users\epiph\Documents\DSH*") do if exist "%%D\travel-planner-kit\deploy-site.sh" (
  "C:\Program Files\Git\bin\bash.exe" -c "cd \"$(cygpath -u '%%D')/travel-planner-kit\" && bash deploy-site.sh"
  goto :done
)
echo [X] 未找到 travel-planner-kit 目录
:done
pause
