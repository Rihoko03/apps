from flask import Blueprint, render_template, flash, url_for, redirect, request, session
from flask_login import login_user, logout_user, login_required, current_user
from apps.app import db
from apps.student.forms import LoginForm, LoanForm, ReturnForm
from apps.teacher.models import Student, Item, Loan
from datetime import datetime

# Blueprintの設定
student = Blueprint(
    "student",
    __name__,
    template_folder="templates",
    static_folder="static"
)

# ログイン
@student.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 入力された学籍番号で学生を検索
        student_user = Student.query.filter_by(student_number=form.student_number.data).first()  # 学籍番号で検索
        if student_user:  # 学籍番号が一致するユーザーがいる場合
            login_user(student_user)  # ログイン処理
            session['user_type'] = 'student'  # セッションにユーザータイプを設定
            return redirect(url_for("student.home"))  # 生徒のホーム画面にリダイレクト
        flash("学籍番号が正しくありません。", "danger")
    return render_template("student/login.html", form=form)
    
# ホーム画面
@student.route("/home")
@login_required
def home():
    if isinstance(current_user, Student):
        return render_template("student/home.html")
    return redirect(url_for("student.login"))

# ログアウト処理
@student.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('user_type', None)
    return redirect(url_for("student.login"))

# アイテム借りる処理
@student.route("/loan", methods=["GET", "POST"])
@login_required
def loan():
    form = LoanForm()
    if isinstance(current_user, Student):
        # 利用可能なアイテムの選択肢をフォームに設定
        form.item_id.choices = [(item.id, item.name) for item in Item.query.filter_by(available=True).all()]
        if form.validate_on_submit():
            item = Item.query.get(form.item_id.data)
            quantity_to_borrow = form.quantity.data  # フォームから借りる数量を取得

            if item:
                # アイテムの貸出処理
                if item.quantity >= quantity_to_borrow:
                    # アイテムの数量が借りる数量以上なら貸し出し可能
                    loan = Loan(student_id=current_user.id, item_id=item.id, loan_date=datetime.utcnow(), quantity=quantity_to_borrow)
                    item.quantity -= quantity_to_borrow  # アイテムの数量を減らす
                    db.session.add(loan)
                    db.session.commit()
                    flash(f"アイテム「{item.name}」を{quantity_to_borrow}個借りました。", "success")
                    return redirect(url_for("student.loan_complete"))
                else:
                    flash(f"アイテム「{item.name}」は十分な数量がありません。", "danger")
            else:
                flash("アイテムの貸出に失敗しました。", "danger")
    return render_template("student/loan.html", form=form)

# 借りられるもの一覧ページ
@student.route("/available_items")
@login_required
def available_items():
    available_items = Item.query.filter(Item.quantity > 0).all()
    return render_template("student/available_items.html", available_items=available_items)

# アイテムを返却する
@student.route("/return", methods=["GET", "POST"])
@login_required
def return_item():
    form = ReturnForm()
    loans = Loan.query.filter_by(student_id=current_user.id, return_date=None).all()
    form.loan_id.choices = [(loan.id, f"{loan.item.name} (個数: {loan.quantity})") for loan in loans]
    
    if form.validate_on_submit():
        # フォームで選択された複数の貸出IDを取得
        selected_loan_ids = request.form.getlist("loan_id")
        
        # 選択された貸出IDに対応するローン情報を処理
        for loan_id in selected_loan_ids:
            loan = Loan.query.get(loan_id)
            if loan and loan.student_id == current_user.id:
                # アイテム返却処理
                loan.return_date = datetime.utcnow()
                loan.item.quantity += loan.quantity  # 在庫を更新
                db.session.commit()
                flash(f"アイテム「{loan.item.name}」を返却しました。", "success")
        
        # 完了画面にリダイレクト
        return redirect(url_for("student.return_complete"))

    return render_template("student/return.html", form=form, loans=loans)

    
# 貸出履歴
@student.route("/loan_history")
@login_required
def loan_history():
    if isinstance(current_user, Student):
        # 日時が新しい順に並べ替え
        loans = Loan.query.filter_by(student_id=current_user.id).order_by(Loan.loan_date.desc()).all()
        return render_template("student/loan_history.html", loans=loans)



# 完了画面（貸出完了）
@student.route("/loan_complete")
@login_required
def loan_complete():
    return render_template("student/loan_complete.html")

# 完了画面（返却完了）
@student.route("/return_complete")
@login_required
def return_complete():
    return render_template("student/return_complete.html")
