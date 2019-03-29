import os
import sys
import unittest

from main import create_app

# test for job table
# description is not null
# Salary is not null
# job is unique

# test for skill table
# description is not null
# skill is unique
# title is not null

# test for skill-job table
# unique skill-job

# test for register table
# email unique
# email is an email (must have @ and .)
# password is same with retype
# cannot be blank

# test for login table
# password is correct
# password cannot be blank
# retrieve password is working
