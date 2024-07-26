import sys
import time
import pyperclip
from googletrans import Translator, LANGUAGES
from plyer import notification
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QWidget, QTextEdit,
                             QTabWidget, QStyleFactory)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QIcon


class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Çeviri Uygulaması")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon('translate_icon.png'))  # İkon ekleyin (dosya yolunu değiştirin)

        self.translator = Translator()
        self.recent_value = ""
        self.running = False

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Tab widget oluştur
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Çeviri sekmesi
        translation_tab = QWidget()
        translation_layout = QVBoxLayout(translation_tab)

        language_layout = QHBoxLayout()
        label = QLabel("Hedef Dil:")
        label.setFont(QFont("Arial", 10, QFont.Bold))
        language_layout.addWidget(label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(list(LANGUAGES.values()))
        self.language_combo.setStyleSheet("QComboBox { min-width: 200px; }")
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()

        translation_layout.addLayout(language_layout)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Başlat")
        self.start_button.clicked.connect(self.start_translation)
        self.start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 5px 10px; }")
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Durdur")
        self.stop_button.clicked.connect(self.stop_translation)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 5px 10px; }")
        button_layout.addWidget(self.stop_button)

        translation_layout.addLayout(button_layout)

        self.status_label = QLabel("Durum: Bekleniyor")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("QLabel { font-weight: bold; }")
        translation_layout.addWidget(self.status_label)

        tab_widget.addTab(translation_tab, "Çeviri")

        # Log sekmesi
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        clear_log_button = QPushButton("Logu Temizle")
        clear_log_button.clicked.connect(self.clear_log)
        clear_log_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 5px 10px; }")
        log_layout.addWidget(clear_log_button)

        tab_widget.addTab(log_tab, "Çeviri Geçmişi")

        central_widget.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(1000)  # Her 1 saniyede bir kontrol et

    def start_translation(self):
        self.running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Durum: Çalışıyor")
        self.status_label.setStyleSheet("QLabel { font-weight: bold; color: green; }")

    def stop_translation(self):
        self.running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Durum: Durduruldu")
        self.status_label.setStyleSheet("QLabel { font-weight: bold; color: red; }")

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