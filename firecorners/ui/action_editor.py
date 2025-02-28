import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QComboBox, QLineEdit, QTextEdit, QFileDialog,
                           QListWidget, QListWidgetItem, QMessageBox, QStackedWidget,
                           QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QPalette

class ActionListItem(QFrame):
    def __init__(self, action_type, value, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setAutoFillBackground(True)
        self.setObjectName("actionListItem")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        
        # Action type label with icon
        type_label = QLabel(action_type.title())
        type_label.setObjectName("actionTypeLabel")
        layout.addWidget(type_label)
        
        # Value label with ellipsis if too long
        value_label = QLabel(value[:50] + "..." if len(value) > 50 else value)
        value_label.setObjectName("actionValueLabel")
        value_label.setWordWrap(True)
        layout.addWidget(value_label)

class ActionEditor(QWidget):
    action_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title and description
        title = QLabel("Corner Actions")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        description = QLabel("Configure actions to be triggered when your cursor reaches this corner.")
        description.setWordWrap(True)
        description.setObjectName("description")
        layout.addWidget(title)
        layout.addWidget(description)
        
        # Action list with custom styling
        list_container = QFrame()
        list_container.setObjectName("actionListContainer")
        list_layout = QVBoxLayout(list_container)
        
        self.action_list = QListWidget()
        self.action_list.setObjectName("actionList")
        self.action_list.currentRowChanged.connect(self._on_action_selected)
        list_layout.addWidget(self.action_list)
        layout.addWidget(list_container)
        
        # Action type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Action Type:")
        type_label.setStyleSheet("font-weight: bold;")
        self.type_combo = QComboBox()
        self.type_combo.setObjectName("actionTypeCombo")
        self.type_combo.addItems(["URL", "Application", "Shell Command", "AppleScript"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Action value input stack
        self.value_stack = QStackedWidget()
        
        # URL input
        url_widget = QWidget()
        url_layout = QVBoxLayout(url_widget)
        url_layout.setContentsMargins(0, 0, 0, 0)
        self.url_input = QLineEdit()
        self.url_input.setObjectName("actionInput")
        self.url_input.setPlaceholderText("Enter URL (e.g., https://www.example.com)")
        url_layout.addWidget(QLabel("URL:"))
        url_layout.addWidget(self.url_input)
        self.value_stack.addWidget(url_widget)
        
        # Application input
        app_widget = QWidget()
        app_layout = QVBoxLayout(app_widget)
        app_layout.setContentsMargins(0, 0, 0, 0)
        self.app_input = QLineEdit()
        self.app_input.setObjectName("actionInput")
        self.app_input.setPlaceholderText("Select an application...")
        self.app_browse = QPushButton("Browse...")
        self.app_browse.setObjectName("browseButton")
        self.app_browse.clicked.connect(self._browse_application)
        app_layout.addWidget(QLabel("Application:"))
        app_layout.addWidget(self.app_input)
        app_layout.addWidget(self.app_browse)
        self.value_stack.addWidget(app_widget)
        
        # Shell command input
        shell_widget = QWidget()
        shell_layout = QVBoxLayout(shell_widget)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        self.shell_input = QTextEdit()
        self.shell_input.setObjectName("actionInput")
        self.shell_input.setPlaceholderText("Enter shell command...")
        shell_layout.addWidget(QLabel("Shell Command:"))
        shell_layout.addWidget(self.shell_input)
        example_label = QLabel("Example: open -a 'Safari.app'")
        example_label.setObjectName("exampleLabel")
        shell_layout.addWidget(example_label)
        self.value_stack.addWidget(shell_widget)
        
        # AppleScript input
        script_widget = QWidget()
        script_layout = QVBoxLayout(script_widget)
        script_layout.setContentsMargins(0, 0, 0, 0)
        self.script_input = QTextEdit()
        self.script_input.setObjectName("actionInput")
        self.script_input.setPlaceholderText("Enter AppleScript...")
        script_layout.addWidget(QLabel("AppleScript:"))
        script_layout.addWidget(self.script_input)
        example_label = QLabel("Example: tell application \"Safari\" to activate")
        example_label.setObjectName("exampleLabel")
        script_layout.addWidget(example_label)
        self.value_stack.addWidget(script_widget)
        
        layout.addWidget(self.value_stack)
        
        # Add and Remove buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.add_button = QPushButton("Add Action")
        self.add_button.setObjectName("addButton")
        
        self.remove_button = QPushButton("Remove Action")
        self.remove_button.setObjectName("removeButton")
        
        self.add_button.clicked.connect(self._add_action)
        self.remove_button.clicked.connect(self._remove_action)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)
        
        # Set initial state
        self._on_type_changed("URL")
        self.remove_button.setEnabled(False)
    
    def _on_type_changed(self, action_type):
        if action_type == "URL":
            self.value_stack.setCurrentIndex(0)
        elif action_type == "Application":
            self.value_stack.setCurrentIndex(1)
        elif action_type == "Shell Command":
            self.value_stack.setCurrentIndex(2)
        elif action_type == "AppleScript":
            self.value_stack.setCurrentIndex(3)
    
    def _browse_application(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Applications (*.app)")
        file_dialog.setDirectory("/Applications")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.app_input.setText(selected_files[0])
    
    def _add_action(self):
        action_type = self.type_combo.currentText()
        value = ""
        
        if action_type == "URL":
            value = self.url_input.text().strip()
            if not value:
                QMessageBox.warning(self, "Invalid Input", "Please enter a URL")
                return
            self.url_input.clear()
        elif action_type == "Application":
            value = self.app_input.text().strip()
            if not value:
                QMessageBox.warning(self, "Invalid Input", "Please select an application")
                return
            self.app_input.clear()
        elif action_type == "Shell Command":
            value = self.shell_input.toPlainText().strip()
            if not value:
                QMessageBox.warning(self, "Invalid Input", "Please enter a shell command")
                return
            self.shell_input.clear()
        elif action_type == "AppleScript":
            value = self.script_input.toPlainText().strip()
            if not value:
                QMessageBox.warning(self, "Invalid Input", "Please enter an AppleScript")
                return
            self.script_input.clear()
        
        self.actions.append({"type": action_type, "value": value})
        self._update_action_list()
        self.action_changed.emit()
    
    def _remove_action(self):
        current_row = self.action_list.currentRow()
        if current_row >= 0:
            del self.actions[current_row]
            self._update_action_list()
            self.action_changed.emit()
    
    def _on_action_selected(self, row):
        self.remove_button.setEnabled(row >= 0)
    
    def _update_action_list(self):
        self.action_list.clear()
        for action in self.actions:
            item = QListWidgetItem()
            item_widget = ActionListItem(action["type"], action["value"])
            item.setSizeHint(item_widget.sizeHint())
            self.action_list.addItem(item)
            self.action_list.setItemWidget(item, item_widget)
    
    def set_actions(self, actions):
        self.actions = actions if actions else []
        self._update_action_list()
    
    def get_actions(self):
        return self.actions 