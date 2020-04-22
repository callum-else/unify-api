
######## AUTHENTICATION MIDDLEWARE SETUP ########

from .db_init import user_loader            
from falcon_auth import JWTAuthBackend

from pem import parse_file

from time import time

# Reading the private key from the certificate file.
p_key = str(
    parse_file("<path-to-private-key>")[0]
)

# Creating the authentication backend needed for Falcon-Auth.
auth_backend = JWTAuthBackend(
    user_loader,                            # Generates a valid user from the jwt payload.
    p_key,                                  # Private key from cert.
    leeway=5,                               # Time in secs before the token is valid (5 secs).
    expiration_delta=(24 * 60 * 60) * 7     # Time in secs before token runs out (1 week).
)

def check_not_expired(epoch):
    curr_time = int(time())
    if(curr_time < epoch):
        return True
    return False

######## ACCOUNT VERIFICATION ########

from requests import post
from random import randint
import re

# Setup data for email sending api.
post_url = "https://api.sendgrid.com/v3/mail/send"
sender_email = "noreply@unifyapp.xyz"
verif_template_id = "d-56a8b2d3ff2a484da7e2ea6d3a074aab"
password_template_id = "d-675d47f3ac8d4867870c1745c02757cb"
auth = "Bearer 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"

# Generates a verification code string from 6 numbers.
def generate_verification_code():
    code = ""
    for i in range(6):
        code += str(randint(0,9))
    return code

# Tests email against RegEx string.
def check_valid_email(email):
    if re.search('[\S]+@[\S]+\.ac\.uk', email):
        return True
    return False

# Sending a post request to the emailing API. 
# Uses custom template stored on API for email format.
# Sends the email, user's name and verif code in the email.
def send_verification_email(email, username, code):
    res = post(
        post_url,
        json={
            "from": {"email":sender_email},
            "personalizations":[{
                "to":[{"email":email}],
                "dynamic_template_data":{
                    "email":email,
                    "username":username,
                    "code":code
                }
            }],
            "template_id":verif_template_id
        },
        headers={
            'Authorization':auth, 
            'Content-Type':'application/json'
        }
    )

def send_change_password_email(email, username, code):
    res = post(
        post_url,
        json={
            "from": {"email":sender_email},
            "personalizations":[{
                "to":[{"email":email}],
                "dynamic_template_data":{
                    "email":email,
                    "username":username,
                    "code":code
                }
            }],
            "template_id":password_template_id
        },
        headers={
            'Authorization':auth, 
            'Content-Type':'application/json'
        }
    )

    print(res.status_code)

######## IMAGE PROCESSING ########

from os.path import join, exists

uuid_format = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'

def validate_image_request(storage_path, file_name, ignore_check=False):
    if ignore_check or re.search(uuid_format, file_name):
        file_path = join(storage_path, file_name)
        if exists(file_path):
            return file_path
    return None