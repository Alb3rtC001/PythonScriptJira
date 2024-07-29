import requests
from requests.auth import HTTPBasicAuth
import json
import datetime
import time
import arrow

#user var
__token = "TOKEN"
__user = "mail"
__pass = "pass"

#Api var
url = "https://admira.atlassian.net/rest/api/3/"
#issue_id = "AP-5442"
#timeSpend_inIssue = "issue/"+ issue_id +"/worklog"
updated_worklog = "worklog/updated" #?since=1682892000
time_tracker = "configuration/timetracking"
workflow = "workflow"
search = "search"
jql = "jql/match"
issue = "issue"

#options var
weekDays = {"Mon" : [0, 4], "Tue": [1, 3], "Wed" : [2, 2], "Thu" : [3, 1], "Fri": [4, 0]}
date = datetime.datetime.now()
today = date.strftime("%a")

startWeek = datetime.datetime(date.year, date.month, date.day - weekDays[today][0])
endsWeek = datetime.datetime(date.year, date.month, date.day + weekDays[today][1])

startWeekStmp = time.mktime(datetime.datetime.strptime(str(startWeek), "%Y-%m-%d %H:%M:%S").timetuple())
endWeekStmp = time.mktime(datetime.datetime.strptime(str(endsWeek), "%Y-%m-%d %H:%M:%S").timetuple())

startTestDate = "2023-05-01"
endTestDate = "2023-05-05"

#En caso de error poner esto al final de la variable [0:10]
#startPrueba = time.mktime(datetime.datetime.strptime("2023-05-8 00:00:00", "%Y-%m-%d %H:%M:%S").timetuple())
#endPrueba = time.mktime(datetime.datetime.strptime("2023-05-12 00:00:00", "%Y-%m-%d %H:%M:%S").timetuple())

#var count hours
time_spend_this_week = 0

#Functions for transforms seconds to date
def format_time(seconds):
minutes, seconds = divmod(seconds, 60)
hours, minutes = divmod(minutes, 60)
time_strings = []
if hours > 0:
time_strings.append(f"{hours} hour{'s' if hours != 1 else ''}")
if minutes > 0:
time_strings.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
if seconds > 0:
time_strings.append(f"{seconds} second{'s' if seconds != 1 else ''}")
if seconds == 0:
time_strings.append(f"{seconds} seconds") 
return ", ".join(time_strings)


#Start app
auth = HTTPBasicAuth(__user, __token)

#str(startWeek)[0:10]
#str(endsWeek)[0:10]

#query
#jql = "project= AP AND updated>=" + startTestDate + " AND updated<=" + endTestDate + " and worklogAuthor = currentUser()"
jql = "project= AP AND updated>=" + "2023-05-15" + " AND updated<=" + "2023-05-19" + " and worklogAuthor = currentUser()"

headers = {
"Accept": "application/json"
#"Content-Type": "application/json"
}

params_gpt = {
"jql": jql,
"maxResults" : 70,
"startAt": 0,
"fileds": "key, summary, updated"
}

response = requests.get(url=url+search, headers=headers, params=params_gpt, auth=auth)
with open("jsonResponse.json", "w") as file:
file.write(response.text)

array_issues_thisWeek = []
print(jql)
try:
#print(json.loads(response.text)["issues"][0])
value = json.loads(response.text)["issues"]
#print(value)
i = 0
for issue in value:
i += 1
#print(str(issue["id"]) + " : ", i)
if(issue["fields"]["assignee"]["displayName"] == "Automation for Jira"):
for subtask in issue["fields"]["subtasks"]:
array_issues_thisWeek.append(subtask["key"])
elif(issue["fields"]["assignee"]["emailAddress"] == __user):
array_issues_thisWeek.append(issue["key"])
if( "parent" in issue["fields"]):
array_issues_thisWeek.append(issue["fields"]["parent"]["key"])
#print(len(issue["fields"]["subtasks"]), issue["key"])
if(len(issue["fields"]["subtasks"]) > 0):
for subtask in issue["fields"]["subtasks"]:
array_issues_thisWeek.append(subtask["key"])
if( "parent" in issue["fields"]):
array_issues_thisWeek.append(issue["fields"]["parent"]["key"])
#print("---------------------")
#print(issue["id"])
#print(issue["key"])
#print(issue["fields"]["assignee"]["emailAddress"])
#print("--------------------")
print(array_issues_thisWeek)
array_issues_thisWeek = list(set(array_issues_thisWeek))
for key_issue in array_issues_thisWeek:
#print(key_issue)
url = "https://admira.atlassian.net/rest/api/3/issue/"+ key_issue
response = requests.request(
"GET",
url,
headers=headers,
auth=auth
)
all_updated = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
#print(all_updated)
#with open("jsonResponse.json", "a") as file:
#file.write(str(all_updated))
all_updated = json.loads(all_updated)["fields"]["worklog"]["worklogs"]
last_change = 0
for time_this_issue in all_updated:
if(time_this_issue["author"]["emailAddress"] == __user):
# "2023-05-08"
# "2023-05-12"
#if((time_this_issue["updated"])[0:10] >= startTestDate and (time_this_issue["updated"])[0:10] <= endTestDate):
if((time_this_issue["updated"])[0:10] >= "2023-05-15" and (time_this_issue["updated"])[0:10] <= "2023-05-19"):
time_spend_this_week += time_this_issue["timeSpentSeconds"]
#print(format_time(time_this_issue["timeSpentSeconds"]))
#print(format_time(time_spend_this_week))
print(format_time(time_spend_this_week))
except Exception as e:
print(e)
