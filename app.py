from flask import Flask, render_template, redirect, session, make_response
from flask_login import LoginManager, current_user, login_required, login_user
from data import db_session
from data.users import User
from data.ads import Ad
from loginform import LoginForm
from register import RegisterForm
from adform import AdForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "CRZDYAMSD!##!@"
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/database.db")


@app.route("/")
def main():
    return render_template("index.html")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        print(form.password.data)
        print(type(form.password.data))
        print(user.hpasw, user.email)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('loginform.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('loginform.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nickname=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/ad_add', methods=['GET', 'POST'])
@login_required
def add_ads():
    form = AdForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        ad = Ad()
        ad.title = form.title.data
        ad.content = form.content.data
        ad.price = form.price.data
        current_user.ads.append(ad)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template("adform.html",
                           title="Добавление объявления", form=form)


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз {current_user.nickname}")


if __name__ == "__main__":
    app.run()
