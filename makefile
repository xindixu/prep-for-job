export FLASK_ENV=development
export FLASK_DEBUG=1
export FLASK_APP=app/main
export FLASK_PORT=8080

website:
	flask run -p${FLASK_PORT}
