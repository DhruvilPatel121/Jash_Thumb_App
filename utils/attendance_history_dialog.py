from PyQt6.QtWidgets import (
     QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QWidget, QComboBox
)
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt
from datetime import datetime

class AttendanceHistoryDialog(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hide()
        self.setFixedSize(1100, 720)
        self.setup_ui()
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.esc_shortcut.activated.connect(self.hide)

    def setup_ui(self):
        self.setObjectName("historyCard")
        # Keep outer card border so it looks like a dialog popup
        self.setStyleSheet("""
        QFrame#historyCard{
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 16px;
        }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # 1. Title
        title_label = QLabel("Attendance History")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
        QLabel{
            color: #1E293B;
            background: transparent;
            font-size: 24px;
            font-weight: bold;
        }
        """)
        main_layout.addWidget(title_label)

        info_frame = QFrame()
        info_frame.setFixedHeight(65) 
        
        info_frame.setStyleSheet("""
        QFrame {
            background-color: #F8FAFC; 
            border: 1px solid #E2E8F0; 
            border-radius: 12px;
        }
        """)
        
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(25, 0, 25, 0) 

        label_style_title = "color: #64748B; font-size: 15px; border: none; background: transparent;"
        self.paid_days_label = QLabel("0")
        self.used_days_label = QLabel("0")
        self.balance_days_label = QLabel("0")
        name_title = QLabel("Patient: ")
        name_title.setStyleSheet(label_style_title)
        
        self.name_label = QLabel("Patient Name")
        self.name_label.setStyleSheet("color: #0F172A; font-size: 20px; font-weight: bold; border: none; background: transparent;")

        # Visits Section 
        visits_title = QLabel("Total Visits: ")
        visits_title.setStyleSheet(label_style_title)
        
        self.visits_label = QLabel("0")
        self.visits_label.setStyleSheet("color: #4F46E5; font-size: 22px; font-weight: bold; border: none; background: transparent;")

        combo_style = """
            QComboBox {
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 5px 15px;
                font-size: 15px;
                font-weight: 600;
                color: #1E293B;
                background-color: #FFFFFF;
                min-width: 120px;
                min-height: 35px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #1E293B; /* અહી કલર એડ કર્યો છે જેથી લિસ્ટના નામ દેખાય */
                border: 1px solid #CBD5E1;
                selection-background-color: #EEF2FF;
                selection-color: #4F46E5;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                color: #1E293B; /* લિસ્ટની દરેક આઈટમનો કલર ડાર્ક કર્યો */
                min-height: 35px; /* લિસ્ટમાં આઇટમ્સ વચ્ચે થોડી જગ્યા વધારી */
            }
        """
        self.month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.month_combo.addItems(months)
        self.month_combo.setMaxVisibleItems(12)
        self.month_combo.setStyleSheet(combo_style)
        self.month_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.year_combo = QComboBox()
        current_year = datetime.now().year
        start_year = 2025 
        max_year = current_year + 10 
        years = [str(y) for y in range(start_year, max_year + 1)]
        self.year_combo.addItems(years)
        self.year_combo.setMaxVisibleItems(7)
        self.year_combo.setStyleSheet(combo_style)
        self.year_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.month_combo.currentIndexChanged.connect(self.filter_and_display)
        self.year_combo.currentIndexChanged.connect(self.filter_and_display)

        info_layout.addWidget(name_title)
        info_layout.addWidget(self.name_label)
        
        info_layout.addStretch() 
        
        info_layout.addWidget(visits_title)
        info_layout.addWidget(self.visits_label)
        
        info_layout.addStretch() 
        
        info_layout.addWidget(self.month_combo)
        info_layout.addSpacing(10)
        info_layout.addWidget(self.year_combo)

        main_layout.addWidget(info_frame)

        
        self.grid_frame = QFrame()
        self.grid_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        
        self.grid_layout = QGridLayout(self.grid_frame)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setSpacing(12) 

        self.day_time_labels = {}

        for day in range(1, 32):
            day_card = QFrame()
            day_card.setMinimumHeight(100) 
            day_card.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                }
            """)
            
            card_layout = QVBoxLayout(day_card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(0)
            
            date_lbl = QLabel(str(day))
            date_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            date_lbl.setFixedHeight(45) 
            date_lbl.setStyleSheet("""
                QLabel {
                    background-color: #EEF2FF;
                    color: #4F46E5;
                    font-weight: bold;
                    font-size: 18px; 
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    border-bottom: 1px solid #CBD5E1;
                }
            """)
            
            time_lbl = QLabel("")
            time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            time_lbl.setMinimumHeight(60) 
            time_lbl.setStyleSheet("""
                QLabel {
                    color: #059669;
                    font-size: 14px; 
                    font-weight: bold;
                    background-color: transparent;
                    border: none;
                }
            """)
            
            card_layout.addWidget(date_lbl)
            card_layout.addWidget(time_lbl)
            
            row = (day - 1) // 8
            col = (day - 1) % 8
            self.grid_layout.addWidget(day_card, row, col)
            
            self.day_time_labels[day] = time_lbl

        main_layout.addWidget(self.grid_frame)

        # 4. Footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.setFixedSize(140, 50) 
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        close_button.setStyleSheet("""
        QPushButton{
            background-color: #DBEAFE; 
            border: none;
            border-radius: 10px;
            font-size: 16px;
            color: #1D4ED8; 
            font-weight: bold;
        }
        QPushButton:hover{ 
            background-color: #BFDBFE; 
        }
        QPushButton:pressed{ 
            border: 1px solid #2563EB; 
            padding-top: 3px; 
            padding-left: 3px; 
        }
        """)
        close_button.clicked.connect(self.hide)

        footer_layout.addWidget(close_button)
        main_layout.addLayout(footer_layout)

    def show_dialog(self, patient_name, history):
        self.load_history(patient_name, history)
        parent = self.parent()

        if parent:
            self.move(
                (parent.width() - self.width()) // 2,
                (parent.height() - self.height()) // 2
            )
        self.raise_()
        self.show()

    def load_history(self, patient_name, history):
        self.name_label.setText(patient_name)
        
        self.full_history = history 
        
        self.month_combo.blockSignals(True)
        self.year_combo.blockSignals(True)

        now = datetime.now()
        self.month_combo.setCurrentIndex(now.month - 1)
        self.year_combo.setCurrentText(str(now.year))
        
        self.month_combo.blockSignals(False)
        self.year_combo.blockSignals(False)

        self.filter_and_display()

    def filter_and_display(self):
        for day, label in self.day_time_labels.items():
            label.setText("")

        selected_month = self.month_combo.currentIndex() + 1
        selected_year = int(self.year_combo.currentText())

        monthly_visits = 0

        if hasattr(self, 'full_history'):
            for record in self.full_history:
                raw_date = str(record.get("attendance_date", ""))
                if raw_date and raw_date != "None":
                    try:
                        date_obj = datetime.strptime(raw_date[:10], "%Y-%m-%d")
                        
                        if date_obj.month == selected_month and date_obj.year == selected_year:
                            day = date_obj.day
                            raw_time = str(record.get("check_in_time", ""))
                            
                            display_time = raw_time 
                            if raw_time:
                                try:
                                    time_obj = datetime.strptime(raw_time, "%H:%M:%S")
                                    display_time = time_obj.strftime("%I:%M %p") 
                                except ValueError:
                                    try:
                                        time_obj = datetime.strptime(raw_time, "%H:%M")
                                        display_time = time_obj.strftime("%I:%M %p")
                                    except ValueError:
                                        pass 
                            
                            # ---- NAVU PAYMENT LOGIC AHIYA THI SHARU THAY CHE ----
                            used_days = int(record.get("used_days", 0) or 0)
                            paid_days = int(record.get("paid_days", 0) or 0)
                            
                            if used_days <= paid_days:
                                # Payment Done - Green Label
                                status_html = "<br><span style='background-color: #DCFCE7; color: #16A34A; padding: 2px 6px; border-radius: 4px; font-size: 11px;'>Paid</span>"
                                time_color = "#16A34A" 
                            else:
                                # Payment Due - Red Label
                                status_html = "<br><span style='background-color: #FEE2E2; color: #DC2626; padding: 2px 6px; border-radius: 4px; font-size: 11px;'>Due</span>"
                                time_color = "#DC2626"
                                
                            # Final text HTML format ma
                            final_text = f"<span style='color: {time_color}; font-size: 13px;'>{display_time}</span>{status_html}"
                            # --------------------------------------------------------
                            
                            if day in self.day_time_labels:
                                self.day_time_labels[day].setTextFormat(Qt.TextFormat.RichText) # Rich text enable karyu
                                self.day_time_labels[day].setText(final_text)
                                monthly_visits += 1 
                    except ValueError:
                        pass
        
        self.visits_label.setText(str(monthly_visits))


