import boto3
import sys

mturk = boto3.client(
    service_name="mturk",
    region_name="us-east-1",
    endpoint_url="https://mturk-requester-sandbox.us-east-1.amazonaws.com",
)

try:
    task_url = sys.argv[1]
except:
    task_url = "https://csb-uwb5h.netlify.com"

response = mturk.create_hit(
    MaxAssignments=1,
    AutoApprovalDelayInSeconds=600,
    LifetimeInSeconds=600,
    AssignmentDurationInSeconds=600,
    Reward="0.5",
    Title="This is a sample HIT created from Python",
    Keywords="sample, HIT, python",
    Description="No action needs to be taken here",
    Question="""<?xml version="1.0" encoding="UTF-8"?>
<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">
  <ExternalURL>{0}</ExternalURL>
  <FrameHeight>0</FrameHeight>
</ExternalQuestion>""".format(
        task_url
    ),
)


print(response)
