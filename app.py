import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="ТехДок База",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stHeader"], #MainMenu, footer {display:none!important;}
[data-testid="stAppViewContainer"] {background:#eef4f9;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#123d64 0%,#0a2f50 58%,#082944 100%);}
[data-testid="stSidebar"] * {color:#eef6fc;}
[data-testid="stSidebar"] .stButton>button {width:100%;text-align:left;justify-content:flex-start;background:transparent;border:0;color:#eaf3fa;padding:.55rem .7rem;border-radius:6px;font-size:.86rem;}
[data-testid="stSidebar"] .stButton>button:hover {background:#2b6fa7;border:0;color:white;}
.block-container {max-width:1600px;padding:1rem 1.25rem 2rem 1.25rem;}
h1,h2,h3 {color:#122b46;}
.demo-badge {display:inline-block;background:#fff3c8;color:#735605;border:1px solid #ead48a;border-radius:999px;padding:5px 10px;font-size:11px;font-weight:700;}
.top-title {font-size:1.15rem;font-weight:800;color:#132d49;margin-bottom:2px;}
.top-sub {font-size:.78rem;color:#71869a;margin-bottom:8px;}
.card {background:white;border:1px solid #dde6ee;border-radius:8px;box-shadow:0 2px 10px rgba(15,49,83,.07);padding:12px;}
.small {font-size:.75rem;color:#70859a;}
.ok {color:#16895b;font-weight:700;}
.warn {color:#b9770b;font-weight:700;}
.review {color:#d13a3a;font-weight:700;}
.kpi-label {font-size:.72rem;color:#536a80;}
.kpi-value {font-size:1.55rem;font-weight:800;color:#102942;line-height:1.1;}
.kpi-delta {font-size:.68rem;color:#149b63;margin-top:5px;}
.section-title {font-size:.96rem;font-weight:800;color:#142d48;margin:0 0 8px 0;}
.tree-line {padding:5px 8px;border-radius:5px;font-size:.82rem;color:#30495f;}
.tree-line.sel {background:#dcecff;color:#0d4c88;font-weight:700;}
.query-chip {background:#f8fbfe;border:1px solid #d8e3eb;border-radius:6px;padding:9px;font-size:.76rem;color:#567086;min-height:54px;}
hr {border-color:#dfe7ee!important;}
div[data-testid="stMetric"] {background:white;border:1px solid #dde6ee;border-radius:8px;padding:10px 12px;box-shadow:0 2px 10px rgba(15,49,83,.07);}
.stTabs [data-baseweb="tab-list"] {gap:4px;}
.stTabs [data-baseweb="tab"] {background:#f4f8fb;border-radius:6px 6px 0 0;padding:8px 12px;}
.stDataFrame {border:1px solid #dde6ee;border-radius:6px;overflow:hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------- DEMO DATA --------------------
# Названия частично похожи на реальный массив проекта; все количества и результаты демонстрационные.
DOCS = [
    ["ECRT0000248608РЭ", "Руководство по ТО и ТР ЭВС360", "v6.5", 71, 1842, 63, "Обработан", "12.09.2026"],
    ["СТМГ190.90.00.000РЭ", "Головная сцепка", "ред. 4", 152, 1216, 38, "Обработан", "11.09.2026"],
    ["СТМГ190.00.00.000РЭ", "Сцепное устройство", "ред. 3", 286, 2408, 74, "Обработан", "10.09.2026"],
    ["DEMO-KSK-01", "Диски КСК", "ред. 2", 94, 812, 26, "Обработан", "09.09.2026"],
    ["DEMO-STAB-01", "Стабилизатор", "ред. 5", 138, 1164, 31, "Обработан", "08.09.2026"],
    ["DEMO-COMP-01", "Компрессорный агрегат", "v4", 286, 1842, 63, "Обработан", "07.09.2026"],
    ["DEMO-BRAKE-01", "Тормозное оборудование", "v3", 412, 3117, 128, "Обработан", "05.09.2026"],
    ["DEMO-DOOR-01", "Дверная система", "v2", 158, 974, 18, "Обработан", "04.09.2026"],
    ["DEMO-HVAC-01", "Климатическая установка", "v1", 320, 2406, 71, "Обработан", "02.09.2026"],
    ["DEMO-BOGIE-01", "Оборудование тележки", "v2", 502, 4881, 210, "Требует проверки", "31.08.2026"],
    ["ECPT0000001768", "Интервалы технического обслуживания", "2026", 48, 386, 12, "Обработан", "29.08.2026"],
    ["DEMO-CONV-01", "Тяговый преобразователь", "v5", 364, 2760, 96, "Обработка", "28.08.2026"],
]
DOC_COLS = ["Обозначение", "Документ", "Версия", "Страниц", "Блоков", "Таблиц", "Статус", "Дата"]
DOC_DF = pd.DataFrame(DOCS, columns=DOC_COLS)

BLOCKS = pd.DataFrame([
    [101, "Заголовок", "5.3 Операции технического обслуживания", 54, "OK"],
    [102, "Текст", "Периодическое техническое обслуживание выполняют...", 54, "OK"],
    [103, "Таблица", "Таблица 5-3. Перечень операций ТО", 55, "OK"],
    [104, "Текст", "Перед началом выполнения работ необходимо...", 56, "OK"],
    [105, "Список", "Убедиться в отсутствии давления...", 56, "OK"],
    [106, "Предупреждение", "ВНИМАНИЕ! Перед снятием крышки...", 56, "OK"],
    [107, "Текст", "Проверить состояние фильтрующего элемента...", 57, "OK"],
    [108, "Рисунок", "Рис. 5-12. Расположение фильтра", 57, "OK"],
    [109, "Текст", "Заменить уплотнительные кольца...", 58, "NEED_REVIEW"],
    [110, "Таблица", "Нормы расхода материалов", 58, "OK"],
], columns=["№", "Тип", "Содержание", "Стр.", "Статус"])

MAINT = pd.DataFrame([
    ["Компрессор", "Проверка состояния воздушного фильтра", "IS50", "Осмотр, очистка при необходимости"],
    ["Компрессор", "Замена фильтрующего элемента", "IS300", "Демонтаж, установка нового элемента"],
    ["Тормозное оборудование", "Проверка герметичности соединений", "IS100", "Визуальный осмотр, устранение утечек"],
    ["Компрессор", "Проверка крепления", "IS300", "Контроль момента затяжки"],
    ["Сцепное устройство", "Контроль состояния механических соединений", "IS600", "Осмотр и проверка состояния"],
    ["Оборудование тележки", "Контроль элементов ходовой части", "IS600", "Осмотр, контроль состояния"],
], columns=["Компонент", "Операция", "Интервал", "Состав работ"])

REQS = pd.DataFrame([
    ["Безопасность", "Работы выполнять после снятия напряжения и подтверждения безопасного состояния", "ЭВС360", "Высокий"],
    ["Пневматика", "Перед разъединением пневматических соединений сбросить давление", "Тормозное оборудование", "Высокий"],
    ["Крепёж", "После установки выполнить контроль крепления", "Компрессор", "Средний"],
    ["Смазка", "Применять материал, указанный в эксплуатационной документации", "Оборудование тележки", "Средний"],
    ["Проверка", "После замены подтвердить результат выполненных работ", "Общие требования", "Высокий"],
], columns=["Тема", "Требование", "Объект", "Важность"])

FAULTS = pd.DataFrame([
    ["Компрессор", "Недостаточная производительность", "Засорение фильтра", "Проверить/очистить фильтр"],
    ["Дверная система", "Дверь не закрывается", "Препятствие или нарушение регулировки", "Осмотр и диагностика"],
    ["Климатическая установка", "Недостаточное охлаждение", "Загрязнение теплообменника", "Проверить состояние"],
    ["Сцепное устройство", "Неполное сцепление", "Механическое препятствие", "Осмотр зоны сцепления"],
], columns=["Компонент", "Неисправность", "Возможная причина", "Действие"])

if "page" not in st.session_state:
    st.session_state.page = "Главная"
if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = 0

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("### ⚙️ ТехДок База")
    st.caption("Структурированная техническая документация")
    st.markdown("---")
    menu = [
        ("🏠", "Главная"), ("📄", "Документы"), ("🔎", "Поиск"),
        ("🧩", "Компоненты"), ("🔧", "Техническое обслуживание"),
        ("📋", "Требования"), ("⚠️", "Неисправности"), ("▦", "Таблицы"),
        ("🖼️", "Рисунки"), ("◴", "Сравнение версий"), ("⬇️", "Экспорт"), ("⚙", "Настройки")
    ]
    for ico, label in menu:
        if st.button(f"{ico}  {label}", key=f"nav_{label}"):
            st.session_state.page = label
            st.rerun()
    st.markdown("---")
    st.caption("Использование")
    st.progress(0.423)
    st.caption("42.3 ГБ из 100 ГБ")
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Документов: 86")
    st.caption("Обновлено: 12.09.2026 14:32")

# -------------------- TOP BAR --------------------
left, middle, right = st.columns([6.5, 2, 1.2])
with left:
    global_search = st.text_input("Поиск", placeholder="Поиск по всей документации... например: операции ТО компрессора", label_visibility="collapsed")
with middle:
    if st.button("💬 Задать вопрос в ChatGPT", use_container_width=True):
        st.session_state.page = "AI-запрос"
        st.rerun()
with right:
    st.markdown('<span class="demo-badge">ДЕМО · 2026</span>', unsafe_allow_html=True)

if global_search:
    st.session_state.page = "Поиск"

page = st.session_state.page

# -------------------- HELPERS --------------------
def title(text, sub=None):
    st.markdown(f'<div class="top-title">{text}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="top-sub">{sub}</div>', unsafe_allow_html=True)


def show_doc_detail(idx):
    d = DOC_DF.iloc[idx]
    title(f'{d["Документ"]} · {d["Обозначение"]}', f'Версия {d["Версия"]} · {d["Страниц"]} стр. · демонстрационные результаты разбора')
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Страниц", int(d["Страниц"]))
    m2.metric("Блоков", f'{int(d["Блоков"]):,}'.replace(","," "))
    m3.metric("Таблиц", int(d["Таблиц"]))
    m4.metric("NEED_REVIEW", "8")
    m5.metric("Статус", d["Статус"])
    st.markdown("### Структура документа")
    c1,c2,c3 = st.columns([.85,1.25,1.25])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="tree-line">▸ 1. Общие сведения</div>', unsafe_allow_html=True)
        st.markdown('<div class="tree-line">▸ 2. Технические характеристики</div>', unsafe_allow_html=True)
        st.markdown('<div class="tree-line">▸ 3. Конструкция и принцип работы</div>', unsafe_allow_html=True)
        st.markdown('<div class="tree-line">▸ 4. Эксплуатация</div>', unsafe_allow_html=True)
        st.markdown('<div class="tree-line">⌄ 5. Техническое обслуживание</div>', unsafe_allow_html=True)
        st.markdown('<div class="tree-line">&nbsp;&nbsp;&nbsp;5.1 Общие указания</div>', unsafe_allow_html=True)
        st.markdown('<div class="tree-line">&nbsp;&nbsp;&nbsp;5.2 Перечень работ</div>', unsafe_allow_html=True)
        st.markdown('<div class="tree-line sel">&nbsp;&nbsp;&nbsp;5.3 Операции ТО</div>', unsafe_allow_html=True)
        st.markdown('<div class="tree-line">&nbsp;&nbsp;&nbsp;5.4 Расходные материалы</div>', unsafe_allow_html=True)
        st.markdown('<div class="tree-line">▸ 6. Неисправности</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("**Блоки раздела 5.3**")
        selected = st.dataframe(BLOCKS, hide_index=True, use_container_width=True, height=355, on_select="rerun", selection_mode="single-row", key=f"blocks_{idx}")
        row = selected.selection.rows[0] if selected.selection.rows else 2
        selected_block = BLOCKS.iloc[row]
    with c3:
        t1,t2,t3 = st.tabs(["Просмотр блока", "Оригинальная страница", "Связанные блоки"])
        with t1:
            st.markdown(f'**{selected_block["Тип"]} · блок {selected_block["№"]}**')
            if selected_block["Тип"] == "Таблица":
                st.dataframe(MAINT.iloc[:5], hide_index=True, use_container_width=True)
            else:
                st.info(selected_block["Содержание"])
            st.caption(f'Страница: {selected_block["Стр."]} · Статус: {selected_block["Статус"]} · ID: DOC_001_B{int(selected_block["№"]):06d}')
        with t2:
            st.markdown("#### Страница 55 · демонстрационный просмотр")
            st.markdown("**5.3 Операции технического обслуживания**")
            st.write("Периодическое техническое обслуживание выполняют в соответствии с установленным интервалом и применимой документацией.")
            st.dataframe(MAINT.iloc[:4], hide_index=True, use_container_width=True)
            st.caption("В реальной системе здесь будет отображаться исходная страница или привязанный фрагмент.")
        with t3:
            st.dataframe(pd.DataFrame([
                [102,"Предыдущий","Периодическое техническое обслуживание..."],
                [103,"Текущий","Таблица 5-3. Перечень операций ТО"],
                [104,"Следующий","Перед началом выполнения работ..."],
            ], columns=["Блок","Связь","Текст"]), hide_index=True, use_container_width=True)

# -------------------- PAGES --------------------
if page == "Главная":
    title("ТехДок База", "Демонстрационный портал структурированной технической документации")
    a,b,c,d,e,f = st.columns(6)
    a.metric("Документов", "86", "+12")
    b.metric("Всего блоков", "48 320", "+3 420")
    c.metric("Таблиц", "2 140", "+217")
    d.metric("Операций ТО", "6 870", "+503")
    e.metric("Компонентов", "4 312")
    f.metric("Требуют проверки", "37", "-8")
    st.write("")
    l,r1,r2 = st.columns([1.65,.95,.85])
    with l:
        st.markdown("#### Последние документы")
        recent = DOC_DF.iloc[:6].copy()
        evt = st.dataframe(recent, hide_index=True, use_container_width=True, height=260, on_select="rerun", selection_mode="single-row", key="home_docs")
        if evt.selection.rows:
            st.session_state.selected_doc = int(evt.selection.rows[0])
    with r1:
        st.markdown("#### Распределение блоков")
        for name,val in [("Текстовые блоки",62),("Таблицы",15),("Списки",8),("Заголовки",6),("Рисунки",4),("Примечания",3),("Предупреждения",1),("Другое",1)]:
            st.caption(f"{name} · {val}%")
            st.progress(val/100)
    with r2:
        st.markdown("#### Типы информации")
        for name,val,num in [("Операции ТО",.84,"6 870"),("Требования",.62,"4 210"),("Тех. характеристики",.55,"3 540"),("Неисправности",.44,"2 980"),("Компоненты",.67,"4 312"),("Интервалы",.54,"3 860")]:
            st.caption(f"{name} · {num}")
            st.progress(val)
    st.write("")
    st.markdown("#### Просмотр выбранного документа")
    show_doc_detail(st.session_state.selected_doc)
    st.write("")
    st.markdown("#### Запросы к базе · примеры")
    qcols = st.columns(6)
    queries = ["Покажи все операции ТО компрессора","Собери требования по смазке","Найди интервалы по тормозам","Сделай Excel по IS300","Покажи противоречия редакций","Собери раздел ТО"]
    for col,q in zip(qcols,queries):
        with col:
            if st.button(q, use_container_width=True, key=f"q_{q}"):
                st.session_state.demo_query = q
                st.session_state.page = "AI-запрос"
                st.rerun()

elif page == "Документы":
    title("Документы", "86 документов в демонстрационной базе · показаны последние 12")
    c1,c2,c3 = st.columns([2,1,1])
    with c1: flt = st.text_input("Фильтр по названию или обозначению")
    with c2: status = st.selectbox("Статус", ["Все","Обработан","Требует проверки","Обработка"])
    with c3: dtype = st.selectbox("Тип", ["Все","РЭ","Руководство","Таблица интервалов"])
    view_df = DOC_DF.copy()
    if flt:
        mask = view_df["Документ"].str.contains(flt, case=False) | view_df["Обозначение"].str.contains(flt, case=False)
        view_df = view_df[mask]
    if status != "Все": view_df = view_df[view_df["Статус"]==status]
    evt = st.dataframe(view_df, hide_index=True, use_container_width=True, height=400, on_select="rerun", selection_mode="single-row", key="docs_all")
    if evt.selection.rows:
        chosen_index = view_df.index[evt.selection.rows[0]]
        st.session_state.selected_doc = int(chosen_index)
    if st.button("Открыть выбранный документ"):
        st.session_state.page = "Документ"
        st.rerun()

elif page == "Документ":
    show_doc_detail(st.session_state.selected_doc)
    if st.button("← К списку документов"):
        st.session_state.page = "Документы"; st.rerun()

elif page == "Поиск":
    title("Поиск по всей базе", "Поиск работает по демонстрационному набору")
    q = global_search or st.text_input("Введите запрос", value="компрессор")
    scope = st.multiselect("Искать в", ["Документах","Операциях ТО","Требованиях","Неисправностях","Таблицах"], default=["Документах","Операциях ТО","Требованиях"])
    st.markdown("### Результаты")
    if q:
        docres = DOC_DF[DOC_DF.astype(str).apply(lambda x: x.str.contains(q, case=False).any(), axis=1)]
        opres = MAINT[MAINT.astype(str).apply(lambda x: x.str.contains(q, case=False).any(), axis=1)]
        if len(docres): st.dataframe(docres, hide_index=True, use_container_width=True)
        if len(opres): st.dataframe(opres, hide_index=True, use_container_width=True)
        if not len(docres) and not len(opres): st.info("Для демонстрации показываем смысловой результат: найдено 14 связанных блоков в 4 документах.")

elif page == "Компоненты":
    title("Компоненты", "Демонстрационное дерево обслуживаемых компонентов")
    comps = pd.DataFrame([
        ["GC-20-00","Кузов и интерьер",82,1240],["GC-21-10","Дверное оборудование",18,416],["GC-22-10","Климатическое оборудование",24,528],["HE-10-00","Компрессорное оборудование",16,387],["BR-20-00","Тормозное оборудование",31,864],["BG-30-00","Оборудование тележки",57,1436],["CP-10-00","Сцепные устройства",22,612]
    ], columns=["SNS","Группа компонентов","Компонентов","Связанных блоков"])
    st.dataframe(comps, hide_index=True, use_container_width=True)
    selected = st.selectbox("Выберите группу", comps["Группа компонентов"].tolist())
    st.success(f"{selected}: найдено 24 операции ТО, 11 требований, 6 таблиц и 3 предупреждения. Данные демонстрационные.")

elif page == "Техническое обслуживание":
    title("Техническое обслуживание", "Операции ТО, интервалы, назначение и состав работ")
    c1,c2 = st.columns(2)
    with c1: interval = st.multiselect("Интервал", sorted(MAINT["Интервал"].unique()), default=[])
    with c2: component = st.selectbox("Компонент", ["Все"] + sorted(MAINT["Компонент"].unique()))
    df = MAINT.copy()
    if interval: df=df[df["Интервал"].isin(interval)]
    if component != "Все": df=df[df["Компонент"]==component]
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.caption("В реальной системе отсюда можно формировать План ТО, Excel и выборки по компонентам.")

elif page == "Требования":
    title("Требования", "Требования, критерии, предупреждения и ограничения")
    topic = st.multiselect("Тема", REQS["Тема"].tolist())
    df=REQS if not topic else REQS[REQS["Тема"].isin(topic)]
    st.dataframe(df, hide_index=True, use_container_width=True)

elif page == "Неисправности":
    title("Неисправности", "Поиск неисправностей, причин и связанных действий")
    st.dataframe(FAULTS, hide_index=True, use_container_width=True)

elif page == "Таблицы":
    title("Таблицы", "2 140 распознанных таблиц · демонстрационная выборка")
    tbl = pd.DataFrame([
        ["ECRT0000248608РЭ","5-3","Операции ТО",55,5,"OK"],["СТМГ190.90.00.000РЭ","4-1","Технические характеристики",42,12,"OK"],["DEMO-COMP-01","7-2","Нормы расхода материалов",118,18,"OK"],["DEMO-BRAKE-01","6-4","Перечень неисправностей",203,24,"NEED_REVIEW"],["ECPT0000001768","1","Интервалы ТО",14,32,"OK"]
    ], columns=["Документ","Таблица","Название","Страница","Строк","Статус"])
    st.dataframe(tbl, hide_index=True, use_container_width=True)

elif page == "Рисунки":
    title("Рисунки", "Демонстрационный каталог рисунков и схем")
    cols=st.columns(3)
    figs=[("Рис. 5-12","Расположение фильтра","DEMO-COMP-01"),("Рис. 4-8","Сцепной механизм","СТМГ190.90.00.000РЭ"),("Рис. 6-3","Размещение оборудования тележки","DEMO-BOGIE-01")]
    for col,(n,t,d) in zip(cols,figs):
        with col:
            st.markdown(f'<div class="card"><div style="height:150px;background:linear-gradient(135deg,#dbe8f3,#f6f9fb);display:flex;align-items:center;justify-content:center;border-radius:6px;font-size:46px">⌗</div><b>{n}</b><br><span class="small">{t}<br>{d}</span></div>', unsafe_allow_html=True)

elif page == "Сравнение версий":
    title("Сравнение версий", "Пример сравнения редакций документа")
    c1,c2 = st.columns(2)
    with c1: st.selectbox("Базовая версия", ["ECRT0000248608РЭ v6.4","СТМГ190.90.00.000РЭ ред.3"])
    with c2: st.selectbox("Новая версия", ["ECRT0000248608РЭ v6.5","СТМГ190.90.00.000РЭ ред.4"])
    st.metric("Изменено блоков", "37")
    diff=pd.DataFrame([["4.4.3","Изменено","Уточнена логика устранения несоответствия"],["6.2","Изменено","Уточнена проверка после выполнения работ"],["Приложение Б","Добавлено","Уточнена ссылка на порядок выполнения операций"],["Таблица интервалов","Без изменений","Содержательная часть не изменилась"]], columns=["Раздел","Статус","Изменение"])
    st.dataframe(diff, hide_index=True, use_container_width=True)

elif page == "Экспорт":
    title("Экспорт", "Как будут собираться выходные файлы из одной базы")
    fmt=st.radio("Формат", ["Excel","Word","CSV","JSON"], horizontal=True)
    dataset=st.selectbox("Состав данных", ["Операции ТО","Требования","Интервалы","Компоненты","NEED_REVIEW","Выбранный документ"])
    cols=st.multiselect("Поля", ["Документ","Компонент","Операция","Интервал","Назначение","Состав работ","Источник","Страница"], default=["Документ","Компонент","Операция","Интервал","Источник"])
    st.info(f"Демо: будет сформирован {fmt} · набор «{dataset}» · полей: {len(cols)}")
    st.button("Сформировать демонстрационный экспорт")

elif page == "Настройки":
    title("Настройки", "Будущие настройки Parser Core и смыслового слоя")
    st.toggle("Сохранять исходный текст блока", value=True, disabled=True)
    st.toggle("Помечать сомнительные блоки NEED_REVIEW", value=True, disabled=True)
    st.toggle("Контроль полноты документа", value=True, disabled=True)
    st.slider("Порог уверенности", 0,100,85, disabled=True)
    st.caption("На демонстрационном этапе настройки не изменяют данные.")

elif page == "AI-запрос":
    title("Запрос к базе", "Демонстрация будущей работы через ChatGPT / Work")
    default_q = st.session_state.get("demo_query", "Покажи все операции ТО для компрессора и интервалы")
    q=st.text_area("Ваш запрос", value=default_q, height=90)
    if st.button("Выполнить демонстрационный запрос", type="primary"):
        st.markdown("### Ответ")
        st.write("Найдено 18 связанных блоков в 4 документах. Ниже показана демонстрационная выборка операций.")
        st.dataframe(MAINT[MAINT["Компонент"].str.contains("Компрессор")], hide_index=True, use_container_width=True)
        st.caption("В рабочей версии ответ будет собираться из фактически разобранной базы с привязкой к источникам.")

else:
    title("Раздел")
    st.info("Демонстрационный раздел.")
