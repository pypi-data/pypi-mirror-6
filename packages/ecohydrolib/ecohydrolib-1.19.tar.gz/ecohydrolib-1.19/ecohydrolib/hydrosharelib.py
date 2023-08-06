"""@package ecohydrolib.hydrosharelib
    
@brief Task-oriented API to HydroShare REST API

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2014, University of North Carolina at Chapel Hill
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the University of North Carolina at Chapel Hill nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF NORTH CAROLINA AT CHAPEL HILL
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


@author Brian Miles <brian_miles@unc.edu>
"""
import httplib
import json


class HydroShareRequestException(Exception):
    def __init__(self, hydroShareLib, response, url, msg):
        # Reconstruct URL
        if hydroShareLib.https:
            myUrl = 'https://'
        else:
            myUrl = 'http://'
        myUrl += url
        
        status = "%d %s" % (response.status, response.reason)
        
        self.msg = "%s. Response from server was %s for URL %s" % (msg, status, myURL)
    def __str__(self):
        return repr(self.msg)


class HydroShareLib(object):
    
    HOST = 'dev.hydroshare.org'
    URL_BASE = '?q=my_services'
    
    URLS = {'connect': 'system/connect.json',
            'login': 'user/login.json',
            'logout': 'user/logout.json',
            'node': 'node.json',
            'file': 'file.json',
            }
    
    def _connect(self):
        url = self.urlBase + '/' + HydroShareLib.URLS["connect"]
        if self.apiKey:
            url += '&api-key=' + str(self.apiKey)
            
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if self.https:
            conn = httplib.HTTPSConnection(self.host)
        else:
            conn = httplib.HTTPConnection(self.host)
        try:
            conn.request('POST', url, headers=headers)
            response = conn.getresponse()
        except socket.error as e:
            raise e
        
        if 200 != response.status:
            raise HydroShareRequestException(self, response, url,
                                             "Unable to connect HydroShare")
    
        contentType = response.getheader('Content-Type')
        if contentType != 'application/json':
            raise HydroShareRequestException(self, response, url,
                                             "Unexpected content type %s" % (contentType,) )
            
        session = json.loads(response.read())
        
        return (conn, session)
        
    def __init__(self, apiKey=None, https=False):
        """ Task-oriented API to HydroShare REST API
        
        Args:
            apiKey (str): Optional API-key to use for HydroShare REST API
            https (boolean): Controls whether connections should be made using HTTPS
        
        >>> with HydroShareLib(apiKey='122d86f') as hsl:
            hsl.sessionID
        
        Will automatically close HTTP connection.
        """
        self.apiKey = apiKey
        self.https = https

        self.host = HydroShareLib.HOST
        self.urlBase = HydroShareLib.URL_BASE
        
        # Connect to get session ID
        (self.connection, self.session) = self._connect()
        self.sessionID = self.session['sessid']
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.connection.close()
        
    def createModel(self):
        """
        
        """
        

