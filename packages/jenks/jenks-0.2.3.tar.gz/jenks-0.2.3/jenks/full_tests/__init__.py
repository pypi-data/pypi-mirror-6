"""
Full tests
import os
from jenkinsapi_utils.jenkins_launcher import JenkinsLancher

state = {}

fulltests_dir, _ = os.path.split(__file__)
war_path = os.path.join(fulltests_dir, 'jenkins.war')
state['launcher'] = JenkinsLancher(war_path)
state['launcher'].start()


def tearDownPackage():
    state['launcher'].stop()

"""
