

PYTHON = venv/bin/python
PIP = venv/bin/pip
BLACK = venv/bin/python -m black
RUFF = venv/bin/python -m ruff 
MESSAGE = "Local Table Migrations"
STEP = 1


venv : 
	python3 -m venv venv
	
activate :
	source /venv/bin/activate

install :
	pip install -r requirements.txt 


local-migration:
	alembic -c local_dev_alembic.ini revision -m "$(MESSAGE)" --autogenerate


local-migrate:
	alembic -c local_dev_alembic.ini upgrade heads



local-migrate-down:
	alembic -c local_dev_alembic.ini downgrade -"$(STEP)"


local-head:
	alembic -c local_dev_alembic.ini heads



agent_server:
	uvicorn project_name.root.app:app --reload --port=8000

admin_server:
	uvicorn project_name.root.app:app --reload --port=8001


	rq worker --with-scheduler


format : 
	$(BLACK) --preview ./project_name

standard:
	$(RUFF) check ./project_name --ignore=E731,E712
