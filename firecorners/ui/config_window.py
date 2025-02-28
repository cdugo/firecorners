import sys
import json
import logging
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTabWidget, QLabel, QCheckBox, 
                           QApplication, QStackedWidget, QSpinBox, QDoubleSpinBox,
                           QFrame, QListWidget, QListWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette, QColor, QFont

from .screen_preview import ScreenPreview
from .action_dialog import ActionDialog
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ActionListItem(QFrame):
    def __init__(self, action_type, value, parent=None):
        super().__init__(parent)
        self.setObjectName("actionListItem")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        type_label = QLabel(action_type)
        type_label.setObjectName("actionTypeLabel")
        value_label = QLabel(value[:100] + "..." if len(value) > 100 else value)
        value_label.setObjectName("actionValueLabel")
        value_label.setWordWrap(True)
        value_label.setMinimumHeight(20)
        
        layout.addWidget(type_label)
        layout.addWidget(value_label)
        
        self.setMinimumHeight(80)

class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FireCorners Configuration")
        self.setMinimumSize(800, 600)
        
        # Initialize config manager and load config
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Set up theme
        self._setup_theme()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Main tab
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left side - Screen Preview
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # Screen preview
        self.screen_preview = ScreenPreview()
        self.screen_preview.corner_selected.connect(self._on_corner_selected)
        left_layout.addWidget(self.screen_preview)
        
        # Preview help text
        preview_help = QLabel("Click on a corner to configure its actions")
        preview_help.setStyleSheet("color: rgba(255, 255, 255, 0.6); background: transparent;")
        preview_help.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(preview_help)
        
        # Launch at login option
        self.launch_login = QCheckBox("Launch at login")
        self.launch_login.stateChanged.connect(self._on_launch_login_changed)
        left_layout.addWidget(self.launch_login)
        
        content_layout.addWidget(left_container)
        
        # Right side - Corner Actions
        right_container = QFrame()
        right_container.setObjectName("cornerActionsContainer")
        right_layout = QVBoxLayout(right_container)
        
        # Corner title
        self.corner_title = QLabel("Top Left Corner")
        self.corner_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background: transparent;")
        right_layout.addWidget(self.corner_title)
        
        corner_description = QLabel("Click on a corner in the screen display to configure actions")
        corner_description.setStyleSheet("color: rgba(255, 255, 255, 0.6); background: transparent;")
        right_layout.addWidget(corner_description)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("separator")
        right_layout.addWidget(separator)
        
        # Actions section
        actions_label = QLabel("Actions:")
        actions_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background: transparent;")
        right_layout.addWidget(actions_label)
        
        # Action list
        self.action_list = QListWidget()
        self.action_list.setObjectName("actionList")
        right_layout.addWidget(self.action_list)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Action")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self._add_action)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.setObjectName("editButton")
        self.edit_button.clicked.connect(self._edit_action)
        self.edit_button.setEnabled(False)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.setObjectName("removeButton")
        self.remove_button.clicked.connect(self._remove_action)
        self.remove_button.setEnabled(False)
        
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        right_layout.addLayout(button_layout)
        
        content_layout.addWidget(right_container)
        
        # Set the content layout stretch factors
        content_layout.setStretchFactor(left_container, 1)
        content_layout.setStretchFactor(right_container, 1)
        
        main_layout.addLayout(content_layout)
        self.tab_widget.addTab(main_tab, "Hot Corners")
        
        # Advanced settings tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add advanced settings here
        advanced_title = QLabel("Advanced Settings")
        advanced_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        advanced_layout.addWidget(advanced_title)
        
        # Corner threshold
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Corner Threshold (pixels):")
        threshold_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setMinimum(1)
        self.threshold_spinbox.setMaximum(50)
        self.threshold_spinbox.setValue(self.config.get("settings", {}).get("threshold", 5))
        self.threshold_spinbox.valueChanged.connect(lambda v: self._update_advanced_setting("threshold", v))
        
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_spinbox)
        threshold_layout.addStretch()
        advanced_layout.addLayout(threshold_layout)
        
        # Dwell time
        dwell_layout = QHBoxLayout()
        dwell_label = QLabel("Dwell Time (seconds):")
        dwell_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        
        self.dwell_spinbox = QDoubleSpinBox()
        self.dwell_spinbox.setMinimum(0.0)
        self.dwell_spinbox.setMaximum(5.0)
        self.dwell_spinbox.setSingleStep(0.1)
        self.dwell_spinbox.setValue(self.config.get("settings", {}).get("dwell", 0.0))
        self.dwell_spinbox.valueChanged.connect(lambda v: self._update_advanced_setting("dwell", v))
        
        dwell_layout.addWidget(dwell_label)
        dwell_layout.addWidget(self.dwell_spinbox)
        dwell_layout.addStretch()
        advanced_layout.addLayout(dwell_layout)
        
        # Cooldown period
        cooldown_layout = QHBoxLayout()
        cooldown_label = QLabel("Cooldown Period (seconds):")
        cooldown_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        
        self.cooldown_spinbox = QDoubleSpinBox()
        self.cooldown_spinbox.setMinimum(0.1)
        self.cooldown_spinbox.setMaximum(10.0)
        self.cooldown_spinbox.setSingleStep(0.1)
        self.cooldown_spinbox.setValue(self.config.get("settings", {}).get("cooldown", 1.0))
        self.cooldown_spinbox.valueChanged.connect(lambda v: self._update_advanced_setting("cooldown", v))
        
        cooldown_layout.addWidget(cooldown_label)
        cooldown_layout.addWidget(self.cooldown_spinbox)
        cooldown_layout.addStretch()
        advanced_layout.addLayout(cooldown_layout)
        
        # Description
        settings_description = QLabel(
            "Corner Threshold: How close to the corner (in pixels) the cursor needs to be to trigger actions.\n"
            "Dwell Time: How long the cursor must stay in the corner before actions are triggered.\n"
            "Cooldown Period: Minimum time between consecutive triggers of the same corner."
        )
        settings_description.setStyleSheet("color: rgba(255, 255, 255, 0.6); margin-top: 10px;")
        settings_description.setWordWrap(True)
        advanced_layout.addWidget(settings_description)
        
        advanced_layout.addStretch()
        self.tab_widget.addTab(advanced_tab, "Advanced")
        
        self.layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.close)
        
        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self._save_config)
        
        bottom_layout.addWidget(self.cancel_button)
        bottom_layout.addWidget(self.save_button)
        
        self.layout.addLayout(bottom_layout)
        
        # Connect action list selection
        self.action_list.currentRowChanged.connect(self._on_action_selected)
        
        # Load initial configuration
        self._load_config()
    
    def _add_action(self):
        dialog = ActionDialog(self)
        if dialog.exec():
            action = dialog.get_action()
            if action:
                self._add_action_to_list(action)
                self._update_config()
    
    def _edit_action(self):
        current_row = self.action_list.currentRow()
        if current_row >= 0:
            current_actions = self.config.get(self.screen_preview.selected_corner, [])
            current_action = current_actions[current_row]
            
            dialog = ActionDialog(self, current_action)
            if dialog.exec():
                action = dialog.get_action()
                if action:
                    current_actions[current_row] = action
                    self._update_action_list()
                    self._update_config()
    
    def _remove_action(self):
        current_row = self.action_list.currentRow()
        if current_row >= 0:
            current_actions = self.config.get(self.screen_preview.selected_corner, [])
            del current_actions[current_row]
            self._update_action_list()
            self._update_config()
    
    def _add_action_to_list(self, action):
        if self.screen_preview.selected_corner:
            if self.screen_preview.selected_corner not in self.config:
                self.config[self.screen_preview.selected_corner] = []
            self.config[self.screen_preview.selected_corner].append(action)
            self._update_action_list()
    
    def _update_action_list(self):
        self.action_list.clear()
        if self.screen_preview.selected_corner:
            actions = self.config.get(self.screen_preview.selected_corner, [])
            for action in actions:
                item = QListWidgetItem()
                widget = ActionListItem(action["type"], action["value"])
                item.setSizeHint(widget.sizeHint())
                self.action_list.addItem(item)
                self.action_list.setItemWidget(item, widget)
    
    def _on_action_selected(self, row):
        self.edit_button.setEnabled(row >= 0)
        self.remove_button.setEnabled(row >= 0)
    
    def _on_corner_selected(self, corner):
        self.corner_title.setText(corner.replace("_", " ").title())
        self._update_action_list()
    
    def _update_config(self):
        """Update configuration after action changes"""
        if self.screen_preview.selected_corner:
            actions = self.config.get(self.screen_preview.selected_corner, [])
            self.config[self.screen_preview.selected_corner] = actions
    
    def _setup_theme(self):
        try:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                
                QWidget {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                
                QComboBox {
                    background-color: #2D2D2D;
                    border: 1px solid #3E3E3E;
                    border-radius: 6px;
                    padding: 12px 16px;
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
                    border-radius: 6px;
                    padding: 8px;
                    selection-background-color: #007AFF;
                }
                
                QComboBox QAbstractItemView::item {
                    padding: 8px 12px;
                    min-height: 24px;
                }
                
                #cornerActionsContainer {
                    background-color: rgba(35, 35, 35, 0.7);
                    border: 1px solid #3E3E3E;
                    border-radius: 8px;
                    padding: 20px;
                }
                
                QListWidget {
                    background-color: rgba(25, 25, 25, 0.7);
                    border: 1px solid #3E3E3E;
                    border-radius: 8px;
                    padding: 8px;
                }
                
                QListWidget::item {
                    background-color: rgba(30, 30, 30, 0.7);
                    border: 1px solid #3E3E3E;
                    border-radius: 6px;
                    padding: 0px;
                    margin-bottom: 10px;
                }
                
                QListWidget::item:selected {
                    background-color: rgba(0, 122, 255, 0.3);
                    border: 1px solid #007AFF;
                    border-radius: 6px;
                }
                
                QListWidget::item:hover:!selected {
                    background-color: rgba(45, 45, 45, 0.7);
                    border: 1px solid #3E3E3E;
                    border-radius: 6px;
                }
                
                #actionListItem {
                    background: transparent;
                    border: none;
                    min-height: 80px;
                }
                
                #actionTypeLabel {
                    color: #007AFF;
                    font-weight: bold;
                    font-size: 16px;
                    background: transparent;
                    padding-bottom: 4px;
                }
                
                #actionValueLabel {
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 14px;
                    line-height: 1.5;
                    background: transparent;
                    padding-bottom: 4px;
                }
                
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                
                #addButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                }
                
                #addButton:hover {
                    background-color: #0051D5;
                }
                
                #editButton, #removeButton {
                    background-color: rgba(60, 60, 60, 0.5);
                    color: white;
                    border: 1px solid #3E3E3E;
                }
                
                #editButton:hover, #removeButton:hover {
                    background-color: rgba(70, 70, 70, 0.7);
                    border-color: #007AFF;
                }
                
                #editButton:disabled, #removeButton:disabled {
                    background-color: rgba(40, 40, 40, 0.3);
                    color: rgba(255, 255, 255, 0.3);
                    border-color: rgba(62, 62, 62, 0.3);
                }
                
                QTabWidget::pane {
                    border: none;
                    background: transparent;
                }
                
                QTabWidget::tab-bar {
                    alignment: left;
                }
                
                QTabBar::tab {
                    background: transparent;
                    color: #FFFFFF;
                    padding: 8px 16px;
                    margin-right: 4px;
                    border: 1px solid transparent;
                    border-radius: 6px;
                }
                
                QTabBar::tab:selected {
                    background-color: rgba(0, 122, 255, 0.2);
                    border-color: #007AFF;
                }
                
                QTabBar::tab:hover:!selected {
                    background-color: rgba(45, 45, 45, 0.7);
                    border-color: #3E3E3E;
                }
                
                #separator {
                    background-color: #3E3E3E;
                    max-height: 1px;
                    margin: 10px 0;
                }
                
                QCheckBox {
                    color: #FFFFFF;
                    spacing: 8px;
                }
                
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 1px solid #3E3E3E;
                    border-radius: 4px;
                    background-color: #2D2D2D;
                }
                
                QCheckBox::indicator:checked {
                    background-color: #007AFF;
                    border-color: #007AFF;
                }
                
                QCheckBox::indicator:hover {
                    border-color: #007AFF;
                }
                
                QSpinBox, QDoubleSpinBox {
                    background-color: #2D2D2D;
                    border: 1px solid #3E3E3E;
                    border-radius: 6px;
                    padding: 8px;
                    color: #FFFFFF;
                    min-width: 100px;
                }
                
                QSpinBox:hover, QDoubleSpinBox:hover {
                    border-color: #007AFF;
                }
                
                QSpinBox::up-button, QDoubleSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 20px;
                    border: none;
                    background: transparent;
                    margin-top: 1px;
                    margin-right: 1px;
                }
                
                QSpinBox::down-button, QDoubleSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 20px;
                    border: none;
                    background: transparent;
                    margin-bottom: 1px;
                    margin-right: 1px;
                }
                
                QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-bottom: 4px solid #FFFFFF;
                }
                
                QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid #FFFFFF;
                }
                
                QSpinBox::up-arrow:hover, QDoubleSpinBox::up-arrow:hover,
                QSpinBox::down-arrow:hover, QDoubleSpinBox::down-arrow:hover {
                    border-bottom-color: #007AFF;
                    border-top-color: #007AFF;
                }
            """)
        except Exception as e:
            logger.error("Error setting up theme: %s", e)
            raise
    
    def _is_dark_mode(self):
        # Check system appearance
        import Foundation
        user_defaults = Foundation.NSUserDefaults.standardUserDefaults()
        style = user_defaults.stringForKey_("AppleInterfaceStyle")
        return style == "Dark"
    
    def _adjust_color(self, color, amount):
        """Adjust hex color brightness"""
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _load_config(self):
        """Load configuration into UI"""
        # Load settings
        settings = self.config.get("settings", {})
        self.launch_login.setChecked(settings.get("launch_at_login", False))
        
        # Load initial corner if any actions exist
        for corner in ["top_left", "top_right", "bottom_left", "bottom_right"]:
            if self.config.get(corner):
                self.screen_preview.selected_corner = corner
                self._update_action_list()
                break
    
    def _save_config(self):
        """Save configuration"""
        # Update settings
        self.config["settings"] = {
            "launch_at_login": self.launch_login.isChecked(),
            "threshold": self.threshold_spinbox.value(),
            "dwell": self.dwell_spinbox.value(),
            "cooldown": self.cooldown_spinbox.value()
        }
        
        # Save configuration
        if self.config_manager.save_config(self.config):
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to save configuration")
    
    def _on_launch_login_changed(self, state):
        """Handle launch at login checkbox changes"""
        self.config["settings"]["launch_at_login"] = bool(state)
    
    def _update_advanced_setting(self, key, value):
        if "settings" not in self.config:
            self.config["settings"] = {}
        self.config["settings"][key] = value

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec()) 