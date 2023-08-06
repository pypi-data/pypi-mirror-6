# -*- coding: utf-8 -*-

from eve import Eve
from eve.io.mongo import Validator
from eve.auth import BasicAuth, TokenAuth, HMACAuth
from hashlib import sha1
import hmac
from flask import request
from redis import Redis

redis = Redis()

class TAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        return token == 'token'

class Auth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        #print "username", username
        self.request_auth_value = username
        return username == 'token'
        #return username == 'admin' and password == 'secret'


class Validator(Validator):
    def _validate_msg_limit(self, msg_limit, field, value):
        pass
        #print msg_limit, field, value

def getting_contatti(documents):
    print ("contatti")
    print (documents)

def getting(resource, documents):
    print ("getting %s" % resource)
    #del(documents[0]['etag'])
    documents[0]['name']="RIFATTO"
    documents[0]['newfield'] = " NEW FIELD YOU FOOL "

def gotit(resource, request, response=None):

    print ('get', resource)
    print (request)
    print (response)

def resource_gotit(request, response):
    print ('get_contacts')
    print (request.data)
    print (response.data)

def resource_post(resource, request, response):
    print response.get_data()
    pass
    #print resource
    ##print (request.authorization)
    #print request.get_data()
    #print response.get_data()

def posting(documents):
    #print ("posting to ", resource)
    #documents[0]["token"] = "mytoken"
    #from flask import request
    #print "usr", request.authorization.username
    print documents

def posting_r(documents):
    print ("posting to resource contacts")


app = Eve(auth=Auth, validator=Validator, redis=redis)

#@app.route('/test')
#def hello_world():
#    return 'Hello World'
#app.config['DOMAIN']['contacts']['auth_username_field'] = 'name'
#app.on_get_contacts += resource_gotit
#app.on_get += gotit
#app.on_pre_GET += getting
#app.on_posting += posting
#app.on_posting_contacts += posting_r
#app.on_fetch_resource += getting
app.on_insert_contacts += posting
#app.on_getting_contacts += getting_contatti
#app.on_post_POST += resource_post

if __name__ == '__main__':
    #app.events.on_getting += pre
    #app.on_GET += gotit
    #app.on_post_POST += resource_post
    app.run(debug=True)
