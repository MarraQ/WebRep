from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired


class AdForm(FlaskForm):
    title = StringField("Название объявления", validators=[DataRequired()])
    content = TextAreaField("Описание объявления", validators=[DataRequired()])
    image = FileField("Изображение", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    price = IntegerField("Цена", validators=[DataRequired()])
    submit = SubmitField("Выложить")
