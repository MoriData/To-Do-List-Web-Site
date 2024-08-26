from sending_email import SendEmail
from flask import Flask, abort, flash, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap5
import datetime as dt
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("DATA_KEY")
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Create  forms

class TodoForm(FlaskForm):
    to_do = StringField("", validators=[DataRequired()])
    submit = SubmitField("start!")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))

    texts = relationship("Todolist", back_populates="text")
    texts_doing = relationship("Doinglist", back_populates="text")
    texts_done = relationship("Donelist", back_populates="text")


class Todolist(db.Model):
    __tablename__ = "todolist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    text_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    text = relationship("User", back_populates="texts")
    todolist: Mapped[str] = mapped_column(String(100))


class Doinglist(db.Model):
    __tablename__ = "doinglist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    text_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    text = relationship("User", back_populates="texts_doing")
    doinglist: Mapped[str] = mapped_column(String(100))


class Donelist(db.Model):
    __tablename__ = "donelist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    text_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    text = relationship("User", back_populates="texts_done")
    donelist: Mapped[str] = mapped_column(String(100))


with app.app_context():
    db.create_all()


# def delete1():
#     result = db.session.execute(db.select(Todolist))
#     tasks = result.scalars().all()
#     for i in tasks:
#         post_to_delete = db.get_or_404(Todolist, i.id)
#         print(post_to_delete)
#         db.session.delete(post_to_delete)
#         db.session.commit()


@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("index.html")


@app.route("/start", methods=["GET", "POST"])
def start():
    todo_form = TodoForm()
    if current_user.is_authenticated:
        # task = request.values.get('todo')
        task = todo_form.to_do.data
        if not task is None:
            new_task = Todolist(
                todolist=task,
                text=current_user
            )

            db.session.add(new_task)
            db.session.commit()
            user_texts_doing = current_user.texts_doing
            user_texts = current_user.texts
            return redirect(
                url_for("start", texts=user_texts, doing_texts=user_texts_doing, todoform=todo_form, user=current_user))
        else:
            user_texts = current_user.texts
            user_texts_doing = current_user.texts_doing
            user_texts_done = current_user.texts_done
            x = dt.datetime.now().today()
            print(x.strftime("%A %d %b %Y"))
            date = x.strftime("%A %d %b %Y")
            return render_template("todo.html", is_edit=True, texts=user_texts, doing_texts=user_texts_doing,
                                   done_texts=user_texts_done,
                                   todoform=todo_form, date=date)
    else:
        return render_template("index.html")


@app.route("/doing/<int:id>", methods=["GET", "POST"])
def doing(id):
    post_to_doing = db.get_or_404(Todolist, id)
    task = post_to_doing.todolist
    new_task = Doinglist(
        doinglist=task,
        text=current_user
    )

    db.session.add(new_task)
    db.session.commit()

    post_to_delete = db.get_or_404(Todolist, id)
    db.session.delete(post_to_delete)
    db.session.commit()
    user_texts = current_user.texts_doing
    return redirect(url_for("start", texts=user_texts))


@app.route("/done/<int:id>", methods=["GET", "POST"])
def done(id):
    post_to_done = db.get_or_404(Doinglist, id)
    task = post_to_done.doinglist
    new_task = Donelist(
        donelist=task,
        text=current_user
    )

    db.session.add(new_task)
    db.session.commit()

    post_to_delete = db.get_or_404(Doinglist, id)
    db.session.delete(post_to_delete)
    db.session.commit()
    user_texts = current_user.texts_done
    return redirect(url_for("start", texts=user_texts))


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("start"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('register'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('start'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/delete/<int:id>', methods=["GET", "POST"])
def delete(id):
    post_to_delete = db.get_or_404(Todolist, id)
    db.session.delete(post_to_delete)
    db.session.commit()
    user_texts = current_user.texts_doing
    return redirect(url_for("start", texts=user_texts))


@app.route('/message')
def send_email():
    SendEmail()
    return redirect(url_for("start"))


@app.route('/delete_all', methods=["GET", "POST"])
def delete_all():
    result = db.session.execute(db.select(Todolist))
    tasks = result.scalars().all()
    result_2 = db.session.execute(db.select(Doinglist))
    tasks_2 = result_2.scalars().all()
    result_3 = db.session.execute(db.select(Donelist))
    tasks_3 = result_3.scalars().all()

    for i in tasks:
        post_to_delete = db.get_or_404(Todolist, i.id)
        print(post_to_delete)
        db.session.delete(post_to_delete)
        db.session.commit()

    for i in tasks_2:
        post_to_delete = db.get_or_404(Doinglist, i.id)
        print(post_to_delete)
        db.session.delete(post_to_delete)
        db.session.commit()

    for i in tasks_3:
        post_to_delete = db.get_or_404(Donelist, i.id)
        print(post_to_delete)
        db.session.delete(post_to_delete)
        db.session.commit()
    return redirect(url_for("start"))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, port=5001)

