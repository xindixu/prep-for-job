import os

from flask import Flask, render_template, g


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # connect to db
    from . import db
    db.init_app(app)

    # routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template("about.html")

    @app.route('/job')
    def job():
        return render_template("job.html")

    @app.route('/skill')
    def skill():
        return render_template("skill.html")

    @app.route('/salary')
    def salary():
        return render_template("salary.html")

    # auth
    from . import auth
    app.register_blueprint(auth.bp)

    @app.url_value_preprocessor
    def get_endpoint(endpoint, values):
        g.endpoint = endpoint
    
    return app


if __name__ == '__main__':
    create_app()
