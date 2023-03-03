import json
import os.path
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
aws_region = 'us=east-1'
s3_client = boto3.client("s3")
ses_client = boto3.client("ses", region_name="us-east-1")

def lambda_handler(event, context):
    s3_response = event["Records"][0]["s3"]
    bucket = str(s3_response["bucket"]["name"])
    key = str(s3_response["object"]["key"])
    print(key)
    attachment_path = "/tmp/" + os.path.basename(key)
    print(attachment_path)
    try:
        s3_client.download_file(bucket, key, attachment_path)
        print('File Downloaded, Sending mail')
        response = send_email(attachment_path)
        print(response)
    except Exception as e:
        print(e)
    
    return

def send_email(file_name):
    # The email body for recipients with non-HTML email clients.
    sender = 'makhtar.pucit@gmail.com'
    recipient = 'ajmal.umair@outlook.com'
    subject = 'Athena query result'
    body_text = "Hello,\r\nPlease find the attached file."
    body_html = """\
    <html>
    <head></head>
    <body>
    <h1>Hello!</h1>
    <p>Please find the attached file.</p>
    </body>
    </html>
    """
    charset = "utf-8"
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject 
    msg['From'] = sender 
    msg['To'] = recipient
    msg_body = MIMEMultipart('alternative')
    textpart = MIMEText(body_text.encode(charset), 'plain', charset)
    htmlpart = MIMEText(body_html.encode(charset), 'html', charset)
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    attachment = MIMEApplication(open(file_name, 'rb').read())
    attachment_name = file_name.split('/')[-1]
    attachment.add_header('Content-Disposition','attachment',filename=attachment_name)
    if os.path.exists(file_name):
        print("File exists")
    else:
        print("File does not exists")
    msg.attach(msg_body)
    msg.attach(attachment)
    try:
        response = ses_client.send_raw_email(
            Source=msg['From'],
            Destinations=[
                msg['To']
            ],
            RawMessage={
                'Data':msg.as_string(),
            }
        )
    except ClientError as e:
        return(e.response['Error']['Message'])
    else:
        return("Email sent! Message ID:", response['MessageId'])
