# 📋 Project Development Log & Technical Journal
## CEN445 - Exploratory Data Visualization Course Project

Bu doküman, projenin başlangıcından teslimine kadar yapılan tüm teknik kararları, kurulan kütüphaneleri, veri işleme adımlarını ve mimari tercihleri adım adım kayıt altında tutmak için hazırlanmıştır.

---

### 📅 [Adım 1] - 10 Kasım 2026: Proje Başlatma & Güvenli Veri İzolasyonu

#### 1.1. Proje Konumu ve Klasör Mimarisi
* **Konum:** `C:\Users\Gaming\Documents\antigravity\cen445-football-viz`
* **Amaç:** Mevcut `cool-einstein` projesine ve çalışan bot/servislerine en ufak bir müdahale olmadan, tamamen bağımsız ve temiz bir çalışma alanı oluşturmak.
* **Klasör Yapısı:**
  * `app.py`: Ana Streamlit web dashboard uygulaması.
  * `data/`: Temizlenmiş ve işlenmiş verilerin tutulduğu dizin.
  * `data/raw/`: Orijinal veritabanından alınan salt okunur kopya.
  * `src/`: Veri yükleyici (`data_loader.py`), görselleştirme fonksiyonları ve makine öğrenmesi modülleri.
  * `docs/`: Geliştirme notları ve ödev rapor taslakları.
  * `.streamlit/`: UI tema ayarları (Koyu tema, wide mode).

#### 1.2. Güvenli Veri Kopyalama
* `cool-einstein/odds_analysis.db` dosyasından bağımsız bir kopya alındı: `data/raw/odds_analysis_copy.db`.
* Orijinal dosyaya hiçbir yazma/değiştirme işlemi yapılmadı, kilitlenme riski sıfırlandı.

---

### 📦 [Adım 2] - Kurulan Kütüphaneler ve Kullanım Amaçları

Ödevin isterleri (interaktif dashboard, 9 görselleştirme metodu, en az 6 advanced tür, 2 makine öğrenmesi modeli) doğrultusunda şu kütüphaneler kuruldu:

| Kütüphane | Sürüm | Neden Kuruldu? (Projedeki Rolü) |
| :--- | :--- | :--- |
| **`streamlit`** | `1.65.0` | **Web Arayüzü & Dashboard:** Python kodunu doğrudan tarayıcıda çalışan interaktif bir panoya dönüştürür. Slider'lar, açılır menüler (dropdown), filtreler ve sayfa sekmeleri bu kütüphaneyle yönetilir. |
| **`plotly`** | `7.1.0` | **İleri Düzey İnteraktif Grafikler:** Ödevin şart koştuğu hover, zoom, pan, tooltip özellikli grafikleri üretmek için. Sankey, Treemap, Parallel Coordinates, Harita (Choropleth), 2D Yoğunluk konturları Plotly ile çizilecek. |
| **`pandas`** | `2.3.3` | **Veri Manipülasyonu:** 4.600+ maçlık veri setini filtrelemek, sütun türetmek, gruplamak (groupby) ve özet istatistikleri hesaplamak için. |
| **`numpy`** | `2.2.6` | **Matematiksel Hesaplamalar:** Bahis oranlarının ima ettiği olasılıkları hesaplama, bookmaker kar marjını sıfırlayarak normalize etme ve matris işlemleri için. |
| **`scikit-learn`** | `1.7.2` | **Makine Öğrenmesi (ML):** Ödevde istenen 2 ML algoritması için: 1) K-Means ile takımların hücum/savunma profillerine göre kümelenmesi, 2) Logistic Regression/Random Forest ile maç sonucu tahmini. |
| **`networkx`** | `3.4.2` | **Ağ Analizi (Network Graph):** Büyük takımların birbirleriyle olan maç sonuçları ve üstünlük ilişkilerini görselleştiren ağ grafiğinin (nodes & edges) matematiksel yapısını kurmak için. |
| **`pyarrow`** | `25.0.1` | **Yüksek Hızlı Veri Saklama (Parquet):** CSV'ye kıyasla 5-10 kat daha hızlı okunan ve sıkıştırılmış `.parquet` formatını yönetmek için. |

---

### 🔍 [Adım 3] - Veri Seti Seçimi, Filtreleme ve Zenginleştirme

Ödev kuralları gereği veri setinin **en az 2.000 satır ve 7 sütun** olması gerekiyordu. 

#### 3.1. Filtreleme Kriterleri:
* **Ligler:** 7 Büyük Avrupa Ligi seçildi:
  * 🏴󠁧󠁢󠁥󠁮󠁧󠁿 İngiltere (Premier League - `E0`)
  * 🇮🇹 İtalya (Serie A - `I1`)
  * 🇩🇪 Almanya (Bundesliga - `D1`)
  * 🇫🇷 Fransa (Ligue 1 - `F1`)
  * 🇳🇱 Hollanda (Eredivisie - `N1`)
  * 🇵🇹 Portekiz (Primeira Liga - `P1`)
  * 🇹🇷 Türkiye (Süper Lig - `T1`)
* **Sezonlar:** Son 2 sezon (`2023-2024` ve `2024-2025`).

#### 3.2. Çıktı Metrikleri:
* **Toplam Satır:** **4.661 Maç** (Ödev şartının 2.3 katı).
* **Toplam Sütun:** **30 Sütun** (Ödev şartının 4.2 katı).
* **Dosya Boyutları:**
  * `processed_matches.csv`: **~796 KB**
  * `processed_matches.parquet`: **~165 KB**

#### 3.3. Türetilen Yeni Özellikler (Feature Engineering):
1. `league_name`, `country`, `country_iso3`: Grafikler ve harita renklendirmesi için ülke kodları.
2. `total_goals` & `goal_diff`: Maçta atılan toplam gol ve averaj.
3. `result_label` & `ht_result_label`: `H`, `D`, `A` kodlarının anlaşılır etiketleri ("Home Win", "Draw", "Away Win").
4. `is_over_25` & `btts`: 2.5 Üst ve Karşılıklı Gol var/yok ikili bayrakları.
5. `match_flow`: İlk yarıdan maçı çevirme durumları (Örn: *Home Comeback (Lost HT -> Won FT)* - Sankey diyagramı için).
6. `prob_home`, `prob_draw`, `prob_away`: Bahis şirketinin kar marjı çıkarılarak hesaplanmış saf olasılıklar.

---

### 🎯 Sıradaki Hedefler (Milestones)
- [x] Proje iskeleti oluşturuldu.
- [x] Gerekli kütüphaneler kuruldu.
- [x] Veri seti filtrelendi, zenginleştirildi ve dışa aktarıldı.
- [x] Geliştirme günlüğü (`DEVELOPMENT_LOG.md`) başlatıldı.
- [ ] **Milestone 1:** `src/charts.py` modülünün yazılması (9 görselleştirme).
- [ ] **Milestone 2:** `src/ml_engine.py` modülünün yazılması (K-Means + Classifier).
- [ ] **Milestone 3:** `app.py` ile interaktif dashboard'ın Streamlit üzerinde canlandırılması.
- [ ] **Milestone 4:** İngilizce 1 sayfalık ödev teslim raporunun (`REPORT.md`) hazırlanması.


---

### 📊 [Adım 4] - 10 Kasım 2026: 9 Görselleştirme Modülü (`src/charts.py`)

Ödevin 2. ve 3. maddelerinde istenen **9 farklı görselleştirme metodu (en az 6'sı advanced)** modüler olarak geliştirildi ve test edildi:

1. **`create_choropleth_map` (Advanced - Harita):** 
   * **Amaç:** Avrupa kıtasında liglerin maç başına gol ve ev sahibi galibiyet oranlarını ülke sınırları üzerinde renklendirme.
   * **İnteraktivite:** Hover üzerinde lig adı, maç sayısı, ortalama gol ve ev sahibi galibiyet yüzdesi gösterimi, harita üzerinde zoom ve pan.
2. **`create_treemap` (Advanced - Treemap):**
   * **Amaç:** Hiyerarşik analiz (*Ligler $\rightarrow$ Takımlar*). Kutu alanı toplam gol sayısını, renk tonu ise kazanılan toplam maç sayısını temsil eder.
3. **`create_sankey_diagram` (Advanced - Sankey Akışı):**
   * **Amaç:** İlk yarı skoru (HT) ile maç sonu skoru (FT) arasındaki momentum akışı. Özellikle ilk yarıyı geride kapatıp maçı kazanan "Comeback" (Geri Dönüş) maçları parlak yeşil ve kırmızı renklerle vurgulanmıştır.
4. **`create_parallel_coordinates` (Advanced - Paralel Koordinatlar):**
   * **Amaç:** Ev Sahibi Oranı, Beraberlik Oranı, Deplasman Oranı, 2.5 Üst Oranı ve Toplam Gol boyutlarının maç sonucuna (Ev/Dep/Beraberlik) göre eşzamanlı izlenmesi.
5. **`create_network_graph` (Advanced - Network Diyagramı):**
   * **Amaç:** Seçilen ligin zirve takımları arasındaki galibiyet/üstünlük ağı (NetworkX tabanlı). Düğümler takımları, yönlü kenarlar galibiyetleri temsil eder; düğüm boyutu toplam galibiyetle büyür.
6. **`create_odds_contour_density` (Advanced - 2D Yoğunluk Konturu):**
   * **Amaç:** Bahis oranlarının piyasadaki yoğunluk yüzeyi ve sürpriz maçların (upsets) toplandığı oran kombinasyonlarının tespiti.
7. **`create_score_heatmap` (Analitik - Isı Haritası):**
   * **Amaç:** En sık görülen skor kombinasyonları (0-5 ev golü x 0-5 deplasman golü frekans matrisi).
8. **`create_calibration_scatter` (Analitik - Değer Bahsi & Kalibrasyon Saçılımı):**
   * **Amaç:** Bahis bürolarının ima ettiği kazanma olasılığı ($1 / \text{odds}$) ile gerçek galibiyet frekansının 45 derecelik ideal doğruluk çizgisiyle karşılaştırılması.
9. **`create_league_goals_violin` (Analitik - Keman/Kutu Grafiği):**
   * **Amaç:** Lig bazında maç başına atılan gollerin dağılımı, çeyreklikler, medyan ve aykırı yüksek skorlu maçların (outliers) tespiti.

---

### 🤖 [Adım 5] - 10 Kasım 2026: Makine Öğrenmesi Modülü (`src/ml_engine.py`)

Ödevin 2. maddesinde istenen **2 temel makine öğrenmesi algoritması** entegre edildi:

1. **Algoritma 1: K-Means Clustering (Takım Taktik Profilleri)**
   * **Girdiler:** Maç başına atılan gol, maç başına yenilen gol, galibiyet yüzdesi.
   * **Kümeleme Sonucu:** Takımlar 3 ana gruba ayrıldı:
     - *Elite Dominators* (Yüksek gol, az gol yiyen, yüksek galibiyetli takımlar)
     - *Balanced Competitors* (Orta sıra dengeli ekipler)
     - *Relegation Strugglers* (Savunma zafiyeti yaşayan ekipler)
   * **Görselleştirme:** İnteraktif 2D saçılım grafiği (ters çevrilmiş Y ekseni ile daha iyi savunmalar yukarıda konumlanır).

2. **Algoritma 2: Logistic Regression (Maç Sonucu Tahmini & Öznitelik Ağırlıkları)**
   * **Girdiler:** Piyasa oranları (`home_odds`, `draw_odds`, `away_odds`) ve saf olasılıklar.
   * **Hedef:** Maç Sonucu (`H`, `D`, `A`).
   * **Başarı:** ~%56 doğruluk (Rastgele 3 sınıf tahmin oranı olan %33'e göre belirgin istatistiksel üstünlük).
   * **Görselleştirme:** Karmaşıklık Matrisi (Confusion Matrix) ve Ev Sahibi Galibiyetini belirleyen en kritik oranların ağırlık çubuk grafiği (Feature Importance).


---

### 🖥️ [Adım 6] - 10 Kasım 2026: Streamlit Arayüzü & İnteraktif Kontrol Paneli (`app.py`)

Ödevin 2., 3. ve 4. gereksinimlerini karşılayan ana uygulama tamamlandı:

#### 6.1. İnteraktif Bileşenler (Ödev En Az 3 Tane İstiyordu $\rightarrow$ 6 Adet Eklendi):
1. **Multiselect Dropdown:** Ligleri tek tek veya topluca seçip filtreleme.
2. **Selectbox:** Sezon seçimi ("All Seasons", "2024-2025", "2023-2024").
3. **Range Slider:** Toplam gol aralığı filtresi (0 - 10 gol).
4. **Float Slider:** Ev sahibi maksimum bahis oranı filtresi (1.0 - 15.0).
5. **Checkbox:** Sadece ilk yarı mağlup olup maçı çeviren sürpriz ("Comeback") maçları filtreleme.
6. **Slider (ML Bölümü):** K-Means küme sayısı seçimi ($k=2 \dots 5$).
7. **Number Inputs (Simülatör):** Canlı maç tahmini için oran simülasyonu.

#### 6.2. Dashboard Düzeni & Görsel Hiyerarşi:
* **KPI Metrik Kartları:** Anlık filtrelenen maç sayısı, maç başına ortalama gol, ev sahibi galibiyet oranı, 2.5 üst oranı, karşılıklı gol (BTTS) oranı.
* **4 Tematik Sekme (Tabs):**
  - **Sekme 1 (Coğrafya & Lig):** Harita (Choropleth), Treemap, Keman/Kutu Dağılımı.
  - **Sekme 2 (Maç Akışı & Oranlar):** Sankey Akış Diyagramı, Paralel Koordinatlar, 2D Yoğunluk Konturu.
  - **Sekme 3 (Skorlar & Ağlar):** Skor Matrisi Isı Haritası, Kalibrasyon Saçılımı, Takım Dominans Ağı (NetworkX).
  - **Sekme 4 (Makine Öğrenmesi):** K-Means Takım Profili Dağılımı, Lojistik Regresyon Karmaşıklık Matrisi, Özellik Ağırlıkları ve Canlı Maç Tahmin Simülatörü.
* **Veri Gezgini & Dışa Aktarma:** Filtrelenmiş tablonun canlı incelenmesi ve CSV formatında indirilebilmesi (`st.download_button`).


---

### 🇪🇸 [Adım 7] - 10 Kasım 2026: İspanya (La Liga - `SP1`) Entegrasyonu

* **Eklenen Lig:** 🇪🇸 İspanya La Liga (`SP1` - ISO3: `ESP`)
* **Eklenen Maç Sayısı:** **+760 Maç**
* **Güncel Toplam Maç Sayısı:** **5.421 Maç**
* **Güncel Lig Sayısı:** **8 Büyük Avrupa Ligi** (İngiltere, İspanya, İtalya, Almanya, Fransa, Hollanda, Portekiz, Türkiye)
* **Etki:** Avrupa Coğrafi Haritasında (Choropleth Map) İber Yarımadası artık Portekiz ile birlikte İspanya'yı da kapsayarak görsel bütünlüğü tamamladı. Treemap ve Takım Ağlarına Real Madrid, Barcelona ve Atletico Madrid gibi devler eklendi.


---

### 🔬 [Adım 8] - 10 Kasım 2026: Kapsamlı Veri Kalitesi & Metrik Denetimi (Audit)

İspanya'nın (La Liga) eklenmesiyle tüm istatistiki metriklerin tutarlılığı ve veri kalitesi baştan sona denetlendi:

#### 8.1. Eksik Değer & Veri Bütünlüğü Kontrolü:
* 5.421 maçlık havuzda sadece 1 adet eksik ilk yarı skoru tespit edildi ve `data_loader.py` pipeline'ına eklenen doğrulama kuralı ile filtrelendi.
* **Nihai Temiz Veri Seti:** Tam olarak **5.420 maç**, **0 eksik değer**.

#### 8.2. Lig Bazlı Metrik Karşılaştırma Matrisi:
| Lig Adı | Maç Sayısı | Maç Başı Gol | Ev Sahibi Galibiyet % | Beraberlik % | Deplasman % | 2.5 Üst % | KG Var (BTTS) % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🇩🇪 Bundesliga | 612 | **3.18** | 41.2% | 26.0% | 32.8% | **61.1%** | 59.5% |
| 🇳🇱 Eredivisie | 612 | **3.11** | 44.3% | 25.0% | 30.7% | **59.5%** | 56.1% |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League | 760 | **3.11** | 43.4% | 23.0% | **33.6%** | **60.7%** | 59.5% |
| 🇹🇷 Süper Lig | 694 | 2.86 | **46.5%** | 25.4% | 28.1% | 52.7% | 55.5% |
| 🇫🇷 Ligue 1 | 611 | 2.83 | 43.0% | 23.4% | **33.6%** | 54.2% | 55.3% |
| 🇵🇹 Primeira Liga | 612 | 2.72 | 43.3% | 25.2% | 31.5% | 52.1% | 51.1% |
| 🇪🇸 **La Liga** | **760** | **2.63** | **44.2%** | **26.8%** | **29.0%** | **47.4%** | **51.8%** |
| 🇮🇹 Serie A | 760 | **2.59** | 40.8% | **29.0%** | 30.3% | 48.7% | 52.0% |
| **GENEL TOPLAM** | **5.420** | **2.87** | **43.4%** | **25.5%** | **31.1%** | **54.3%** | **55.1%** |

#### 8.3. Kritik Analitik Çıkarımlar:
1. **La Liga & Serie A Benzerliği:** İspanya La Liga (2.63 gol/maç) ve İtalya Serie A (2.59 gol/maç), Avrupa'nın taktiksel savunma disiplini en yüksek iki ligi olarak öne çıkıyor. İspanya'da maçların sadece %47.4'ü 2.5 üst biterken, Bundesliga'da bu oran %61.1'e ulaşıyor.
2. **Ev Sahibi Avantajı Lideri:** Avrupa'da evinde en çok kazanan lig **%46.5** ile **Türkiye Süper Lig** oldu.
3. **İlk Yarı Üstünlüğü:** İlk yarıyı önde kapatan bir takımın maçı kazanma olasılığı genel ortalamada **%75.5** (1.394 / 1.846 maç).
4. **Geri Dönüş (Comeback) Nadirliği:** İlk yarıyı mağlup kapatıp maçı kazanan takım sayısı tüm maçlar içinde sadece **%5.6** (302 maç).
