#!/usr/bin/env python3
# Пакет для российского хостинга с PHP (Beget, Timeweb, REG.RU …).
# Запуск из корня проекта: python3 tools/package_hosting.py
# Результат: dist/hosting/public_html (сайт + api/lead.php + .htaccess), dist/hosting/private (образец настроек)
# и архив dist/wagner-hosting.zip. Как выложить — server/README.md.
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist', 'hosting')
PUB = os.path.join(DIST, 'public_html')
PRIV = os.path.join(DIST, 'private')

shutil.rmtree(DIST, ignore_errors=True)
os.makedirs(PUB)
os.makedirs(PRIV)

# Статика: стили, скрипты, картинки
for d in ('css', 'js', 'img'):
    shutil.copytree(os.path.join(ROOT, d), os.path.join(PUB, d))

# Страницы — тем же сборщиком, но с адресом обработчика заявок
env = dict(os.environ, BUILD_OUT=PUB, LEAD_API='api/lead.php')
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_pages.py')], env=env, check=True)

# Обработчик заявок и правила сервера
shutil.copytree(os.path.join(ROOT, 'server', 'api'), os.path.join(PUB, 'api'))
shutil.copy(os.path.join(ROOT, 'server', 'public.htaccess'), os.path.join(PUB, '.htaccess'))

# private: образец настроек + запрет доступа на случай, если папку по ошибке положат внутрь сайта
shutil.copy(os.path.join(ROOT, 'server', 'private', 'config.sample.php'), os.path.join(PRIV, 'config.sample.php'))
with open(os.path.join(PRIV, '.htaccess'), 'w') as f:
    f.write('Require all denied\n')

archive = shutil.make_archive(os.path.join(ROOT, 'dist', 'wagner-hosting'), 'zip', DIST)
print('Готово:', os.path.relpath(DIST, ROOT), '+', os.path.relpath(archive, ROOT))
