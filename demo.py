#Demo project for TPM position at Google.
#Author: Jose F. Medrano
#date: March, 2023

#This project is heavily based on the code by Sebastian Opałczyński
#https://levelup.gitconnected.com/write-your-tools-simple-jira-automation-c0421aaf6ec

#Other useful sources are: 
#https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
#https://realpython.com/python-requests/
#https://realpython.com/python-f-strings/
#https://scripteverything.com/python-inline-for-loop-with-if-statements/
#https://stackoverflow.com/questions/49764843/jira-api-error-operation-value-must-be-a-string-trying-to-set-value-neste
#https://developer.atlassian.com/server/jira/platform/updating-an-issue-via-the-jira-rest-apis-6848604/
#https://www.codecademy.com/forum_questions/509f1eaedc99f2a6050000c0
#https://support.atlassian.com/cloud-automation/docs/convert-usernames-to-account-ids/
#https://pyyaml.org/wiki/PyYAMLDocumentation
#https://pynative.com/python-yaml/
#https://stackoverflow.com/questions/27146477/how-to-update-issue-status-as-done-through-rest-api
#https://community.developer.atlassian.com/t/not-able-to-update-the-custom-field-on-jira-issues/53521/6
#https://stackoverflow.com/questions/25016301/class-requests-models-response-to-json
#https://docs.pytest.org/en/7.2.x/getting-started.html#get-started
#https://stackoverflow.com/questions/49433234/how-to-import-function-in-pytest
#https://www.educative.io/answers/what-is-http-response-in-python
#https://medium.com/@novyludek/custom-status-code-matcher-for-api-testing-in-python-with-pyhamcrest-43183d65475d
#https://www.mygreatlearning.com/blog/readme-file/#:~:text=readme%20file%20is.-,What%20is%20a%20README%20File%3F,about%20the%20patches%20or%20updates.

import json, requests, config, yaml
from requests.auth import HTTPBasicAuth

print(config.Variables["EMAIL"])

#CONFIGURATION VARIABLES
PROJECT_KEY = config.Variables["PROJECT_KEY"]
API_TOKEN = config.Variables["API_TOKEN"]
BASE_URL = config.Variables["BASE_URL"]
EMAIL = config.Variables["EMAIL"]
CONFIG_DICT = {
  "PROJECT_KEY":PROJECT_KEY,
  "API_TOKEN" : API_TOKEN,
  "BASE_URL" : BASE_URL,
  "EMAIL" : EMAIL,
  "HEADERS" : {'Content-Type': 'application/json','Accept': 'application/json'},
  "NO_CHECK_HEADERS" : {"Accept": "application/json", "X-Atlassian-Token": "no-check"},
  "AUTH" : HTTPBasicAuth(EMAIL, API_TOKEN)
  }

#projectInfo returns a dictionary with PROJECT_ID and ISSUE_TYPE_TASK
def projectInfo():
  #Project ID
  response = requests.get(
      f"{BASE_URL}/rest/api/3/project/{CONFIG_DICT['PROJECT_KEY']}",
      headers=CONFIG_DICT['HEADERS'],
      auth=CONFIG_DICT['AUTH'],
  )
  project_id = response.json()["id"]

  #Project Issue Types
  response = requests.get(
      f"{BASE_URL}/rest/api/3/issuetype",
      headers=CONFIG_DICT['HEADERS'],
      auth=CONFIG_DICT['AUTH']
  )
  issues_types = response.json()
  
  #print("From all of the issues that are tasks, give me just the first one. (Because there should only be one). And we need it's id number.")
  issue_type_task = [issue_type for issue_type in issues_types if issue_type["name"] == "Task"][0]
  
  project_info = {"PROJECT_ID":project_id,"ISSUE_TYPE_TASK":issue_type_task}
  return project_info


def assignIssue(issue_id, account_id):
  #Assigning Issue to Me
  payload = json.dumps( {
    "accountId": "63ff76d80e0ddcdce18cb2c7"
  } )

  response = requests.put(
      f"{BASE_URL}/rest/api/3/issue/{issue_id.upper()}/assignee",
      headers=CONFIG_DICT['HEADERS'],
      auth=CONFIG_DICT['AUTH'],
      data=payload
  )

  print(response)
  return response

def addComment(issue_id,comment):
  #Adding Comment
  print("------------------------------------------------")
  print("Add Comment")

  payload = json.dumps( {
    "body": {
      "content": [
        {
          "content": [
            {
              "text": "Nuevo comentario.",
              "type": "text"
            }
          ],
          "type": "paragraph"
        }
      ],
      "type": "doc",
      "version": 1
    }
  } )


  response = requests.post(
      f"{BASE_URL}/rest/api/3/issue/AD-1/comment",
      headers=CONFIG_DICT['HEADERS'],
      auth=CONFIG_DICT['AUTH'],
      data=payload
  )

  print(response)
  print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

def addAttachment(issue_id,filename):
  #Add Attachment
  print("------------------------------------------------")
  print("Attachment")

  payload = json.dumps( {
    "accountId": "63ff76d80e0ddcdce18cb2c7"
  } )

  response = requests.post(
      f"{BASE_URL}/rest/api/3/issue/AD-1/attachments",
      headers=CONFIG_DICT["NO_CHECK_HEADERS"],
      auth=CONFIG_DICT['AUTH'], 
      files = {
          "file": ("python-write-to-files.png", open("./python-write-to-files.png","rb"), "application-type")
      }
  )

  print(response)
  print(response.text)

#----------- DATA FUNCTIONS AND FORMATS ------------------
def create_task_content(task):
    content = [{
        "type": "paragraph",
        "content": [
            {
                "text": "Tasks",
                "type": "text"
            }
        ]
    }]
    tasks = [
        {'type': 'listItem',
         'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': item}]}]}
        for item in task["tasks"]
    ]
    content.append({'type': 'bulletList', 'content': tasks})
    content.append({
        "type": "paragraph",
        "content": [
            {
                "text": "Definition of Done",
                "type": "text"
            }
        ]
    })
    dod = [
        {'type': 'listItem',
         'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': item}]}]}
        for item in task["dod"]
    ]
    content.append({'type': 'bulletList', 'content': dod})
    return content

def createIssueData(task_data,issue_type_task,project_id):
  issueData = {
      "update": {},
      "fields": {
          "summary": task_data["title"],
          "issuetype": {
              "id": issue_type_task["id"]
          },
          "project": {
              "id": project_id
          },
          "description": {
              'version': 1,
              'type': 'doc',
              'content': create_task_content(task_data)
          },
      }
  }
  return issueData

#END OF----------- DATA FUNCTIONS AND FORMATS ------------------

#----------- UPDATE AND CREATE API CALLS   ------------------
def updateIssue(issue_data, issue_id):
  response = requests.put(
  #response = requests.post(
    f"{BASE_URL}/rest/api/3/issue/{issue_id}/",
    #f"{BASE_URL}/rest/api/3/issue/{issue_id}/transition/",
    headers=CONFIG_DICT['HEADERS'],
    auth=CONFIG_DICT['AUTH'],
    data=json.dumps(issue_data)
    )
  return response

def createIssue(issue_data):
  response = requests.post(
    f"{BASE_URL}/rest/api/3/issue",
    headers=CONFIG_DICT['HEADERS'],
    auth=CONFIG_DICT['AUTH'],
    data=json.dumps(issue_data)
  )
  print(response.json())
  return response
#END OF----------- UPDATE AND CREATE API CALLS ------------------

#//// MAIN PROGRAM ////
print("Read SEPARATE TASKS from file")
print("------------------------------------------------")

list_of_tasks = []

#Reading tasks from file
with open("separatetasksfile.yml","r") as f:
    list_of_tasks = list(yaml.safe_load_all(f))
    print(list_of_tasks)

PROJECT_INFO = projectInfo()

for task_data in list_of_tasks:
  print("Task:")
  print(task_data)

  issue_data = createIssueData(task_data,PROJECT_INFO['ISSUE_TYPE_TASK'],PROJECT_INFO['PROJECT_ID'])
  issue_id = "" 
  if ("ID" in task_data): 
      issue_id = task_data["ID"]
  elif ("id" in task_data): 
      issue_id = task_data["id"]
  elif ("iD" in task_data): 
      issue_id = task_data["iD"]
  elif ("Id" in task_data):
      issue_id = task_data["Id"]
  
  else:
      #New task then Create task
      print("Creating task...")
      response = createIssue(issue_data)
      print(response)      
  
  if ( ("ID" in task_data) or ("id" in task_data) or ("iD" in task_data) or ("Id" in task_data) ):
    #Task ID was found then...
    print("Updating Task...")
    response = updateIssue(issue_data, issue_id)
    print(response) 

#//// END OF MAIN PROGRAM ////

print(assignIssue("AD-95", "1"))