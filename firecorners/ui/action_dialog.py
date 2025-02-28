from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QLineEdit, QTextEdit, QPushButton,
                           QFileDialog, QFrame)
from PyQt6.QtCore import Qt

class ActionDialog(QDialog):
    def __init__(self, parent=None, action=None):
        super().__init__(parent)
        self.setWindowTitle("Add Action" if action is None else "Edit Action")
        self.setMinimumWidth(500)
        self.action = action
        
        # Set up theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            
            QLabel {
                color: #FFFFFF;
                background: transparent;
            }
            
            QComboBox {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                border-radius: 6px;
                padding: 8px 12px;
                color: #FFFFFF;
                min-width: 200px;
            }
            
            QComboBox:hover {
                background-color: #2D2D2D;
                border-color: #007AFF;
            }
            
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            
            QComboBox QAbstractItemView {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                selection-background-color: #007AFF;
                padding: 0;
                margin: 0;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                margin: 0;
                min-height: 20px;
                border-bottom: 1px solid #3E3E3E;
            }
            
            QComboBox QAbstractItemView::item:last {
                border-bottom: none;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #007AFF;
                color: white;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #2D2D2D;
            }
            
            QLineEdit, QTextEdit {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                border-radius: 6px;
                padding: 8px;
                color: #FFFFFF;
            }
            
            QLineEdit:hover, QTextEdit:hover {
                background-color: #2D2D2D;
                border-color: #007AFF;
            }
            
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            
            #saveButton {
                background-color: #007AFF;
                color: white;
                border: none;
            }
            
            #saveButton:hover {
                background-color: #0051D5;
            }
            
            #cancelButton {
                background-color: rgba(60, 60, 60, 0.5);
                color: white;
                border: 1px solid #3E3E3E;
            }
            
            #cancelButton:hover {
                background-color: rgba(70, 70, 70, 0.5);
            }
            
            #exampleLabel {
                color: rgba(255, 255, 255, 0.6);
                font-size: 12px;
            }
        """)
        
        self._setup_ui()
        
        if action:
            self._load_action(action)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Action type selector
        type_layout = QHBoxLayout()
        type_layout.setSpacing(12)
        type_label = QLabel("Action Type:")
        type_label.setStyleSheet("font-weight: bold;")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["URL", "Application", "Shell Command", "AppleScript"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Input container
        self.input_container = QFrame()
        self.input_container.setObjectName("inputContainer")
        input_layout = QVBoxLayout(self.input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        # URL input
        self.url_widget = QFrame()
        url_layout = QVBoxLayout(self.url_widget)
        url_layout.setContentsMargins(0, 0, 0, 0)
        self.url_input = QLineEdit()
        self.url_input.setObjectName("actionInput")
        self.url_input.setPlaceholderText("Enter URL (e.g., https://www.example.com)")
        url_layout.addWidget(QLabel("URL:"))
        url_layout.addWidget(self.url_input)
        
        # Application input
        self.app_widget = QFrame()
        app_layout = QVBoxLayout(self.app_widget)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout_input = QHBoxLayout()
        self.app_input = QLineEdit()
        self.app_input.setObjectName("actionInput")
        self.app_input.setPlaceholderText("Select an application...")
        self.app_browse = QPushButton("Browse...")
        self.app_browse.setObjectName("browseButton")
        self.app_browse.clicked.connect(self._browse_application)
        app_layout_input.addWidget(self.app_input)
        app_layout_input.addWidget(self.app_browse)
        app_layout.addWidget(QLabel("Application:"))
        app_layout.addLayout(app_layout_input)
        
        # Shell command input
        self.shell_widget = QFrame()
        shell_layout = QVBoxLayout(self.shell_widget)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        self.shell_input = QTextEdit()
        self.shell_input.setObjectName("actionInput")
        self.shell_input.setPlaceholderText("Enter shell command...")
        shell_layout.addWidget(QLabel("Shell Command:"))
        shell_layout.addWidget(self.shell_input)
        example_label = QLabel("Example: open -a 'Safari.app'")
        example_label.setObjectName("exampleLabel")
        shell_layout.addWidget(example_label)
        
        # AppleScript input
        self.script_widget = QFrame()
        script_layout = QVBoxLayout(self.script_widget)
        script_layout.setContentsMargins(0, 0, 0, 0)
        self.script_input = QTextEdit()
        self.script_input.setObjectName("actionInput")
        self.script_input.setPlaceholderText("Enter AppleScript...")
        script_layout.addWidget(QLabel("AppleScript:"))
        script_layout.addWidget(self.script_input)
        example_label = QLabel("Example: tell application \"Safari\" to activate")
        example_label.setObjectName("exampleLabel")
        script_layout.addWidget(example_label)
        
        # Add all input widgets
        input_layout.addWidget(self.url_widget)
        input_layout.addWidget(self.app_widget)
        input_layout.addWidget(self.shell_widget)
        input_layout.addWidget(self.script_widget)
        layout.addWidget(self.input_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Add Action" if self.action is None else "Save Changes")
        self.save_button.setObjectName("saveButton")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)
        
        # Set initial state
        self._on_type_changed("URL")
    
    def _on_type_changed(self, action_type):
        self.url_widget.setVisible(action_type == "URL")
        self.app_widget.setVisible(action_type == "Application")
        self.shell_widget.setVisible(action_type == "Shell Command")
        self.script_widget.setVisible(action_type == "AppleScript")
    
    def _browse_application(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Applications (*.app)")
        file_dialog.setDirectory("/Applications")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.app_input.setText(selected_files[0])
    
    def _load_action(self, action):
        self.type_combo.setCurrentText(action["type"])
        if action["type"] == "URL":
            self.url_input.setText(action["value"])
        elif action["type"] == "Application":
            self.app_input.setText(action["value"])
        elif action["type"] == "Shell Command":
            self.shell_input.setText(action["value"])
        elif action["type"] == "AppleScript":
            self.script_input.setText(action["value"])
    
    def get_action(self):
        action_type = self.type_combo.currentText()
        value = ""
        
        if action_type == "URL":
            value = self.url_input.text().strip()
        elif action_type == "Application":
            value = self.app_input.text().strip()
        elif action_type == "Shell Command":
            value = self.shell_input.toPlainText().strip()
        elif action_type == "AppleScript":
            value = self.script_input.toPlainText().strip()
        
        return {"type": action_type, "value": value} if value else None 