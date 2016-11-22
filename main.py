#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import datetime
from model.post import Post
from jinja2 import Environment, FileSystemLoader

template_dir = os.path.join(os.path.dirname(__file__), 'template')
jinja_env = Environment(loader = FileSystemLoader(template_dir), autoescape=True)


def minutes_since_post_created(creation_timestamp):
    seconds_passed = (datetime.datetime.utcnow() - creation_timestamp).seconds
    if (seconds_passed / 86400) > 1:
        return "%d days ago" % (seconds_passed / 86400)
    elif (seconds_passed / 3600) > 1:
        return "%d hours ago" % (seconds_passed / 3600)
    elif (seconds_passed / 60) > 1:
        return "%d minutes ago" % (seconds_passed / 60)
    else:
        return "moments ago"
jinja_env.filters['post_age'] = minutes_since_post_created


class FrontPageHandler(webapp2.RequestHandler):
    template = jinja_env.get_template('posts.html')

    def get(self):
        self.response.out.write(self.template.render(posts=Post().query()))

app = webapp2.WSGIApplication([
    ('/', FrontPageHandler)
], debug=True)
