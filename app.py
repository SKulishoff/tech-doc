import streamlit as st

st.set_page_config(
    page_title="ТехДок База — демонстрационный портал",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    r'''
<style>
:root {
  --navy:#0d3153;
  --navy-2:#123f69;
  --blue:#2d7ff9;
  --blue-2:#4a98ff;
  --bg:#eef4f9;
  --panel:#ffffff;
  --line:#d8e3ec;
  --text:#132238;
  --muted:#6b7f95;
  --green:#17a56b;
  --orange:#f0a33b;
  --red:#df3c3c;
  --shadow:0 2px 10px rgba(15,49,83,.08);
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
[data-testid="stHeader"], [data-testid="stToolbar"], footer, #MainMenu {display:none !important;}
.block-container {max-width:none !important; padding:0 !important; margin:0 !important;}
[data-testid="stAppViewContainer"] > .main {overflow-x:hidden;}

*{box-sizing:border-box}
.portal{min-height:100vh;background:var(--bg);}
.sidebar{
  position:fixed;left:0;top:0;bottom:0;width:196px;
  background:linear-gradient(180deg,#123d64 0%,#0a2f50 55%,#082944 100%);
  color:#fff;z-index:100;box-shadow:3px 0 14px rgba(3,26,46,.12);
}
.brand{height:67px;padding:14px 14px 12px 16px;border-bottom:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:10px}
.logo{width:33px;height:33px;border-radius:10px;background:#eaf4ff;color:#174b77;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;box-shadow:inset 0 0 0 1px rgba(255,255,255,.7)}
.brand-title{font-size:18px;font-weight:800;line-height:1.05;letter-spacing:.1px}.brand-sub{font-size:10.5px;color:#bdd2e4;margin-top:5px;white-space:nowrap}
.nav{padding:9px 7px}.nav-item{height:42px;display:flex;align-items:center;gap:11px;padding:0 11px;border-radius:6px;color:#e8f1f8;font-size:13px;margin-bottom:1px}
.nav-item.active{background:linear-gradient(90deg,#2f78b9,#286aa2);box-shadow:inset 0 0 0 1px rgba(255,255,255,.05)}
.nav-ico{width:18px;text-align:center;font-size:15px;opacity:.95}.nav-item span:last-child{line-height:1.2}
.side-bottom{position:absolute;bottom:13px;left:17px;right:17px;font-size:11px;color:#d8e5ef}.side-title{font-weight:700;margin-bottom:9px;color:#fff}.meter{height:9px;background:#2c5577;border-radius:999px;overflow:hidden;margin-bottom:7px}.meter>div{width:42.3%;height:100%;background:#64a9ef;border-radius:999px}.side-meta{margin-top:22px;line-height:2;color:#d6e5ef}

.topbar{position:fixed;z-index:90;left:196px;right:0;top:0;height:66px;background:linear-gradient(90deg,#154875,#0e3c66);display:flex;align-items:center;padding:0 22px;gap:18px;box-shadow:0 2px 9px rgba(11,46,79,.14)}
.search{height:39px;background:#fff;border-radius:6px;flex:1;max-width:625px;display:flex;align-items:center;color:#8aa0b6;font-size:13px;padding:0 13px;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.search .glass{margin-left:auto;color:#0c3155;font-size:18px;border-left:1px solid #e4eaf0;padding-left:15px}
.top-actions{margin-left:auto;display:flex;align-items:center;gap:15px;color:#fff}.chat-btn{background:#2f81e8;border:1px solid rgba(255,255,255,.18);padding:10px 16px;border-radius:6px;font-size:12.5px;font-weight:700;box-shadow:0 4px 12px rgba(0,80,190,.22)}
.help{width:22px;height:22px;border:1px solid #b8cde0;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px}.avatar{width:34px;height:34px;background:#fff;color:#2f6aa5;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800}.admin{font-size:12px}.demo-badge{background:#fff3c8;color:#725607;border:1px solid #ead48a;padding:5px 8px;border-radius:999px;font-size:10px;font-weight:700}

.main-area{margin-left:196px;padding:78px 13px 22px 13px;min-width:900px}
.kpis{display:grid;grid-template-columns:repeat(6,minmax(150px,1fr));gap:8px;margin-bottom:10px}.card{background:var(--panel);border:1px solid #dfe8ef;border-radius:5px;box-shadow:var(--shadow)}
.kpi{height:88px;padding:13px 13px;display:flex;align-items:center;gap:12px}.kpi-icon{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:700}.kpi-icon.blue{background:#e4f0ff;color:#2d7ff9}.kpi-icon.gray{background:#edf2f6;color:#63788d}.kpi-icon.green{background:#e2f5ec;color:#20956c}.kpi-icon.red{background:#fde8e8;color:#d94040}
.kpi-label{font-size:11px;color:#31475b}.kpi-value{font-size:22px;font-weight:800;margin-top:2px;line-height:1}.delta{font-size:10px;color:#0b9c5d;margin-top:8px;font-weight:600}.delta.down{color:#df3333}

.top-grid{display:grid;grid-template-columns:1.65fr .93fr .82fr;gap:9px;margin-bottom:10px}.panel{padding:0;overflow:hidden}.panel-head{height:41px;padding:0 14px;display:flex;align-items:center;border-bottom:1px solid #edf1f5;font-size:14px;font-weight:800;color:#142d48}.panel-link{margin-left:auto;color:#1776dd;font-size:10px;font-weight:600}.panel-body{padding:10px 12px}
table{border-collapse:collapse;width:100%}.docs th,.docs td{height:32px;border-bottom:1px solid #edf1f4;text-align:left;padding:0 8px;font-size:10.5px;white-space:nowrap}.docs th{background:#f2f7fb;color:#2b4257;font-weight:700}.docs td:first-child{color:#1672d6;font-weight:600}.pdfico{color:#e03131;margin-right:6px}.status{display:inline-flex;align-items:center;padding:4px 7px;border-radius:5px;font-size:9.5px;font-weight:600}.status.ok{background:#dff6ea;color:#16895b}.status.work{background:#fff0d0;color:#b9770b}

.chart-wrap{display:flex;align-items:center;justify-content:center;gap:20px;height:198px}.donut{width:142px;height:142px;border-radius:50%;background:conic-gradient(#2d7ff9 0 62%,#4ca4b5 62% 77%,#8ec4d4 77% 85%,#8d72d5 85% 91%,#b5a8aa 91% 95%,#f06742 95% 98%,#dc5d69 98% 99%,#9caab7 99% 100%);position:relative;flex:0 0 auto}.donut:after{content:"";position:absolute;inset:30px;background:white;border-radius:50%;box-shadow:inset 0 0 0 1px #eef2f5}.donut-center{position:absolute;inset:0;z-index:2;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:18px;font-weight:800}.donut-center small{font-size:10px;font-weight:500;margin-top:1px}.legend{font-size:10px;line-height:1.82}.legend-row{display:flex;align-items:center;gap:7px}.dot{width:9px;height:9px;border-radius:50%;display:inline-block}.b1{background:#2d7ff9}.b2{background:#4ca4b5}.b3{background:#8ec4d4}.b4{background:#8d72d5}.b5{background:#b5a8aa}.b6{background:#f06742}.b7{background:#dc5d69}.b8{background:#9caab7}
.types{padding:8px 13px 11px}.type-row{display:grid;grid-template-columns:105px 1fr 45px;gap:8px;align-items:center;height:27px;font-size:10.5px}.bar{height:13px;background:#e8eef3;border-radius:3px;overflow:hidden}.bar>div{height:100%;border-radius:3px}.num{text-align:right;font-weight:700;color:#18314c}

.mid-grid{display:grid;grid-template-columns:.72fr 1.2fr 1.32fr;gap:9px;margin-bottom:10px;min-height:462px}.tree{padding:7px 10px 10px}.tree-title{font-weight:700;font-size:12px;margin-bottom:6px}.tree-row{height:28px;display:flex;align-items:center;gap:7px;padding:0 7px;font-size:10.5px;border-radius:3px}.tree-row.sel{background:#dcecff;color:#0d4c88;font-weight:700}.tree-row.indent{padding-left:28px}.tree-row.indent2{padding-left:47px}.folder{color:#607b93}.docicon{color:#617d98}.chev{width:11px;color:#48657d}.tree-row.root{height:34px;font-size:12px;font-weight:700;border-bottom:1px solid #edf1f4;margin-bottom:5px}

.filter-row{display:flex;gap:7px;padding:8px 10px;border-bottom:1px solid #edf1f4}.small-btn,.fake-input,.select{height:30px;border:1px solid #cbd8e4;border-radius:4px;background:#fff;display:flex;align-items:center;padding:0 9px;font-size:10px;color:#40586c}.small-btn{width:79px}.fake-input{flex:1;color:#8799aa}.select{width:120px;justify-content:space-between}.blocks th,.blocks td{height:37px;border-bottom:1px solid #e8eef3;padding:0 8px;font-size:10px;text-align:left}.blocks th{background:#f4f8fb;height:28px;color:#526a7f}.blocks tr.selected{background:#dceeff}.type-ico{width:17px;display:inline-block}.warn{color:#d93838}.need{display:inline-flex;background:#fff0d0;color:#b6740a;border-radius:4px;padding:3px 5px;font-size:8.5px;font-weight:700}.okbadge{display:inline-flex;background:#dff6e9;color:#17895b;border-radius:4px;padding:3px 6px;font-size:8.5px}.pagination{display:flex;justify-content:flex-end;gap:4px;padding:11px}.page{width:27px;height:27px;border:1px solid #ccd9e4;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:10px;background:white}.page.active{background:#d9ebff;color:#1e6dc4;border-color:#a9cdef}.shown{float:left;color:#657d91;font-size:9.5px;margin:18px 0 0 10px}

.tabs{height:40px;border-bottom:1px solid #dce6ee;display:flex;align-items:flex-end}.tab{height:39px;padding:0 15px;display:flex;align-items:center;font-size:10.5px;color:#687d91}.tab.active{color:#116bd0;font-weight:700;border-bottom:2px solid #2c80ea;background:#f9fcff}.preview{padding:11px}.preview-title{font-size:13px;font-weight:800;margin-bottom:9px;display:flex;align-items:center}.preview-tools{margin-left:auto;font-size:12px;color:#46647c;letter-spacing:5px}.mini-table th,.mini-table td{border:1px solid #d4dde5;padding:7px 5px;font-size:8.5px;vertical-align:top}.mini-table th{text-align:center;background:#f6f8fa;font-weight:800}.meta-title{font-size:10.5px;font-weight:800;margin:10px 0 7px}.metadata{display:grid;grid-template-columns:1fr 1fr;column-gap:18px}.meta-col{display:grid;grid-template-columns:94px 1fr;row-gap:7px;font-size:8.8px}.meta-key{color:#455c72}.meta-val{color:#324c65}.meta-ok{display:inline-flex;background:#dff5e8;color:#17865a;padding:2px 7px;border-radius:4px}

.bottom{padding:0 10px 12px}.bottom-head{height:39px;display:flex;align-items:center;font-size:13px;font-weight:800}.open-chat{margin-left:auto;background:#2d7fe8;color:white;border-radius:4px;padding:6px 10px;font-size:10px;font-weight:700}.queries{display:grid;grid-template-columns:repeat(6,1fr);gap:7px}.query{height:56px;border:1px solid #d8e3eb;border-radius:4px;background:#fbfdff;padding:9px 11px;font-size:9.7px;color:#567086;display:flex;align-items:flex-start;line-height:1.35}

@media (max-width: 1150px){
 .kpis{grid-template-columns:repeat(3,1fr)}
 .top-grid{grid-template-columns:1fr 1fr}.top-grid .panel:last-child{grid-column:1/-1}
 .mid-grid{grid-template-columns:.8fr 1.2fr}.mid-grid .panel:last-child{grid-column:1/-1}
}
@media (max-width: 850px){
 .sidebar{display:none}.topbar{left:0}.main-area{margin-left:0;min-width:720px}.admin,.demo-badge{display:none}
}
</style>

<div class="portal">
  <aside class="sidebar">
    <div class="brand">
      <div class="logo">⚙</div>
      <div><div class="brand-title">ТехДок База</div><div class="brand-sub">Структурированная техническая документация</div></div>
    </div>
    <div class="nav">
      <div class="nav-item active"><span class="nav-ico">⌂</span><span>Главная</span></div>
      <div class="nav-item"><span class="nav-ico">▤</span><span>Документы</span></div>
      <div class="nav-item"><span class="nav-ico">⌕</span><span>Поиск</span></div>
      <div class="nav-item"><span class="nav-ico">◉</span><span>Компоненты</span></div>
      <div class="nav-item"><span class="nav-ico">⌘</span><span>Техническое<br>обслуживание</span></div>
      <div class="nav-item"><span class="nav-ico">▣</span><span>Требования</span></div>
      <div class="nav-item"><span class="nav-ico">⚠</span><span>Неисправности</span></div>
      <div class="nav-item"><span class="nav-ico">▦</span><span>Таблицы</span></div>
      <div class="nav-item"><span class="nav-ico">▧</span><span>Рисунки</span></div>
      <div class="nav-item"><span class="nav-ico">◴</span><span>Сравнение версий</span></div>
      <div class="nav-item"><span class="nav-ico">⇩</span><span>Экспорт</span></div>
      <div class="nav-item"><span class="nav-ico">⚙</span><span>Настройки</span></div>
    </div>
    <div class="side-bottom">
      <div class="side-title">Использование</div>
      <div class="meter"><div></div></div>
      <div>42.3 ГБ из 100 ГБ</div>
      <div class="side-meta">Документов: 186<br>Обновлено: 12.09.2026 14:32</div>
    </div>
  </aside>

  <header class="topbar">
    <div class="search">Поиск по всей документации... (например: операции ТО компрессора)<span class="glass">⌕</span></div>
    <div class="top-actions">
      <div class="demo-badge">ДЕМО · ДАННЫЕ ВЫМЫШЛЕНЫ</div>
      <div class="chat-btn">▱ &nbsp; Задать вопрос в ChatGPT</div>
      <div class="help">?</div>
      <div class="avatar">АП</div>
      <div class="admin">Администратор &nbsp;⌄</div>
    </div>
  </header>

  <main class="main-area">
    <section class="kpis">
      <div class="card kpi"><div class="kpi-icon blue">▤</div><div><div class="kpi-label">Документов</div><div class="kpi-value">186</div><div class="delta">↑ +12 в этом месяце</div></div></div>
      <div class="card kpi"><div class="kpi-icon gray">▰</div><div><div class="kpi-label">Всего блоков</div><div class="kpi-value">48 320</div><div class="delta">↑ +3 420</div></div></div>
      <div class="card kpi"><div class="kpi-icon green">▦</div><div><div class="kpi-label">Таблиц</div><div class="kpi-value">2 140</div><div class="delta">↑ +217</div></div></div>
      <div class="card kpi"><div class="kpi-icon gray">🔧</div><div><div class="kpi-label">Операций ТО</div><div class="kpi-value">6 870</div><div class="delta">↑ +503</div></div></div>
      <div class="card kpi"><div class="kpi-icon gray">⚙</div><div><div class="kpi-label">Компонентов</div><div class="kpi-value">4 312</div><div class="delta">&nbsp;</div></div></div>
      <div class="card kpi"><div class="kpi-icon red">⚠</div><div><div class="kpi-label">Требуют проверки</div><div class="kpi-value" style="color:#d72f2f">37</div><div class="delta down">↓ -8</div></div></div>
    </section>

    <section class="top-grid">
      <div class="card panel">
        <div class="panel-head">Последние документы <span class="panel-link">Все документы →</span></div>
        <div class="panel-body" style="padding:0 10px 8px">
          <table class="docs"><thead><tr><th>Название</th><th>Тип</th><th>Версия</th><th>Страниц</th><th>Блоков</th><th>Таблиц</th><th>Статус</th><th>Дата</th></tr></thead>
          <tbody>
            <tr><td><span class="pdfico">▣</span>РЭ компрессора</td><td>PDF</td><td>v4</td><td>286</td><td>1 842</td><td>63</td><td><span class="status ok">✓ Обработан</span></td><td>12.09.2026</td></tr>
            <tr><td><span class="pdfico">▣</span>РЭ тормозной системы</td><td>PDF</td><td>v2</td><td>412</td><td>3 117</td><td>128</td><td><span class="status ok">✓ Обработан</span></td><td>10.09.2026</td></tr>
            <tr><td><span class="pdfico">▣</span>РЭ дверей</td><td>PDF</td><td>v3</td><td>158</td><td>974</td><td>18</td><td><span class="status ok">✓ Обработан</span></td><td>08.09.2026</td></tr>
            <tr><td><span class="pdfico">▣</span>РЭ кондиционера</td><td>PDF</td><td>v1</td><td>320</td><td>2 406</td><td>71</td><td><span class="status ok">✓ Обработан</span></td><td>05.09.2026</td></tr>
            <tr><td><span class="pdfico">▣</span>РЭ ходовой части</td><td>PDF</td><td>v2</td><td>502</td><td>4 881</td><td>210</td><td><span class="status work">◌ Обработка</span></td><td>02.09.2026</td></tr>
          </tbody></table>
        </div>
      </div>

      <div class="card panel">
        <div class="panel-head">Распределение блоков</div>
        <div class="chart-wrap">
          <div class="donut"><div class="donut-center">48 320<small>блоков</small></div></div>
          <div class="legend">
            <div class="legend-row"><span class="dot b1"></span>Текстовые блоки&nbsp;&nbsp;62%</div>
            <div class="legend-row"><span class="dot b2"></span>Таблицы&nbsp;&nbsp;15%</div>
            <div class="legend-row"><span class="dot b3"></span>Списки&nbsp;&nbsp;8%</div>
            <div class="legend-row"><span class="dot b4"></span>Заголовки&nbsp;&nbsp;6%</div>
            <div class="legend-row"><span class="dot b5"></span>Рисунки&nbsp;&nbsp;4%</div>
            <div class="legend-row"><span class="dot b6"></span>Примечания&nbsp;&nbsp;3%</div>
            <div class="legend-row"><span class="dot b7"></span>Предупреждения&nbsp;&nbsp;1%</div>
            <div class="legend-row"><span class="dot b8"></span>Другое&nbsp;&nbsp;1%</div>
          </div>
        </div>
      </div>

      <div class="card panel">
        <div class="panel-head">Типы информации</div>
        <div class="types">
          <div class="type-row"><span>Операции ТО</span><div class="bar"><div style="width:84%;background:#2e82df"></div></div><span class="num">6 870</span></div>
          <div class="type-row"><span>Требования</span><div class="bar"><div style="width:62%;background:#49ae79"></div></div><span class="num">4 210</span></div>
          <div class="type-row"><span>Технические хар-ки</span><div class="bar"><div style="width:55%;background:#8a68d4"></div></div><span class="num">3 540</span></div>
          <div class="type-row"><span>Неисправности</span><div class="bar"><div style="width:44%;background:#eb873b"></div></div><span class="num">2 980</span></div>
          <div class="type-row"><span>Компоненты</span><div class="bar"><div style="width:67%;background:#579cec"></div></div><span class="num">4 312</span></div>
          <div class="type-row"><span>Предупреждения</span><div class="bar"><div style="width:25%;background:#d96d6d"></div></div><span class="num">1 240</span></div>
          <div class="type-row"><span>Интервалы</span><div class="bar"><div style="width:54%;background:#66aebf"></div></div><span class="num">3 860</span></div>
          <div class="type-row"><span>Другое</span><div class="bar"><div style="width:77%;background:#8da0b1"></div></div><span class="num">5 320</span></div>
        </div>
      </div>
    </section>

    <section class="mid-grid">
      <div class="card panel">
        <div class="panel-head">Структура документа</div>
        <div class="tree">
          <div class="tree-row root"><span>▣</span><span>РЭ компрессора (v4)</span><span style="margin-left:auto">⌃</span></div>
          <div class="tree-row"><span class="chev">›</span><span class="folder">■</span><span>1. Общие сведения</span></div>
          <div class="tree-row"><span class="chev">›</span><span class="folder">■</span><span>2. Технические характеристики</span></div>
          <div class="tree-row"><span class="chev">›</span><span class="folder">■</span><span>3. Конструкция и принцип работы</span></div>
          <div class="tree-row"><span class="chev">›</span><span class="folder">■</span><span>4. Эксплуатация</span></div>
          <div class="tree-row"><span class="chev">⌄</span><span class="folder">■</span><span>5. Техническое обслуживание</span></div>
          <div class="tree-row indent"><span class="docicon">▧</span><span>5.1 Общие указания</span></div>
          <div class="tree-row indent"><span class="docicon">▧</span><span>5.2 Перечень работ</span></div>
          <div class="tree-row indent sel"><span class="docicon">▣</span><span>5.3 Операции ТО</span></div>
          <div class="tree-row indent"><span class="docicon">▧</span><span>5.4 Расходные материалы</span></div>
          <div class="tree-row indent"><span class="docicon">▧</span><span>5.5 Контроль состояния</span></div>
          <div class="tree-row"><span class="chev">›</span><span class="folder">■</span><span>6. Неисправности и их устранение</span></div>
          <div class="tree-row"><span class="chev">›</span><span class="folder">■</span><span>7. Хранение</span></div>
          <div class="tree-row"><span class="chev">›</span><span class="folder">■</span><span>8. Транспортирование</span></div>
        </div>
      </div>

      <div class="card panel">
        <div class="panel-head">Блоки раздела: 5.3 Операции ТО</div>
        <div class="filter-row"><div class="small-btn">▽&nbsp; Фильтры</div><div class="fake-input">⌕ &nbsp; Поиск в разделе...</div><div class="select">Все типы <span>⌄</span></div></div>
        <table class="blocks"><thead><tr><th>№</th><th>Тип</th><th>Содержание (начало текста)</th><th>Стр.</th><th>Статус</th></tr></thead>
        <tbody>
          <tr><td>101</td><td><span class="type-ico">▧</span>Заголовок</td><td>5.3 Операции ТО</td><td>54</td><td><span class="okbadge">OK</span></td></tr>
          <tr><td>102</td><td><span class="type-ico">▤</span>Текст</td><td>Периодическое техническое обслуж...</td><td>54</td><td><span class="okbadge">OK</span></td></tr>
          <tr class="selected"><td>103</td><td><span class="type-ico">▦</span>Таблица</td><td>Таблица 5-3. Перечень операций ТО</td><td>55</td><td><span class="okbadge">OK</span></td></tr>
          <tr><td>104</td><td><span class="type-ico">▤</span>Текст</td><td>Перед началом выполнения работ...</td><td>56</td><td><span class="okbadge">OK</span></td></tr>
          <tr><td>105</td><td><span class="type-ico">☷</span>Список</td><td>– убедиться в отсутствии давления...</td><td>56</td><td><span class="okbadge">OK</span></td></tr>
          <tr><td>106</td><td><span class="type-ico warn">⚠</span>Предупреждение</td><td>ВНИМАНИЕ! Перед снятием крышки...</td><td>56</td><td><span class="okbadge">OK</span></td></tr>
          <tr><td>107</td><td><span class="type-ico">▤</span>Текст</td><td>Проверить состояние фильтров...</td><td>57</td><td><span class="okbadge">OK</span></td></tr>
          <tr><td>108</td><td><span class="type-ico">▧</span>Рисунок</td><td>Рис. 5-12. Расположение фильтра</td><td>57</td><td><span class="okbadge">OK</span></td></tr>
          <tr><td>109</td><td><span class="type-ico">▤</span>Текст</td><td>Заменить уплотнительные кольца...</td><td>58</td><td><span class="need">NEED_REVIEW</span></td></tr>
          <tr><td>110</td><td><span class="type-ico">▦</span>Таблица</td><td>Нормы расхода материалов</td><td>58</td><td><span class="okbadge">OK</span></td></tr>
        </tbody></table>
        <div class="shown">Показано 10 из 142 блоков</div><div class="pagination"><span class="page">‹</span><span class="page active">1</span><span class="page">2</span><span class="page">3</span><span class="page">4</span><span class="page">5</span><span class="page">…</span><span class="page">15</span><span class="page">›</span></div>
      </div>

      <div class="card panel">
        <div class="tabs"><div class="tab active">Просмотр блока</div><div class="tab">Оригинальная страница</div><div class="tab">Связанные блоки</div></div>
        <div class="preview">
          <div class="preview-title">Таблица 5-3. Перечень операций ТО <span class="preview-tools">▣ ⛶</span></div>
          <table class="mini-table"><thead><tr><th>№<br>п/п</th><th>Наименование<br>операции</th><th>Состав работ</th><th>Интервал</th><th>Примечание</th></tr></thead>
          <tbody>
            <tr><td>1</td><td>Проверка состояния воздушного фильтра</td><td>Осмотр, очистка при необходимости</td><td>IS50</td><td>–</td></tr>
            <tr><td>2</td><td>Замена фильтрующего элемента</td><td>Демонтаж, установка нового элемента</td><td>IS300</td><td>Использовать Р/Н 123-456</td></tr>
            <tr><td>3</td><td>Проверка герметичности соединений</td><td>Визуальный осмотр, устранение утечек</td><td>IS100</td><td>–</td></tr>
            <tr><td>4</td><td>Проверка крепления компрессора</td><td>Контроль момента затяжки</td><td>IS300</td><td>Момент 45 Н·м</td></tr>
            <tr><td>5</td><td>Замена уплотнительных колец</td><td>Демонтаж, замена, контроль герметичности</td><td>IS600</td><td>Комплект Р/Н 789-012</td></tr>
          </tbody></table>
          <div class="meta-title">Метаданные блока</div>
          <div class="metadata">
            <div class="meta-col"><span class="meta-key">ID блока</span><span class="meta-val">DOC_001_B000103</span><span class="meta-key">Тип</span><span class="meta-val">table</span><span class="meta-key">Страница</span><span class="meta-val">55</span><span class="meta-key">Раздел</span><span class="meta-val">5.3</span><span class="meta-key">Предыдущий блок</span><span class="meta-val">DOC_001_B000102</span><span class="meta-key">Следующий блок</span><span class="meta-val">DOC_001_B000104</span></div>
            <div class="meta-col"><span class="meta-key">Статус</span><span class="meta-val"><span class="meta-ok">OK</span></span><span class="meta-key">Координаты</span><span class="meta-val">x: 72, y: 180, w: 468, h: 320</span><span class="meta-key">Источник</span><span class="meta-val">РЭ компрессора v4.pdf</span><span class="meta-key">Порядковый №</span><span class="meta-val">103</span><span class="meta-key">Создан</span><span class="meta-val">12.09.2026 14:32</span><span class="meta-key">Версия парсера</span><span class="meta-val">1.0.3-demo</span></div>
          </div>
        </div>
      </div>
    </section>

    <section class="card bottom">
      <div class="bottom-head">Запросы к базе (пример) <span class="open-chat">▱ &nbsp; Открыть чат с ChatGPT</span></div>
      <div class="queries">
        <div class="query">Покажи все операции ТО для компрессора</div>
        <div class="query">Собери все требования по смазке</div>
        <div class="query">Найди все интервалы, связанные с тормозами</div>
        <div class="query">Сделай Excel по IS300: нормы расхода</div>
        <div class="query">Покажи противоречия между редакциями</div>
        <div class="query">Собери раздел «Техническое обслуживание»</div>
      </div>
    </section>
  </main>
</div>
''',
    unsafe_allow_html=True,
)
