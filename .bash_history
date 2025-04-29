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
