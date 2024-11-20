from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, ValidationError
from apps.teacher.models import Item  # Item モデルを正しくインポート

class LoginForm(FlaskForm):
    student_number = StringField('学籍番号', validators=[DataRequired("学籍番号は必須です。")])
    submit = SubmitField("ログイン")

class LoanForm(FlaskForm):
    item_id = SelectField("借りたいアイテムを選択", coerce=int, validators=[DataRequired()])
    quantity = IntegerField("借りる個数", validators=[DataRequired()])
    submit = SubmitField("借りる")

    def __init__(self, *args, **kwargs):
        super(LoanForm, self).__init__(*args, **kwargs)
        # 借りられるアイテムの選択肢を動的に設定
        self.item_id.choices = [(item.id, item.name) for item in Item.query.all()]

    def validate_quantity(self, field):
        # 選択されたアイテムを取得
        item = Item.query.get(self.item_id.data)
        if item and field.data > item.quantity:
            raise ValidationError(f"借りる個数は在庫数({item.quantity})以下にしてください。")

class ReturnForm(FlaskForm):
    loan_id = SelectField("借りているアイテムを選択", coerce=int, validators=[DataRequired()])
    submit = SubmitField("返却")

    def __init__(self, *args, **kwargs):
        super(ReturnForm, self).__init__(*args, **kwargs)
        # 借りているアイテムの選択肢を動的に設定
        self.loan_id.choices = [
            (loan.id, f"{loan.item.name} (個数: {loan.quantity})")
            for loan in kwargs.get('loans', [])
        ]
