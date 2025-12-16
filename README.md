# 🍅 Pomodoro Odaklanma & To-Do Uygulaması

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-FF4B4B?style=flat-square&logo=streamlit)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-CC342D?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)

---

## Proje Açıklaması

Modern web teknolojileri ile inşa edilmiş, tamamen işlevsel bir Pomodoro zamanlayıcı ve kalıcı görev listesi uygulaması. 

**Teknoloji Yığını:** Streamlit • SQLAlchemy • SQLite • Python • CSS3 • Docker

Demo link: https://4eb00711-f5fb-41ca-acbb-8d6c7291813f-00-3tkh8anv511b5.sisko.replit.dev/

## Demo

![Demo](https://github.com/thisiscenkcetin/yetgim-pomodoro-todo/blob/main/demo.png?raw=true) 

![Demo](https://github.com/thisiscenkcetin/yetgim-pomodoro-todo/blob/main/demo2.png?raw=true) 

![Demo](https://github.com/thisiscenkcetin/yetgim-pomodoro-todo/blob/main/demo3.png?raw=true) 

![Demo](https://github.com/thisiscenkcetin/yetgim-pomodoro-todo/blob/main/demo4.png?raw=true) 

---

## Teknik Uygulama Detayları

### Veritabanı Modelleri (SQLAlchemy ORM)

```python
# models.py - SQLAlchemy ile tanımlanmış ORM modelleri
class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_type = Column(String, nullable=False, index=True)  # 'pomodoro' | 'short_break' | 'coffee_break'
    
    # Zaman Takibi
    start_time = Column(DateTime, nullable=False, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    planned_duration = Column(Integer, nullable=False)
    actual_duration = Column(Integer, nullable=True)
    
    # Durumu
    completed = Column(Boolean, default=False, index=True)
    date = Column(DateTime, nullable=False, default=datetime.now, index=True)
```

**Öne Çıkan Özellikler:**
- İlişkisel veri bütünlüğü ve otomatik migration desteği
- Tarih-tabanlı raporlama için indexed columns
- Soft-delete pattern desteği (abandoned sessions)

---

### State Management & Timer Persistensi

```python
# app.py - Streamlit Session State Yapılandırması
if 'mode' not in st.session_state:
    st.session_state.mode = 'pomodoro'
if 'pomodoro_time' not in st.session_state:
    st.session_state.pomodoro_time = 25 * 60
if 'short_break_time' not in st.session_state:
    st.session_state.short_break_time = 5 * 60
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'current_time' not in st.session_state:
    st.session_state.current_time = 25 * 60
if 'session_number' not in st.session_state:
    st.session_state.session_number = 1
if 'active_session_id' not in st.session_state:
    st.session_state.active_session_id = None
if 'session_start_time' not in st.session_state:
    st.session_state.session_start_time = None
if 'show_report_modal' not in st.session_state:
    st.session_state.show_report_modal = False
```

**Mimari Avantajlar:**
- Streamlit rerender sırasında timer durumunu korur
- Multilevel state tracking (mode, timing, session management)
- Veritabanında oturum persistence ile frontend state senkronizasyonu

---

### Timer Mantığı & Oturum Kaydı

```python
# app.py - Timer döngüsü ve veritabanı entegrasyonu
if st.session_state.timer_running:
    if st.session_state.current_time > 0:
        time.sleep(1)
        st.session_state.current_time -= 1
        st.rerun()
    else:
        st.session_state.timer_running = False
        
        # Oturumu tamamlandı olarak işaretle
        if st.session_state.active_session_id:
            db = next(get_db())
            session = db.query(PomodoroSession).filter(
                PomodoroSession.id == st.session_state.active_session_id
            ).first()
            if session:
                session.end_time = datetime.now()
                session.actual_duration = int(
                    (datetime.now() - session.start_time).total_seconds() / 60
                )
                session.completed = True
                db.commit()
            db.close()
            st.session_state.active_session_id = None
        
        st.balloons()
        st.rerun()
```

**Teknik Detaylar:**
- 1 saniyelik uyku ile smooth timer güncellemesi
- Gerçek süre hesaplaması (planlanan vs. gerçek)
- Veritabanı senkronizasyonu tamamlanmada

---

### İstatistik Hesaplamaları & Raporlama

```python
# app.py - Gelişmiş query ve analitik hesaplamalar
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
week_ago = today - timedelta(days=7)

# Günlük Pomodoro oturumları
today_work_sessions = db.query(PomodoroSession).filter(
    PomodoroSession.date >= today,
    PomodoroSession.completed == True,
    PomodoroSession.session_type == 'pomodoro'
).all()

# Haftalık mola oturumları
week_break_sessions = db.query(PomodoroSession).filter(
    PomodoroSession.date >= week_ago,
    PomodoroSession.completed == True,
    PomodoroSession.session_type.in_(['short_break', 'coffee_break'])
).all()

# Toplam istatistikler
today_work_mins = sum([(s.actual_duration or 0) for s in today_work_sessions]) / 60
week_break_mins = sum([(s.actual_duration or 0) for s in week_break_sessions]) / 60

# Tamamlama oranı
total_sessions = db.query(PomodoroSession).count()
completed_sessions = len(all_sessions)
completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0

# Streak hesaplaması (ardışık günler)
all_dates = db.query(PomodoroSession.date).filter(
    PomodoroSession.completed == True
).distinct().order_by(PomodoroSession.date.desc()).all()

streak = 0
current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
for date_tuple in all_dates:
    session_date = date_tuple[0].replace(hour=0, minute=0, second=0, microsecond=0)
    if session_date == current_date:
        streak += 1
        current_date = current_date - timedelta(days=1)
    elif session_date == current_date - timedelta(days=1):
        streak += 1
        current_date = current_date - timedelta(days=1)
    else:
        break
```

**Sorgu Özellikleri:**
- Index kullanan optimal filtering
- Dinamik agregasyon (SUM, COUNT, DISTINCT)
- Tarih-tabanlı periyodik analiz
- Motivasyon metrikleri (streak tracking)

---

### Görev Yönetimi & Dinamik UI

```python
# app.py - CRUD operasyonları ve interaktif görev listesi
tasks = db.query(Todo).order_by(Todo.created_at.desc()).all()

for task in tasks:
    col_check, col_text, col_del = st.columns([0.8, 4, 1], gap="small")
    
    with col_check:
        # Type casting - SQLAlchemy Column to Python bool
        task_completed: bool = cast(bool, task.is_done)
        is_done = st.checkbox(
            "✓", 
            value=task_completed, 
            key=f"check_{task.id}", 
            label_visibility="collapsed"
        )
        if is_done != task_completed:
            task.is_done = is_done
            db.commit()
            st.rerun()
    
    with col_text:
        task_completed = cast(bool, task.is_done)
        task_class = 'task-completed' if task_completed else 'task-item'
        st.markdown(
            f"<div class='{task_class}'>{task.title}</div>", 
            unsafe_allow_html=True
        )
    
    with col_del:
        if st.button("✕", key=f"del_{task.id}", help="Görev sil"):
            db.delete(task)
            db.commit()
            st.rerun()
```


## Hızlı Başlangıç

### Seçenek 1: Docker ile (Önerilen)

```bash
git clone https://github.com/yourusername/yetgim-pomodoro-todo.git
cd yetgim-pomodoro-todo

docker build -t pomodoro-app .
docker run -p 8501:8501 pomodoro-app
```

Ardından tarayıcıda `http://localhost:8501` adresine gidin.

---

### Seçenek 2: Manuel Kurulum

```bash
# Depoyu klonla
git clone https://github.com/yourusername/yetgim-pomodoro-todo.git
cd yetgim-pomodoro-todo

# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı çalıştır
streamlit run app.py
```

Tarayıcı otomatik olarak `http://localhost:8501` adresinde açılır.

---

## Özellikler

✨ **Pomodoro Zamanlayıcı**
- 25 dakika çalışma, 5 dakika kısa mola, 15 dakika kahve molası
- Özelleştirilebilir zaman aralıkları

✨ **Kalıcı Görev Listesi**
- SQLite veritabanında saklanan görevler
- Tamamlanmış/Tamamlanmamış durumu takibi

✨ **Gelişmiş İstatistikler**
- Günlük ve haftalık çalışma raporları
- Tamamlama oranları ve Streak takibi
- Modal popup ile detaylı analitik

✨ **Modern Tasarım**
- Glassmorphism UI konsepti
- Responsif ve kullanıcı dostu arayüz
- Türkçe tam lokalizasyon

---

## Proje Yapısı

```
yetgim-pomodoro-todo/
├── app.py                 # Ana Streamlit uygulaması
├── models.py              # SQLAlchemy ORM tanımları
├── requirements.txt       # Python bağımlılıkları
├── Dockerfile             # Docker konfigürasyonu
├── todos.db               # SQLite veritabanı (otomatik oluşturulur)
└── README.md              # Dokumentasyon
```

---

## 📦 Gereksinimler

- Python 3.10+
- Streamlit 1.20+
- SQLAlchemy 2.0+
- Docker (opsiyonel)

Tüm bağımlılıklar `requirements.txt` dosyasında listelenir.

---

**Geliştirici:** Cenk Çetin  
**Email:** dev.cenkcetin@gmail.com  

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır.
