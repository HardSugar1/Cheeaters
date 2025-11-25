import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QLineEdit, QPushButton, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QSize, Qt, QObject, pyqtSlot
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtWebChannel import QWebChannel

class Bridge(QObject):
    # JavaScript'ten çağrılacak Python fonksiyonları için köprü
    def __init__(self, browser_instance):
        super().__init__()
        self.browser_instance = browser_instance

    @pyqtSlot(str)
    def navigateToUrl(self, url):
        # Bu fonksiyon HTML içindeki JavaScript'ten çağrılarak tarayıcının yeni URL'e gitmesini sağlar.
        self.browser_instance.browser.setUrl(QUrl(url))
        print(f"JavaScript'ten gelen URL: {url}")

    @pyqtSlot(str)
    def updateTheme(self, theme):
        # HTML sayfası eğer temayı değiştirdiğini Python'a bildirmek isterse kullanabilir.
        # Şu an için sadece konsola yazdırıyoruz.
        print(f"HTML'den gelen tema güncellemesi: {theme}")

class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cheetares Web Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Sadece pencere ikonu (cheetares.png) ve HTML logosu (cheetares_logo.svg) için varlık kontrolü
        self._ensure_assets_exist() 
        self.setWindowIcon(QIcon('cheetares.png'))
        
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # WebChannel kurulumu
        self.channel = QWebChannel(self.browser.page())
        self.bridge = Bridge(self)
        self.channel.registerObject("pyqt", self.bridge)
        self.browser.page().setWebChannel(self.channel)

        self.navigation_bar = QToolBar("Gezinme Çubuğu")
        self.addToolBar(Qt.TopToolBarArea, self.navigation_bar)
        self.navigation_bar.setIconSize(QSize(0, 0)) # İkon boyutunu 0 tutalım
        self.navigation_bar.setMovable(False)
        self.navigation_bar.setToolButtonStyle(Qt.ToolButtonTextOnly) # Sadece metin göster

        # Butonlar için QAction'lar, objectName ile CSS tarafından hedeflenecek
        back_action = QAction("Geri", self)
        back_action.setObjectName("backButton")
        back_action.triggered.connect(self.browser.back)
        self.navigation_bar.addAction(back_action)

        forward_action = QAction("İleri", self)
        forward_action.setObjectName("forwardButton")
        forward_action.triggered.connect(self.browser.forward)
        self.navigation_bar.addAction(forward_action)

        reload_action = QAction("Yenile", self)
        reload_action.setObjectName("reloadButton")
        reload_action.triggered.connect(self.browser.reload)
        self.navigation_bar.addAction(reload_action)

        home_action = QAction("Ana Sayfa", self)
        home_action.setObjectName("homeButton")
        home_action.triggered.connect(self.go_home)
        self.navigation_bar.addAction(home_action)

        self.navigation_bar.addSeparator()

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setFont(QFont("Segoe UI", 10))
        self.url_bar.setPlaceholderText("Web adresini girin veya arama yapın...")
        self.navigation_bar.addWidget(self.url_bar)
        
        self.navigation_bar.addSeparator()

        settings_action = QAction("Tema", self)
        settings_action.setObjectName("themeButton")
        settings_action.triggered.connect(self.toggle_theme)
        self.navigation_bar.addAction(settings_action)
        
        # Arama motoru butonu, artık HTML sayfasındaki seçimi etkileyecek
        self.search_engine_button = QPushButton("Google") # Başlangıçta Google göster
        self.search_engine_button.setObjectName("searchEngineButton")
        self.search_engine_button.clicked.connect(self.change_search_engine)
        self.search_engine_button.setFixedSize(80, 32)
        self.search_engine_button.setFont(QFont("Segoe UI", 9))
        self.navigation_bar.addWidget(self.search_engine_button)

        self.browser.urlChanged.connect(self.update_url_bar)
        self.browser.titleChanged.connect(self.setWindowTitle)

        self.current_theme = "light"

        self.search_engines = [
            ("Google", "https://www.google.com/search?q="),
            ("DuckDuckGo", "https://duckduckgo.com/?q="),
            ("Yandex", "https://yandex.com.tr/search/?text=")
        ]
        self.current_engine_index = 0
        
        self.home_page_path = os.path.abspath("index.html")
        
        self.apply_theme() # QSS teması uygulandı
        self.go_home() # HTML ana sayfası yüklendi

    def _ensure_assets_exist(self):
        # Pencere ikonu için PNG
        window_icon_name = 'cheetares.png'
        if not os.path.exists(window_icon_name):
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent) # Şeffaf bir placeholder
            pixmap.save(window_icon_name)
            print(f"{window_icon_name} bulunamadı, boş bir placeholder oluşturuldu.")
        
        # HTML ana sayfası için SVG logo
        html_logo_name = 'cheetares_logo.svg'
        if not os.path.exists(html_logo_name):
            print(f"{html_logo_name} bulunamadı. Lütfen elle bir SVG logo dosyası oluşturun ve bu dizine yerleştirin.")
            # Boş bir SVG dosyası oluşturmak, çoğu zaman işe yaramaz.
            # Ancak uygulamanın çökmesini engellemek için minimum bir SVG yazılabilir.
            with open(html_logo_name, 'w') as f:
                f.write('<svg width="150" height="150" viewBox="0 0 150 150" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="none"/></svg>')


    def go_home(self):
        self.browser.setUrl(QUrl.fromLocalFile(self.home_page_path))
        # HTML sayfasının yüklendiğinden emin olduktan sonra JS çağrısı yapın.
        # Bu, sayfanın yüklenmesi tamamlandığında tetiklenmeli.
        # `loadFinished` sinyalini kullanmak daha güvenli olabilir.
        self.browser.loadFinished.connect(self._on_home_page_load_finished)

    def _on_home_page_load_finished(self, ok):
        # Sinyal sadece bir kez bağlanmalı, aksi halde her yüklemede tekrar bağlanır.
        try:
            self.browser.loadFinished.disconnect(self._on_home_page_load_finished)
        except TypeError: # Disconnect etmeye çalışırken zaten bağlı değilse hata verir.
            pass
        
        if ok: # Sayfa başarıyla yüklendiyse
            # HTML sayfasındaki temayı ve arama motorunu Python'dan ayarla
            self.browser.page().runJavaScript(f"setBrowserTheme('{self.current_theme}');")
            # HTML'deki select'i güncellemek için JS çağrısı.
            # 'google', 'duckduckgo' gibi küçük harfli değerler bekleniyor.
            current_engine_val = self.search_engines[self.current_engine_index][0].lower()
            self.browser.page().runJavaScript(f"updateSearchEngineSelector('{current_engine_val}');")
        else:
            print("Ana sayfa yüklenirken bir hata oluştu.")


    def navigate_to_url(self):
        url_text = self.url_bar.text()
        if url_text.startswith("file:///"):
            self.browser.setUrl(QUrl(url_text))
        elif not url_text.startswith("http://") and not url_text.startswith("https://"):
            search_query = self.search_engines[self.current_engine_index][1] + QUrl.toPercentEncoding(url_text).data().decode('utf-8')
            self.browser.setUrl(QUrl(search_query))
        else:
            self.browser.setUrl(QUrl(url_text))

    def update_url_bar(self, q):
        # Eğer yüklenen URL bizim yerel HTML sayfamız ise, adres çubuğunu boş bırakabiliriz
        if q.toLocalFile() == self.home_page_path:
            self.url_bar.clear()
            self.url_bar.setPlaceholderText("Web adresini girin veya arama yapın...")
        else:
            self.url_bar.setText(q.toString())
        
    def toggle_theme(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        self.apply_theme() # QSS teması güncellendi
        # HTML sayfasındaki temayı da güncellemek için JS çağrısı
        self.browser.page().runJavaScript(f"setBrowserTheme('{self.current_theme}');")

    def apply_theme(self):
        # Dinamik QSS stilini burada oluşturuyoruz
        stylesheet = f"""
            QMainWindow {{ 
                background-color: {'#1e1e1e' if self.current_theme == 'dark' else '#f0f2f5'}; 
                color: {'white' if self.current_theme == 'dark' else 'black'}; 
            }}
            QToolBar {{ 
                background-color: {'#2e2e2e' if self.current_theme == 'dark' else '#ffffff'}; 
                border: none; 
                border-bottom: 1px solid {'#3a3a3a' if self.current_theme == 'dark' else '#e0e0e0'};
                padding: 5px;
            }}
            QLineEdit {{ 
                background-color: {'#3e3e3e' if self.current_theme == 'dark' else '#f8f9fa'}; 
                color: {'white' if self.current_theme == 'dark' else 'black'}; 
                border: 1px solid {'#555' if self.current_theme == 'dark' else '#ced4da'}; 
                border-radius: 10px; 
                padding: 5px 10px; 
            }}
            QToolButton {{
                background-color: {'#4e4e4e' if self.current_theme == 'dark' else '#f8f9fa'}; 
                color: {'white' if self.current_theme == 'dark' else 'black'};
                border: 1px solid {'#555' if self.current_theme == 'dark' else '#ced4da'};
                border-radius: 5px;
                margin: 2px;
                padding: 5px 8px 5px 30px; 
                font-size: 14px;
                position: relative; 
            }}
            QToolButton:hover {{
                background-color: {'#6a6a6a' if self.current_theme == 'dark' else '#e2e6ea'};
            }}
            QToolButton:pressed {{
                background-color: {'#888888' if self.current_theme == 'dark' else '#dae0e5'};
            }}

            /* CSS Pseudo-elementleri ile ikonlar */
            QToolButton#backButton::before {{
                content: "⬅️"; 
                position: absolute;
                left: 8px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 16px;
                color: {'white' if self.current_theme == 'dark' else 'black'};
            }}
            QToolButton#forwardButton::before {{
                content: "➡️"; 
                position: absolute;
                left: 8px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 16px;
                color: {'white' if self.current_theme == 'dark' else 'black'};
            }}
            QToolButton#reloadButton::before {{
                content: "🔄"; 
                position: absolute;
                left: 8px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 16px;
                color: {'white' if self.current_theme == 'dark' else 'black'};
            }}
            QToolButton#homeButton::before {{
                content: "🏠"; 
                position: absolute;
                left: 8px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 16px;
                color: {'white' if self.current_theme == 'dark' else 'black'};
            }}
            QToolButton#themeButton::before {{
                content: "🌙"; 
                position: absolute;
                left: 8px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 16px;
                color: {'white' if self.current_theme == 'dark' else 'black'};
            }}

            QPushButton#searchEngineButton {{
                background-color: {'#4e4e4e' if self.current_theme == 'dark' else '#007bff'}; 
                color: {'white' if self.current_theme == 'dark' else 'white'}; 
                border: none; 
                border-radius: 5px; 
                padding: 5px; 
                margin: 2px;
                font-size: 14px;
            }}
            QPushButton#searchEngineButton:hover {{ 
                background-color: {'#6a6a6a' if self.current_theme == 'dark' else '#0056b3'}; 
            }}
            QPushButton#searchEngineButton:pressed {{
                background-color: {'#888888' if self.current_theme == 'dark' else '#003e80'};
            }}
        """
        self.setStyleSheet(stylesheet)
            
    def change_search_engine(self):
        # Arama motoru butonuna tıklandığında Python'daki motoru değiştir.
        self.current_engine_index = (self.current_engine_index + 1) % len(self.search_engines)
        engine_name_text = self.search_engines[self.current_engine_index][0]
        self.search_engine_button.setText(engine_name_text)
        
        # Eğer ana sayfadaysak (HTML yüklüyse), HTML'deki select'i de güncelle.
        if self.browser.url().toLocalFile() == self.home_page_path:
            current_engine_val = self.search_engines[self.current_engine_index][0].lower()
            self.browser.page().runJavaScript(f"updateSearchEngineSelector('{current_engine_val}');")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebBrowser()
    window.show()
    sys.exit(app.exec_())