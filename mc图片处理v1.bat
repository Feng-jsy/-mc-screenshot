@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ========== 源目录（已固定为您指定的路径）==========
set "SOURCE_DIR=D:\MC  PCL2\.minecraft\versions"
:: ===================================================

set "DESKTOP=%USERPROFILE%\Desktop"
set "TARGET_DIR=%DESKTOP%\输出文件夹"

if not exist "%SOURCE_DIR%" (
    echo 错误：源目录 "%SOURCE_DIR%" 不存在！
    pause
    exit /b 1
)

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

set "EXTENSIONS=.jpg .jpeg .png .bmp .gif .tiff .tif .webp"

echo 开始检索图片...
echo 源目录：%SOURCE_DIR%
echo 目标目录：%TARGET_DIR%
echo.

for /r "%SOURCE_DIR%" %%f in (*) do (
    set "fullname=%%f"
    set "ext=%%~xf"
    for %%e in (%EXTENSIONS%) do (
        if /i "!ext!"=="%%e" (
            set "filename=%%~nxf"
            :: 获取相对路径并提取第一级目录名（版本名）
            set "relpath=!fullname:%SOURCE_DIR%=!"
            if "!relpath:~0,1!"=="\" set "relpath=!relpath:~1!"
            for /f "delims=\" %%a in ("!relpath!") do set "version=%%a"
            if defined version (
                set "newfilename=!version!_!filename!"
            ) else (
                set "newfilename=!filename!"
            )
            copy /y "%%f" "%TARGET_DIR%\!newfilename!" >nul
            echo 已复制：[!version!] !filename!  ->  !newfilename!
        )
    )
)

echo.
echo 全部完成！按任意键退出...
pause >nul