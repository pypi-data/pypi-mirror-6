
#  Copyright (c) 2013-2014, The University of Chicago
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of The University of Chicago nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.

import yaml
import math
import os.path
import chisubmit.core
from chisubmit.common.utils import set_datetime_timezone_utc
import urllib2
from chisubmit.core import ChisubmitException


class ChisubmitModelException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class Course(object):
    def __init__(self, course_id, name, extensions):
        self.id = course_id
        self.name = name
        self.extensions = extensions
        
        self.github_organization = None
        self.github_admins_team = None
        
        self.git_staging_username = None
        self.git_staging_hostname = None
        
        self.students = {}
        self.projects = {}
        self.teams = {}
        
        self.course_file = None
        
    def save(self, course_file = None):
        if self.course_file is None and course_file is None:
            raise ChisubmitModelException("Course object has no file associated with it.")

        if course_file is None:
            course_file = self.course_file
            
        try:
            f = open(course_file, 'w')
            yaml.dump(self, f)
            f.close()
        except IOError, ioe:
            raise ChisubmitException("Error when saving course to file %s: %s" % (course_file, ioe.meesage), ioe)
        
    @staticmethod
    def from_file(course_file):
        course = yaml.load(course_file)
        if type(course) != Course:
            raise ChisubmitModelException("Course file does not contain a Course object.")
        return course

    @staticmethod
    def from_url(course_url):
        try:
            req = urllib2.Request(course_url)
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, he:
            raise ChisubmitException("Error when accessing %s: %s %s" % (course_url, he.code, he.msg), he)
        except urllib2.URLError, ue:
            raise ChisubmitException("Error when accessing %s: %s" % (course_url, ue.reason), ue)
        
        course = yaml.load(response)
        if type(course) != Course:
            raise ChisubmitModelException("Course file does not contain a Course object.")        
        
        return course
    
    @staticmethod
    def from_course_id(course_id):
        course_file = chisubmit.core.get_course_filename(course_id)
        if not os.path.exists(course_file):
            return None
        course_file = open(course_file)
        course_obj = Course.from_file(course_file)
        course_file.close()
        return course_obj
    
    def get_student(self, student_id):
        return self.students.get(student_id)
        
    def add_student(self, student):
        self.students[student.id] = student

    def get_project(self, project_id):
        return self.projects.get(project_id)

    def add_project(self, project):
        self.projects[project.id] = project

    def get_team(self, team_id):
        return self.teams.get(team_id)

    def add_team(self, team):
        self.teams[team.id] = team
        
        
class GradeComponent(object):
    def __init__(self, name, points):
        self.name = name
        self.points = points        


class Project(object):
    def __init__(self, project_id, name, deadline):
        self.id = project_id
        self.name = name
        self.deadline = deadline
        self.grade_components = []
        
    def add_grade_component(self, grade_component):
        self.grade_components.append(grade_component)

    # We need to do this because PyYAML doesn't load
    # timezone data when reading dates. 
    def get_deadline(self):
        return set_datetime_timezone_utc(self.deadline)
        
    def extensions_needed(self, submission_time):
        delta = (submission_time - self.get_deadline()).total_seconds()
        
        extensions_needed = math.ceil(delta / (3600.0 * 24))
        
        if extensions_needed <= 0:
            return 0
        else:
            return int(extensions_needed)        
        
    def get_grading_branch_name(self):
        return self.id + "-grading"
        

class Student(object):
    def __init__(self, student_id, first_name, last_name, email, github_id):
        self.id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.github_id = github_id
        
        self.dropped = False
        
    def __repr__(self):
        return "<Student %s: %s>" % (self.id, self.get_full_name())
        
    def get_full_name(self, comma = False):
        if comma:
            return "%s, %s" % (self.last_name, self.first_name)
        else:
            return "%s %s" % (self.first_name, self.last_name)
            
        
   
class Grader(object):
    def __init__(self, student_id, first_name, last_name, email, github_id):
        self.id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.github_id = github_id

        
class Team(object):
    def __init__(self, team_id):
        self.id = team_id

        self.students = []
        self.active = True
        self.github_repo = None
        self.github_team = None
        self.github_email_sent = False
        
        self.projects = {}

    def __repr__(self):
        return "<Team %s>" % self.id
        
    def add_student(self, student):
        self.students.append(student)
        
    def add_project(self, project):
        self.projects[project.id] = TeamProject(project)
        
        
class TeamProject(object):
    def __init__(self, project):
        self.project = project
        
        self.grader = None
        self.extensions_used = 0
        self.grades = {}
        
    def set_grade(self, grade_component, points):
        self.grades[grade_component] = points
    