import os

from flask import Flask, render_template, g, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from bls_datasets import oes, qcew
from passlib.hash import sha256_crypt
from app.forms import RegistrationForm, LoginForm
from app.models import Users, Skills, Jobs, db
# from secrets import DB_STRING
import datetime


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        SQLALCHEMY_DATABASE_URI='postgresql://postgres:dbPassword1@157.230.173.38:5432/maindb2',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)

    @app.before_first_request
    def setup():
        db.create_all()

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

    num_jobs = 20
    num_skills = 30

    # routes
    @app.route('/')
    def index():
        # WARNING: changed! we are calling apis while we don't have to!

        return render_template('index.html', num_jobs=num_jobs, num_skills=num_skills)

    @app.route('/about')
    def about():
        commits = requests.get("https://gitlab.com/api/v4/projects/11264402/repository/commits", params={"all": "true", "per_page": 100}).json()
        issues = requests.get("https://gitlab.com/api/v4/projects/11264402/issues?scope=all", params={"scope": "all", "per_page": 100}).json()

        member_contribs = {
            "aidan": {"commits": 0, "issues": 0},
            "xindi": {"commits": 0, "issues": 0},
            "srishtti": {"commits": 0, "issues": 0},
            "dylan": {"commits": 0, "issues": 0},
            "yiran": {"commits": 0, "issues": 0}
        }

        for commit in commits:
            if commit["committer_email"] == "periodicaidan@gmail.com":
                member_contribs["aidan"]["commits"] += 1
            elif commit["committer_email"] == "xindixu@utexas.edu":
                member_contribs["xindi"]["commits"] += 1
            elif commit["committer_email"] == "tsrishtti@gmail.com":
                member_contribs["srishtti"]["commits"] += 1
            elif commit["committer_email"] == "dmulrooney@utexas.edu":
                member_contribs["dylan"]["commits"] += 1
            elif commit["committer_email"] == "yiranzhang@utexas.edu":
                member_contribs["yiran"]["commits"] += 1

        for issue in issues:
            if issue["author"]["username"] == "periodicaidan":
                member_contribs["aidan"]["issues"] += 1
            elif issue["author"]["username"] == "xindixu":
                member_contribs["xindi"]["issues"] += 1
            elif issue["author"]["username"] == "stalwar5":
                member_contribs["srishtti"]["issues"] += 1
            elif issue["author"]["username"] == "dmulrooney":
                member_contribs["dylan"]["issues"] += 1
            elif issue["author"]["username"] == "yiranzhang":
                member_contribs["yiran"]["issues"] += 1

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
                "bio": "Advertising, Elements of Computing Certificate (May 2020). Front End Developer",
                "responsibilities": "Job Info Page, Salary page, BLS API connection, Login/Register & database, Front End",
                "contribs": member_contribs["xindi"],
                "photo": "xindi"
            },
            {
                "name": "Srishtti Talwar",
                "bio": "Mathematics and Economics major. Pursuing Elements of Computing Certificate. Graduating May 2020.",
                "responsibilities": "Skills Page, Technical Report",
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
        members = sorted(members, reverse=True, key=lambda m: sum(m["contribs"].values()))

        stats = {
            "total_commits": 0,
            "total_issues": 0,
            "total_unittests": 0
        }

        for _, contribs in member_contribs.items():
            stats["total_commits"] += contribs["commits"]
            stats["total_issues"] += contribs["issues"]

        return render_template("about.html", members=members, stats=stats)

    @app.route('/auth/register/', methods=('GET', 'POST'))
    def register():
        form = RegistrationForm()
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            try:
                u = Users.new_member(email, password)
                if not u:
                    flash(f"User {email} already exists", "danger")
                    return render_template("auth/register.html", form=form)
            except Exception as e:  # todo: make this more specific
                print(e)
                flash(f"User {email} already exists", "danger")
                return render_template("auth/register.html", form=form)
            k = u.view_members()
            print(k)
            flash("You have been registered successfully", category="success")
            return redirect(url_for("login"))
        else:
            return render_template("auth/register.html", form=form)

    @app.route('/auth/login/', methods=('GET', 'POST'))
    def login():
        form = LoginForm()
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            u = Users.query.filter_by(email=email).one_or_none()
            if u is None:
                flash(f"{email} was not found.", "danger")
            elif u.hash != password:
                flash(f"Incorrect password for {email}", "danger")
            else:
                return redirect(url_for("profile", user_id=u.id))

        return render_template("auth/login.html", form=form)

    @app.route('/auth/logout/', methods=('GET', 'POST'))
    def logout():
        return "TODO: add session, hash passwords, add postgress uri, and test db functions"

    @app.route("/profile/<user_id>")
    def profile(user_id):
        u = Users.query.filter_by(id=4).first()
        # user = {
        #     "name": "John Smith",
        #     "email": "johnsmith1@example.com",
        #     "profile_picture": None,
        #     "bio": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aliquam eaque ipsa labore pariatur porro sequi tenetur? Commodi nemo nisi nulla quam quos suscipit temporibus voluptatibus?",
        #     "education": "Fuck school, teach yourself",
        #     "location": "Hell, MI"
        # }
        return render_template("profile.html", user=u)

    @app.route('/job/')
    @app.route('/job/<string:code>')
    def job(code=None, job_title=None):
        if code is None:
            # TODO: load next batch of data
            headers = {"Authorization":"Basic dXRleGFzOjk3NDRxZmc=", "Accept": "application/json"}
            jobs = requests.get("https://services.onetcenter.org/ws/mnm/careers/", headers=headers)
            return render_template("job.html", jobs=json.loads(jobs.text))
        else:
            # connect any api with onet
            # QUESTION: skill relationship in onet only or anyapi
            job_obj = requests.get(f"http://api.dataatwork.org/v1/jobs/{code}")
            uuid = (json.loads(job_obj.text))["uuid"]
            related_skills = requests.get(f"http://api.dataatwork.org/v1/jobs/{uuid}/related_skills")

            headers = {"Authorization":"Basic dXRleGFzOjk3NDRxZmc=", "Accept": "application/json"}
            job_info = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}", headers=headers)
            knowledge = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/knowledge", headers=headers)
            skills = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/skills", headers=headers)
            abilities = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/abilities", headers=headers)
            technology = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/technology", headers=headers)
            related_jobs = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/explore_more", headers=headers)



            # construct seriesid for bls api for wage
            base = 'OEUN'
            area_code = '0000000' # national wide
            industry_code = '000000' # total

            arr = code[:7].split('-')
            job_code = arr[0]+arr[1]

            # hourly wage
            statistic_code = '03'
            seriesid = base+area_code+industry_code+job_code+statistic_code

            headers = {'Content-type': 'application/json'}
            data = json.dumps({"seriesid": [seriesid], "startyear": "2018", "endyear": "2018"})
            wage = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)




            if job_info.status_code != 200:
                return "Not Found", 404
            else:
                return render_template("job_info.html", job=json.loads(job_info.text),
                                       job_obj=json.loads(job_obj.text),
                                       related_skills=json.loads(related_skills.text),
                                       knowledge=json.loads(knowledge.text),
                                       skills=json.loads(skills.text),
                                       abilities=json.loads(abilities.text),
                                       technology=json.loads(technology.text),
                                       related_jobs=json.loads(related_jobs.text),
                                       wage=json.loads(wage.text)
                                       )

    @app.route('/skill/')
    @app.route('/skill/<string:uuid>')
    def skill(uuid=None):
        if uuid is None:
            skills = requests.get(f"http://api.dataatwork.org/v1/skills", params={"limit": num_skills, "offset" : 19930})
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
        # TODO: load multiple wage data
        # connect job titles back to job page

        df_oes = oes.get_data(year=2017)
        detailed = df_oes[df_oes.OCC_GROUP == 'detailed']
        job = detailed.OCC_TITLE.values
        code = detailed.OCC_CODE.values
        salary = detailed.A_MEDIAN.values

        salary_info = zip(job,code,salary)

        # for i in job.index:
        #     salary_info += {'title': job.get(i), 'code': code.get(i), 'salary': salary.get(i)}
            # salary = detailed[detailed.OCC_TITLE == j].A_MEDIAN.values[0]


        # avg weekly wage
        df_qcew = qcew.get_data('industry', rtype='dataframe', year='2017', qtr='1', industry='10')
        austin = df_qcew[(df_qcew.own_code == 0) & (df_qcew.area_fips == '48015')]
        weekly_avg = austin.avg_wkly_wage.values[0]


        # TODO: load multiple wage data
        # api

        base = 'OEUN'
        # national wide
        area_code = '0000000'
        # total
        industry_code = '000000'
        # Registered Nurses
        job_code = '291141'
        # hourly wage
        statistic_code = '03'
        seriesid = base+area_code+industry_code+job_code+statistic_code

        # url = "http://api.bls.gov/publicAPI/v2/timeseries/data/"
        # wage = requests.get(url, data=data, headers=headers)


        headers = {'Content-type': 'application/json'}
        data = json.dumps({"seriesid": [seriesid]})
        wage = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)


        return render_template("salary.html", salary_info=salary_info, loc_to_salary=weekly_avg)

    # auth
    @app.url_value_preprocessor
    def get_endpoint(endpoint, values):
        g.endpoint = endpoint

    return app

#if __name__ == '__main__':
# may need a run file or something
app = create_app()
