from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField, FileField
from wtforms.validators import DataRequired, Email, length, EqualTo, NumberRange


class StudentForm(FlaskForm):
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名は必須です。"),
            length(max=30, message="30文字以内で入力してください。"),
        ],
    )

    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスは必須です。"),
            Email(message="メールアドレスの形式で入力してください。"),
        ],
    )

    student_number = StringField('学籍番号', validators=[DataRequired(message="学籍番号は必須です。")])
    submit = SubmitField("新規登録")


class TeacherForm(FlaskForm):
    teachername = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名は必須です。"),
            length(max=30, message="30文字以内で入力してください。"),
        ],
    )

    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスは必須です。"),
            Email(message="メールアドレスの形式で入力してください。"),
        ],
    )

    password = PasswordField("パスワード", validators=[DataRequired(message="パスワードは必須です。")])

    submit = SubmitField("新規登録")



class TeacherLoginForm(FlaskForm):
    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired("メールアドレスは必須です。"),
            Email("メールアドレスの形式で入力してください。"),
        ],
    )
    password = PasswordField(
        "パスワード", validators=[DataRequired("パスワードは必須です。")]
    )
    submit = SubmitField("ログイン")



class ItemForm(FlaskForm):
    name = StringField('アイテム名', validators=[DataRequired()])
    quantity = IntegerField('数量', validators=[DataRequired(), NumberRange(min=0, message="数量は0以上にしてください")])
    image = FileField('画像', validators=[DataRequired()])

    submit = SubmitField("アイテム登録")


