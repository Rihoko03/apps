from apps.teacher.forms import StudentForm, TeacherForm, TeacherLoginForm, ItemForm
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from apps.app import db
from apps.teacher.models import Student, Teacher, Item, Loan  # Loan モデルをインポート
from flask_login import login_required, login_user, logout_user, current_user
import os, io, base64
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict

teacher = Blueprint(
    "teacher",
    __name__,
    template_folder="templates",
    static_folder="static",
)

@teacher.route("/")
def index():
    return render_template("teacher/index.html")

# 生徒一覧
@teacher.route("/students")
@login_required
def student_index():
    students = Student.query.all()
    return render_template("teacher/student_index.html", students=students)

# 教師一覧
@teacher.route("/teachers")
@login_required
def teacher_index():
    teachers = Teacher.query.all()
    return render_template("teacher/teacher_index.html", teachers=teachers)

# 生徒新規登録
@teacher.route("/students/new", methods=["GET", "POST"])
def create_student():
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(
            username=form.username.data,
            email=form.email.data,
            student_number=form.student_number.data,  # 学籍番号を追加
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("teacher.student_index"))
    return render_template("teacher/student_create.html", form=form)

# 教師新規登録
@teacher.route("/teachers/new", methods=["GET", "POST"])
def create_teacher():
    form = TeacherForm()
    if form.validate_on_submit():
        teacher = Teacher(
            teachername=form.teachername.data,
            email=form.email.data,
            password=form.password.data,
        )
        db.session.add(teacher)
        db.session.commit()
        return redirect(url_for("teacher.teacher_index"))
    return render_template("teacher/teacher_create.html", form=form)

# 生徒情報変更
@teacher.route("/students/<student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    form = StudentForm()
    student = Student.query.filter_by(id=student_id).first()
    if form.validate_on_submit():
        student.username = form.username.data
        student.email = form.email.data
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("teacher.student_index"))
    return render_template("teacher/student_edit.html", student=student, form=form)

# 教師情報変更
@teacher.route("/teachers/<teacher_id>", methods=["GET", "POST"])
@login_required
def edit_teacher(teacher_id):
    form = TeacherForm()
    teacher = Teacher.query.filter_by(id=teacher_id).first()
    if form.validate_on_submit():
        teacher.teachername = form.teachername.data
        teacher.email = form.email.data
        teacher.password = form.password.data
        db.session.add(teacher)
        db.session.commit()
        return redirect(url_for("teacher.teacher_index"))
    return render_template("teacher/teacher_edit.html", teacher=teacher, form=form)

# 生徒情報削除
@teacher.route("/students/<student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    student = Student.query.filter_by(id=student_id).first()
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for("teacher.student_index"))

# 教師情報削除
@teacher.route("/teachers/<teacher_id>/delete", methods=["POST"])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.filter_by(id=teacher_id).first()
    db.session.delete(teacher)
    db.session.commit()
    return redirect(url_for("teacher.teacher_index"))

# 教師ログイン
@teacher.route("/login", methods=["GET", "POST"])
def login():
    form = TeacherLoginForm()
    if form.validate_on_submit():
        teacher = Teacher.query.filter_by(email=form.email.data).first()
        if teacher is not None and teacher.verify_password(form.password.data):
            login_user(teacher)
            return redirect(url_for("teacher.home"))
        flash("メールアドレスかパスワードが不正です")
    return render_template("teacher/login.html", form=form)

# 教師ログアウト
@teacher.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('user_type', None)
    return redirect(url_for("teacher.login"))

# 教師ホーム画面
@teacher.route("/home")
@login_required
def home():
    if isinstance(current_user, Teacher):
        return render_template("teacher/home.html")  # 生徒の貸し出し状況は表示しない
    else:
        return redirect(url_for("student.home"))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# アップロードされたファイルの拡張子が許可されているかチェック
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@teacher.route('/teacher/items/new', methods=['GET', 'POST'])
@login_required
def new_item():
    form = ItemForm()
    if form.validate_on_submit():
        name = form.name.data
        quantity = form.quantity.data
        image = form.image.data

        # 画像がアップロードされていれば保存
        image_filename = None
        if image:
            # secure_filenameでファイル名の安全性を確保
            image_filename = secure_filename(image.filename)

            # flaskbook/static/images/ディレクトリのパスを取得
            # ここでは現在のアプリのstaticフォルダのパスを使用します
            app_root = os.path.dirname(os.path.abspath(__file__))

            # flaskbook/static/images/の絶対パスを作成
            image_path = os.path.join(app_root, '..', 'static', 'images', image_filename)

            # フォルダが存在しなければ作成
            if not os.path.exists(os.path.dirname(image_path)):
                os.makedirs(os.path.dirname(image_path))

            # 画像を保存
            image.save(image_path)

        # アイテム作成
        item = Item(
            name=name,
            quantity=quantity,
            image=image_filename,  # 画像ファイル名を保存
            teacher_id=current_user.id
        )

        # データベースに追加してコミット
        db.session.add(item)
        db.session.commit()

        # アイテム一覧ページへリダイレクト
        return redirect(url_for('teacher.item'))

    # GETリクエストの場合はフォームを表示
    return render_template('teacher/new_item.html', form=form)

    
# アイテム一覧ページ
@teacher.route('/items')
@login_required
def item():
    items = Item.query.all()
    return render_template('teacher/item.html', items=items)

# アイテム編集
@teacher.route('/teacher/items/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)

    if form.validate_on_submit():
        item.name = form.name.data
        item.quantity = form.quantity.data

        # 変更内容をデータベースに反映
        db.session.commit()
        return redirect(url_for('teacher.item'))

    return render_template('teacher/edit_item.html', item=item, form=form)

# アイテム削除
@teacher.route('/items/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('teacher.item'))

# 生徒全員の貸出状況表示
@teacher.route("/loan_status")
@login_required
def loan_status():
    students = Student.query.all()  
    loan_data = {}  

    for student in students:
        loans = Loan.query.filter_by(student_id=student.id, return_date=None).order_by(Loan.loan_date.desc()).all()
        returned_loans = Loan.query.filter_by(student_id=student.id).filter(Loan.return_date.isnot(None)).order_by(Loan.return_date.desc()).all()

        loan_data[student] = {
            "loans": loans,
            "returned_loans": returned_loans
        }

    return render_template(
        "teacher/loan_status.html",
        loan_data=loan_data
    )


@teacher.route("/loan_statistics")
@login_required
def loan_statistics():
    loans = Loan.query.all()
    items = Item.query.all()

    item_stats = {}
    item_tables = {}
    
    for item in items:
        # 貸出情報をアイテムごと
        item_loans = [loan for loan in loans if loan.item_id == item.id and loan.loan_date]

        # 日ごとの貸出数を集計
        date_buckets = defaultdict(int)
        for loan in item_loans:
            loan_date = loan.loan_date.date()  
            date_buckets[loan_date] += loan.quantity  

        # 集計結果を日付順にソート
        sorted_buckets = sorted(date_buckets.items())
        dates = [b[0].strftime("%Y-%m-%d") for b in sorted_buckets] 
        counts = [b[1] for b in sorted_buckets]

        # テーブル用データを作成
        table_data = zip(dates, counts)
        item_tables[item.name] = table_data

        # グラフを生成
        fig, ax = plt.subplots()
        bars = ax.bar(dates, counts, color="skyblue")
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of Loans")
        ax.set_title("Loan Statistics")
        plt.xticks(rotation=0)  

        # 縦軸
        max_count = max(counts) if counts else 1
        ax.set_yticks(range(0, max_count + 2, 1))  

        # 各バーの上に個数を表示
        for bar, count in zip(bars, counts):
            yval = bar.get_height()  
            ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, str(count), ha='center', va='bottom', fontsize=10)

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close(fig)  

        item_stats[item.name] = image_data

    return render_template("teacher/loan_statistics.html", item_stats=item_stats, item_tables=item_tables)
