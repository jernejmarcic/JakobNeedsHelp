"""

This is a simple blog web application.

The aim of this web application is to show how to use Flask
framework to start the web server, do simple web page routing
and web page error handling.

Bootstrap framework is used for the formatting of this web
application. This example also shows how to use templates to
format generated web pages.

@author     Gregor Anželj <gregor.anzelj@gmail.com>
@license    GNU GPL
@copyright  (C) Gregor Anželj 2020

"""

# Import Flask modules
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.exceptions import HTTPException

# Import Flask WTForms modules
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

# Import Flask SQLAlchemy modules
from flask_sqlalchemy import SQLAlchemy

# Import other modules
from datetime import datetime


# ========== Create application ========== #

app = Flask(__name__, instance_relative_config=False)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)


# ========== Route definitions ========== #
#
#  HTTP method | URL path          | Controller function
# -------------+-------------------+----------------------
#  GET         | /                 | list_posts()
#  GET         | /posts            | list_posts()
#  GET, POST   | /post/add         | add_post()
#  GET, POST   | /post/edit/<id>   | edit_post(id)
#  GET, POST   | /post/delete/<id> | delete_post(id)
#  GET         | /post/view/<id>   | view_post(id)
# -------------+-------------------+----------------------
#

# Index page for blog web application
@app.route('/', methods=['GET'])
@app.route('/posts', methods=['GET'])
def list_posts():
    # Get all blog posts, newest first
    records = db.session.query(Blogpost).order_by(Blogpost.created.desc()).all()

    return render_template('index.html', data=records)


# Add new blog post
@app.route('/post/add', methods=['GET', 'POST'])
def add_post():
    # Setup form
    form = AddPostForm()

    # Process form; no default values here
    if form.validate_on_submit():
        # Handle creating blog post in the database
        if request.method == 'POST' and 'submit' in request.form:

            # Save blog post to the database
            timestamp = datetime.now()
            record = Blogpost(
                created = timestamp,
                updated = timestamp,
                title   = request.form.get('title'),
                summary = request.form.get('summary'),
                content = request.form.get('content')
            )
            db.session.add(record)
            db.session.commit()
            #flash('Blogpost was successfully created.')

        return redirect(url_for('list_posts'))

    return render_template('add.html', title='Add post', form=form)


# Edit and update existing blog post
@app.route('/post/edit/<id>', methods=['GET', 'POST'])
def edit_post(id):
    # Get existing blog post by id
    record = db.session.query(Blogpost).get(id)

    # Setup form
    form = EditPostForm(obj=record)

    # Process form; no default values here
    if form.validate_on_submit():
        # Handle updating blog post in the database
        if request.method == 'POST' and 'submit' in request.form:

            # Update blog post in the database
            timestamp = datetime.now()
            record.updated = timestamp
            record.title   = request.form.get('title')
            record.summary = request.form.get('summary')
            record.content = request.form.get('content')
            db.session.commit()
            #flash('Blogpost was successfully updated.')

        return redirect(url_for('list_posts'))

    return render_template('edit.html', title='Edit post', form=form)


# Delete existing blog post
@app.route('/post/delete/<id>', methods=['GET', 'POST'])
def delete_post(id):
    # Get existing blog post by id
    record = db.session.query(Blogpost).get(id)

    # Setup form
    form = DeletePostForm()

    # Process form; no default values here
    if form.validate_on_submit():
        # Handle deleting blog post from the database
        if request.method == 'POST' and 'submit' in request.form:

            # Delete blog post from the database
            db.session.delete(record)
            db.session.commit()
            #flash('Blogpost was successfully deleted.')

        return redirect(url_for('list_posts'))

    return render_template('delete.html', title='Delete post', form=form)


# View and read blog post
@app.route('/post/view/<id>', methods=['GET', 'POST'])
def view_post(id):
    # Get existing blog post by id
    record = db.session.query(Blogpost).get(id)

    return render_template('view.html', title='View post', data=record)


# Handle HTTP exceptions
@app.errorhandler(HTTPException)
def handle_exception(error):
    return render_template('error.html', error=error), error.code


# ========== Form definitions ========== #

# Form to add blog post
class AddPostForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired('You must provide blog post title!')]
    )
    summary = TextAreaField(
        'Summary',
        validators=[DataRequired('You must provide blog post summary!')]
    )
    content = TextAreaField(
        'Content',
        validators=[DataRequired('You must provide blog post content!')]
    )
    submit = SubmitField('Add')


# Form to edit blog post
class EditPostForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired('You must provide blog post title!')]
    )
    summary = TextAreaField(
        'Summary',
        validators=[DataRequired('You must provide blog post summary!')]
    )
    content = TextAreaField(
        'Content',
        validators=[DataRequired('You must provide blog post content!')]
    )
    submit = SubmitField('Edit')


# Form to delete blog post
class DeletePostForm(FlaskForm):
    submit = SubmitField('Delete')


# ========== Database model definitions ========== #

# Database model for Blogpost entity
class Blogpost(db.Model):
    __tablename__ = 'blogpost'
    id      = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)
    title   = db.Column(db.String, nullable=False)
    summary = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)

    def __init__(self, created, updated, title, summary, content):
        self.created = created
        self.updated = updated
        self.title   = title
        self.summary = summary
        self.content = content

    def __repr__(self):
        return '<Blogpost %r>' % self.title


# ========== Create DB with default values ========== #

with app.app_context():
    # Create the database/tables if it/they don't exist yet
    # This call has to be after database model definitions!
    db.create_all()

    # Check if test data exist in the database
    exists = Blogpost.query.first()

    # Add test data to the database if it doesn't exist
    if not exists:
        timestamp = datetime.now()
        posts = [
            Blogpost(
                created = timestamp,
                updated = timestamp,
                title   = 'Lorem ipsum dolor sit amet',
                summary = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed dictum tincidunt eleifend. Morbi vulputate bibendum consectetur. Aenean mollis, massa pellentesque porta elementum, velit magna convallis libero, eu iaculis augue ex in nunc. Sed pretium nibh sagittis, aliquam leo ut, aliquet libero. Morbi justo lacus, accumsan eget mattis non, mollis eget risus. Nam vitae tortor elit. Fusce eget nunc sed urna vestibulum vulputate.',
                content = 'Nam non ante eget justo vehicula fermentum a ut erat. Sed quis tellus sit amet odio aliquet commodo. Suspendisse tincidunt ante sed iaculis varius. Nullam malesuada mauris eget libero commodo consectetur. Nunc a sem neque. Vestibulum tempor rhoncus justo vel congue. Donec sodales orci porttitor massa convallis condimentum. Etiam at sem eros. Aenean congue iaculis viverra. Nulla elementum scelerisque ligula, nec malesuada enim maximus quis. Morbi vitae orci volutpat nibh sagittis finibus in ac erat. Curabitur ut enim eu purus ornare egestas. Donec gravida est et bibendum aliquam. In fermentum ultricies leo, vel gravida odio rutrum vitae. Phasellus nec cursus justo, sit amet porta orci. Maecenas ultricies, mauris et fermentum mollis, metus metus feugiat lacus, vitae congue mi diam a arcu.'
            ),
            Blogpost(
                created = timestamp,
                updated = timestamp,
                title   = 'Integer et posuere tortor',
                summary = 'Integer et posuere tortor. Maecenas pellentesque suscipit velit, a lobortis nunc cursus ac. Suspendisse potenti. Vestibulum imperdiet, nibh vitae rhoncus luctus, nisi orci eleifend nibh, eget porta libero lacus quis lacus. In auctor gravida lacinia. Sed vel sagittis nisi. Donec pellentesque cursus euismod.',
                content = 'Quisque vel leo rutrum, laoreet tellus quis, suscipit magna. Fusce ut quam vitae arcu efficitur mattis a ut lectus. Proin ante dolor, pellentesque ac pulvinar et, porttitor sit amet nunc. Phasellus quis purus varius, mattis sapien eu, pellentesque sem. Nunc placerat sit amet turpis pretium auctor. Integer laoreet eget risus sit amet pharetra. Mauris vitae posuere nunc, quis lacinia est. Nulla placerat erat pharetra justo condimentum ultrices. Sed eget congue felis, vel vehicula metus. Nam varius tellus neque, quis scelerisque est fermentum eget. Duis commodo pharetra justo sit amet maximus. Praesent convallis massa non odio iaculis, nec tincidunt eros accumsan. Maecenas facilisis ligula molestie arcu porta, ac dictum lectus maximus. Maecenas sed ex at ex cursus fermentum vitae non elit.'
            ),
            Blogpost(
                created = timestamp,
                updated = timestamp,
                title   = 'Aliquam tincidunt tortor auctor',
                summary = 'Aliquam tincidunt tortor auctor. Suspendisse potenti. Aenean laoreet purus eget est aliquet ullamcorper. Etiam nec nisi libero. Donec id dolor nisl. Vestibulum vitae blandit est. Nullam pretium tellus fringilla, molestie urna quis, pharetra justo.',
                content = 'In id dolor vitae nisi malesuada vehicula. Etiam euismod feugiat sagittis. Duis lectus mi, rutrum ac sem fringilla, vehicula porta massa. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Pellentesque quis efficitur mauris. Integer ultricies leo a cursus dapibus. Praesent volutpat bibendum lectus eget sollicitudin. Donec rutrum libero neque, non vehicula tortor pellentesque quis. Maecenas eu elit efficitur, ornare ante eget, laoreet velit. Curabitur placerat sapien molestie est accumsan, at iaculis diam aliquam. Nullam bibendum est vitae ex placerat, vel sollicitudin arcu sollicitudin. Pellentesque sit amet pharetra purus, nec aliquam leo. Fusce ac libero tincidunt nisl convallis feugiat.'
            )
        ]
        for post in posts:
            db.session.add(post)
        db.session.commit()


# ========== Run application ========== #

if __name__ == '__main__':
    # Run application and development server
    app.run(debug=True)
