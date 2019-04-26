from flask_sqlalchemy import SQLAlchemy
import requests
import json
from datetime import datetime
from markupsafe import Markup
from passlib.hash import sha256_crypt
import secrets


db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"
    hash = db.Column(db.String(256), nullable=False)
    salt = db.Column(db.String(16), nullable=False, unique=True)
    email = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(75), nullable=False)
    location = db.Column(db.String(100))
    education = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    bio = db.Column(db.Text())
    id = db.Column(db.Integer(), primary_key=True)
    image = db.Column(db.String(500))

    def __repr__(self):
        return f"User({self.id}, {self.email})"

    @classmethod
    def exists(cls, email):
        if cls.query.filter_by(email=email).one_or_none() is not None:
            return True
        else:
            return False

    @classmethod
    def get_password(cls, email):
        cc = cls.query.filter_by(email=email).one_or_none()
        try:
            return cc.hash
        except:
            print("cant access password hash :(")

    @classmethod
    def new_member(cls, email, password, first_name, last_name):
        salt = secrets.token_hex(8)
        hash = str(sha256_crypt.using(salt=salt, relaxed=True).hash(password))
        print(password, hash)
        u = cls(email=email, hash=hash, salt=salt, first_name=first_name, last_name=last_name)
        db.session.add(u)
        db.session.commit()
        return u

    @classmethod
    def view_members(cls):
        return cls.query.all()

    def check_password(self, password):
        check_hash = sha256_crypt.using(salt_size=16, salt=self.salt).hash(password)
        print("Password Provided:", check_hash)
        print("Actual Password:", self.hash)
        if check_hash == self.hash:
            return True
        else:
            return False

    def __html__(self):
        html = u"<table>"
        for k, v in self.__dict__.items():
            html += u"<tr><th>{}</th><td>{}</td></tr>".format(k, v)
        html += u"</table>"
        return Markup(html)

class Jobs(db.Model):
    """
    code: primary key, page number from the API requests
    jobs: name of the job
    skills: API request fetching related skills to viewed job (code) 
    abilities: API request requesting required abilities to do a particular career (code) 
    technology:  API request fetching the technology associated with a given career (code) 
    knowledge:  API request getting the knowledge needed for a given career (code) 
    related job: API request looking for closely matched jobs given a career (code), allows exploring 
    job_info: Stored object created with API responses, stored for speedy calculations
    wage: general hourly wage for the job 
    """
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,nullable = False, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime,nullable = False, default=datetime.utcnow())
    code = db.Column(db.String(255), nullable=False)
    #title = db.Column(db.String(255), nullable=False)
    #job = db.Column(db.String(255), nullable=False)
    job_info = db.Column(db.Text, nullable=False)
    knowledge = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    abilities = db.Column(db.Text, nullable=False)
    technology = db.Column(db.Text, nullable=False)
    related_jobs = db.Column(db.Text, nullable=False)
    wage = db.Column(db.Text)

    @classmethod
    def new_job(cls, code):
        """
        create a new job with api if it's not cached in db
        detail API description go on WiKi page
        """
        if cls.query.filter_by(code=code).one_or_none() is None:
            #from onet
            headers = {"Authorization":"Basic dXRleGFzOjk3NDRxZmc=", "Accept": "application/json"}
            job_info = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}", headers=headers)
            knowledge = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/knowledge", headers=headers)
            skills = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/skills", headers=headers)
            abilities = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/abilities", headers=headers)
            technology = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/technology", headers=headers)
            related_jobs = requests.get(f"https://services.onetcenter.org/ws/mnm/careers/{code}/explore_more", headers=headers)
            if job_info.status_code != 200:
                return "Not Found", 404 #this does not work btw

            base = 'OEUN'
            area_code = '0000000' # national wide
            industry_code = '000000' # total

            arr = code[:7].split('-')
            job_code = arr[0]+arr[1]

            # hourly wage
            statistic_code = '03'
            seriesid = base + area_code + industry_code + job_code + statistic_code

            headers = {'Content-type': 'application/json'}
            data = json.dumps({"seriesid": [seriesid], "startyear": "2018", "endyear": "2018"})
            wage = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
            u = cls(code=code, job_info=job_info.text, knowledge=knowledge.text, skills=skills.text, abilities=abilities.text, technology=technology.text, related_jobs=related_jobs.text, wage=wage.text)
            db.session.add(u)
            db.session.commit()
            return [job_info, knowledge, skills, abilities, technology, related_jobs, wage]
        else:
            print("No need to call!")
            return None

    @classmethod
    def need_cache_code(cls, code):
        # TODO hash password before passing
        u = cls.query.filter_by(code=code).first()
        if u == None:
            return True
        else:
            return False
    @classmethod
    def get_code(cls, code):
        """
        get the job object from the db
        """
        u = cls.query.filter_by(code=code).first()
        jarray = [u.job_info, u.knowledge, u.skills, u.abilities, u.technology, u.related_jobs, u.wage]
        return jarray

    @classmethod
    def get_related_jobs_in_sallary_range(cls, deviation):
        pass

    def __html__(self):
        html = u"<table>"
        for k, v in self.__dict__.items():
            html += u"<tr><th>{}</th><td>{}</td></tr>".format(k, v)
        html += u"</table>"
        return Markup(html)


class JobPages (db.Model):
    """
    page: primary key, page number from the API requests
    jobs: name of the job
    """
    __tablename__ = "jobpages"
    page = db.Column(db.Integer, nullable = False, primary_key=True, autoincrement=False)
    created_at = db.Column(db.DateTime,nullable = False, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime,nullable = False, default=datetime.utcnow())
    jobs = db.Column(db.Text, nullable=False)
    @classmethod
    def new_page(cls, page):
        if cls.query.filter_by(page=page).one_or_none() is None:
            print("NEED TO POPULATE DB PAGE #"+str(page)+"!")
            headers = {"Authorization":"Basic dXRleGFzOjk3NDRxZmc=", "Accept": "application/json"}
            url = "https://services.onetcenter.org/ws/mnm/careers/"
            if page is not None:
                url += f"?start={(page-1)*20+1}"
            print("API REQUESTED FOR PAGE: "+str(page))
            jobs = requests.get(url, headers=headers)
            jobs = jobs.text
            u = cls(page=page, jobs=str(jobs))
            print("INSERTED!")
            #u = cls(id=page, code=code, title=title, job=job, job_obj=job_obj, related_skills=related_skills, knowledge=knowledge, skills=skills, abilities=abilities, technology=technology, related_jobs=related_jobs, wage=wage)
            db.session.add(u)
            db.session.commit()
            return jobs

    @classmethod
    def need_cache_page(cls, page):
        """
        determine the page need to be cached
        """
        # todo hash password before passing
        u = cls.query.filter_by(page=page).one_or_none()
        if u == None:
            return True
        else:
            return False

    @classmethod
    def get_page(cls, page):
        """
        get the page from the db
        """
        return cls.query.filter_by(page=page).one_or_none()


class Salary (db.Model):
    __tablename__ = "salary"
    id = db.Column(db.Integer, nullable = False, primary_key=True, autoincrement=False)
    salary_info = db.Column(db.Text, nullable = False)
    weekly_avg = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime,nullable = False, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime,nullable = False, default=datetime.utcnow())

    @classmethod
    def new_salary_page(cls):
        """
        populates the database if needed
        """
        if cls.query.filter_by(id=1).one_or_none() is None:
            print("NEED TO POPULATE DB PAGE #"+str(page)+"!")
            headers = {"Authorization":"Basic dXRleGFzOjk3NDRxZmc=", "Accept": "application/json"}
            url = "https://services.onetcenter.org/ws/mnm/careers/"
            if page is not None:
                url += f"?start={(page-1)*20+1}"
            print("API REQUESTED FOR PAGE: "+str(page))
            jobs = requests.get(url, headers=headers)
            jobs = jobs.text
            u = cls(page=page, jobs=str(jobs))
            print("INSERTED!")
            #u = cls(id=page, code=code, title=title, job=job, job_obj=job_obj, related_skills=related_skills, knowledge=knowledge, skills=skills, abilities=abilities, technology=technology, related_jobs=related_jobs, wage=wage)
            db.session.add(u)
            db.session.commit()
            return jobs
        else:
            # not done!
            print("DATABASE source:")

    @classmethod
    def need_cache_page(cls, page):
        """
        checks if the page needs caching and returns True or False accordingly
        """
        u = cls.query.filter_by(page=page).one_or_none()
        if u == None:
            return True
        else:
            return False

    @classmethod
    def get_page(cls, page):
        """
        this will get the page that is needed
        """
        return cls.query.filter_by(page=page).one_or_none()

    def __html__(self):
        html = u"<table>"
        for k, v in self.__dict__.items():
            html += u"<tr><th>{}</th><td>{}</td></tr>".format(k, v)
        html += u"</table>"
        return Markup(html)
