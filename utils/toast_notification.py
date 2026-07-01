from PyQt6.QtWidgets import (QWidget, QFrame, QLabel, QPushButton, QVBoxLayout,QGridLayout, QGraphicsDropShadowEffect)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, pyqtProperty)
from PyQt6.QtGui import QColor, QFont


class MessageManager:
    @staticmethod
    def show_message(label, message, message_type="error", duration=5000):
        styles = {
            "error": {"bg": "#2B1D1D", "border": "#FF4D4F", "text": "#FF7875", "icon": "❌"},
            "success": {"bg": "#1F2E1F", "border": "#52C41A", "text": "#95DE64", "icon": "✅"},
            "warning": {"bg": "#2D2416", "border": "#FAAD14", "text": "#FFD666", "icon": "⚠️"},
            "info": {"bg": "#162312", "border": "#1677FF", "text": "#69B1FF", "icon": "ℹ️"},
        }
        style = styles.get(message_type, styles["error"])
        label.setText(f"{style['icon']}  {message}")
        label.setStyleSheet(
            f"QLabel{{color: {style['text']}; padding: 8px; font-size: 16px; font-weight: 600;}}"
        )
        label.show()
        QTimer.singleShot(duration, lambda: MessageManager.clear_message(label))

    @staticmethod
    def clear_message(label):
        label.setText(" ")
        label.setStyleSheet(
            "QLabel{background: transparent; border: none; padding: 0px;}"
        )

        
class ToastNotification(QWidget):
    STYLES = {
        "success": {"icon": "✓", "color": "#16A34A", "light": "#DCFCE7"},
        "warning": {"icon": "⚠", "color": "#F59E0B", "light": "#FEF3C7"},
        "error": {"icon": "✕", "color": "#EF4444", "light": "#FEE2E2"},
        "info": {"icon": "ℹ", "color": "#0284C7", "light": "#DBEAFE"}
    }

    @classmethod
    def show_toast(cls, parent, toast_type, title, message, duration=None):
        alert = cls(parent, toast_type, title, message, duration)
        alert.show()
        return alert

    def __init__(self, parent, toast_type, title, message, duration):
        super().__init__(parent)
        self.duration = duration
        style = self.STYLES.get(toast_type, self.STYLES["info"])

        self.resize(parent.width(), parent.height())
        self.setStyleSheet("""
            QWidget{
                background-color: rgba(15, 23, 42, 130);
            }
        """)

        # MAIN CARD
        self.card = QFrame(self)
        self.card.setFixedSize(450, 320)
        self.card.setStyleSheet(f"""
            QFrame{{
                background: white;
                border: 2px solid {style["light"]};
                border-radius: 24px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.card.setGraphicsEffect(shadow)
        self.card.move((self.width() - self.card.width()) // 2, (self.height() - self.card.height()) // 2)

        # CARD LAYOUT
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ICON
        self.icon_label = QLabel(style["icon"])
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            QLabel{{
                color: {style["color"]};
                font-size: 80px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(self.icon_label)

        # TITLE
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(f"""
            QLabel{{
                color: {style["color"]};
                font-size: 26px;
                font-weight: 700;
                border: none;
                background: transparent;
                margin-bottom: 5px;
            }}
        """)
        layout.addWidget(self.title_label)

        # MESSAGE
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("""
            QLabel{
                color: #475569;
                font-size: 16px;
                font-weight: 500;
                border: none;
                background: transparent;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(self.message_label)

        # BUTTON
        self.ok_btn = QPushButton("Got It")
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.setFixedSize(140, 45)
        self.ok_btn.setStyleSheet(f"""
            QPushButton{{
                background: {style["color"]};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 700;
            }}
            QPushButton:hover{{
                background: {style["color"]};
                opacity: 0.9;
            }}
            QPushButton:pressed{{
                padding-top: 2px;
            }}
        """)
        self.ok_btn.clicked.connect(self.close_alert)
        layout.addWidget(self.ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # SHOW ANIMATION
        self.setWindowOpacity(0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(250)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_in.start()

        # AUTO CLOSE
        if duration:
            QTimer.singleShot(duration, self.close_alert)
        else:
            QTimer.singleShot(5000, self.close_alert)

    def close_alert(self):
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(200)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.finished.connect(self.deleteLater)
        self.fade_out.start()


# CUSTOM WIDGET FOR GPAY STYLE ANIMATION
class SuccessIcon(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("✓")
        self.base_style = """
            color: white;
            background-color: #16A34A;
            border-radius: {radius}px; 
            font-weight: bold;
        """
        self.iconSize = 0 

    @pyqtProperty(int)
    def iconSize(self):
        return getattr(self, '_size', 0)

    @iconSize.setter
    def iconSize(self, value):
        self._size = value
        self.setFixedSize(QSize(value, value))
        font_size = max(10, int(value * 0.6))
        self.setStyleSheet(self.base_style.replace("{radius}", str(value // 2)))
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class SuccessIcon(QWidget):
    # Standard GPay style checkmark animation
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 70)
        self.icon_size = 0
        self.setStyleSheet("background: transparent;")

    # Standard Python method - NO pyqtProperty needed!
    def set_icon_size(self, size):
        self.icon_size = size
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background circle
        painter.setBrush(QColor("#16A34A"))
        painter.setPen(Qt.PenStyle.NoPen)
        circle_rect = QRect(0, 0, self.icon_size, self.icon_size)
        circle_rect.moveCenter(self.rect().center())
        painter.drawEllipse(circle_rect)

        # Draw checkmark when animation is advanced
        if self.icon_size > 50:
            pen = QPen(Qt.GlobalColor.white)
            pen.setWidth(4)
            # Fixes the crash error
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            
            p1 = QPoint(int(self.width()*0.3), int(self.height()*0.5))
            p2 = QPoint(int(self.width()*0.45), int(self.height()*0.65))
            p3 = QPoint(int(self.width()*0.7), int(self.height()*0.35))
            painter.drawLine(p1, p2)
            painter.drawLine(p2, p3)

class PatientSuccessModal(QWidget):
    @classmethod
    def show_modal(cls, parent, name, age, gender, department, problem, used_days, paid_days, serial_no=None, duration=5000 ):
        modal = cls(parent, name, age, gender, department, problem, used_days, paid_days, serial_no, duration)
        modal.show()

    def __init__(self, parent, name, age, gender, department, problem, used_days, paid_days, serial_no=None, duration=5000):
        super().__init__(parent)
        is_payment_due = int(used_days) > int(paid_days)
        last_day = int(paid_days) - int(used_days)
        self.duration = duration
        self.resize(parent.width(), parent.height())
        self.setStyleSheet("""
            QWidget{
                background-color: rgba(15, 23, 42, 120);
            }
        """)

        # MAIN CARD
        self.card = QFrame(self)
        self.card.setFixedSize(800, 580) # Increased height slightly to fit the box perfectly
        self.card.setStyleSheet("""
            QFrame{
                background-color: white;
                border: 1px solid #BBF7D0;
                border-radius: 24px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 35))
        self.card.setGraphicsEffect(shadow)
        self.card.move((self.width() - self.card.width()) // 2, (self.height() - self.card.height()) // 2)

        # CARD LAYOUT
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(40, 35, 40, 35)
        layout.setSpacing(15)

        # SUCCESS ANIMATION ICON
        icon_layout = QVBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_icon = SuccessIcon()
        icon_layout.addWidget(self.success_icon)
        layout.addLayout(icon_layout)

        # TITLE
        title = QLabel("Patient Check-In Successful")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel{
                color:#16A34A;
                font-size:30px;
                font-weight:700;
                border:none;
                background: transparent;
            }
        """)
        layout.addWidget(title)

        subtitle = QLabel("The patient has successfully checked in.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel{
                color:#64748B;
                font-size:16px;
                border:none;
                background: transparent;
            }
        """)
        layout.addWidget(subtitle)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background:#DCFCE7; border:none;")
        layout.addWidget(divider)

        # --- DEDICATED SERIAL NUMBER BOX ---
        if serial_no:
            # Default (Paid)
            box_bg = "#DCFCE7"
            border_color = "#22C55E"
            text_color = "#14532D"
            label_color = "#166534"

            # Payment Due (Highest Priority)
            if is_payment_due:
                box_bg = "#FEE2E2"
                border_color = "#DC2626"
                text_color = "#DC2626"
                label_color = "#B91C1C"

            # Last Day Remaining
            elif last_day == 1:
                box_bg = "#FFF7D6"
                border_color = "#FFBF00"
                text_color = "#B7791F"
                label_color = "#A16207"

            serial_box = QFrame()
            serial_box.setFixedHeight(55)
            serial_box.setStyleSheet(f"""
                QFrame {{
                    background-color: {box_bg};
                    border: 2px solid {border_color};
                    border-radius: 12px;
                }}
            """)

            serial_layout = QHBoxLayout(serial_box)
            serial_layout.setContentsMargins(20, 0, 20, 0)

            sr_title = QLabel("Serial No:")
            sr_title.setStyleSheet(f"""
                QLabel {{
                    color: {label_color};
                    font-size: 18px;
                    font-weight: 700;
                    border: none;
                    background: transparent;
                }}
            """)

            sr_value = QLabel(str(serial_no))
            sr_value.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-size: 22px;
                    font-weight: 900;
                    border: none;
                    background: transparent;
                }}
            """)

            serial_layout.addStretch()
            serial_layout.addWidget(sr_title)
            serial_layout.addSpacing(10)
            serial_layout.addWidget(sr_value)
            serial_layout.addStretch()

            layout.addWidget(serial_box)
        # INFO CARD
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame{
                background:#F8FAFC;
                border:1px solid #E2E8F0;
                border-radius:16px;
            }
        """)
        layout.addWidget(info_card)

        grid = QGridLayout(info_card)
        grid.setContentsMargins(30, 20, 30, 20)
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(15)

        def add_row(row, label, value):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("""
                QLabel{
                    color:#475569;
                    font-size:17px;
                    font-weight:500;
                    border:none;
                    background: transparent;
                }
            """)
            value_widget = QLabel(str(value))
            value_widget.setWordWrap(True)
            value_widget.setStyleSheet("""
                QLabel{
                    color:#0F172A;
                    font-size:17px;
                    font-weight:700;
                    border:none;
                    background: transparent;
                }
            """)
            grid.addWidget(label_widget, row, 0)
            grid.addWidget(value_widget, row, 1)

        # Add rest of fields directly (Serial No is already handled above)
        add_row(0, "Name", name)
        add_row(1, "Age", age)
        add_row(2, "Gender", gender)
        add_row(3, "Department", department)
        add_row(4, "Problem", problem)

        layout.addStretch()

        footer = QLabel("Timestamp and attendance data recorded.")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            QLabel{
                color:#64748B;
                font-size:15px;
                border:none;
                background: transparent;
            }
        """)
        layout.addWidget(footer)

        # SHOW ANIMATION
        self.setWindowOpacity(0)
        self.show_anim = QPropertyAnimation(self, b"windowOpacity")
        self.show_anim.setDuration(250)
        self.show_anim.setStartValue(0)
        self.show_anim.setEndValue(1)
        self.show_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # GPay Style Icon Pop-up Animation (Using QVariantAnimation)
        self.icon_anim = QVariantAnimation(self)
        self.icon_anim.setDuration(600)
        self.icon_anim.setStartValue(0)
        self.icon_anim.setEndValue(70)
        self.icon_anim.setEasingCurve(QEasingCurve.Type.OutBack) 
        self.icon_anim.valueChanged.connect(self.success_icon.set_icon_size)

        self.show_anim.start()
        QTimer.singleShot(100, self.icon_anim.start)

        # AUTO CLOSE
        QTimer.singleShot(self.duration, self.close_modal)

    def close_modal(self):
        self.hide_anim = QPropertyAnimation(self, b"windowOpacity")
        self.hide_anim.setDuration(250)
        self.hide_anim.setStartValue(1)
        self.hide_anim.setEndValue(0)
        self.hide_anim.finished.connect(self.deleteLater)
        self.hide_anim.start()