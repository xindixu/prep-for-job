import os

from flask import Flask, render_template, g
import json
import requests


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

    @app.route('/job/')
    @app.route('/job/<string:uuid>')
    def job(uuid=None):
        if uuid is None:
            jobs = requests.get(f"http://api.dataatwork.org/v1/jobs", params={"limit": 10})
            if jobs.status_code != 200:
                return "Not Found", 404
            else:
                return render_template("job.html", jobs=jobs.json())
        else:
            job_info = requests.get(f"http://api.dataatwork.org/v1/jobs/{uuid}")
            related_jobs = requests.get(f"http://api.dataatwork.org/v1/jobs/{uuid}/related_jobs")
            related_skills = requests.get(f"http://api.dataatwork.org/v1/jobs/{uuid}/related_skills")
            if job_info.status_code != 200 or related_skills.status_code != 200 or related_jobs.status_code != 200:
                return "Not Found", 404
            else:
                return render_template("job_info.html", job=job_info.json(), skills=related_skills.json(), related_jobs=related_jobs.json())

    @app.route('/skill/')
    @app.route('/skill/<string:uuid>')
    def skill(uuid=None):
        if uuid is None:
            skills = requests.get(f"http://api.dataatwork.org/v1/skills", params={"limit": 30, "offset" : 19930})
            if skills.status_code != 200:
                return "Not Found", 404
            else:
                return render_template("skill.html", skills=skills.json())
        else:
            skills_info = requests.get(f"http://api.dataatwork.org/v1/skills/{uuid}")
            related_jobs = requests.get(f"http://api.dataatwork.org/v1/skills/{uuid}/related_jobs")
            print(skills_info, related_jobs, sep="\n")
            # if skills_info.status_code != 200 or related_jobs.status_code != 200:
            #         return "Not Found", 404
            # else:
            return render_template("skills_info.html", skills=skills_info.json(), jobs=related_jobs.json())


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
