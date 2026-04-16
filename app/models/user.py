from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """使用者帳號 Model"""
    __tablename__ = 'user'

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username      = db.Column(db.String(50),  nullable=False, unique=True)
    email         = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)

    # Relationships
    notes = db.relationship('Note', backref='author',  lazy=True, cascade='all, delete-orphan')
    exams = db.relationship('Exam', backref='student', lazy=True, cascade='all, delete-orphan')

    # ------------------------------------------------------------------
    # 密碼工具
    # ------------------------------------------------------------------
    def set_password(self, password: str) -> None:
        """以 bcrypt 雜湊方式儲存密碼"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """驗證密碼是否正確"""
        return check_password_hash(self.password_hash, password)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, username: str, email: str, password: str) -> 'User':
        """建立新使用者並寫入資料庫"""
        user = cls(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_all(cls) -> list['User']:
        """取得所有使用者（管理用）"""
        return cls.query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_id(cls, user_id: int) -> 'User | None':
        """以 ID 查詢單一使用者"""
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email: str) -> 'User | None':
        """以 email 查詢使用者（登入用）"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_username(cls, username: str) -> 'User | None':
        """以 username 查詢使用者"""
        return cls.query.filter_by(username=username).first()

    def update(self, username: str = None, email: str = None, password: str = None) -> 'User':
        """更新使用者資訊"""
        if username:
            self.username = username
        if email:
            self.email = email
        if password:
            self.set_password(password)
        db.session.commit()
        return self

    def delete(self) -> None:
        """刪除此使用者（關聯資料 CASCADE 刪除）"""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f'<User id={self.id} username={self.username}>'
