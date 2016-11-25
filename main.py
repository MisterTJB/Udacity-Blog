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
from handler import posts, users, comments

app = webapp2.WSGIApplication([
    ('/', posts.FrontPageHandler),
    ('/posts/new', posts.NewPostFormHandler), # TODO merge in to PostsHandler as GET on /posts
    ('/posts', posts.PostsHandler),
    ('/posts/(\d+)', posts.PostHandler),

    ('/users/new', users.SignUpHandler),
    ('/users/in', users.SignInHandler),
    ('/users/out', users.SignOutHandler),
    ('/users/welcome', users.WelcomeHandler),

    webapp2.Route('/posts/<post_id:\d+>/comments', handler=comments.CreateCommentHandler),
    webapp2.Route('/posts/<post_id:\d+>/comments/<comment_id:\d+>/edit', handler=comments.UpdateCommentHandler),
    webapp2.Route('/posts/<post_id:\d+>/comments/<comment_id:\d+>', handler=comments.UpdateCommentHandler),
    webapp2.Route('/posts/<post_id:\d+>/comments/<comment_id:\d+>/delete', handler=comments.DeleteCommentHandler)

], debug=True)
