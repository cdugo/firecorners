import sys
from PyQt6.QtWidgets import QWidget, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QPainterPath, QLinearGradient
import Quartz
from AppKit import NSWorkspace, NSScreen
import logging

logger = logging.getLogger(__name__)

class ScreenPreview(QWidget):
    corner_selected = pyqtSignal(str)  # Signal emitted when a corner is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("screenPreview")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(250, 141)  # 16:9 aspect ratio
        self.setMaximumSize(400, 225)  # Reduced maximum size
        
        self.selected_corner = None
        self.corner_radius = 12
        self.corner_positions = {
            "top_left": (-self.corner_radius, -self.corner_radius),
            "top_right": (self.corner_radius, -self.corner_radius),
            "bottom_left": (-self.corner_radius, self.corner_radius),
            "bottom_right": (self.corner_radius, self.corner_radius)
        }
        
        self.hover_corner = None
        self.wallpaper = None
        
        # Try to load the wallpaper
        try:
            self.wallpaper = self._get_desktop_wallpaper()
            if self.wallpaper:
                logger.info("Successfully loaded desktop wallpaper")
            else:
                logger.warning("Could not load desktop wallpaper, using fallback background")
        except Exception as e:
            logger.error("Failed to load wallpaper: %s", e, exc_info=True)
        
        self.setMouseTracking(True)
    
    def _get_desktop_wallpaper(self):
        """Get the current desktop wallpaper as a QPixmap"""
        try:
            # Get the main screen
            screen = NSScreen.mainScreen()
            if not screen:
                logger.warning("Could not get main screen")
                return None
            
            # Get the workspace
            workspace = NSWorkspace.sharedWorkspace()
            if not workspace:
                logger.warning("Could not get shared workspace")
                return None
            
            # Get the wallpaper URL
            url = workspace.desktopImageURLForScreen_(screen)
            if not url:
                logger.warning("Could not get desktop wallpaper URL")
                return None
            
            # Get the path and create a QPixmap
            path = url.path()
            if not path:
                logger.warning("Could not get wallpaper path")
                return None
            
            pixmap = QPixmap(path)
            if pixmap.isNull():
                logger.warning("Created QPixmap is null")
                return None
            
            return pixmap
        except Exception as e:
            logger.error("Error getting wallpaper: %s", e, exc_info=True)
            return None
    
    def resizeEvent(self, event):
        """Handle resize events to maintain aspect ratio"""
        try:
            super().resizeEvent(event)
            # Maintain 16:9 aspect ratio
            self.setFixedHeight(int(self.width() * 0.5625))
        except Exception as e:
            logger.error("Error in resize event: %s", e, exc_info=True)
    
    def paintEvent(self, event):
        """Paint the screen preview with wallpaper and corner circles"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Calculate screen rect with padding for corner circles
            padding = self.corner_radius * 2
            screen_rect = self.rect().adjusted(padding, padding, -padding, -padding)
            
            # Draw wallpaper if available
            if self.wallpaper and not self.wallpaper.isNull():
                try:
                    scaled_wallpaper = self.wallpaper.scaled(
                        screen_rect.size(),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    painter.drawPixmap(screen_rect, scaled_wallpaper)
                    
                    # Add a slight dark overlay for better visibility
                    painter.fillRect(screen_rect, QColor(0, 0, 0, 40))
                except Exception as e:
                    logger.error("Error drawing wallpaper: %s", e, exc_info=True)
                    self._draw_fallback_background(painter, screen_rect)
            else:
                self._draw_fallback_background(painter, screen_rect)
            
            # Draw corner circles
            for corner, offset in self.corner_positions.items():
                try:
                    self._draw_corner(painter, corner, offset, screen_rect)
                except Exception as e:
                    logger.error("Error drawing corner %s: %s", corner, e, exc_info=True)
        except Exception as e:
            logger.error("Error in paint event: %s", e, exc_info=True)
    
    def _draw_fallback_background(self, painter, rect):
        """Draw a gradient background as fallback"""
        try:
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor("#2D2D2D"))
            gradient.setColorAt(1, QColor("#1E1E1E"))
            
            painter.setPen(QPen(QColor("#3E3E3E"), 1))
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(rect, 8, 8)
        except Exception as e:
            logger.error("Error drawing fallback background: %s", e, exc_info=True)
    
    def _draw_corner(self, painter, corner, offset, screen_rect):
        """Draw a single corner circle with appropriate styling"""
        try:
            x = screen_rect.right() if "right" in corner else screen_rect.left()
            y = screen_rect.bottom() if "bottom" in corner else screen_rect.top()
            
            # Adjust position based on offset
            x = x + offset[0]
            y = y + offset[1]
            
            # Set colors based on state
            if corner == self.selected_corner:
                painter.setBrush(QBrush(QColor("#007AFF")))
                painter.setPen(QPen(QColor("#FFFFFF"), 2))
                
                # Draw glow effect
                glow_color = QColor("#007AFF")
                glow_color.setAlpha(30)
                painter.setBrush(QBrush(glow_color))
                painter.setPen(QPen(glow_color, 1))
                painter.drawEllipse(x - self.corner_radius - 4, y - self.corner_radius - 4, 
                                  (self.corner_radius + 4) * 2, (self.corner_radius + 4) * 2)
                
                # Reset colors for main circle
                painter.setBrush(QBrush(QColor("#007AFF")))
                painter.setPen(QPen(QColor("#FFFFFF"), 2))
            elif corner == self.hover_corner:
                painter.setBrush(QBrush(QColor("#4D4D4D")))
                painter.setPen(QPen(QColor("#FFFFFF"), 1))
            else:
                painter.setBrush(QBrush(QColor("#3E3E3E")))
                painter.setPen(QPen(QColor("#FFFFFF"), 1))
            
            # Draw main circle
            painter.drawEllipse(x - self.corner_radius, y - self.corner_radius, 
                              self.corner_radius * 2, self.corner_radius * 2)
        except Exception as e:
            logger.error("Error drawing corner: %s", e, exc_info=True)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for hover effects"""
        try:
            self.hover_corner = self._corner_at_pos(event.pos())
            self.update()
        except Exception as e:
            logger.error("Error in mouse move event: %s", e, exc_info=True)
    
    def mousePressEvent(self, event):
        """Handle mouse press events for corner selection"""
        try:
            corner = self._corner_at_pos(event.pos())
            if corner:
                self.selected_corner = corner
                self.corner_selected.emit(corner)
                self.update()
        except Exception as e:
            logger.error("Error in mouse press event: %s", e, exc_info=True)
    
    def leaveEvent(self, event):
        """Handle mouse leave events"""
        try:
            self.hover_corner = None
            self.update()
        except Exception as e:
            logger.error("Error in leave event: %s", e, exc_info=True)
    
    def _corner_at_pos(self, pos):
        """Determine which corner (if any) is at the given position"""
        try:
            padding = self.corner_radius * 2
            screen_rect = self.rect().adjusted(padding, padding, -padding, -padding)
            
            for corner, offset in self.corner_positions.items():
                x = screen_rect.right() if "right" in corner else screen_rect.left()
                y = screen_rect.bottom() if "bottom" in corner else screen_rect.top()
                
                # Adjust position based on offset
                x = x + offset[0]
                y = y + offset[1]
                
                # Calculate distance from cursor to corner center
                dx = pos.x() - x
                dy = pos.y() - y
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance <= self.corner_radius:
                    return corner
            
            return None
        except Exception as e:
            logger.error("Error calculating corner position: %s", e, exc_info=True)
            return None
    
    def get_selected_corner(self):
        """Get the currently selected corner"""
        return self.selected_corner 