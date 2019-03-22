export FLASK_ENV=development
export FLASK_DEBUG=1
export PORT=8080

website: db
	flask run -p${PORT}

db:
	flask init-db