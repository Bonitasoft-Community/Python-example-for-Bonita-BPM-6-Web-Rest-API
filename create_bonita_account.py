#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# Author:   Jérémy Jacquier-Roux
# create_bonita_account.py
#==============================================================================

import argparse
import httplib2
import json
import urllib

#==============================================================================
def portal_login(url,username,password,disable_cert_validation):
    http = httplib2.Http(disable_ssl_certificate_validation=disable_cert_validation)
    API="/loginservice"
    URL=url+API
    body={'username': username, 'password': password, 'redirect': 'false'}
    headers={"Content-type":"application/x-www-form-urlencoded"}
    response, content = http.request(URL,'POST',headers=headers,body=urllib.urlencode(body))
    if response.status!=200:
      raise Exception("HTTP STATUS: "+str(response.status))
    return response['set-cookie']

#==============================================================================
def create_user(url,cookie,username,password,firstname,lastname,disable_cert_validation):
    http = httplib2.Http(disable_ssl_certificate_validation=disable_cert_validation)
    API="/API/identity/user/"
    URL=url+API
    headers={"Content-type":"application/json",'Cookie': cookie}
    data={"userName":username,"password":password,"firstname":firstname,"lastname":lastname, "enabled": "true"}
    data = json.dumps(data)
    response, content = http.request(URL, 'POST',headers=headers, body=data)
    if response.status!=200:
      raise Exception("HTTP STATUS: "+str(response.status)+" "+content)
    else:
      data = json.loads(content)
      return data['id']

#==============================================================================
def get_profile_id(url,cookie,name,disable_cert_validation):
    http = httplib2.Http(disable_ssl_certificate_validation=disable_cert_validation)
    API="/API/userXP/profile"
    params="?f=name="+str(name)
    URL=url+API+params
    headers={"Content-type":"application/x-www-form-urlencoded",'Cookie': cookie}
    response, content = http.request(URL, 'GET',headers=headers)
    data = json.loads(content)
    try:
      return data[0]['id']
    except Exception, e:
      return None

#==============================================================================
def add_user_to_profile(url,cookie,uid,pid,disable_cert_validation):
    http = httplib2.Http(disable_ssl_certificate_validation=disable_cert_validation)
    API="/API/userXP/profileMember/"
    URL=url+API
    headers={"Content-type":"application/json",'Cookie': cookie}
    data={"profile_id":pid,"member_type":"USER","user_id": uid}
    data = json.dumps(data)
    response, content = http.request(URL, 'POST',headers=headers, body=data)
    if response.status!=200:
      raise Exception("HTTP STATUS: "+str(response.status)+" "+content)

#==============================================================================
def main():
    parser = argparse.ArgumentParser(description='Create a Bonita account',
        add_help=False)
    # required arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument("--login",
        required=True,
        help="Account used to authenticate you on Bonita",
        metavar="install")
    required.add_argument("--password",
        required=True,
        help="Password used with your account",
        metavar="install")
    required.add_argument("--url",
        required=True,
        help="Bonita BPM url",
        metavar="http://example.com:8080/bonita")
    required.add_argument("--new_login",
        required=True,
        help="New account that will be created",
        metavar="john.smith")
    required.add_argument("--new_password",
        required=True,
        help="Password used for the new account",
        metavar="mysecret")
    required.add_argument("--firstname",
        required=True,
        help="First name used for the new account",
        metavar="John")
    required.add_argument("--lastname",
        required=True,
        help="Last name used for the new account",
        metavar="Smith")
    # optional arguments
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-h', '--help',
        action='help',
        help="Show this help message and exit")
    optional.add_argument("--disable_ssl_certificate_validation",
        help="Used this only for tests with a self-signed certificate",
        action="store_true")
    optional.add_argument("--is_admin",
        help="Assign user to Administrator profile",
        action="store_true")

    args = parser.parse_args()

    cookie=portal_login(args.url,args.login,args.password,args.disable_ssl_certificate_validation)
    uid=create_user(args.url,cookie,args.new_login,args.new_password,args.firstname,args.lastname,args.disable_ssl_certificate_validation)
    if args.is_admin:
        admin_pid=get_profile_id(args.url,cookie,"Administrator",args.disable_ssl_certificate_validation)
        add_user_to_profile(args.url,cookie,uid,admin_pid,args.disable_ssl_certificate_validation)
    user_pid=get_profile_id(args.url,cookie,"User",args.disable_ssl_certificate_validation)
    add_user_to_profile(args.url,cookie,uid,user_pid,args.disable_ssl_certificate_validation)

#==============================================================================
if __name__ == "__main__":
    main()
