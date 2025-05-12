from flask import Flask, render_template, redirect, session, make_response, request, abort, jsonify
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_restful import abort, Api

from adform import AdForm
from ads_resources import AdsListResource, AdsResource
from data import db_session
from data.ads import Ad
from data.users import User
from loginform import LoginForm
from register import RegisterForm

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = "CRZDYAMSD!##!@"
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/database.db")

api.add_resource(AdsListResource, '/api/ads')
api.add_resource(AdsResource, '/api/ads/<int:ad_id>')


@app.route("/")
def main():
    db_sess = db_session.create_session()
    ads = db_sess.query(Ad).all()
    return render_template("mainpage.html", ads=ads)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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
        ad.description = form.content.data
        ad.price = form.price.data
        current_user.ads.append(ad)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template("adform.html",
                           title="Добавление объявления", form=form)


@app.route('/ad/<int:ad_id>')
def show_ads(ad_id):
    db_sess = db_session.create_session()
    ad = db_sess.query(Ad).filter(Ad.id == ad_id).first()
    if ad:
        params = {}
        params["id"] = ad.id
        params["title"] = ad.title
        params["content"] = ad.description
        params["price"] = ad.price
        params["date"] = str(ad.date).split(':')[0]
        params["owner_id"] = ad.owner_id
        return render_template("ad.html", **params)
    else:
        return render_template("notfound.html")


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route("/ad/buy/<int:ad_id>")
@login_required
def buy_ad(ad_id):
    db_sess = db_session.create_session()
    ad = db_sess.query(Ad).filter(Ad.id == ad_id).first()
    params = {}
    params["id"] = ad.id
    params["title"] = ad.title
    return render_template("buy.html", **params)


@app.route("/ad/bought/<int:ad_id>")
@login_required
def bought_ad(ad_id):
    db_sess = db_session.create_session()
    ad = db_sess.query(Ad).filter(Ad.id == ad_id).first()
    if ad:
        db_sess.delete(ad)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/")


@app.route('/ad/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ad(id):
    form = AdForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        ad = db_sess.query(Ad).filter(Ad.id == id,
                                      Ad.user == current_user
                                      ).first()
        if ad:
            form.title.data = ad.title
            form.content.data = ad.description
            form.price.data = ad.price
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        ad = db_sess.query(Ad).filter(Ad.id == id,
                                      Ad.user == current_user
                                      ).first()
        if ad:
            ad.title = form.title.data
            ad.description = form.content.data
            ad.price = form.price.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('adform.html',
                           title='Редактирование объявления',
                           form=form)


@app.route('/ad/delete/<int:ad_id>', methods=['GET', 'POST'])
@login_required
def delete_ad(ad_id):
    db_sess = db_session.create_session()
    ad = db_sess.query(Ad).filter(Ad.id == ad_id,
                                  Ad.user == current_user
                                  ).first()
    if ad:
        db_sess.delete(ad)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/user/<int:user_id>")
def profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    params = {}
    params["id"] = user.id
    params["nickname"] = user.nickname
    params["email"] = user.email
    params["date"] = user.created_date
    return render_template("user.html", **params)


if __name__ == "__main__":
    app.run()
