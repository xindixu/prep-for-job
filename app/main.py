import os

from flask import Flask, render_template, g, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from bls_datasets import oes, qcew
from passlib.hash import sha256_crypt
from forms import RegistrationForm, LoginForm
from models import Users, Skills, JobPages, Jobs, db
# from secrets import DB_STRING
import datetime


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        SQLALCHEMY_DATABASE_URI='postgresql://postgres:postgres@localhost:5434/prep-for-job',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)

    @app.before_first_request
    def setup():
        db.drop_all()
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
        # TODO: fix this when network is slow
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
            first_name = form.first_name.data
            last_name = form.last_name.data
            try:
                u = Users.new_member(email, password, first_name, last_name)
                if u is None:
                    print(u)
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
        u = Users.query.filter_by(id=user_id).first()
        print(u)
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
    def job(page=None, code=None):
        page = int(request.args.get('page', 1))
        if code is None:
            if JobPages.need_cache_page(page):
                jobs = JobPages.new_page(page)
                jobs = json.loads(jobs)
            else:
                jobs = json.loads(str(JobPages.get_page(page).jobs))
            return render_template("job.html", jobs=jobs, page=page)
        else:
            if Jobs.need_cache_code(code):
                print("Grabbing from API for first time and storing it!")
                jarray = Jobs.new_job(code)
            else:
                print("Pulling cached value from DB!")
                jarray = Jobs.get_code(code)

            job_obj = jarray[0]
            uuid = jarray[1]
            related_skills = jarray[2]
            job_info = jarray[3]
            knowledge = jarray[4]
            skills = jarray[5]
            abilities = jarray[6]
            technology = jarray[7]
            related_jobs = jarray[8]
            wage = jarray[9]

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
    @app.route('/skill/<string:id>')
    def skill(id=None):
        headers = {"Authorization":"Basic dXRleGFzOjk3NDRxZmc=", "Accept": "application/json"}
        if id is None:
            # Hot technology listing
            url = 'https://services.onetcenter.org/ws/online/hot_technology/'
            technology = requests.get(url, headers=headers)
            return render_template("skill.html", technology=json.loads(technology.text))
        else:
            technology = requests.get(f"https://services.onetcenter.org/ws/online/hot_technology/{id}",headers=headers)
            technology = json.loads(technology.text)
            occupations = []
            for job in technology["occupation"]:
                obj = {
                    "code": job["code"],
                    "title": job["title"]
                }
                occupations.append(obj)

            return render_template("skill_info.html", technology=technology,occupations=occupations)


    @app.route('/salary')
    @app.route('/salary/<string:code>')
    def salary(job_title=None, code=None):
        job_title = request.args.get('job_title')
        print(job_title)

        if code is None:
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
        else:
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
            return render_template("salary_info.html", wage=json.loads(wage.text), job_title=job_title)

    # auth
    @app.url_value_preprocessor
    def get_endpoint(endpoint, values):
        g.endpoint = endpoint

    return app

#if __name__ == '__main__':
# may need a run file or something
app = create_app()
