# Overview
This project implements a multi-user blog using Google App Engine. Users are able to sign up for accounts; contribute posts; and add comments to blog posts. Additionally, all submitted content (i.e. posts and comments) can be edited or deleted.

# Running The Project

### Remotely

The project is hosted at [http://nd004-blog.appspot.com](http://nd004-blog.appspot.com). You'll know you're in the right place when you see this page:

![Homepage](screenshots/homepage.png)

### Locally

Running the project locally requires the [Google App Engine SDK for Python](https://cloud.google.com/appengine/docs/python/download) to be installed on your local machine.

Assuming that the SDK is installed, the project can be run by:

1. Downloading or cloning this project to your local machine
2. Navigating to the project directory in the terminal. E.g. `cd /path/to/Udacity-Blog`
3. Running `dev_appserver.py .` from the terminal
4. The site should now be available at [http://localhost:8080](http://localhost:8080) in your web browser

# Functionality and Usage

## Accounts

### Signing Up

New users can sign up for an account via the Sign Up page

![Signup](screenshots/signup.png)

Note that new users must propose a unique username, and that both a username and password must be supplied

![Validation Errors](screenshots/signup-validation.png)

### Signing In

Existing users can log in via the Sign In page, which is accessed via the 'Sign In' link. This link is only visible to visitors that are not signed in.

![Signin](screenshots/signin.png)

Note that invalid credentials will cause a validation error. (For the sake of security, the data that triggered the validation error is not indicated).

![Signin validation errors](screenshots/signin-validation.png)

When users sign in, they receive a warm greeting

![Welcome page](screenshots/welcome.png)

### Signing Out

Only signed in users have the option to sign out; users sign out by clicking the 'Sign Out' link.

![Sign out](screenshots/signout.png)

## Posts

The primary entity in a blog are posts: posts can be read by anyone, but may only be created by account holders; furthermore, only authors are able to edit, and delete their posts.

Signed in users can also 'Like' a post, which elevates the position of the post on the main page.

### Create A Post

Any signed in user can create a post by clicking the 'New Post' link; this will direct them to a form for creating new posts.

![New post form](screenshots/new-post.png)

In order to submit a new post, all fields must be filled out, otherwise the page will be re-rendered with validation errors.

![New post validation errors](screenshots/new-post-validation.png)

### Read Posts

Any user can see a list of posts on the homepage (accessible via the 'Home' link); posts are listed in order of popularity, and then by newest.

![Homepage link to post](screenshots/post-link.png) 

A specific post can be viewed in its entirety by clicking on its title; this directs users to the page for that post.

![Post page](screenshots/post.png)

### Edit A Post

If a user is signed in as the author of a given post, they can perform edits on it. The Edit link is only available to users that are authors of a given post.

![Edit link](screenshots/edit-link.png)

Clicking the Edit link renders the editing page, which allows user to submit their edit (which is subject to validation) or cancel their edit.

![Edit page](screenshots/edit-page.png)

### Delete A Post

If a user is signed in as the author of a given page, they are also able to delete a post by clicking the Delete link. This will permanently remove a post from the blog.

![Delete](screenshots/delete-post.png)

### Like / Unlike A Post

A signed in user who has _not_ authored a given post is eligible to 'Like' that post. Liking a post is carried out by clicking the Like link on the post's page.

![Liking a post](screenshots/like.png)

Once a page has been 'Liked', a user can revoke that action by clicking 'Unlike'.

![Unliking a post](screenshots/unlike.png)

Liking posts affects the counter associated with each post, which determines the position of a post on the main page.

## Comments

Every post may be associated with comments about that post. Comments can be added by any signed in user, but only authors of a given comment may edit or delete their comment.

### Add A Comment

If a user is signed in, they are eligible to add a comment; otherwise they are prompted to sign in.

![Sign in to comment](screenshots/sign-in-to-comment.png)

A signed in user posts a comment via the comment form.

![Add a comment](screenshots/add-comment.png)

### Reading Comments

Any user can read comments. Comments are displayed in chronological order underneath a post so that they can be read from top to bottom as one continuous conversation.

![Read comments](screenshots/read-comments.png)

### Edit A Comment

A signed in user is given the option to edit their own comments. Users access the edit page for the comments by clicking the Edit link.

![Edit comment](screenshots/edit-comment-link.png)

The edit page displays a form in the context of the conversation so that users are able to access the post and neighbouring comments from the same page.

![Edit page](screenshots/comment-edit-page.png)

The timestamp of edited comments is not affected, so comments continue to appear in order of their creation.

### Delete A Comment

A signed in user is given the option to delete their own comments. Users delete a comment by clicking the Delete link

![Edit delete comment](screenshots/delete-comment-link.png)