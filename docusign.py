import json
import sys
import requests

import urllib
import urllib2

#enter your info:
templateId = "c98a7ff4-9d1e-47e8-8358-346a57af1a66"

DOCUSIGN_USERNAME = '94a312bd-7654-4a97-9953-ad0463ac9734'
DOCUSIGN_KEY = 'DEVE-36b01693-4a89-48e6-9cb9-f8c2467c924c'
DOCUSIGN_PASSWORD = 'soulvest_dev'

authenticateStr = "<DocuSignCredentials>" \
                    "<Username>" + DOCUSIGN_USERNAME + "</Username>" \
                    "<Password>" + DOCUSIGN_PASSWORD + "</Password>" \
                    "<IntegratorKey>" + DOCUSIGN_KEY + "</IntegratorKey>" \
                    "</DocuSignCredentials>"

# login and get base url and account id
def docusign_login():
  url = 'https://demo.docusign.net/restapi/v2/login_information'
  headers = {'X-DocuSign-Authentication': authenticateStr, 'Accept': 'application/json'}

  r = requests.get(url, headers=headers)

  if r.status_code != 200:
    print("Error calling webservice, status is: %s" % r.status_code); sys.exit()

  # get the baseUrl and accountId from the response body
  data = json.loads(r.text)
  loginInfo = data.get('loginAccounts')
  D = loginInfo[0]
  baseUrl = D['baseUrl']
  accountId = D['accountId']
  return baseUrl, accountId

# construct the JSON body for our enevelop creation request
def make_docusign_envelope_request_body(account_id, username, user_email, user_id):
  return json.dumps({
    "accountId": account_id,
    "status": "sent",
    "emailSubject": "Soulvest acocunt setup",
    "emailBlurb": "Soulvest account setup",
    "templateId": templateId,
    "templateRoles": [
      {
        "email": user_email,
        "name": username,
        "roleName": "FirstSigner",
        "clientUserId": user_id
      }
    ]
  })

# create an envelop for this user
def get_docusign_envelope_uri(account_id, base_url, username, user_email, user_id):
  # append "/envelopes" to baseURL and use in the request
  url = base_url + "/envelopes"

  requestBody = make_docusign_envelope_request_body(account_id, username, user_email, user_id)

  headers = {
    'X-DocuSign-Authentication': authenticateStr,
    'Content-Type': 'application/json',
    'Content-Length': len(requestBody)}
  try:
    req = urllib2.Request(url, requestBody, headers)
    response = urllib2.urlopen(req)
    data = json.loads(response.read())
    uri = data.get('uri')
    return uri
  except urllib2.HTTPError as e:
    print e.code
    print e.read()

# construct the JSON body for our (iframe) envelop view for this user
def make_embedded_view_request_body(username, user_email, user_id):
  return json.dumps({
      "authenticationMethod": "email",
      "email": user_email,
      "returnUrl": "http://www.docusign.com",
      "clientUserId": user_id,
      "userName": username})

# get the URL for the envelop for this user
def get_embedded_docusign_send_view(username, user_email, user_id):

  # login and get base url for subsequent requests
  base_url, account_id = docusign_login()

  # get envelop uri
  uri = get_docusign_envelope_uri(account_id, base_url, username, user_email, user_id)

  print uri

  requestBody = make_embedded_view_request_body(username, user_email, user_id)

  # append uri + "/views/recipient" to baseUrl and use in the request
  url = base_url + uri + "/views/recipient"
  headers = {
    'X-DocuSign-Authentication': authenticateStr,
    'Content-Type': 'application/json',
    'Content-Length': len(requestBody)}

  try:
    req = urllib2.Request(url, requestBody, headers)
    response = urllib2.urlopen(req)
    data = json.loads(response.read())
    view_url = data.get('url')
    return view_url
  except urllib2.HTTPError as e:
    print e.code
    print e.read()


if __name__ == "__main__":
  view_url = get_embedded_docusign_send_view("John Doe", "jefflutzenberger@gmail.com", 1)
  print ("View URL = %s\n" % view_url)
