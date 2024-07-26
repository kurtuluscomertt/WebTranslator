import sys
import time
import pyperclip
from googletrans import Translator, LANGUAGES
from plyer import notification
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QWidget, QTextEdit,
                             QTabWidget, QStyleFactory, QFrame)
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QFont, QIcon, QColor, QMouseEvent


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super(CustomTitleBar, self).__init__(parent)
        self.parent = parent
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Modern Çeviri Uygulaması")
        title.setStyleSheet("color: #ecf0f1;")
        layout.addWidget(title)

        layout.addStretch()

        self.minimize_button = QPushButton("—")
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.minimize_button)

        self.close_button = QPushButton("✕")
        self.close_button.clicked.connect(self.parent.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

        self.start = QPoint(0, 0)
        self.pressing = False

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            end = self.mapToGlobal(event.pos())
            movement = end - self.start
            self.parent.setGeometry(self.parent.x() + movement.x(),
                                    self.parent.y() + movement.y(),
                                    self.parent.width(),
                                    self.parent.height())
            self.start = end

    def mouseReleaseEvent(self, event):
        self.pressing = False


class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowTitle("Modern Çeviri Uygulaması")
        self.setGeometry(100, 100, 600, 400)

        self.translator = Translator()
        self.recent_value = ""
        self.running = False

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_frame = QFrame(self)
        self.setCentralWidget(main_frame)
        main_frame.setObjectName("mainFrame")

        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom title bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        main_layout.addWidget(content_widget)

        # Tab widget
        self.tab_widget = QTabWidget()
        content_layout.addWidget(self.tab_widget)

        # Çeviri sekmesi
        translation_tab = QWidget()
        translation_layout = QVBoxLayout(translation_tab)

        language_layout = QHBoxLayout()
        label = QLabel("Hedef Dil:")
        label.setFont(QFont("Arial", 10, QFont.Bold))
        language_layout.addWidget(label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(list(LANGUAGES.values()))
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()

        translation_layout.addLayout(language_layout)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Başlat")
        self.start_button.clicked.connect(self.start_translation)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Durdur")
        self.stop_button.clicked.connect(self.stop_translation)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        translation_layout.addLayout(button_layout)

        self.status_label = QLabel("Durum: Bekleniyor")
        self.status_label.setAlignment(Qt.AlignCenter)
        translation_layout.addWidget(self.status_label)

        self.tab_widget.addTab(translation_tab, "Çeviri")

        # Log sekmesi
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        clear_log_button = QPushButton("Logu Temizle")
        clear_log_button.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_log_button)

        self.tab_widget.addTab(log_tab, "Çeviri Geçmişi")

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(1000)  # Her 1 saniyede bir kontrol et

    def apply_styles(self):
        self.setStyleSheet("""
        #mainFrame {
            background-color: rgba(30, 42, 58, 0.95);
            border-radius: 10px;
        }
        QTabWidget::pane {
            border: 1px solid #3a4a5a;
            background-color: rgba(30, 42, 58, 0.8);
            border-radius: 5px;
        }
        QTabBar::tab {
            background-color: rgba(44, 62, 80, 0.7);
            color: #ecf0f1;
            padding: 8px 20px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }
        QTabBar::tab:selected {
            background-color: rgba(52, 73, 94, 0.8);
        }
        QLabel {
            color: #ecf0f1;
        }
        QComboBox {
            background-color: rgba(52, 73, 94, 0.7);
            color: #ecf0f1;
            border: 1px solid #3a4a5a;
            padding: 5px;
            border-radius: 3px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-width: 1px;
            border-left-color: #3a4a5a;
            border-left-style: solid;
        }
        QComboBox::down-arrow {
            image: url(down_arrow.png);
        }
        QComboBox QAbstractItemView {
            background-color: #34495e;
            color: #ecf0f1;
            selection-background-color: #2c3e50;
        }
        QPushButton {
            background-color: rgba(52, 152, 219, 0.8);
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: rgba(41, 128, 185, 0.9);
        }
        QPushButton:disabled {
            background-color: rgba(149, 165, 166, 0.8);
        }
        QTextEdit {
            background-color: rgba(52, 73, 94, 0.6);
            color: #ecf0f1;
            border: 1px solid #3a4a5a;
            border-radius: 5px;
        }
        """)

        self.title_bar.setStyleSheet("""
        QWidget {
            background-color: rgba(30, 42, 58, 0.95);
            color: #ecf0f1;
        }
        QPushButton {
            background-color: transparent;
            color: #ecf0f1;
            border: none;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: rgba(52, 73, 94, 0.7);
        }
        """)

        # Özel buton stilleri
        self.start_button.setStyleSheet("""
        QPushButton {
            background-color: rgba(46, 204, 113, 0.8);
        }
        QPushButton:hover {
            background-color: rgba(39, 174, 96, 0.9);
        }
        """)

        self.stop_button.setStyleSheet("""
        QPushButton {
            background-color: rgba(231, 76, 60, 0.8);
        }
        QPushButton:hover {
            background-color: rgba(192, 57, 43, 0.9);
        }
        """)

    def start_translation(self):
        self.running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Durum: Çalışıyor")
        self.status_label.setStyleSheet("color: #2ecc71;")

    def stop_translation(self):
        self.running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Durum: Durduruldu")
        self.status_label.setStyleSheet("color: #e74c3c;")

    def translate_text(self, text, dest_language):
        try:
            translated = self.translator.translate(text, dest=dest_language)
            return translated.text
        except Exception as e:
            return f"Çeviri hatası: {e}"

    def check_clipboard(self):
        if self.running:
            clipboard_value = pyperclip.paste()
            if clipboard_value != self.recent_value:
                self.recent_value = clipboard_value
                dest_language = self.language_combo.currentText()
                translated_text = self.translate_text(clipboard_value, dest_language)
                if len(translated_text) > 256:
                    notification_text = translated_text[:253] + '...'
                else:
                    notification_text = translated_text

                notification.notify(
                    title='Çeviri',
                    message=notification_text,
                    timeout=10
                )

                # Log the translation
                log_entry = f"Orijinal: {clipboard_value}\nÇeviri ({dest_language}): {translated_text}\n\n"
                self.log_text.append(log_entry)

    def clear_log(self):
        self.log_text.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))  # Modern görünüm için Fusion stilini kullan
    translator_app = TranslatorApp()
    translator_app.show()
    sys.exit(app.exec_())