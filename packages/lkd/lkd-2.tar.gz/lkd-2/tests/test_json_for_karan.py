#!/usr/bin/env python

from lkd import lkd

l = lkd('karan')

def test_about_username():
    '''
    Check if the username is karan or not
    '''
    assert l.about()['username'] == 'karan'

def test_about_id():
    '''
    Check if the id is 7092 or not
    '''
    assert l.about()['id'] == '7092'

def test_get_json_about_added():
    '''
    Check if the date added is correct or not
    '''
    assert l.get_json()['about']['added'] == '2013-07-09 08:52:53'

def test_get_json_links_gplus():
    '''
    Check if the g+ link is correct or not
    '''
    assert l.get_json()['links']['google-plus']['url'] == 'https://plus.google.com/u/102240996167520070348'