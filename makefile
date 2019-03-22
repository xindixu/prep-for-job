export FLASK_ENV=development
export FLASK_DEBUG=1
export PORT=8080

website:
	flask run -p${PORT}