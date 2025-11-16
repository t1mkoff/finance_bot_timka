@echo off
title Открытие документации

echo.
echo ========================================
echo   📚 Открытие документации проекта
echo ========================================
echo.

REM Проверяем существование папки docs
if not exist "docs" (
    echo ❌ Папка docs не найдена!
    echo 💡 Создание документации...
    echo.
)

REM Проверяем наличие Obsidian
set OBSIDIAN_EXE=%LOCALAPPDATA%\Obsidian\Obsidian.exe
if exist "%OBSIDIAN_EXE%" (
    echo ✅ Obsidian найден
    echo 📂 Открытие документации в Obsidian...
    echo.

    REM Открываем index.md в Obsidian
    start "" "%OBSIDIAN_EXE%" "obsidian://open?vault=finance-bot&file=index"

    timeout /t 2 >nul
    echo 📚 Документация открыта в Obsidian
    echo.
    echo 💡 Если Obsidian не открыл vault автоматически:
    echo    1. Откройте Obsidian
    echo    2. Откройте vault: %cd%
    echo    3. Перейдите к файлу: docs/index.md

) else (
    echo ❌ Obsidian не найден!
    echo.
    echo 📋 Как установить Obsidian:
    echo    1. Скачайте с сайта: https://obsidian.md/
    echo    2. Установите приложение
    echo    3. Создайте vault для папки проекта
    echo.
    echo 🌐 Или откройте документацию в браузере:
    echo    📄 docs/index.md - Главная страница
    echo    📄 docs/telegram-bot.md - Telegram бот
    echo    📄 docs/database.md - База данных
    echo    📄 docs/streamlit-dashboard.md - Дашборд
    echo.

    REM Предлагаем открыть в браузере
    set /p choice="Открыть docs/index.md в браузере? (y/n): "
    if /i "%choice%"=="y" (
        echo 🌐 Открытие документации в браузере...
        start "" "docs/index.md"
    )
)

echo.
echo 📋 Список файлов документации:
if exist "docs\index.md" echo    ✅ docs/index.md - Главная страница
if exist "docs\telegram-bot.md" echo    ✅ docs/telegram-bot.md - Telegram бот
if exist "docs\database.md" echo    ✅ docs/database.md - База данных
if exist "docs\streamlit-dashboard.md" echo    ✅ docs/streamlit-dashboard.md - Streamlit дашборд
if exist "docs\ideas-and-improvements.md" echo    ✅ docs/ideas-and-improvements.md - Идеи и улучшения
if exist "docs\troubleshooting.md" echo    ✅ docs/troubleshooting.md - Траблшутинг

echo.
echo 🎯 Документация включает:
echo    📖 Подробное описание архитектуры
echo    🛠️ Инструкции по установке и настройке
echo    💡 Идеи для улучшения проекта
echo    🐛 Решение распространенных проблем
echo    🔗 Связи между компонентами
echo    🏷️ Теги для Obsidian
echo.

pause