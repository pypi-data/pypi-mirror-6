# Converted from IAM_Policies_SNS_Publish_To_SQS.template located at:
# http://aws.amazon.com/cloudformation/aws-cloudformation-templates/

from troposphere import GetAtt, Output, Ref, Template
from troposphere.sns import Subscription, Topic
from troposphere.sqs import Queue, QueuePolicy

try:
    from awacs.aws import Policy
except:
    import sys
    print("awacs is needed for this test")
    try:
        sys.exit(0)
    except:
        pass


t = Template()

t.add_description("AWS CloudFormation Sample Template: This template "
                  "demonstrates the creation of a DynamoDB table.")

sqsqueue = t.add_resource(Queue("SQSQueue"))

snstopic = t.add_resource(Topic(
    "SNSTopic",
    Subscription=[Subscription(
        Protocol="sqs",
        Endpoint=GetAtt(sqsqueue, "Arn")
    )]
))

t.add_output(Output(
    "QueueArn",
    Value=GetAtt(sqsqueue, "Arn"),
    Description="ARN of SQS Queue",
))

from awacs.aws import Allow, ArnEquals, Condition, Statement, AWSPrincipal
import awacs.sqs as sqs
t.add_resource(QueuePolicy(
    "AllowSNS2SQSPolicy",
    Queues=[Ref(sqsqueue)],
    PolicyDocument=Policy(
        Version="2008-10-17",
        Id="PublicationPolicy",
        Statement=[Statement(
            Sid="Allow-SNS-SendMessage",
            Effect=Allow,
            Principal=[AWSPrincipal("*")],
            Action=[sqs.SendMessage],
            Resource=[GetAtt(sqsqueue, "Arn")],
            Condition=Condition(
                ArnEquals("aws:SourceArn", Ref(snstopic)),
            )
        )],
    )
))

print(t.to_json())
