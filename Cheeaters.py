import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QLineEdit, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon

class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Pencere başlığını ve boyutlarını ayarla
        self.setWindowTitle("Cheetares")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('cheetares.png'))
        
        # WebEngineView bileşenini oluştur
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # Navigasyon çubuğu (Toolbar) oluştur
        self.navigation_bar = QToolBar("Gezinme Çubuğu")
        self.addToolBar(self.navigation_bar)

        # Geri butonu
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon('Geri.png'))
        self.back_button.setToolTip("Geri")
        self.back_button.clicked.connect(self.browser.back)
        self.navigation_bar.addWidget(self.back_button)

        # İleri butonu
        self.forward_button = QPushButton()
        self.forward_button.setIcon(QIcon('İleri.png'))
        self.forward_button.setToolTip("İleri")
        self.forward_button.clicked.connect(self.browser.forward)
        self.navigation_bar.addWidget(self.forward_button)

        # Yenile butonu
        self.reload_button = QPushButton("Yenile")
        self.reload_button.clicked.connect(self.browser.reload)
        self.navigation_bar.addWidget(self.reload_button)

        # Ana Sayfa butonu
        self.home_button = QPushButton("Ana Sayfa")
        self.home_button.clicked.connect(self.go_home)
        self.navigation_bar.addWidget(self.home_button)

        # Ayarlar butonu (Tema değiştirme)
        self.settings_button = QPushButton("Tema değiş")
        self.settings_button.clicked.connect(self.toggle_theme)
        self.navigation_bar.addWidget(self.settings_button)
        
        # Arama motoru değiştirme butonu
        self.search_engine_button = QPushButton("Google") # Başlangıçta Google
        self.search_engine_button.clicked.connect(self.change_search_engine)
        self.navigation_bar.addWidget(self.search_engine_button)

        # Adres çubuğu
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navigation_bar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url_bar)

        # Temayı takip etmek için değişken
        self.current_theme = "light"

        # Arama motorlarını takip etmek için değişkenler
        self.search_engines = ["https://www.google.com/search?q=", "https://duckduckgo.com/?q=", "https://yandex.com.tr/search/?text="]
        self.current_engine_index = 0
        self.home_url = self.search_engines[self.current_engine_index].split('?')[0]
        
        # İlk temayı uygula
        self.apply_theme()
        
        # Varsayılan ana sayfayı yükle
        self.go_home()

    def go_home(self):
        self.browser.setUrl(QUrl(self.home_url))

    def navigate_to_url(self):
        url_text = self.url_bar.text()
        if not url_text.startswith("http://") and not url_text.startswith("https://"):
            # Arama yapmak için URL'i bir arama motoru sorgusuna dönüştür
            search_url = self.search_engines[self.current_engine_index] + QUrl.toPercentEncoding(url_text).data().decode('utf-8')
            self.browser.setUrl(QUrl(search_url))
        else:
            self.browser.setUrl(QUrl(url_text))

    def update_url_bar(self, q):
        self.url_bar.setText(q.toString())
        
    def toggle_theme(self):
        # Temayı beyazdan siyaha, siyahtan beyaza çevir
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        self.apply_theme()

    def apply_theme(self):
        if self.current_theme == "dark":
            # Koyu tema için stil sayfası
            dark_stylesheet = """
                QMainWindow { 
                    background-color: #1e1e1e; /* Tüm ana pencereyi koyu yapar */
                }
                QToolBar { 
                    background-color: #2e2e2e; /* Gezinme çubuğunu biraz daha açık koyu yapar */
                    border: none; 
                }
                QLineEdit { 
                    background-color: #3e3e3e; /* Adres çubuğunu da koyu yapar */
                    color: white; 
                    border: 1px solid #555; 
                    padding: 4px; 
                }
                QPushButton { 
                    background-color: #2e2e2e; 
                    color: white; 
                    border: 1px solid #555; 
                    padding: 5px; 
                }
                QPushButton:hover { 
                    background-color: #4e4e4e; /* Buton üzerine gelindiğinde rengi değiştirir */
                }
            """
            self.setStyleSheet(dark_stylesheet)
        else:
            # Açık tema için stil sayfası (eskisi gibi kalabilir)
            light_stylesheet = """
                QMainWindow { background-color: #f0f0f0; }
                QToolBar { background-color: #e0e0e0; border: none; }
                QLineEdit { background-color: white; color: black; border: 1px solid #ccc; padding: 4px; }
                QPushButton { background-color: #f5f5f5; color: black; border: 1px solid #ccc; padding: 5px; }
                QPushButton:hover { background-color: #e8e8e8; }
            """
            self.setStyleSheet(light_stylesheet)
            
    def change_search_engine(self):
        # Bir sonraki arama motoruna geç
        self.current_engine_index += 1
        if self.current_engine_index >= len(self.search_engines):
            self.current_engine_index = 0  # Başa dön
            
        # Ana sayfa URL'ini güncelle
        self.home_url = self.search_engines[self.current_engine_index].split('?')[0]
        
        # Butonun metnini güncelle
        engine_name = self.search_engines[self.current_engine_index].split('/')[2].split('.')[1]
        self.search_engine_button.setText(engine_name.capitalize())
        
        # Ana sayfaya git
        self.go_home()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebBrowser()
    window.show()
    sys.exit(app.exec_())