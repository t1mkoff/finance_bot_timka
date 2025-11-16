"""
Установка зависимостей для дашборда
"""

import subprocess
import sys
import os

def install_package(package_name, import_name=None):
    """Установить пакет, если он не установлен"""
    if import_name is None:
        import_name = package_name.lower().replace('-', '_')

    try:
        __import__(import_name)
        print(f"✅ {package_name} уже установлен")
        return True
    except ImportError:
        print(f"📦 Установка {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} успешно установлен")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Ошибка при установке {package_name}")
            return False

def main():
    print("=" * 50)
    print("🚀 Установка зависимостей для финансового дашборда")
    print("=" * 50)

    # Список пакетов для установки
    packages = [
        ("streamlit==1.39.0", "streamlit"),
        ("plotly==5.24.1", "plotly"),
        ("pandas==2.2.3", "pandas"),
        ("Pillow==10.4.0", "PIL"),
    ]

    success_count = 0
    total_count = len(packages)

    for package, import_name in packages:
        if install_package(package, import_name):
            success_count += 1

    print("\n" + "=" * 50)
    if success_count == total_count:
        print("🎉 Все зависимости успешно установлены!")
        print("\n🚀 Теперь можно запускать дашборд:")
        print("   python dashboard/run_dashboard.py")
        print("   или")
        print("   start_dashboard.bat")
    else:
        print(f"⚠️ Установлено {success_count}/{total_count} пакетов")
        print("❌ Пожалуйста, установите недостающие пакеты вручную:")
        for package, _ in packages:
            print(f"   pip install {package}")

    print("=" * 50)

if __name__ == "__main__":
    main()