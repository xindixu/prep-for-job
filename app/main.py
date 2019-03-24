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
    import db
    db.init_app(app)

    # routes
    @app.route('/')
    def index():
        jobs = requests.get(f"http://api.dataatwork.org/v1/jobs", params={"limit": 10})
        if jobs.status_code != 200:
            num_jobs = 0
        else:
            num_jobs = len(jobs.json()[:-1])

        skills = requests.get(f"http://api.dataatwork.org/v1/skills", params={"limit": 30, "offset" : 19930})
        if skills.status_code != 200:
            num_skills = 0
        else:
            num_skills = len(skills.json()[:-1])
        return render_template('index.html', num_jobs=num_jobs, num_skills=num_skills)

    @app.route('/about')
    def about():
        commits = requests.get("https://gitlab.com/api/v4/projects/11264402/repository/commits", params={"all": "true", "per_page": 100}).json()
        issues = requests.get("https://gitlab.com/api/v4/projects/11264402/issues?scope=all", params={"scope": "all", "per_page": 100}).json()


        member_contribs = {
            "aidan": {
                "commits": len([commit for commit in commits
                                if commit["committer_email"] == "periodicaidan@gmail.com"]),
                "issues": len([issue for issue in issues
                               if issue["author"]["username"] == "periodicaidan"])
            },
            "xindi": {
                "commits": len([commit for commit in commits
                                if commit["committer_email"] == "xindixu@utexas.edu"]),
                "issues": len([issue for issue in issues
                               if issue["author"]["username"] == "xindixu"])
            },
            "srishtti": {
                "commits": len([commit for commit in commits
                                if commit["committer_email"] == "tsrishtti@gmail.com"]),
                "issues": len([issue for issue in issues
                               if issue["author"]["username"] == "stalwar5"])
            },
            "dylan": {
                "commits": len([commit for commit in commits
                                if commit["committer_email"] == "dmulrooney@utexas.edu"]),
                "issues": len([issue for issue in issues
                               if issue["author"]["username"] == "dmulrooney"])
            },
            "yiran": {
                "commits": len([commit for commit in commits
                                if commit["committer_email"] == "yiranzhang@utexas.edu"]),
                "issues": len([issue for issue in issues
                               if issue["author"]["username"] == "yiranzhang"])
            }
        }

        members = [  # TODO: sort by number of commits
            {
                "name": "Aidan T. Manning",
                "bio": "Computational chemistry major (May 2020). Interested in writing software to assist chemical research and education. Also makes bot accounts in his spare time.",
                "responsibilities": "Backend, about page, job and skill info pages",
                "contribs": member_contribs["aidan"],
                "photo": "aidan"
            },
            {
                "name": "Xindi Xu",
                "bio": "Advertising and Japanese; Completed Elements of Computing Certificate. Graduating May 2020.",
                "responsibilities": "Job Info Page, Front End",
                "contribs": member_contribs["xindi"],
                "photo": "xindi"
            },
            {
                "name": "Srishtti Talwar",
                "bio": "Mathematics and Economics major. Pursuing Elements of Computing Certificate. Graduating May 2020.",
                "responsibilities": "Skills Page, GCP Deployment (Co-partnering with Dylan), Technical Report",
                "contribs": member_contribs["srishtti"],
                "photo": "srishtti"
            },
            {
                "name": "Dylan Mulrooney",
                "bio": "Undeclared, Computer Science internal transfer. Blockchain developer.",
                "responsibilities": "Google Cloud Platform and home page",
                "contribs": member_contribs["dylan"],
                "photo": "dylan"
            },
            {
                "name": "Yiran Zhang",
                "bio": "senior, actuarial science major, pursuing elements of computing certificate, music lover and drum player.",
                "responsibilities": "Tech report, Salary page",
                "contribs": member_contribs["yiran"],
                "photo": "yiran"
            }
        ]

        stats = {
            "total_commits": 0,
            "total_issues": 0,
            "total_unittests": 0
        }

        for _, contribs in member_contribs.items():
            stats["total_commits"] += contribs["commits"]
            stats["total_issues"] += contribs["issues"]

        return render_template("about.html", members=members, stats=stats)

    @app.route('/job/')
    @app.route('/job/<string:uuid>')
    def job(uuid=None):
        if uuid is None:
            jobs = requests.get(f"http://api.dataatwork.org/v1/jobs", params={"limit": 10})
            if jobs.status_code != 200:
                return "Not Found", 404
            else:
                return render_template("job.html", jobs=jobs.json()[:-1])
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
                return render_template("skill.html", skills=skills.json()[:-1])
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
    import auth
    app.register_blueprint(auth.bp)

    @app.url_value_preprocessor
    def get_endpoint(endpoint, values):
        g.endpoint = endpoint
    return app

#if __name__ == '__main__':
#may need a run file or something
app = create_app()
