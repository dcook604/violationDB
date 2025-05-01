cd ~
sudo
sudo apt-get update
sudo apt-get install -y default-libmysqlclient-dev build-essential pkg-config
w
ps uax
ps au
ps aux
sudo apt-get install -y python3-dev python3.11-dev
w
ps aux
docker ps
exit
mkdir -p app/uploads/photos app/uploads/pdfs
pip install -r requirements.txt
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
sudo apt-get update
sudo apt-get install -y default-libmysqlclient-dev build-essential pkg-config
sudo apt-get update
sudo apt-get install -y default-libmysqlclient-dev build-essential pkg-config
./venv/bin/pip install -r requirements.txt
sudo apt-get install -y python3-dev python3.11-dev
./venv/bin/pip install -r requirements.txt
mkdir -p app/templates app/static
pip install -r requirements.txt
python3 -m venv venv
venv/bin/pip install -r requirements.txt
git status
git init
git add .
git remote add origin https://github.com/dcook604/violation.git
git commit -m "Initial commit: Strata Violation Logging App"
git config --global user.email "dcook@spectrum4.ca"
git config --global user.name "Daniel"
git remote add origin https://github.com/dcook604/violation.git
git push -u origin master
git commit -m "Initial commit: Strata Violation Logging App"
git push -u origin master
git rm -r --cached venv .cache .windsurf-server .codeium
git add .gitignore
git commit -am "Remove large and unnecessary files; add .gitignore"
git push -u origin master
pip install git-filter-repo
git filter-repo --path .cache --path venv --path .windsurf-server --path .codeium --invert-paths
pipx install git-filter-repo
sudo apt update
sudo apt install git-filter-repo
git filter-repo --path .cache --path venv --path .windsurf-server --path .codeium --invert-paths
git filter-repo --force --path .cache --path venv --path .windsurf-server --path .codeium --invert-paths
git push -u --force origin master
mkdir -p tests
venv/bin/pip install pytest
venv/bin/pytest --maxfail=3 --disable-warnings -v
venv/bin/pip install -r requirements.txt
venv/bin/pytest --maxfail=3 --disable-warnings -v
venv/bin/pip install flask-wtf
venv/bin/pytest --maxfail=3 --disable-warnings -v
sqlite3 violation.db '.tables' && sqlite3 violation.db 'select * from users;'
venv/bin/pytest --maxfail=3 --disable-warnings -v
venv/bin/pytest --maxfail=3 --disable-warnings -v tests/test_violations.py
venv/bin/pytest --maxfail=3 --disable-warnings -v tests/test_auth.py
venv/bin/pytest --maxfail=3 --disable-warnings -v tests/test_violations.py
venv/bin/pytest --maxfail=5 --disable-warnings -v tests/test_violations.py
venv/bin/pytest --maxfail=6 --disable-warnings -v tests/test_violations.py
venv/bin/pytest --maxfail=6 --disable-warnings -v
alembic revision --autogenerate -m "Add violation reference and extra_fields"
pip install alembic
venv/bin/pip install alembic
venv/bin/alembic revision --autogenerate -m "Add violation reference and extra_fields"
venv/bin/alembic init migrations
venv/bin/pip install mariadb
venv/bin/alembic revision --autogenerate -m "Add violation reference and extra_fields"
venv/bin/alembic upgrade head
pytest --maxfail=3 --disable-warnings -v
pip install pytest
python3 -m venv .venv && .venv/bin/pip install pytest
.venv/bin/pytest --maxfail=3 --disable-warnings -v
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest --maxfail=3 --disable-warnings -v
.venv/bin/pip install flask-wtf
.venv/bin/pytest --maxfail=3 --disable-warnings -v
pytest --maxfail=3 --disable-warnings -q
pip install pytest
pip install --break-system-packages pytest
~/.local/bin/pytest --maxfail=3 --disable-warnings -q
pip install --break-system-packages -r requirements.txt
~/.local/bin/pytest --maxfail=3 --disable-warnings -q
pip install --break-system-packages flask-wtf
~/.local/bin/pytest --maxfail=3 --disable-warnings -q
cd /home/violation/app
rm /home/violation/app/auth.py
cd /home/violation
git add . && git commit -m "Refactor: Modularize blueprints, update requirements and docs, improve architecture and product documentation" && git push
python3 run.py
python3 run.py --port=5001
python3 run.py
python3 run.py --port=5005
python3 run.py --port=5010
python3 run.py --port=5010 --host=127.0.0.1
python3 run.py --port=5005
python3 run.py --port=5006
git add . && git commit -m "Fix template inheritance: remove navbar override and use container block for login, register, reset_password. Add debug for block rendering. Update docs and memory." && git push
/bin/python3 /home/violation/.windsurf-server/extensions/ms-python.python-2025.4.0/python_files/printEnvVariablesToFile.py /home/violation/.windsurf-server/extensions/ms-python.python-2025.4.0/python_files/deactivate/bash/envVars.txt
cd ~
dir
cd violation/
dir
cd ..
dir
rm violation
cd violation/
dir
cd ..
rm -rf violation
dir
nano requirements.txt 
mysql -h 45.41.204.94 -P 3307 -u violationuser -p
mysql
mysql -h 45.41.204.94 -P 3307 -u violationuser -p
sudo apt update && sudo apt install mariadb-client -y~
su -
dc ~
dir
tail -f flask_error.log 
ps aux
w
su -
git add app/templates/login.html app/static/login.css && git commit -m "Modernize login page: centered card, blue theme, floating labels, error display, responsive, Bootstrap 5, custom CSS" && git push
git add app/templates/register.html app/templates/reset_password.html && git commit -m "Apply modern, responsive card design to registration and password reset pages (Bootstrap 5, floating labels, error display, custom CSS)" && git push
export FLASK_APP=run.py && export FLASK_ENV=development && flask run --port=5001
export FLASK_APP=run.py && export FLASK_ENV=development && flask run --port=5002
git commit
git commit -am "Auto-commit: significant code change or test passed" && git push
git status memory_bank.md
git fetch origin
git checkout master
git merge main
git merge origin/main
git merge git merge master
git merge main
git merge git origin/main
git add requirements.txt
git commit -m "Add gunicorn to requirements.txt for Render deployment"
git push
git add app/__init__.py && git commit -m "Fix ImportError: import and register auth_routes blueprint correctly for deployment" && git push
git add app/auth_routes.py && git commit -m "Add Flask-Login user_loader to fix session loading error on deployment" && git push
git add app/auth_routes.py app/__init__.py && git commit -m "Move Flask-Login user_loader to app/__init__.py for correct session handling" && git push
git add app/__init__.py && git commit -m "Remove duplicate import os statement in app/__init__.py for code cleanliness" && git push
export FLASK_APP=run.py && export FLASK_ENV=development && flask run --port=5000
export FLASK_APP=run.py && export FLASK_ENV=development && flask run --port=5001
flask run --debug
git add app/__init__.py && git commit -m "Add logging configuration to save error logs to flask_error.log" && git push
sudo netstat -tulnp | grep 5000
sudo netstat -tulnp | grep 5001
sudo netstat -tulnp | grep 5002
kill -9 219630
sudo netstat -tulnp | grep 5003
sudo netstat -tulnp | grep 5004
/bin/python3 /home/violation/.windsurf-server/extensions/ms-python.python-2025.4.0/python_files/printEnvVariablesToFile.py /home/violation/.windsurf-server/extensions/ms-python.python-2025.4.0/python_files/deactivate/bash/envVars.txt
/bin/python3 /home/violation/.windsurf-server/extensions/ms-python.python-2025.4.0/python_files/printEnvVariablesToFile.py /home/violation/.windsurf-server/extensions/ms-python.python-2025.4.0/python_files/deactivate/bash/envVars.txt
/memory enable
/bin/python3 /home/violation/.windsurf-server/extensions/ms-python.python-2025.4.0/python_files/printEnvVariablesToFile.py /home/violation/.windsurf-server/extensions/ms-python.python-2025.4.0/python_files/deactivate/bash/envVars.txt
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
git status
git add app/templates/login.html run.py
git commit -m "Remove debug text from login page and always run Flask on 0.0.0.0"
git push
python3 -c "from app import db, create_app; app = create_app(); with app.app_context(): from app.models import User; u = User.query.filter_by(email='dcook@spectrum4.ca').first();\nif u: u.promote_to_admin(); else: print('User not found')"
python3
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
python3 manage.py shell
python3
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
python add_admin.py
python3 add_admin.py
python3 init_db.py
python3 add_admin.py
mkdir -p app/templates/user_management
python3 init_db.py
mysql -u root -p -e "SHOW DATABASES;"
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
git status | cat
git add app/__init__.py app/admin_routes.py app/forms.py app/models.py app/templates/base.html app/templates/user_management/ app/user_routes.py
git commit -m "feat: Implement comprehensive user management system" -m "- Add user roles (user, manager, admin) - Add temporary password functionality - Create user management interface with CRUD operations - Implement role-based access control - Add user activation/deactivation - Update navigation for admin access - Remove duplicate user management routes"
git push
python3 update_db.py
git add app/templates/base.html update_db.py && git commit -m "fix: Update template routes and add database migration script" -m "- Fix incorrect route references in base template (main.index -> main.dashboard) - Add robust database migration script for user management columns - Add better error handling for database updates - Fix navigation menu links"
ps aux | grep python3 | grep -v grep
git status | cat
git add app/models.py app/user_routes.py docs/ app/templates/base.html
git commit -m "Refactor user management system with improved error handling and documentation"
git push origin master
export FLASK_APP=run.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5004
flask run --host=0.0.0.0 --port=5004 --debug
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
export FLASK_APP=run.py && export FLASK_ENV=development && flask run --host=0.0.0.0 --port=5003
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
export FLASK_APP=run.py && export FLASK_ENV=development && flask run --port=5003
source venv/bin/activate
alembic stamp head
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
alembic revision -m "add field definition and violation field value tables" --autogenerate
pip install alembic
python3 -m venv venv
source venv/bin/activate && pip install alembic
source venv/bin/activate && alembic revision -m "add field definition and violation field value tables" --autogenerate
source venv/bin/activate && alembic upgrade head
source venv/bin/activate && alembic stamp head
rm migrations/versions/3387b41a9239_add_field_definition_and_violation_.py
source venv/bin/activate && alembic revision -m "add field definition and violation field value tables" --autogenerate
source venv/bin/activate && alembic stamp 48165b6d57e2
source venv/bin/activate && alembic revision -m "add field definition and violation field value tables" --autogenerate
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pytest
cd frontend && npx cypress run
sudo apt-get update && sudo apt-get install -y xvfb
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
npx cypress run
cd frontend && npx cypress run
npx cypress run
cd frontend && npx cypress run
npx cypress run
python3 app/add_admin.py dcook@spectrum4.ca password
python3 add_admin.py dcook@spectrum4.ca password
python3 /home/violation/add_admin.py dcook@spectrum4.ca password
cd frontend && npx cypress run
npx cypress run
alembic upgrade head
source venv/bin/activate && alembic upgrade head
source ../venv/bin/activate && alembic upgrade head
cd /home/violation && source venv/bin/activate && alembic upgrade head
cd frontend && npx cypress run
cd frontend && rm -rf node_modules package-lock.json && npm install
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd frontend && npx cypress run
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
npm ls react
cd frontend && npm ls react
cat package.json
npm ls react-dom
npm ls react
cd .. && rm -rf node_modules package-lock.json && cd frontend && rm -rf node_modules package-lock.json && npm install
cd frontend && rm -rf node_modules package-lock.json && npm install
cd ~/frontend && rm -rf node_modules package-lock.json && npm install
cd frontend && npm install react-router-dom axios react-beautiful-dnd
npm install react-router-dom axios react-beautiful-dnd
npm install react@18.3.1 react-dom@18.3.1
npm install react-router-dom axios react-beautiful-dnd
npm uninstall react-router-dom && npm install react-router-dom@6.22.3
cd app && sed -i "s/app.register_blueprint(user_routes.bp)/app.register_blueprint(user_routes.user_api)/" __init__.py
cd ../app && sed -i "s/app.register_blueprint(user_routes.bp)/app.register_blueprint(user_routes.user_api)/" __init__.py
cd ~/app && flask db upgrade
cd ~/app && python3
python3 -c "from app import db; db.create_all()"
python3
npx create-react-app frontend
flask run --host=0.0.0.0 --port=5004 --debug
cd /home/violation/app
python
python3
cd ..
flask db upgrade
cd app
dir
ls ~/ap
ls ~/app
python3
/home/violation
cd /home/violation
python3 -m app
export FLASK_APP=__init__.py
flask shell
cd app
export FLASK_APP=__init__.py
flask shell
nano models.py 
pip install Flask-CORS==4.0.0
source /home/violation/.venv/bin/activate
npm install react-router-dom axios react-beautiful-dnd
source /home/violation/.venv/bin/activate
source /home/violation/.venv/bin/activate
cd frontend
rm -rf node_modules package-lock.json
source /home/violation/.venv/bin/activate
npm install
source /home/violation/.venv/bin/activate
npm ls react
source /home/violation/.venv/bin/activate
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
ps aux | grep python | grep run.py | cat
netstat -tlpn | grep python | cat
netstat -tlpn | grep :5003 | cat
python run.py
python3 run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
curl -v http://localhost:5003/api/auth/session
hostname -I | awk '{print $1}'
sudo iptables -L | cat
pkill -9 -f "python.*run.py" && sleep 2 && source .venv/bin/activate && python run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
netstat -tlpn | grep python | cat
source .venv/bin/activate && python run.py
pkill -9 -f "python.*run.py" && sleep 2 && source .venv/bin/activate && python run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pkill -f node
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
source .venv/bin/activate && python run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pkill -f "python.*run.py" && python3 run.py
source .venv/bin/activate && pip install flask-cors
python3 run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd frontend && npm start
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd frontend && npm install @fortawesome/fontawesome-free@5.15.3 @popperjs/core@2.9.1 @tailwindcss/forms@0.2.1 chart.js@2.9.4 tailwindcss@2.0.4
cd /home/violation && flask db migrate -m "Add violation status fields"
pip install flask-cors flask-migrate
python3 -m venv venv && source venv/bin/activate && pip install flask-cors flask-migrate flask-sqlalchemy
export FLASK_APP=run.py && flask db init && flask db migrate -m "Add violation status fields"
source .venv/bin/activate && python3 run.py
python3 run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pkill -9 -f "python.*run.py" && sleep 2 && source .venv/bin/activate && python run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
source .venv/bin/activate && python
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pkill -9 -f "python.*run.py" && sleep 2 && source .venv/bin/activate && python run.py
python3 run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
source .venv/bin/activate && python run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pkill -f "python.*run.py" && python run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
pkill -f "python.*run.py" && python run.py
python
>>> from app import create_app, db
>>> from app.models import User
>>> app = create_app()
>>> with app.app_context():
...     user = User(email='test@example.com', role='admin')
...     user.set_password('password123')
...     db.session.add(user)
...     db.session.commit()
flask shell
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
npm start
cd frontend/
npm start
npm install react-router-dom@6.22.3
npm start
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
npm start
cd frontend/
npm start
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd frontend && npm start
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
npm start
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
npm start
npm run
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd frontend && npm start
npm start
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
source .venv/bin/activate && python run.py
source /home/violation/.venv/bin/activate
cd frontend && npm start
cd ~
dir
su -
cd ~
dir
cd frontend/
dir
ufc
ufw
su -
cd ..
dir
nano __init__.py
cd app
dir
nano __init__.py
su -
source /home/violation/.venv/bin/activate
cd frontend/
npx cypress open
npm install --save-dev cypress
cd ..
dir
python3 app/add_admin.py dcook@spectrum4.ca password
python 3 add_admin.py dcook@spectrum4.ca password
python3 add_admin.py dcook@spectrum4.ca password
pwd
python3 init_db.py
python3 add_admin.py dcook@spectrum4.ca password
npx cypress open
cd frontend/
npm start
source /home/violation/.venv/bin/activate
npm start
cd frontend/
npm start
npm install
cd ..
npx cypress open
npm start
npx cypress open
npm start
cd frontend/
dir
npm run
npn start
npm start
flask run 
cd ..
dir
flask run 
dir
source .venv/bin/activate
cd app
flask app
dir
flask run
dir
cd ..
dir
run.py
python3 run.py
dir
cd app
export FLASK_APP=violation_routes.py  # or your main app file
export FLASK_ENV=development
flask run
rm -rf node_modules package-lock.json && npm install
npm start
ls node_modules/react-router-dom/dist/index.mjs
pip install Flask-CORS==4.0.0
cd .l
cd ..
python3 run.py
flask run --host=0.0.0.0 --port=5004 --debug
python3 run.py
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
cd frontend && npm start
. "\home\violation\.cursor-server\cli\servers\Stable-0781e811de386a0c5bcb07ceb259df8ff8246a50\server\out\vs\workbench\contrib\terminal\common\scripts\shellIntegration-bash.sh"
python3 -c "from app import db; from app.models import User; print('\n'.join(str(u.email) for u in User.query.all()))"
source .venv/bin/activate && python3 -c "from app import create_app, db; from app.models import User; from werkzeug.security import generate_password_hash; app = create_app(); app.app_context().push(); admin = User(email='admin@test.com', password_hash=generate_password_hash('admin123'), is_admin=True, is_active=True, role='admin'); db.session.add(admin); db.session.commit(); print('Admin user created')"
source .venv/bin/activate && python3 -c "from app import create_app, db; from app.models import User; from werkzeug.security import generate_password_hash; app = create_app(); app.app_context().push(); admin = User.query.filter_by(email='admin@test.com').first(); admin.password_hash = generate_password_hash('admin123'); admin.is_active = True; admin.is_admin = True; admin.role = 'admin'; db.session.commit(); print('Admin user updated')"
cat app/admin_routes.py | head -6
grep -A10 "def login" app/auth_routes.py
grep -A10 "def check_session" app/auth_routes.py
echo 'from app import create_app, db; app=create_app(); app.app_context().push(); print("Browser cookie name:", app.config.get("SESSION_COOKIE_NAME")); print("Session cookie domain:", app.config.get("SESSION_COOKIE_DOMAIN")); print("Session cookie samesite:", app.config.get("SESSION_COOKIE_SAMESITE")); print("Session cookie secure:", app.config.get("SESSION_COOKIE_SECURE"))'| source .venv/bin/activate && python
source .venv/bin/activate && python -c "from app import create_app; app=create_app(); print('Session cookie name:', app.config.get('SESSION_COOKIE_NAME')); print('Session cookie domain:', app.config.get('SESSION_COOKIE_DOMAIN')); print('Session cookie samesite:', app.config.get('SESSION_COOKIE_SAMESITE')); print('Session cookie secure:', app.config.get('SESSION_COOKIE_SECURE'))"
source .venv/bin/activate && python -c "from flask.sessions import SecureCookieSessionInterface; print(dir(SecureCookieSessionInterface))"
curl -I http://localhost:3001
cd frontend && npm install --save-dev http-proxy-middleware
