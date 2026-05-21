.PHONY: setup backend frontend serve dev test install-frontend clean help

help:
	@echo "Commandes disponibles:"
	@echo "  make setup           - Installe toutes les dépendances"
	@echo "  make backend         - Lance le serveur Flask (port 5000)"
	@echo "  make frontend        - Lance le serveur React (port 3000)"
	@echo "  make serve           - Lance les deux serveurs"
	@echo "  make dev             - Alias pour 'serve'"
	@echo "  make test            - Lance les tests API"
	@echo "  make clean           - Nettoie les fichiers générés"

setup: install-frontend
	pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

backend:
	cd src && python app.py

frontend:
	cd frontend && npm run dev

serve: backend frontend

dev: serve

test:
	python test_api.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
