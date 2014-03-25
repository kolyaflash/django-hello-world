MANAGE=django-admin.py
PROJECT_DIR=django_hello_world

test:
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(PROJECT_DIR).settings $(MANAGE) test hello

test_coverage:
	cd $(PROJECT_DIR) && coverage run --source='.' manage.py test hello
	cd $(PROJECT_DIR) && coverage report

run:
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(PROJECT_DIR).settings $(MANAGE) runserver

syncdb:
	PYTHONPATH=`pwd` DJANGO_SETTINGS_MODULE=$(PROJECT_DIR).settings $(MANAGE) syncdb --noinput

validate:
	pep8 $(PROJECT_DIR)/hello --exclude="migrations"
	pyflakes $(PROJECT_DIR)/hello
