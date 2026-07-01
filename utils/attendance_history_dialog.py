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
        self.setFixedSize(1200, 860)
        self.setup_ui()
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.esc_shortcut.activated.connect(self.hide)

    def setup_ui(self):
        self.setObjectName("historyCard")
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
            font-size: 26px; /* ફોન્ટ મોટા કર્યા */
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

        label_style_title = "color: #64748B; font-size: 16px; border: none; background: transparent;"
        self.paid_days_label = QLabel("0")
        self.used_days_label = QLabel("0")
        self.balance_days_label = QLabel("0")
        name_title = QLabel("Patient: ")
        name_title.setStyleSheet(label_style_title)
        
        self.name_label = QLabel("Patient Name")
        self.name_label.setStyleSheet("color: #0F172A; font-size: 20px; font-weight: bold; border: none; background: transparent;")

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
                min-height: 38px; /* કોમ્બો બોક્સ મોટા કર્યા */
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #1E293B; 
                border: 1px solid #CBD5E1;
                selection-background-color: #EEF2FF;
                selection-color: #4F46E5;
                outline: none;
            }
            QComboBox QAbstractItemView::item { min-height: 35px; }
        """
        self.month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.month_combo.addItems(months)
        self.month_combo.setMaxVisibleItems(12)
        self.month_combo.setStyleSheet(combo_style)
        self.month_combo.setCursor(Qt.CursorShape.PointingHandCursor)

        self.year_combo = QComboBox()
        current_year = datetime.now().year
        years = [str(y) for y in range(2025, current_year + 11)]
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

        # આ નવી ડિક્શનરી છે જેમાં આખું કાર્ડ અને લેબલ સ્ટોર થશે
        self.day_cards = {} 

        for day in range(1, 32):
            day_card = QFrame()
            day_card.setMinimumHeight(130) # બોક્સની હાઈટ 100 થી વધારીને 130 કરી 
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
            time_lbl.setMinimumHeight(75) # ટાઈમ માટે જગ્યા વધારી 
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
            
            # આખા બોક્સનું એક્સેસ સ્ટોર કર્યું
            self.day_cards[day] = {
                'card': day_card,
                'date_lbl': date_lbl,
                'time_lbl': time_lbl
            }

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
        QPushButton:hover{ background-color: #BFDBFE; }
        QPushButton:pressed{ border: 1px solid #2563EB; padding-top: 3px; padding-left: 3px; }
        """)
        close_button.clicked.connect(self.hide)

        footer_layout.addWidget(close_button)
        main_layout.addLayout(footer_layout)

    def show_dialog(self, patient_name, history, created_at=None, consultancy_fees=0):
        self.load_history(patient_name, history, created_at, consultancy_fees)
        parent = self.parent()

        if parent:
            self.move(
                (parent.width() - self.width()) // 2,
                (parent.height() - self.height()) // 2
            )
        self.raise_()
        self.show()

    def load_history(self, patient_name, history, created_at, consultancy_fees):
        self.name_label.setText(patient_name)
        
        self.full_history = history 
        self.created_at = created_at
        self.consultancy_fees = consultancy_fees
        
        self.month_combo.blockSignals(True)
        self.year_combo.blockSignals(True)

        now = datetime.now()
        self.month_combo.setCurrentIndex(now.month - 1)
        self.year_combo.setCurrentText(str(now.year))
        
        self.month_combo.blockSignals(False)
        self.year_combo.blockSignals(False)

        self.filter_and_display()

    def filter_and_display(self):
        DEFAULT_CARD_STYLE = """
            QFrame { background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; }
        """
        DEFAULT_DATE_STYLE = """
            QLabel { background-color: #EEF2FF; color: #4F46E5; font-weight: bold; font-size: 18px; border-top-left-radius: 7px; border-top-right-radius: 7px; border-bottom: 1px solid #CBD5E1; }
        """
        PURPLE_CARD_STYLE = """
            QFrame { background-color: #FAF5FF; border: 2px solid #D8B4FE; border-radius: 8px; }
        """
        PURPLE_DATE_STYLE = """
            QLabel { background-color: #F3E8FF; color: #9333EA; font-weight: bold; font-size: 18px; border-top-left-radius: 6px; border-top-right-radius: 6px; border-bottom: 1px solid #D8B4FE; }
        """

        for day, widgets in self.day_cards.items():
            widgets['time_lbl'].setText("")
            widgets['card'].setStyleSheet(DEFAULT_CARD_STYLE)
            widgets['date_lbl'].setStyleSheet(DEFAULT_DATE_STYLE)

        selected_month = self.month_combo.currentIndex() + 1
        selected_year = int(self.year_combo.currentText())
        monthly_visits = 0
        
        day_data = {day: {'time': None, 'time_color': None, 'is_consulting': False, 'status_html': None} for day in range(1, 32)}
        
        # Consulting 
        if hasattr(self, 'created_at') and self.created_at:
            fees = int(self.consultancy_fees) if self.consultancy_fees else 0
            if fees > 0:
                if isinstance(self.created_at, str):
                    try:
                        reg_date = datetime.strptime(self.created_at[:10], "%Y-%m-%d")
                    except ValueError:
                        reg_date = None
                else:
                    reg_date = self.created_at
                
                if reg_date and reg_date.month == selected_month and reg_date.year == selected_year:
                    day_data[reg_date.day]['is_consulting'] = True

        # Attendance 
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
                            
                            used_days = int(record.get("used_days", 0) or 0)
                            paid_days = int(record.get("paid_days", 0) or 0)
                            
                            if used_days <= paid_days:
                                status_html = "<span style='background-color: #DCFCE7; color: #16A34A; padding: 3px 8px; border-radius: 4px; font-size: 12px;'>Paid</span>"
                                time_color = "#16A34A" 
                            else:
                                status_html = "<span style='background-color: #FEE2E2; color: #DC2626; padding: 3px 8px; border-radius: 4px; font-size: 12px;'>Due</span>"
                                time_color = "#DC2626"
                            
                            day_data[day]['time'] = display_time
                            day_data[day]['time_color'] = time_color
                            day_data[day]['status_html'] = status_html
                            monthly_visits += 1 
                    except ValueError:
                        pass
        
        for day, widgets in self.day_cards.items():
            data = day_data[day]
            elements = []
            
            if data['is_consulting']:
                widgets['card'].setStyleSheet(PURPLE_CARD_STYLE)
                widgets['date_lbl'].setStyleSheet(PURPLE_DATE_STYLE)

            if data['is_consulting']:
                elements.append("<span style='color: #9333EA; font-size: 13px; font-weight: bold;'>Consulting</span>")
                
            if data['time']:
                elements.append(f"<span style='color: {data['time_color']}; font-size: 14px; font-weight: bold;'>{data['time']}</span>")
            
            
            if data['status_html']:
                elements.append(data['status_html'])
            
            if elements:
                final_text = "<br>".join(elements)
                widgets['time_lbl'].setTextFormat(Qt.TextFormat.RichText)
                widgets['time_lbl'].setText(final_text)
        
        self.visits_label.setText(str(monthly_visits))