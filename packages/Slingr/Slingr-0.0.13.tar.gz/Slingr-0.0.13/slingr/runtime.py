# -*- coding: utf-8 -*-

"""Slingr Runtime"""

from __future__ import print_function, unicode_literals

from ua_parser import user_agent_parser
import pystache
from flask import request
from ua_parser import user_agent_parser

from slingr import app, ospath

__all__ = (
    "cob_page",
    "find_page",
    "process_page",
    )

def profileParser(ua, request, pathParams):
    # TODO: allow this to be overridden in a Cob
    if ua['user_agent']['family'] == "IE" and float(ua['user_agent']['major']) <= 7:
        profileName = 'legacyWeb'
    elif ua['user_agent']['family'] == "Chrome":
        profileName = 'chromeWeb'
    else:
        profileName = 'modernWeb'
    return profileName

def processLang(lang):
    if 'fr;' in lang:
        currLang = 'fr'
    else:
        currLang = 'en'

    #do checks and assign normalized lang shorthand ####################################
    return currLang

def parseLang(root, value, lang, location, loc):
    #parse lang to string
    def parseFile(root, *configPath):
        # Total hack. Return hardcoded values that make the page "work"
        return {
            "head": {"title": "Tytle"},
            "nav": {"lang": {"value": "this is in nav"}}
        }

    def parseLangKeys(keyString, langJson):
        result = langJson
        for splitKey in keyString.split('.'):
            result = result[splitKey]

        return result

    if location:
        langJson = parseFile(root, location, 'lang', lang, loc['lang'])
    else:
        langJson = parseFile(root, 'lang', lang, loc['lang'])

    if not langJson:
        app.logger.error('badly formed path in parseLang')
    else:
        return parseLangKeys(value, langJson)

class Profile(object):
    def __init__(self, name, ua, path, params, lang, built_page):
        self.name, self.ua, self.path, self.params, self.lang, self.built_page = (
            name, ua, path, params, lang, built_page)

    def __repr__(self):
        return "<%s name=%r, ua=%r, path=%r, params=%r, lang=%r, built_page=%r>" % (
            self.__class__.__name__,
            self.name, self.ua, self.path, self.params, self.lang, self.built_page)

def match_page_profile(page_name, profile_name):
    built_page = app.build.cobstate.pages[page_name]
    # TODO: better fallback if no matching profile
    built_page = built_page.get(profile_name) or built_page.values()[0]
    built_page = app.build.revalidate_page(built_page)
    return built_page


class View(object):
    def __init__(self, root_dir, profile, built_view):
        self.root_dir = root_dir
        self.profile = profile
        self.built_view = built_view
        self.name = built_view.name

    def __repr__(self):
        return "<%s name=%r, root_dir=%r, profile=%r, name=%r>" % (
                self.__class__.__name__,
                self.root_dir, self.profile, self.built_view.name)

    def get_html(self, fileName=False):
        #TODO: expand this able to access all html files using standard accessor,
        # instead of just local files
        return self.built_view.html.templates and self.built_view.html.templates[0]

    def get_lang(self, langObj=False):
        #TODO: this isn't very efficient, as it parses the file again for every value
        fileName = langObj.get('lang', self.name)
        location = False if 'location' in langObj else self.location

        return parseLang(
            self.root_dir,
            langObj['value'],
            fileName,
            location,
            {'lang': self.profile.lang}
        )

    def render(self, template, content=False):
        if content is False:
            content = template
            template = None
        viewTemplate = self.get_html(template)

        return viewTemplate and pystache.render(viewTemplate.data, content)

class Page(object):
    def __init__(self, root_dir, profile, built_page, views):
        self.root_dir = root_dir
        self.profile = profile
        self.built_page = built_page
        self.name = built_page.name
        self.views = views

    def __repr__(self):
        return "<%s root_dir=%r, profile=%r, name=%r>" % (
            self.__class__.__name__,
            self.root_dir, self.profile, self.name)

    def get_index(self):
        return self.profile.built_page.index_page.content

    def get_lang(self, langObj):
        return parseLang(
            self.root_dir,
            langObj['value'],
            self.name,
            ospath.join('pages', self.name),
            {'lang' : self.profile.lang}
        )

    def render(self, content, options={}):
        if isinstance(content, dict):
            self.baseTemplate = self.get_index()
            return pystache.render(self.baseTemplate, content)
        elif isinstance(content, basestring):
            return content
        else:
            return 'Page Error: content is not object or string'

def cob_page(page):
    """Default controller for pages"""
    pageContent = {
        'title':   page.profile.name + ' Home Page', # FIXME
        'content': page.get_lang({'value' : 'head.title'})
    }
    for view in page.views:
        pageContent[view.name] = view.render(None)

    return page.render(pageContent)

def find_page(page_name, root_dir=None, pathParams=None, **view_args):
    """populates the profile variables"""

    root_dir = root_dir or app.root_dir
    pathParams = pathParams or {}
    ua = user_agent_parser.Parse(request.headers.get('User-Agent', ''))
    lang = processLang(request.headers.get('Accept-Language', ''))
    profile_name = profileParser(ua, request, pathParams)
    built_page = match_page_profile(page_name, profile_name)
    profile = Profile(profile_name, ua, request.path, pathParams, lang, built_page)
    views = [View(root_dir, profile, view) for view in built_page.views.values()]
    return Page(root_dir, profile, built_page, views)

def process_page(root_dir, page_controller, page_name, pathParams=None, **view_args):
    """populates the profile variables and fires the run-time page controller"""

    page = find_page(page_name, root_dir, pathParams=None, **view_args)

    try:
        return page_controller(page)
    except Exception as e:
        if app.error_page:
            return app.error_page(e)
        else:
            raise
