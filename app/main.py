import os
from flask import Flask, render_template, g, request, flash, redirect, url_for
import requests
import json
from bls_datasets import oes, qcew
from forms import RegistrationForm, LoginForm
from models import Users, JobPages, Jobs, db

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        SQLALCHEMY_DATABASE_URI='postgresql://postgres:dbPassword1@157.230.173.38:5432/maindb5',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)

    @app.before_first_request
    def setup():
        db.create_all()

    # routes
    @app.route('/')
    def index():
        # WARNING: changed! we are calling apis while we don't have to!
        card_dict = {
            "job": ["Find your next dream job.", "info", "briefcase"] ,
            "salary": ["Get more information about the your next monthly income.", "success", "credit-card"],
            "skill": ["Look up required skills for your dream job.", "danger", "spinner"],
            "about": ["Learn more about us and the story behind our project.", "warning", "question-circle"]
        }
        return render_template('index.html', card_dict=card_dict)

    @app.route('/about')
    def about():
        # TODO: fix this when network is slow
        commits = []
        issues = []

        # Get all the commits. They are paginated, and pages are limited to a max of 100 per request, so we must
        # loop to get all the pages.
        page = 1
        commits_req = requests.get("https://gitlab.com/api/v4/projects/11264402/repository/commits",
                                   params={"all": "true", "per_page": 100, "page": page})
        while page <= int(commits_req.headers["X-Total-Pages"]):
            commits.extend(commits_req.json())
            page += 1
            commits_req = requests.get("https://gitlab.com/api/v4/projects/11264402/repository/commits",
                                       params={"all": "true", "per_page": 100, "page": page})

        # Get all the issues. Same caveat applies here as it does for commits.
        page = 1
        issues_req = requests.get("https://gitlab.com/api/v4/projects/11264402/issues",
                                  params={"scope": "all", "per_page": 100, page: 1})
        while page <= int(issues_req.headers["X-Total-Pages"]):
            issues.extend(issues_req.json())
            page += 1
            issues_req = requests.get("https://gitlab.com/api/v4/projects/11264402/issues",
                                      params={"scope": "all", "per_page": 100, page: 1})

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

        members = [
            {
                "name": "Aidan T. Manning",
                "bio": "Computational chemistry major (May 2020). Interested in writing software to assist chemical research and education. Also makes bot accounts in his spare time.",
                "responsibilities": "Backend, about page, job and skill info pages, SQLAlchemy, worked with authentication, debugging and code refactoring",
                "contribs": member_contribs["aidan"],
                "photo": "aidan"
            },
            {
                "name": "Xindi Xu",
                "bio": "Advertising major, Elements of Computing Certificate (May 2020). Front End Developer",
                "responsibilities": "Job, Job_info, Skill, Skill_info, Salary, Salary_info, Home pages, O*Net/BLS API connection, Frontend & styling",
                "contribs": member_contribs["xindi"],
                "photo": "xindi"
            },
            {
                "name": "Srishtti Talwar",
                "bio": "Mathematics and Economics major. Pursuing Elements of Computing Certificate. Graduating May 2020.",
                "responsibilities": "Skills Page, Technical Report, Splash page, skill_salary_info page, About page",
                "contribs": member_contribs["srishtti"],
                "photo": "srishtti"
            },
            {
                "name": "Dylan Mulrooney",
                "bio": "Undeclared, Computer Science internal transfer. Blockchain developer.",
                "responsibilities": "Google Cloud Platform and home page, Database, Caching, Deployment, Register and Login Page, unit tests",
                "contribs": member_contribs["dylan"],
                "photo": "dylan"
            },
            {
                "name": "Yiran Zhang",
                "bio": "senior, actuarial science major, pursuing elements of computing certificate, music lover and drum player.",
                "responsibilities": "Technical report, Salary page, unit tests, and data-model",
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

    @app.route('/skill_salary/<string:code>', methods=('GET', 'POST'))
    def skill_salary(code):
        if Jobs.need_cache_code(code):
            print("Grabbing from API for first time and storing it!")
            using_api = True
            jarray = Jobs.new_job(code)
        else:
            print("Pulling cached value from DB!")
            using_api = False
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

        if using_api == True:
            return render_template("skill_salary.html", job=json.loads(job_info.text),
                               job_obj=json.loads(job_obj.text),
                               related_skills=json.loads(related_skills.text),
                               knowledge=json.loads(knowledge.text),
                               skills=json.loads(skills.text),
                               abilities=json.loads(abilities.text),
                               technology=json.loads(technology.text),
                               related_jobs=json.loads(related_jobs.text),
                               wage=json.loads(wage.text)
                               )
        else:
            return render_template("skill_salary.html", job=json.loads(job_info),
                               job_obj=json.loads(job_obj),
                               related_skills=json.loads(related_skills),
                               knowledge=json.loads(knowledge),
                               skills=json.loads(skills),
                               abilities=json.loads(abilities),
                               technology=json.loads(technology),
                               related_jobs=json.loads(related_jobs),
                               wage=json.loads(wage)
                               )

    @app.route('/auth/register/', methods=('GET', 'POST'))
    def register():
        form = RegistrationForm()
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data.lower()
            password = form.password.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            if Users.exists(email):
                flash("User {} already exists".format(email))
            else:
                u = Users.new_member(email, password, first_name, last_name)
                flash("You have been registered successfully!", "success")
                return redirect(url_for("profile", user_id=u.id))

        return render_template("auth/register.html", form=form)

    @app.route('/auth/login/', methods=('GET', 'POST'))
    def login():
        form = LoginForm()
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            if not Users.exists(email):
                flash("User {} does not exist".format(email), "danger")
            else:
                u = Users.query.filter_by(email=email).first()
                if u.check_password(password):
                    flash("Logged in successfully!", "success")
                    return redirect(url_for("profile", user_id=u.id))
                else:
                    flash("Incorrect password for "+email, "danger")

        return render_template("auth/login.html", form=form)



    @app.route('/auth/logout/', methods=('GET', 'POST'))
    def logout():
        return "TODO: add session, hash passwords, add postgress uri, and test db functions"

    @app.route("/profile/<user_id>")
    def profile(user_id):
        u = Users.query.filter_by(id=user_id).first()
        print(u)
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
                using_api = True
                print("Grabbing from API for first time and storing it!")
                jarray = Jobs.new_job(code)
            else:
                print("Pulling cached value from DB!")
                using_api = False
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

            if using_api == True:
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
            else:
                return render_template("job_info.html", job=json.loads(job_info),
                                   job_obj=json.loads(job_obj),
                                   related_skills=json.loads(related_skills),
                                   knowledge=json.loads(knowledge),
                                   skills=json.loads(skills),
                                   abilities=json.loads(abilities),
                                   technology=json.loads(technology),
                                   related_jobs=json.loads(related_jobs),
                                   wage=json.loads(wage)
                                   )

    @app.route('/skill/')
    @app.route('/skill/<string:id>')
    def skill(page=None, id=None):
        page = int(request.args.get('page', 1))
        headers = {"Authorization":"Basic dXRleGFzOjk3NDRxZmc=", "Accept": "application/json"}
        if id is None:
            # Hot technology listing
            url = 'https://services.onetcenter.org/ws/online/hot_technology'
            if page is not None:
                start = (page-1)*20+1
                end = start + 20
                url += f"?start={start}&end={end}"
            technology = requests.get(url, headers=headers)
            return render_template("skill.html", technology=json.loads(technology.text), page=page)
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
    def salary():
        # TODO: load multiple wage data
        # connect job titles back to job page
        df_oes = oes.get_data(year=2017)
        detailed = df_oes[df_oes.OCC_GROUP == 'detailed']
        job = detailed.OCC_TITLE.values
        code = detailed.OCC_CODE.values
        salary = detailed.A_MEDIAN.values
        salary_info = zip(job,code,salary)

        # avg weekly wage
        df_qcew = qcew.get_data('industry', rtype='dataframe', year='2017', qtr='1', industry='10')
        austin = df_qcew[(df_qcew.own_code == 0) & (df_qcew.area_fips == '48015')]
        weekly_avg = austin.avg_wkly_wage.values[0]

        return render_template("salary.html", salary_info=salary_info, loc_to_salary=weekly_avg)

        # base = 'OEUN'
        # # national wide
        # area_code = '0000000'
        # # total
        # industry_code = '000000'
        # # hourly wage
        # statistic_code = '03'
        # seriesid = base+area_code+industry_code+job_code+statistic_code
        #
        # headers = {'Content-type': 'application/json'}
        # data = json.dumps({"seriesid": [seriesid]})
        # wage = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
        #
        # return render_template("salary_info.html", status=wage.json()["status"], wage=wage.json()["Results"]["series"][0]["data"][0])

    @app.errorhandler(404)
    def error404(err):
        return render_template("error404.html", err=err), 404

    # auth
    @app.url_value_preprocessor
    def get_endpoint(endpoint, values):
        g.endpoint = endpoint

    return app

#if __name__ == '__main__':
# may need a run file or something
app = create_app()
