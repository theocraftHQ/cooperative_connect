

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

local_migrate_init :
	alembic -c local_dev_alembic.ini init .local_migrations

local_migrate :
	alembic -c local_dev_alembic.ini revision -m $(MESSAGE) --autogenerate


local_migrate_up:
	alembic -c local_dev_alembic.ini upgrade heads



local_migrate_down:
	alembic -c local_dev_alembic.ini downgrade -"$(STEP)"

local-head:
	alembic -c local_dev_alembic.ini heads

member_server:
	uvicorn theocraft_coop.root.app:app --reload --port=8000
coop_server:
	uvicorn theocraft_coop.root.app:app --reload --port=8001

format : 
	$(BLACK) --preview ./project_name

standard:
	$(RUFF) check ./project_name --ignore=E731,E712
