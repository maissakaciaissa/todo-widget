from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

import json
import os
from datetime import date

class TodoWidget(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.tasks = self.load_tasks()
        self.drag_pos = None
        self.drag_edge = None
        self.drag_offset = None
        self.setMouseTracking(True)
        # load custom fonts
        qtg.QFontDatabase.addApplicationFont("fonts/Sarina-Regular.ttf")
        qtg.QFontDatabase.addApplicationFont("fonts/Righteous-Regular.ttf")
        self.setWindowTitle("my tasks ✦")

        self.resize(380, 400)    
        self.setWindowFlags(qtc.Qt.FramelessWindowHint)
        self.setAttribute(qtc.Qt.WA_TranslucentBackground)
        
        self.layout = qtw.QVBoxLayout()
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        self.container = qtw.QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(28, 28, 30, 0.92);
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        
        self.container_layout = qtw.QVBoxLayout()
        self.container_layout.setContentsMargins(20, 20, 20, 20)
        self.container_layout.setSpacing(10)
        self.container.setLayout(self.container_layout)
        self.layout.addWidget(self.container)

        # date navigation
        self.viewing_date = date.today()
        
        nav_layout = qtw.QHBoxLayout()
        
        self.prev_btn = qtw.QPushButton("←")
        self.next_btn = qtw.QPushButton("→")
        self.date_label = qtw.QLabel()
        
        nav_btn_style = """
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255,255,255,0.5);
                font-size: 16px;
                font-family: Sarina;
            }
            QPushButton:hover {
                color: rgba(255,255,255,0.9);
            }
        """
        self.prev_btn.setStyleSheet(nav_btn_style)
        self.next_btn.setStyleSheet(nav_btn_style)
        self.date_label.setStyleSheet("""
            color: rgba(255,255,255,0.85);
            font-size: 13px;
            border: none;
            font-family: Sarina;                               
                            
        """)
        self.date_label.setAlignment(qtc.Qt.AlignCenter)
        
        self.prev_btn.clicked.connect(self.go_prev)
        self.next_btn.clicked.connect(self.go_next)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.date_label)
        nav_layout.addWidget(self.next_btn)
        self.container_layout.addLayout(nav_layout)



        input_layout = qtw.QHBoxLayout()
        
        self.task_input = qtw.QLineEdit()
        self.task_input.setFixedHeight(34)
        self.task_input.setPlaceholderText("add a task...")
        self.task_input.setStyleSheet("""
           QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                color: rgba(255,255,255,0.85);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 6px 10px;
                font-family: Righteous;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        self.add_btn = qtw.QPushButton("+")
        self.add_btn.setFixedSize(35, 35)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(232, 196, 208, 0.15);
                color: #e8c4d0;
                border: 1px solid rgba(232, 196, 208, 0.3);
                border-radius: 10px;
                font-size: 20px;
                font-family: Righteous;
            }
            QPushButton:hover {
                background-color: rgba(232, 196, 208, 0.3);
            }
        """)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_btn)
        self.container_layout.addLayout(input_layout)

        self.scroll = qtw.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 4px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: rgba(232, 196, 208, 0.3);
                border-radius: 2px;
            }
        """)

        self.scroll_widget = qtw.QWidget()
        self.scroll_widget.setStyleSheet("background: transparent;")
        self.tasks_layout = qtw.QVBoxLayout()
        self.tasks_layout.setAlignment(qtc.Qt.AlignTop)
        self.tasks_layout.setSpacing(8)
        self.scroll_widget.setLayout(self.tasks_layout)
        self.scroll.setWidget(self.scroll_widget)
        self.container_layout.addWidget(self.scroll)

        self.add_btn.clicked.connect(self.add_task)
        self.task_input.returnPressed.connect(self.add_task)
        self.update_date_label()

        # back to today button
        self.today_btn = qtw.QPushButton("back to today")
        self.today_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255,255,255,0.6);
                font-family: Righteous;
                font-size: 14px;
            }
            QPushButton:hover {
                color: rgba(255,255,255,0.9);
            }
        """)
        self.today_btn.clicked.connect(self.go_today)
        self.container_layout.addWidget(self.today_btn)

        # resize grip bottom right corner
        self.grip = qtw.QSizeGrip(self)
        self.grip.setStyleSheet("background: transparent;")
        self.grip.resize(16, 16)
        self.render_tasks()
    

    def go_prev(self):
        from datetime import timedelta
        self.viewing_date -= timedelta(days=1)
        self.update_date_label()
        self.render_tasks()

    def go_next(self):
        from datetime import timedelta
        self.viewing_date += timedelta(days=1)
        self.update_date_label()
        self.render_tasks()

    def go_today(self):
        self.viewing_date = date.today()
        self.update_date_label()
        self.render_tasks()

    def update_date_label(self):
        formatted = self.viewing_date.strftime("%A, %b %d")
        self.date_label.setText(formatted)

    def toggle_task(self, index):
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save_tasks()
        self.render_tasks()

    def delete_task(self, index):
        self.tasks.pop(index)
        self.save_tasks()
        self.render_tasks()

    def render_tasks(self):
        for i in reversed(range(self.tasks_layout.count())):
            self.tasks_layout.itemAt(i).widget().deleteLater()
        
        viewing = str(self.viewing_date)
        for index, task in enumerate(self.tasks):
            if task["date"] == viewing:
                row = qtw.QWidget()
                row.setStyleSheet("background: transparent;")
                row_layout = qtw.QHBoxLayout()
                row_layout.setContentsMargins(0, 0, 0, 0)
                row.setLayout(row_layout)

                checkbox = qtw.QCheckBox()
                checkbox.setChecked(task["done"])
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        border-radius: 10px;
                        border: 1px solid rgba(232, 196, 208, 0.4);
                        background: transparent;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #e8c4d0;
                    }
                """)
                checkbox.stateChanged.connect(lambda state, i=index: self.toggle_task(i))

                task_label = qtw.QLabel(task["text"])
                task_label.setStyleSheet(f"""
                    color: {"rgba(232,196,208,0.4)" if task["done"] else "#e8c4d0"};
                    font-family: Righteous;
                    font-size: 17px;
                    text-decoration: {"line-through" if task["done"] else "none"};
                    border: none;
                """)

                del_btn = qtw.QPushButton("×")
                del_btn.setFixedSize(24, 24)
                del_btn.setStyleSheet("""
                    QPushButton {
                        color: rgba(232, 196, 208, 0.4);
                        background: transparent;
                        border: none;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        color: #e8c4d0;
                    }
                """)
                del_btn.clicked.connect(lambda checked, i=index: self.delete_task(i))

                row_layout.addWidget(checkbox)
                row_layout.addWidget(task_label)
                row_layout.addStretch()
                row_layout.addWidget(del_btn)
                self.tasks_layout.addWidget(row)

    def add_task(self):
        text = self.task_input.text().strip()
        if text == "":
            return
        new_task = {
            "text": text,
            "done": False,
            "date": str(self.viewing_date)
        }
        self.tasks.append(new_task)
        self.save_tasks()
        self.task_input.clear()
        self.render_tasks()

    def load_tasks(self):
        if os.path.exists("tasks.json"):
            with open("tasks.json", "r") as f:
                content = f.read()
                if content.strip() == "":
                    return []
                tasks = json.loads(content)
                
                today = str(date.today())
                for task in tasks:
                    if task["done"] == False and task["date"] < today:
                        task["date"] = today
                
                with open("tasks.json", "w") as f:
                    json.dump(tasks, f, indent=4)
                
                return tasks
        return []
   
    def save_tasks(self):
        with open("tasks.json", "w") as f:
            json.dump(self.tasks, f, indent=4)

    def mousePressEvent(self, event):
        self.drag_pos = event.globalPos()
        self.drag_rect = self.geometry()
        self.drag_edge = self.get_edge(event.pos())
        if self.drag_edge is None:
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == qtc.Qt.LeftButton:
            if self.drag_edge is None:
                self.move(event.globalPos() - self.drag_offset)
            else:
                self.do_resize(event.globalPos())
        else:
            self.update_cursor(event.pos())

    def mouseReleaseEvent(self, event):
        self.drag_edge = None
        self.setCursor(qtg.QCursor(qtc.Qt.ArrowCursor))

    def get_edge(self, pos):
        margin = 15
        rect = self.rect()
        left = pos.x() < margin
        right = pos.x() > rect.width() - margin
        top = pos.y() < margin
        bottom = pos.y() > rect.height() - margin
        if top and left: return "top_left"
        if top and right: return "top_right"
        if bottom and left: return "bottom_left"
        if bottom and right: return "bottom_right"
        if left: return "left"
        if right: return "right"
        if top: return "top"
        if bottom: return "bottom"
        return None

    def update_cursor(self, pos):
        edge = self.get_edge(pos)
        cursors = {
            "left": qtc.Qt.SizeHorCursor,
            "right": qtc.Qt.SizeHorCursor,
            "top": qtc.Qt.SizeVerCursor,
            "bottom": qtc.Qt.SizeVerCursor,
            "top_left": qtc.Qt.SizeFDiagCursor,
            "bottom_right": qtc.Qt.SizeFDiagCursor,
            "top_right": qtc.Qt.SizeBDiagCursor,
            "bottom_left": qtc.Qt.SizeBDiagCursor,
        }
        cursor = cursors.get(edge, qtc.Qt.ArrowCursor)
        self.setCursor(qtg.QCursor(cursor))

    def do_resize(self, global_pos):
        delta = global_pos - self.drag_pos
        rect = self.drag_rect
        min_w, min_h = self.minimumWidth(), self.minimumHeight()

        if self.drag_edge == "right":
            self.setGeometry(rect.x(), rect.y(), max(min_w, rect.width() + delta.x()), rect.height())
        elif self.drag_edge == "bottom":
            self.setGeometry(rect.x(), rect.y(), rect.width(), max(min_h, rect.height() + delta.y()))
        elif self.drag_edge == "left":
            self.setGeometry(rect.x() + delta.x(), rect.y(), max(min_w, rect.width() - delta.x()), rect.height())
        elif self.drag_edge == "top":
            self.setGeometry(rect.x(), rect.y() + delta.y(), rect.width(), max(min_h, rect.height() - delta.y()))
        elif self.drag_edge == "bottom_right":
            self.setGeometry(rect.x(), rect.y(), max(min_w, rect.width() + delta.x()), max(min_h, rect.height() + delta.y()))
        elif self.drag_edge == "bottom_left":
            self.setGeometry(rect.x() + delta.x(), rect.y(), max(min_w, rect.width() - delta.x()), max(min_h, rect.height() + delta.y()))
        elif self.drag_edge == "top_right":
            self.setGeometry(rect.x(), rect.y() + delta.y(), max(min_w, rect.width() + delta.x()), max(min_h, rect.height() - delta.y()))
        elif self.drag_edge == "top_left":
            self.setGeometry(rect.x() + delta.x(), rect.y() + delta.y(), max(min_w, rect.width() - delta.x()), max(min_h, rect.height() - delta.y()))