"""
Запуск финансового дашборда
"""

import os
import sys
import subprocess

def check_database():
    """Проверить наличие базы данных"""
    db_path = "finance_bot.db"
    if not os.path.exists(db_path):
        print("❌ Ошибка: База данных не найдена!")
        print("📋 Пожалуйста, сначала запустите Telegram бота, чтобы создать базу данных.")
        print("💡 Выполните: python main.py")
        return False
    return True

def install_requirements():
    """Установить зависимости для дашборда"""
    print("📦 Проверка зависимостей для дашборда...")

    required_packages = [
        'streamlit',
        'plotly',
        'pandas',
        'Pillow'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("📦 Установка зависимостей...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ Зависимости успешно установлены!")
        except subprocess.CalledProcessError:
            print("❌ Ошибка при установке зависимостей")
            print("💡 Установите вручную: pip install streamlit plotly pandas Pillow")
            return False
    else:
        print("✅ Все зависимости уже установлены!")

    return True

def run_dashboard():
    """Запустить дашборд"""
    print("🚀 Запуск финансового дашборда...")
    print("📊 Дашборд будет доступен по адресу: http://localhost:8501")
    print("⏹️  Для остановки нажмите Ctrl+C в этом окне")

    try:
        # Запускаем streamlit
        os.system("streamlit run dashboard/app.py")
    except KeyboardInterrupt:
        print("\n⏹️  Дашборд остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска дашборда: {e}")

def main():
    print("=" * 60)
    print("🚀 Финансовый дашборд - Старт")
    print("=" * 60)

    # Проверяем базу данных
    if not check_database():
        return

    # Устанавливаем зависимости
    if not install_requirements():
        return

    # Запускаем дашборд
    run_dashboard()

if __name__ == "__main__":
    main()