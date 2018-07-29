#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Fast-written. Dirty. Stupid.
"""

import csv
import datetime
import requests


from config import access_token


class AsanaApi:
    def __init__(self, access_token, baseurl='https://app.asana.com/api/1.0'):
        self.baseurl = baseurl
        self.access_token = access_token
        self.session = None

    def __auth(self):
        if not self.session:
            s = requests.session()
            s.headers.update({'Authorization': 'Bearer {}'.format(self.access_token)})
            print(s.headers)
            self.session = s

    def __get(self, query_string):
        # ToDo: use smth like @auth?
        if not self.session:
            print("Authenticating")
            self.__auth()
        print('[U]: {}'.format(self.baseurl + query_string))
        response = self.session.get(self.baseurl + query_string).json()
        return response

    def get_projects(self):
        # Not sure about pagination if you have too many projects
        return self.__get('/projects')['data']

    def get_tasks(self, project_id):
        # Todo: make getting all tasks optional
        query_string = '/tasks?project=' + str(project_id) + "&limit=100&opt_fields=completed_at,due_on,name,notes,projects,created_at,modified_at,assignee,parent"
        # print(query_string)
        tasks = self.__get(query_string)
        res = tasks['data']
        # print(project_id, tasks['next_page'])
        while tasks['next_page'] is not None:
            query_string = tasks['next_page']['path']
            tasks = self.__get(query_string)
            res += tasks['data']
        return res

    def get_all_tasks(self):
        projects = self.get_projects()
        project_dict = {x['id']: x['name'] for x in projects}
        res = []
        for x in projects:
            tasks = self.get_tasks(x['id'])
            for t in tasks:
                t['projects'] = [project_dict[x['id']] for x in t['projects']]
            res += tasks
        return res


def main():
    asana = AsanaApi(access_token)

    res = asana.get_all_tasks()

    with open('Asana_{}.csv'.format(datetime.datetime.today().strftime('%Y-%m-%d')), 'w') as csvfile:

        # ToDo: get fieldnames from tasks & sort in special order?
        fieldnames = ['id', 'assignee', 'completed_at', 'created_at', 'due_on', 'modified_at', 'name', 'notes', 'parent', 'projects']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(res)


if __name__ == '__main__':
    main()
