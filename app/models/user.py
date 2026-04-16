from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    使用者帳號 Model。

    Attributes:
        id:            主鍵，自動遞增。
        username:      使用者名稱，需唯一。
        email:         電子郵件，需唯一（作為登入識別）。
        password_hash: werkzeug bcrypt 雜湊後的密碼。
        created_at:    帳號建立時間。
    """
    __tablename__ = 'user'

    id            = db.Column(db.Integer,     primary_key=True, autoincrement=True)
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
        """以 werkzeug 雜湊方式儲存密碼。"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """驗證明文密碼是否與雜湊值吻合。"""
        return check_password_hash(self.password_hash, password)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, username: str, email: str, password: str) -> 'User | None':
        """
        建立新使用者並寫入資料庫。

        Args:
            username: 使用者名稱（需唯一）。
            email:    電子郵件（需唯一）。
            password: 明文密碼，會自動雜湊後儲存。

        Returns:
            成功：User 物件；失敗（如 email 重複）：None。
        """
        try:
            user = cls(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print(f"[User.create] 失敗：{e}")
            return None

    @classmethod
    def get_all(cls) -> list['User']:
        """取得所有使用者（管理用），依建立時間倒序。"""
        try:
            return cls.query.order_by(cls.created_at.desc()).all()
        except Exception as e:
            print(f"[User.get_all] 失敗：{e}")
            return []

    @classmethod
    def get_by_id(cls, user_id: int) -> 'User | None':
        """
        以 ID 查詢單一使用者。

        Args:
            user_id: 使用者主鍵。

        Returns:
            User 物件或 None（找不到時）。
        """
        try:
            return db.session.get(cls, user_id)
        except Exception as e:
            print(f"[User.get_by_id] 失敗：{e}")
            return None

    @classmethod
    def get_by_email(cls, email: str) -> 'User | None':
        """
        以 email 查詢使用者（登入驗證用）。

        Args:
            email: 電子郵件地址。

        Returns:
            User 物件或 None。
        """
        try:
            return cls.query.filter_by(email=email).first()
        except Exception as e:
            print(f"[User.get_by_email] 失敗：{e}")
            return None

    @classmethod
    def get_by_username(cls, username: str) -> 'User | None':
        """
        以 username 查詢使用者（註冊重複檢查用）。

        Args:
            username: 使用者名稱。

        Returns:
            User 物件或 None。
        """
        try:
            return cls.query.filter_by(username=username).first()
        except Exception as e:
            print(f"[User.get_by_username] 失敗：{e}")
            return None

    def update(self, username: str = None, email: str = None, password: str = None) -> bool:
        """
        更新使用者資訊。

        Args:
            username: 新使用者名稱（不傳則不更新）。
            email:    新電子郵件（不傳則不更新）。
            password: 新明文密碼（不傳則不更新）。

        Returns:
            True：更新成功；False：更新失敗。
        """
        try:
            if username:
                self.username = username
            if email:
                self.email = email
            if password:
                self.set_password(password)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[User.update] 失敗：{e}")
            return False

    def delete(self) -> bool:
        """
        刪除此使用者（關聯筆記與測驗 CASCADE 刪除）。

        Returns:
            True：刪除成功；False：刪除失敗。
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[User.delete] 失敗：{e}")
            return False

    def __repr__(self) -> str:
        return f'<User id={self.id} username={self.username}>'
