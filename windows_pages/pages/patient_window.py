from PyQt6.QtWidgets import (QWidget,QHBoxLayout,QVBoxLayout,QPushButton,QFrame,QLabel,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QLineEdit)
from PyQt6.QtCore import Qt
from utils.update_patient_dialog import UpdatePatientDialog
from utils.delete_patient_dialog import DeletePatientDialog
from database.patient_repository import PatientRepository
from utils.session import Session


class PatientPage(QWidget):

    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.patient_repository = PatientRepository()
        self.setup_ui()

    def setup_ui(self):
        # Main Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        # Content Area
        self.content_area = QFrame()
        self.content_area.setStyleSheet("""
        QFrame{
            background-color: #F8FAFC;
        }
        """)
        self.main_layout.addWidget(self.content_area)

        # Content Layout
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(20)
        self.content_area.setLayout(self.content_layout)

        # Page Title
        self.page_title = QLabel("Patient Management")
        self.page_title.setStyleSheet("""
        QLabel{
            color: #1E293B;
            font-size: 28px;
            font-weight: bold;
        }
        """)
        self.content_layout.addWidget(self.page_title)

        # Search Layout
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patient...")
        self.search_input.setFixedHeight(45)
        self.search_input.setStyleSheet("""
        QLineEdit{
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding-left: 15px;
            font-size: 14px;
            color: #334155;
        }
        QLineEdit:focus{
            border: 2px solid #5C62D6;
        }
        """)
        self.search_layout.addWidget(self.search_input)
        self.search_input.textChanged.connect(self.search_patients)
        self.content_layout.addLayout(self.search_layout)

        # Table Container
        self.table_frame = QFrame()
        self.table_frame.setStyleSheet("""
        QFrame{
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
        }
        """)
        self.content_layout.addWidget(self.table_frame)

        # Table Layout
        self.table_layout = QVBoxLayout()
        self.table_layout.setContentsMargins(10, 0, 10, 10)
        self.table_frame.setLayout(self.table_layout)

        # Patient Table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(9)
        self.patient_table.setHorizontalHeaderLabels([
            "#", "Name", "Mobile", "Age", "Gender", 
            "Department", "Problem", "Created Date", "Actions"
        ])

        self.patient_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.patient_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.patient_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.patient_table.setShowGrid(False)
        self.patient_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.patient_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.patient_table.verticalHeader().setVisible(False)
        self.patient_table.verticalHeader().setDefaultSectionSize(70)
        self.patient_table.setFrameShape(QFrame.Shape.NoFrame)
        self.patient_table.horizontalHeader().setHighlightSections(False)
        self.patient_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        self.patient_table.setStyleSheet("""
        QTableWidget{
            background-color: #FFFFFF;
            border: none;
            color: #334155;
            font-size: 14px;
        }

        QTableWidget::item{
            padding: 8px;
            border-bottom: 1px solid #EDF2F7;
        }

        QHeaderView::section{
            background-color: #FFFFFF;
            color: #475569;
            border: none;
            padding: 18px;
            font-size: 14px;
            font-weight: 600;
        }

        /* VERTICAL SCROLLBAR */

        QScrollBar:vertical{
            background: transparent;
            width: 10px;
            margin: 0px;
            border: none;
        }

        QScrollBar::handle:vertical{
            background: #CBD5E1;
            min-height: 40px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical:hover{
            background: #94A3B8;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical{
            height: 0px;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical{
            background: transparent;
        }

        /* HORIZONTAL SCROLLBAR */

        QScrollBar:horizontal{
            background: transparent;
            height: 10px;
            margin: 0px;
            border: none;
        }

        QScrollBar::handle:horizontal{
            background: #CBD5E1;
            min-width: 40px;
            border-radius: 5px;
        }

        QScrollBar::handle:horizontal:hover{
            background: #94A3B8;
        }

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal{
            width: 0px;
        }

        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal{
            background: transparent;
        }
        """)

        self.table_layout.addWidget(self.patient_table)

        header = self.patient_table.horizontalHeader()
        header.setFixedHeight(60)

        self.patient_table.setColumnWidth(0, 60)
        self.patient_table.setColumnWidth(3, 80)
        self.patient_table.setColumnWidth(4, 100)
        self.patient_table.setColumnWidth(8, 180)

        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Department
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Problem
        self.update_dialog = UpdatePatientDialog(self.content_area)
        self.update_dialog.patient_updated.connect(self.load_patients)
        self.delete_dialog = DeletePatientDialog(self.content_area)
        self.delete_dialog.patient_deleted.connect(self.load_patients)


        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(0, 15, 0, 0)
        
        self.footer_label = QLabel("Handicraft By ShivVilon Solution ")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setStyleSheet("""
            QLabel {
                color: #94A3B8; 
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
        """)
        self.footer_layout.addWidget(self.footer_label)
        self.content_layout.addLayout(self.footer_layout)


    def load_patients(self, search_text=None):
        patients = self.patient_repository.get_all_by_organization(
            Session.organization_id,
            search_text
        )

        self.patient_table.setRowCount(len(patients))

        for row, patient in enumerate(patients):
            
            # Helper function for setting cell
            def set_item(col, text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.patient_table.setItem(row, col, item)

            set_item(0, row + 1)
            set_item(1, patient.get("name", ""))
            set_item(2, patient.get("mobile", ""))
            set_item(3, patient.get("age", ""))
            set_item(4, patient.get("gender", ""))
            set_item(5, patient.get("department", "--"))
            set_item(6, patient.get("problem", ""))

            created_date = ""
            if patient.get("created_at"):
                created_date = patient["created_at"].strftime("%d-%m-%Y")
            set_item(7, created_date)

            self.create_action_buttons(row, patient)

    def create_action_buttons(self, row, patient):
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        update_btn = QPushButton("✏️")
        delete_btn = QPushButton("🗑️")

        update_btn.setFixedSize(40, 40)
        delete_btn.setFixedSize(40, 40)
        update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        update_btn.setStyleSheet("""
        QPushButton{
            background-color:#DBEAFE;
            border:none;
            border-radius:8px;
            font-size:16px;
        }
        QPushButton:hover{ background-color:#BFDBFE; }
        """)

        delete_btn.setStyleSheet("""
        QPushButton{
            background-color:#FEE2E2;
            border:none;
            border-radius:8px;
            font-size:16px;
        }
        QPushButton:hover{ background-color:#FECACA; }
        """)

        layout.addWidget(update_btn)
        layout.addWidget(delete_btn)
        container.setLayout(layout)

        self.patient_table.setCellWidget(row, 8, container)

        # Connecting signals to the Dialog Classes
        update_btn.clicked.connect(lambda _, p=patient: self.update_dialog.show_form(p))
        delete_btn.clicked.connect(lambda _, p=patient: self.delete_dialog.show_dialog(p))

    def search_patients(self):
        search_text = self.search_input.text().strip()
        self.load_patients(search_text)