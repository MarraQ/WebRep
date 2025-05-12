from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length


class AdForm(FlaskForm):
    title = StringField("Название объявления",
                        validators=[DataRequired(), Length(max=100, message="Максимум 100 символов в названии")])
    content = TextAreaField("Описание объявления",
                            validators=[DataRequired(), Length(max=500, message="Максимум 500 символов в описании")])
    image = FileField("Изображение", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')])
    price = IntegerField("Цена", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Выложить")
