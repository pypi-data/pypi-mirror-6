"""
Python wrapper for lkd.to API.

@author Karan Goel
@email karan@goel.im

The MIT License (MIT)
Copyright (c) 2013 Karan Goel
 
Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests

class lkd(object):
    def __init__(self, user):
        """
        Initialize a new lkd object for the passed user.
        """
        self.user = user
        self.data = self.get_json()
        if self.data['about'] == False:
            raise Exception('Invalid username.')
        
    def get_json(self):
        """
        Returns the json response for the user.
        """
        url = 'http://lkd.to/api/' + self.user
        response = requests.get(url)
        return response.json()

    def about(self):
        """
        Returns a dictionary with details about the user. Contains:
        id, username, email, realname, bio, status, added, updated,
        theme
        """
        return self.data['about']

    def links(self):
        """
        Returns a dictionary with user's social links
        """
        links = {}
        data = self.data['links']
        for key in data:
            links[key] = data[key]['url']
        return links

    def vcf(self):
        """
        Downloads the vcf card for the user in current directory.
        """
        name = self.user + '.vcf'
        url = 'http://lkd.to/api/' + name
        r = requests.get(url)
        with open(name, 'wb') as code:
            code.write(r.content)
