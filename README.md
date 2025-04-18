# VDI Studios
![VDI](/aws_cdk_architecture_for_vdi.png)

## HLD
The project uses AWS CDK and python to create the [Stack](cdk/disney_stack.py) for this workflow.
1. API Gateway
2. Lambda function to authorize the webhook (don't believe a Lambda Authorizer fits with how Jira webhook sends a signed signature).  This function will integrate with SQS
3. AWS Step functions will work the SQS queue.  Rough POC
   1. Prep the data from SQS 
   2. Jira can retry requests using header field X-Atlassian-Webhook-Identifier
   3. Store necessary data in Aurora RDS (Postgres)
   4. Integrate with Jira to update status and comments
   5. Integrate with Secrets Manager 
   6. Integrate with Leostream specifics, may be good to expand the VDI.Update function into it's own state machine to orchestrate all the Leostream api calls
   7. In Step 2, assuming that we need to run an ec2 instance to add Leostream.  As part of that the python script will send the run instance with a user data and the provide ansible scripts:
[create ec2](lambda/step_function/create_ec2.py)
![Step Function Main](/stepfunctions_graph.png)

## Using the REST API: Registration

Can register jira webhook either the jira admin or via jira rest api during cdk deploy

POST /rest/api/3/webhook
To register webhooks through the REST API, make a POST request to https://your-domain.atlassian.net/rest/api/2/webhook. The registered URL must use the same base URL as the app. An example request body is shown below:
```markdown
{
  "name": "my first webhook via rest",
  "description": "description of my first webhook",
  "url": "https://www.example.com/webhooks",
  "events": [
    "jira:issue_created",
    "jira:issue_updated"
  ],
  "filters": {
    "issue-related-events-section": "Project = JRA AND resolution = Fixed"
  },
  "excludeBody" : false,
  "secret" : "G8j4166a5OkXRD4WbqV3"
}
```

Jira will use your secret token to create a HMAC signature and include it in a X-Hub-Signature header, formatted as method=signature, as defined by WebSub.
See [jira_authorizer](lambda/auth/jira_authorizer.py)

[Sample webhook payload](jira_webhook.txt)

Basic url format
   http://localhost:8080/rest/api/2/issue/QA-31

With PAT (personal access token)
```markdown
curl -H "Authorization: Bearer <yourToken>" https://{baseUrlOfYourInstance}/rest/api/content

```
Update an issue
```markdown
{
    "fields" : {
        "summary": "Summary",
        "description": "Description",
        "customfield_10200" : "Test 1",
        "customfield_10201" : "Value 1"
    }
}
```


```markdown
Add comment with update format
{
   "update": {
   "description": [
         {
            "set": "JIRA should also come with a free pony"
         }
      ],
      "comment": [
         {
            "add": {
               "body": "This request was originally written in French, which most of our developers can't read"
            }
         }
      ]
   }
}
```


# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
