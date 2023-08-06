#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

""" how to use formv with webob """

import os, formv
from formv.configuration import build
from formv.validators import *
from formv.exception import Invalid

from formv.utils import dict_object
from formv.utils.compat import PY2
from formv.utils.fileinfo import BaseFileInfo, ReusedFileInfo 

from tests import multipart
from examples import to_str, setup_mime_types, make_environ as env

from datetime import datetime
from mimetypes import guess_type
from webob import Request, Response

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# configuration is required only if you use validators based on 
# geographic data: countries, currencies, languages, post-codes, 
# latitude, longitude, geo-distance calculation,...

formv.config = build(config_root=os.path.join(app_root, 'tests'))
mime_types = setup_mime_types()

session = dict_object(files=dict_object())
 
class WebForm(VSchema):     
    fields = {         
        'first_name': VString(min_len=3, max_len=50), 
        'last_name': VString(min_len=3, max_len=50), 
        'postcode': VString(), 
        'state': VString(),
        'country': VCountry(required=True, mode='by-name'), 
        'email': VEmail(required=True), 
        'password': VPassword(special_chars=3),
        'file_upload': VPipe(VUploadFile(mime_types=mime_types,
                                         temp_dir='/tmp/formv/test/tmp',), 
                             VWatermarkImage(type='image', 
                                             file=os.path.join(app_root, 'tests/watermarks/copyright.jpg'), 
                                             opacity=.04, angle=45), 
                             VWatermarkImage(text='formv text watermark', angle=25, 
                                             color=(0,0,0,128), opacity=1), 
                             VImprintImage(text='Note the image watermark in the background',  
                                           color=(0,128,128,255)), 
                             VImprintImage(text=datetime.strftime(datetime.utcnow(),  
                                                                  'Uploaded on %Y/%m/%d - %H:%M:%S GMT'), 
                                           color=(255,128,128,255), 
                                           margin=(25,10)), 
                       ) 
    } 

    chains = { 
        'coordinates': VCountryPostcode(country_field='country',     # extracts (latitude, longitude) pair
                                        postcode_field='postcode'),         
        'password': VEncodedPair(required_field='password',          # encodes (password, email) pair
                                 required_label='Password', 
                                 available_field='email'),
        'state': VState(country_field='country',                     # validates state against country
                        state_field='state', mode='by-name'),
    } 
     
class Application(object):
    def __call__(self, environ, start_response):
        self.request = Request(make_environ())  
        response = self.request.get_response(self.response())
        return response(self.request.environ, start_response)
    
    def response(self):
        try:
            form = self.validate(self.request.POST) # - form validation
            body = to_str(form)
        except Invalid as e:
            # - recover successfully uploaded files 
            if isinstance(e.value.get('file_upload'), BaseFileInfo): 
                session.files['file_upload'] = ReusedFileInfo(e.value['file_upload']) 
                                
            body = e.message
            body += '<br/>errors'
            body += to_str(e.errors)
            body += '<br/>values'
            body += to_str(e.value)

        response = Response()                        
        response.text = unicode(body) if PY2 else body
        return response
        
    def validate(self, request): 
        form = WebForm(allow_missing_keys=True, 
                       allow_extra_keys=True, 
                       replace_empty_value=True, 
                       empty_values={ 
                           # inject recovered file back into form if no new file has been uploaded 
                           'file_upload': session.files.get('file_upload'), 
                       }) 
        return form.validate(request) 
            
application = Application()  
     
def make_environ():
    ''' simulates a POST request (multipart/form-data) '''
    
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_files_dir = os.path.join(app_root, 'tests/files')    
    form = []

    # - plain fields
    form.append(multipart.field('first_name', 'John'))
    form.append(multipart.field('last_name', 'Smith'))
    form.append(multipart.field('email', 'dummy@dummy.com'))
    form.append(multipart.field('postcode', '99501'))
    form.append(multipart.field('state', 'Alaska'))
    form.append(multipart.field('country', 'U.S.A.'))
    form.append(multipart.field('password', 'dummy-secret-password-1'))
    
    # - file upload
    f = os.path.join(test_files_dir, 'test.jpg')
    form.append(multipart.file('file_upload', filename=f, 
                               content_type=guess_type(f, False)[0]))            
    return env(*form)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server   
    httpd = make_server('127.0.0.1', 9000, application)
    sn = httpd.socket.getsockname()
    print("Serving HTTP on", sn[0], "port", sn[1], "...")            
    httpd.serve_forever()

        
        
        
