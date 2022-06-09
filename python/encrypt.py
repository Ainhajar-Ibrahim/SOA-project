import os
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog
import cv2
import numpy as np
import math
import string
import random
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
key=id_generator()

def stegano(direction):
    path="D:\SOA Project\python\img\img.jpg"
    load_image = Image.open(path)
    np_load_image = np.asarray(load_image)
    np_load_image = Image.fromarray(np.uint8(np_load_image))
        # Step 2
    data =key
    # load the image
    img = cv2.imread(path)
    # break the image into its character level. Represent the characyers in ASCII.
    data = [format(ord(i), '08b') for i in data]
    _, width, _ = img.shape
    # algorithm to encode the image
    PixReq = len(data) * 3

    RowReq = PixReq/width
    RowReq = math.ceil(RowReq)

    count = 0
    charCount = 0
    # Step 3
    for i in range(RowReq + 1):
        # Step 4
        while(count < width and charCount < len(data)):
            char = data[charCount]
            charCount += 1
            # Step 5
            for index_k, k in enumerate(char):
                if((k == '1' and img[i][count][index_k % 3] % 2 == 0) or (k == '0' and img[i][count][index_k % 3] % 2 == 1)):
                    img[i][count][index_k % 3] -= 1
                if(index_k % 3 == 2):
                    count += 1
                if(index_k == 7):
                    if(charCount*3 < PixReq and img[i][count][2] % 2 == 1):
                        img[i][count][2] -= 1
                    if(charCount*3 >= PixReq and img[i][count][2] % 2 == 0):
                        img[i][count][2] -= 1
                    count += 1
        count = 0
    # Step 6
    # Write the encrypted image into a new file
    cv2.imwrite(direction+".png", img)

def create_multipart_message(
        sender: str, recipients: list, title: str, text: str=None, html: str=None, attachments: list=None)\
        -> MIMEMultipart:

    multipart_content_subtype = 'alternative' if text and html else 'mixed'
    msg = MIMEMultipart(multipart_content_subtype)
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    mypath=""
    # Record the MIME types of both parts - text/plain and text/html.
    # According to RFC 2046, the last part of a multipart message, in this case the HTML message, is best and preferred.
    if text:
        part = MIMEText(text, 'plain')
        msg.attach(part)
    if html:
        part = MIMEText(html, 'html')
        msg.attach(part)

    # Add attachments
    for attachment in attachments or []:
        mypath=id_generator()
        stegano('D:/SOA Project/python/img/'+mypath)
        with open('D:/SOA Project/python/img/'+mypath+".png", 'rb') as f:
            part = MIMEApplication(f.read())
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename('./'+mypath+".png"))
            msg.attach(part)
        os.remove('D:/SOA Project/python/img/'+mypath+".png")
    return msg


def send_mail(
        sender: str, recipients: list, title: str, text: str=None, html: str=None, attachments: list=None) -> dict:
    """
    Send email to recipients. Sends one mail to all recipients.
    The sender needs to be a verified email in SES.
    """
    msg = create_multipart_message(sender, recipients, title, text, html, attachments)
    ses_client = boto3.client('ses',region_name="eu-west-3",    aws_access_key_id="secret",
    aws_secret_access_key="secret")
     # Use your settings here
    return ses_client.send_raw_email(
        Source=sender,
        Destinations=recipients,
        RawMessage={'Data': msg.as_string()}
    )


sender_ = "abdrrahim.elhimmer@gmail.com"
recipients_ = ["abdrrahimelhimer@gmail.com"]
title_ = 'A beautiful day'
text_ = 'Art is the earliest form of encryption.'
body_ = """<html><head></head><body><h1></h1><br>."""
attachments_ = ['./images/krystian-dulnik-1-00023.jpg']
response_ = send_mail(sender_, recipients_, title_, text_, body_, attachments_)
print(response_)


print(key)
encoded=key.encode()
result = hashlib.sha256(encoded)
hexa=result.hexdigest()
print(hexa)
f = open("D:\SOA Project\encrypt_app\src\components\keycheck.js", "w")
f.write("""import React from 'react';\nexport const hashed_key="%s";\nconst KEYCHECK = props => <h1>Home</h1>;\nexport default KEYCHECK;"""%hexa)
f.close()
cred = credentials.Certificate('D:\SOA Project\python\chat-encrypt-firebase-adminsdk-4eh85-bad7c2d93d.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
doc=db.collection(u'messages')
st=doc.stream()
for i in st:
    doc.document(i.id).delete()