init-env:
	python3 -m venv env
act-env:
	. env/bin/activate
i:
	pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
mig:
	make migration && make migrate
cru:
	python manage.py createsuperuser
test:
	python3 manage.py test
run-asgi:
	uvicorn core.asgi:application --host 0.0.0.0 --port 1024 --reload
run-wsgi:
	gunicorn core.wsgi:application --bind 0.0.0.0:1024
run:
	python manage.py runserver 0.0.0.0:1024

#others
git-rm-idea:
	git rm -r --cached .idea/
collect:
	python manage.py collectstatic --no-input
rm-static:
	rm -rf staticfiles/
migration:
	python3 manage.py makemigrations
migrate:
	python3 manage.py migrate
startapp:
	python manage.py startapp $(name)
clear-linux:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete && find . -path "*/migrations/*.pyc"  -delete
clear-windows:
	Get-ChildItem -Path "*\migrations\0*.py" | Remove-Item -Force
	Get-ChildItem -Path "*\migrations\*.pyc" | Remove-Item -Force
no-sqlite-db:
	rm -rf db.sqlite3
re-django:
	pip3 uninstall Django -y && pip3 install Django
no-venv:
	rm -rf env/ venv/ .venv/
re-mig:
	make no-sqlite-db && make clear-linux && make re-django & make i && make mig && make cru && make collect && make test && make run-asgi
	