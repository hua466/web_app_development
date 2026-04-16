from app import db
from datetime import datetime


class Note(db.Model):
    """
    筆記資料 Model。

    Attributes:
        id:          主鍵，自動遞增。
        user_id:     外鍵，對應 user.id。
        title:       筆記標題。
        raw_content: 使用者原始輸入的文字。
        summary:     AI 整理後的結構化摘要（整理前為 None）。
        created_at:  建立時間。
        updated_at:  最後更新時間。
    """
    __tablename__ = 'note'

    id          = db.Column(db.Integer,     primary_key=True, autoincrement=True)
    user_id     = db.Column(db.Integer,     db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title       = db.Column(db.String(200), nullable=False)
    raw_content = db.Column(db.Text,        nullable=False)
    summary     = db.Column(db.Text,        nullable=True)
    created_at  = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exams = db.relationship('Exam', backref='source_note', lazy=True, cascade='all, delete-orphan')

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @classmethod
    def create(cls, user_id: int, title: str, raw_content: str, summary: str = None) -> 'Note | None':
        """
        建立新筆記並寫入資料庫。

        Args:
            user_id:     筆記所屬使用者的 ID。
            title:       筆記標題。
            raw_content: 使用者原始輸入文字。
            summary:     AI 整理後的摘要（可為 None，之後再更新）。

        Returns:
            成功：Note 物件；失敗：None。
        """
        try:
            note = cls(
                user_id=user_id,
                title=title,
                raw_content=raw_content,
                summary=summary
            )
            db.session.add(note)
            db.session.commit()
            return note
        except Exception as e:
            db.session.rollback()
            print(f"[Note.create] 失敗：{e}")
            return None

    @classmethod
    def get_all(cls) -> list['Note']:
        """取得所有筆記（管理用），依建立時間倒序。"""
        try:
            return cls.query.order_by(cls.created_at.desc()).all()
        except Exception as e:
            print(f"[Note.get_all] 失敗：{e}")
            return []

    @classmethod
    def get_by_user(cls, user_id: int) -> list['Note']:
        """
        取得某使用者的所有筆記，依建立時間倒序。

        Args:
            user_id: 使用者主鍵。

        Returns:
            Note 物件清單（查詢失敗時回傳空清單）。
        """
        try:
            return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
        except Exception as e:
            print(f"[Note.get_by_user] 失敗：{e}")
            return []

    @classmethod
    def get_by_id(cls, note_id: int) -> 'Note | None':
        """
        以 ID 查詢單一筆記。

        Args:
            note_id: 筆記主鍵。

        Returns:
            Note 物件或 None（找不到時）。
        """
        try:
            return db.session.get(cls, note_id)
        except Exception as e:
            print(f"[Note.get_by_id] 失敗：{e}")
            return None

    def update(self, title: str = None, raw_content: str = None, summary: str = None) -> bool:
        """
        更新筆記內容。

        Args:
            title:       新標題（不傳則不更新）。
            raw_content: 新原始內容（不傳則不更新）。
            summary:     新 AI 摘要（不傳則不更新）。

        Returns:
            True：更新成功；False：更新失敗。
        """
        try:
            if title is not None:
                self.title = title
            if raw_content is not None:
                self.raw_content = raw_content
            if summary is not None:
                self.summary = summary
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Note.update] 失敗：{e}")
            return False

    def delete(self) -> bool:
        """
        刪除此筆記（關聯測驗 CASCADE 刪除）。

        Returns:
            True：刪除成功；False：刪除失敗。
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"[Note.delete] 失敗：{e}")
            return False

    def __repr__(self) -> str:
        return f'<Note id={self.id} title={self.title!r} user_id={self.user_id}>'
