import streamlit as st
from datetime import date

# -----------------------------------------------------------------------------
# 1. KONFIGURACIJA I CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="LegalTech Suite Pro", page_icon="⚖️", layout="wide")

# CSS - Dizajn prilagođen za Word
css_stilovi = """
<style>
    body {
        font-family: 'Times New Roman', serif;
        font-size: 12pt;
        line-height: 1.15;
    }
    .legal-doc { 
        background-color: white; 
        padding: 60px; 
        color: black;
        border: 1px solid #ddd;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .header-doc { 
        text-align: center; 
        font-weight: bold; 
        font-size: 14pt;
        margin-bottom: 20px; 
        text-transform: uppercase;
        font-family: 'Times New Roman', serif;
    }
    
    .party-info {
        text-align: left; 
        margin-bottom: 15px;
        font-family: 'Times New Roman', serif;
    }

    .doc-body {
        text-align: justify;
        text-justify: inter-word;
        margin-bottom: 10px;
        font-family: 'Times New Roman', serif;
    }

    .justified {
        text-align: justify;
        text-justify: inter-word;
    }

    .section-title {
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
        font-family: 'Times New Roman', serif;
        text-transform: uppercase;
        font-size: 11pt;
    }
    
    .cost-table {
        margin-top: 20px;
        border-collapse: collapse;
        width: 100%;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
    }
    .cost-table td {
        border-bottom: 1px solid #ddd;
        padding: 5px;
    }
    
    .clausula {
        font-weight: bold;
        font-style: italic;
        background-color: #f9f9f9;
        padding: 10px;
        border-left: 3px solid #333;
    }
    
    .signature-row {
        display: flex;
        justify-content: space-between;
        margin-top: 50px;
    }
    .signature-block {
        text-align: center;
        width: 45%;
    }
</style>
"""

st.markdown(css_stilovi, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. POMOĆNE FUNKCIJE
# -----------------------------------------------------------------------------

def pripremi_za_word(html_sadrzaj):
    return f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
        <meta charset="utf-8">
        <title>Dokument</title>
        {css_stilovi}
        <xml>
            <w:WordDocument>
                <w:View>Print</w:View>
                <w:Zoom>100</w:Zoom>
                <w:DoNotOptimizeForBrowser/>
            </w:WordDocument>
        </xml>
    </head>
    <body>
        <div class="legal-doc">
            {html_sadrzaj}
        </div>
    </body>
    </html>
    """

def format_text(text):
    if text:
        return text.replace('\n', '<br>')
    return ""

def formatiraj_troskovnik(troskovi):
    if not troskovi: return ""
    stavka = troskovi.get('stavka', 0.0)
    pdv = troskovi.get('pdv', 0.0)
    materijalni = troskovi.get('materijalni', 0.0)
    pristojba = troskovi.get('pristojba', 0.0)
    ukupno = stavka + pdv + materijalni + pristojba
    
    html = f"""
    <div class='section-title' style='margin-top: 30px;'>POPIS TROŠKOVA POSTUPKA:</div>
    <table class='cost-table'>
        <tr><td width="70%">1. Sastav podneska/isprave (Tbr. Tarife):</td><td width="30%" align="right">{stavka:.2f} EUR</td></tr>
    """
    # ISPRAVAK: Zamijenjeni vanjski navodnici u jednostruke da se ne sudaraju s HTML navodnicima
    if pdv > 0: html += f'<tr><td>2. PDV (25%) na stavku 1.:</td><td align="right">{pdv:.2f} EUR</td></tr>'
    if materijalni > 0: html += f'<tr><td>3. Materijalni troškovi / JB Nagrada:</td><td align="right">{materijalni:.2f} EUR</td></tr>'
    if pristojba > 0: html += f'<tr><td>4. Sudska pristojba:</td><td align="right">{pristojba:.2f} EUR</td></tr>'
    html += f'<tr style="font-weight: bold; background-color: #f0f0f0;"><td style="padding: 10px;">UKUPNO:</td><td style="padding: 10px;" align="right">{ukupno:.2f} EUR</td></tr></table>'
    return html

def unos_stranke(oznaka, key_prefix):
    st.markdown(f"**{oznaka}**")
    tip = st.radio(f"Tip ({oznaka})", ["Fizička osoba", "Pravna osoba"], key=f"{key_prefix}_tip", horizontal=True, label_visibility="collapsed")
    col1, col2 = st.columns(2)
    has_valid_data = False
    
    if tip == "Fizička osoba":
        ime = col1.text_input(f"Ime i Prezime", key=f"{key_prefix}_ime")
        oib = col2.text_input(f"OIB", max_chars=11, key=f"{key_prefix}_oib")
        adresa = st.text_input(f"Adresa (Ulica, Grad)", key=f"{key_prefix}_adresa")
        if ime and oib:
            has_valid_data = True
            return f"<b>{ime}</b><br>Adresa: {adresa}<br>OIB: {oib}", "Fizička", has_valid_data
        return "____________________ (ime), OIB: ____________________", "Fizička", has_valid_data
    else: 
        tvrtka = col1.text_input(f"Tvrtka", key=f"{key_prefix}_tvrtka")
        oib = col2.text_input(f"OIB", max_chars=11, key=f"{key_prefix}_oib_pravna")
        mbs = col1.text_input(f"MBS", key=f"{key_prefix}_mbs")
        zastupnik = col2.text_input(f"Zastupan po", key=f"{key_prefix}_zastupnik")
        sjediste = st.text_input(f"Sjedište", key=f"{key_prefix}_sjediste")
        if tvrtka and oib:
            has_valid_data = True
            return f"<b>{tvrtka}</b><br>Sjedište: {sjediste}<br>OIB: {oib}, MBS: {mbs}<br>Zastupana po: {zastupnik}", "Pravna", has_valid_data
        return "____________________ (tvrtka), OIB: ____________________", "Pravna", has_valid_data

def zaglavlje_sastavljaca():
    with st.expander("ℹ️ PODACI O ZASTUPANJU (Punomoćnik)", expanded=False):
        status = st.radio("Dokument sastavlja:", ["Stranka osobno", "Odvjetnik po punomoći"], horizontal=True)
        if status == "Odvjetnik po punomoći":
            odvjetnik = st.text_input("Podaci o odvjetniku/uredu")
            return f"<br>Zastupan po punomoćniku: {odvjetnik}<br>"
        return ""

# -----------------------------------------------------------------------------
# 3. GENERATORI DOKUMENATA (PRO VERZIJE)
# -----------------------------------------------------------------------------

# === NOVI GENERATOR: PRILAGOĐENI UGOVOR ===
def generiraj_prilagodeni_ugovor(naslov, mjesto, datum, rok_vazenja, s1, s2, urbroj, struktura):
    """
    Generira ugovor na temelju dinamičke strukture koju je korisnik složio.
    """
    datum_str = datum.strftime("%d.%m.%Y.")
    rok_str = f"<br>Ugovor vrijedi do: <b>{rok_vazenja.strftime('%d.%m.%Y.')}</b>" if rok_vazenja else "<br>Ugovor se sklapa na neodređeno vrijeme."
    urbroj_str = f"<div style='text-align: right; font-size: 10pt;'>UrBroj: {urbroj}</div><br>" if urbroj else ""

    html = f"""
    {urbroj_str}
    <div class='header-doc'>{naslov.upper()}</div>
    <div class='justified'>
    Sklopljen u mjestu <b>{mjesto}</b>, dana {datum_str} godine.
    <br><br>
    <b>IZMEĐU:</b>
    <br><br>
    1. <b>{s1['uloga']}:</b><br>
    {s1['tekst']}
    <br><br>
    2. <b>{s2['uloga']}:</b><br>
    {s2['tekst']}
    <br><br>
    {rok_str}
    </div>
    <br>
    """
    
    # Dinamičko generiranje članaka
    brojac_clanka = 1
    rimski_brojevi = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

    for i, dio in enumerate(struktura):
        # Naslov dijela (npr. I. OPĆI UVJETI)
        oznaka_dijela = rimski_brojevi[i] if i < len(rimski_brojevi) else f"{i+1}"
        
        # Prikaz naslova dijela (ako postoji)
        if dio['naslov']:
            html += f"<div class='header-doc' style='font-size: 12pt; margin-top: 30px; margin-bottom: 10px;'>{oznaka_dijela}. {dio['naslov'].upper()}</div>"
        
        # Članci unutar dijela
        for tekst_clanka in dio['clanci']:
            if tekst_clanka.strip(): # Samo ako ima teksta
                html += f"""
                <div class='section-title' style='text-align: center;'>Članak {brojac_clanka}.</div>
                <div class='justified'>{format_text(tekst_clanka)}</div>
                """
                brojac_clanka += 1

    # Potpisi
    html += f"""
    <div class='signature-row'>
        <div class='signature-block'>
            <b>{s1['uloga'].upper()}</b>
            <br><br><br>
            ______________________
        </div>
        <div class='signature-block'>
            <b>{s2['uloga'].upper()}</b>
            <br><br><br>
            ______________________
        </div>
    </div>
    """
    return html

# === OSTALI GENERATORI ===
def generiraj_tuzbu_pro(sud, zastupanje, tuzitelj, tuzenik, vps, vrsta, data, troskovi_dict):
    troskovnik_html = formatiraj_troskovnik(troskovi_dict)
    return f"""
    <div style="font-weight: bold; font-size: 14px;">{sud.upper()}</div>
    <div style="font-size: 12px;">{zastupanje}</div>
    <br>
    <div class='justified'>
    <b>TUŽITELJ:</b> {tuzitelj}<br>
    <b>TUŽENIK:</b> {tuzenik}
    <br><br>
    <b>Radi:</b> {vrsta}<br>
    <b>Vrijednost predmeta spora (VPS): {vps:,.2f} EUR</b>
    </div>
    <br>
    <div class='header-doc'>TUŽBA</div>
    <div class='section-title'>I. ČINJENIČNI NAVODI</div>
    <div class='justified'>{format_text(data['cinjenice'])}</div>
    <div class='section-title'>II. DOKAZI</div>
    <div class='justified'>Predlaže se izvođenje sljedećih dokaza:<br>{format_text(data['dokazi'])}</div>
    <div class='section-title'>III. TUŽBENI ZAHTJEV</div>
    <div class='justified'>Slijedom navedenog, budući da Tuženik nije podmirio svoju dospjelu obvezu, Tužitelj predlaže da naslovni Sud donese sljedeću<br><br>
    <div style="text-align: center; font-weight: bold;">PRESUDU</div><br>
    <b>I. Nalaže se Tuženiku</b> da Tužitelju isplati iznos od <b>{vps:,.2f} EUR</b> zajedno sa zakonskom zateznom kamatom koja teče od dana dospijeća {data['datum_dospijeca']} pa do isplate, po stopi određenoj zakonom.<br><br>
    <b>II. Nalaže se Tuženiku</b> da Tužitelju naknadi troškove ovog parničnog postupka, u roku od 15 dana, zajedno sa zateznom kamatom od dana donošenja presude do isplate.
    </div>
    {troskovnik_html}
    <br><br>
    <div class='signature-row'><div style='display:inline-block; width: 50%;'><b>PRILOZI:</b><br>1. Punomoć<br>2. Dokaz o uplati pristojbe<br>3. Dokazi navedeni u točki II.</div> 
    <div class='signature-block'><b>TUŽITELJ</b><br>(po punomoćniku)<br><br>______________________</div></div>
    """

def generiraj_ovrhu_pro(jb, ovrhovoditelj, ovrsenik, trazbina, isprava, troskovi_dict):
    troskovnik_html = formatiraj_troskovnik(troskovi_dict)
    ukupno_trosak = troskovi_dict.get('stavka', 0) + troskovi_dict.get('pdv', 0) + troskovi_dict.get('materijalni', 0) + troskovi_dict.get('pristojba', 0)
    return f"""
    <div style="font-weight: bold;">JAVNOM BILJEŽNIKU {jb.upper()}</div>
    <br>
    <div class='justified'><b>OVRHOVODITELJ:</b> {ovrhovoditelj}<br><b>OVRŠENIK:</b> {ovrsenik}<br><br><b>Radi:</b> Ovrhe na temelju vjerodostojne isprave<br><b>Vrijednost tražbine: {trazbina['glavnica']:,.2f} EUR</b></div>
    <br><div class='header-doc'>PRIJEDLOG ZA OVRHU<br><span style='font-size:11pt; font-weight:normal'>na temelju vjerodostojne isprave</span></div>
    <div class='justified'>Na temelju vjerodostojne isprave – <b>{isprava}</b> od dana {trazbina['datum_racuna']}, iz koje proizlazi dospjela tražbina Ovrhovoditelja prema Ovršeniku, Ovrhovoditelj predlaže da Javni bilježnik donese sljedeće:</div>
    <div style='border: 2px solid black; padding: 15px; margin: 20px 0;'><div class='header-doc' style='margin:0;'>RJEŠENJE O OVRSI</div><div style='text-align:center; font-size:10pt;'>(na temelju vjerodostojne isprave)</div><br>
    <div class='justified'><b>I. NALAŽE SE Ovršeniku</b> da Ovrhovoditelju u roku od osam dana od dana dostave ovog rješenja namiri tražbinu u iznosu od <b>{trazbina['glavnica']:,.2f} EUR</b>, zajedno sa zakonskim zateznim kamatama koje teku od dana dospijeća <b>{trazbina['dospjece']}</b> pa do isplate, kao i da mu naknadi troškove ovog postupka u iznosu od <b>{ukupno_trosak:.2f} EUR</b>.<br><br>
    <b>II. ODREĐUJE SE OVRHA</b> radi naplate tražbine iz točke I. ovog rješenja i troškova postupka. Ovrha će se provesti na novčanim sredstvima Ovršenika po svim računima kod banaka, te na cjelokupnoj imovini Ovršenika.</div></div>
    {troskovnik_html}
    <br><br><div class='signature-row'><div style='display:inline-block; width: 50%;'></div><div class='signature-block'><b>OVRHOVODITELJ</b><br><br><br>______________________</div></div>
    """

def generiraj_zalbu_pro(sud_prvi, sud_drugi, stranke, podaci_o_presudi, razlozi, tekst_obrazlozenja, troskovnik):
    troskovnik_html = formatiraj_troskovnik(troskovnik)
    danas = date.today().strftime("%d.%m.%Y.")
    razlozi_html = "<ul>" + "".join([f"<li>{r}</li>" for r in razlozi]) + "</ul>"
    return f"""
    <div style="font-weight: bold; font-size: 14px;">{sud_drugi.upper()}</div><div>(kao drugostupanjskom sudu)</div><br><div>putem</div><br><div style="font-weight: bold;">{sud_prvi.upper()}</div><div>(kao prvostupanjskog suda)</div><br><br>
    <div class='justified'><b>PRAVNA STVAR:</b><br><b>TUŽITELJ:</b> {stranke['tuzitelj']}<br><b>TUŽENIK:</b> {stranke['tuzenik']}<br><b>Poslovni broj: {podaci_o_presudi['broj']}</b></div><br>
    <div class='header-doc'>ŽALBA</div><div style="text-align: center;">protiv presude {sud_prvi} poslovni broj {podaci_o_presudi['broj']} od dana {podaci_o_presudi['datum']}</div><br>
    <div class='justified'>Žalitelj ovime pravovremeno, u otvorenom zakonskom roku, podnosi žalbu protiv navedene presude {podaci_o_presudi['opseg']} zbog sljedećih zakonskih razloga (čl. 353. ZPP):</div>
    {razlozi_html}
    <div class='section-title'>I. OBRAZLOŽENJE</div><div class='justified'>{format_text(tekst_obrazlozenja)}</div>
    <div class='section-title'>II. PRIJEDLOG</div><div class='justified'>Slijedom navedenog, predlaže se da naslovni drugostupanjski sud ovu žalbu uvaži, pobijanu presudu ukine i predmet vrati prvostupanjskom sudu na ponovno suđenje.</div>
    {troskovnik_html}
    <br><br><div style="text-align: right;">U {podaci_o_presudi['mjesto']}, dana {danas}</div>
    <table width="100%"><tr><td width="50%"></td><td width="50%" align="center"><b>ŽALITELJ</b><br>(po punomoćniku)<br><br>______________________</td></tr></table>
    """

def generiraj_ugovor_standard(tip_ugovora, stranka1, stranka2, podaci, opcije, troskovi_dict=None):
    datum = date.today().strftime("%d.%m.%Y.")
    dodatni_tekst = f"<br><b>Kapara:</b> Ugovorne strane potvrđuju da je Kupac isplatio kaparu u iznosu od {opcije['iznos_kapare']} EUR." if opcije.get('kapara') else ""
    solemnizacija_clanak = """<div class='section-title'>Članak (Solemnizacija)</div><div class='doc-body'>Ugovorne strane suglasne su da se ovaj Ugovor solemnizira (potvrdi) kod Javnog bilježnika.</div>""" if opcije.get('solemnizacija') else ""
    titles = {"Kupoprodaja": ("UGOVOR O KUPOPRODAJI", "PRODAVATELJ", "KUPAC"), "Najam/Zakup": ("UGOVOR O NAJMU", "NAJMODAVAC", "NAJMOPRIMAC"), "Ugovor o djelu (Usluga)": ("UGOVOR O DJELU", "NARUČITELJ", "IZVOĐAČ"), "Zajam": ("UGOVOR O ZAJMU", "ZAJMODAVAC", "ZAJMOPRIMAC")}
    naslov, u1, u2 = titles[tip_ugovora]
    trosak_prikaz = formatiraj_troskovnik(troskovi_dict) if troskovi_dict else ""
    return f"""<div class='header-doc'>{naslov}</div><div class='doc-body'>Sklopljen u {podaci['mjesto']}, dana {datum}, između:</div><div class='party-info'>1. <b>{u1}:</b><br>{stranka1}<br><br>2. <b>{u2}:</b><br>{stranka2}</div><div class='section-title'>Članak 1.</div><div class='doc-body'>{format_text(podaci['predmet_clanak'])}</div><div class='section-title'>Članak 2.</div><div class='doc-body'>{format_text(podaci['cijena_clanak'])}{dodatni_tekst}</div><div class='section-title'>Članak 3.</div><div class='doc-body'>{format_text(podaci['rok_clanak'])}</div>{solemnizacija_clanak}<br><br>{trosak_prikaz}<br><table width="100%"><tr><td width="50%" align="center"><b>{u1}</b><br><br>__________</td><td width="50%" align="center"><b>{u2}</b><br><br>__________</td></tr></table>"""

def generiraj_ugovor_o_radu(poslodavac, radnik, podaci):
    datum = date.today().strftime("%d.%m.%Y.")
    vrsta_tekst = "NA NEODREĐENO VRIJEME"
    clanak_trajanje = "Ugovor se sklapa na neodređeno vrijeme."
    if podaci.get('vrsta') == "Određeno":
        vrsta_tekst = "NA ODREĐENO VRIJEME"
        clanak_trajanje = f"Ugovor se sklapa na određeno vrijeme do {podaci.get('datum_do', '_______')}, zbog: {podaci.get('razlog_odredeno', 'povećanog opsega posla')}."
    probni_rad_txt = f"Ugovara se probni rad u trajanju od {podaci.get('probni_rad_mj', 3)} mjeseca/mjeseci." if podaci.get('probni_rad') else ""
    return f"""
    <div class='header-doc'>UGOVOR O RADU<br><span style='font-size: 12pt; font-weight: normal;'>{vrsta_tekst}</span></div>
    <div class='justified'>Sklopljen u {podaci.get('mjesto_sklapanja', 'Zagrebu')}, dana {datum} godine, između:<br><br>1. <b>POSLODAVAC:</b><br>{poslodavac}<br><br>2. <b>RADNIK:</b><br>{radnik}</div>
    <div class='section-title'>Članak 1. (Predmet i početak rada)</div><div class='justified'>Radnik počinje s radom dana <b>{podaci.get('datum_start', '_______')}</b>. {clanak_trajanje} {probni_rad_txt}</div>
    <div class='section-title'>Članak 2. (Mjesto i opis poslova)</div><div class='justified'>Radnik će obavljati poslove na radnom mjestu: <b>{podaci.get('naziv_radnog_mjesta', '_______')}</b>.<br><b>Opis poslova:</b> {podaci.get('opis_posla', 'Opisani u opisu radnog mjesta kod Poslodavca')}.<br>Mjesto rada je: {podaci.get('mjesto_rada', 'u sjedištu Poslodavca i na terenu po potrebi')}.</div>
    <div class='section-title'>Članak 3. (Radno vrijeme i odmori)</div><div class='justified'>Radnik će raditi u punom radnom vremenu od {podaci.get('radno_vrijeme', 40)} sati tjedno. Radnik ima pravo na dnevni odmor (stanku) u trajanju od 30 minuta.</div>
    <div class='section-title'>Članak 4. (Plaća i naknade)</div><div class='justified'>Za obavljeni rad Poslodavac će Radniku isplaćivati osnovnu bruto plaću u iznosu od <b>{podaci.get('bruto_placa', 0):.2f} EUR</b> mjesečno.</div>
    <div class='section-title'>Članak 5. (Godišnji odmor)</div><div class='justified'>Radnik ima pravo na plaćeni godišnji odmor u trajanju od najmanje {podaci.get('godisnji_odmor', 20)} radnih dana.</div>
    <div class='section-title'>Članak 6. (Završne odredbe)</div><div class='justified'>Ovaj Ugovor sastavljen je u 3 (tri) istovjetna primjerka.</div>
    <div class='signature-row'><div class='signature-block'><b>ZA POSLODAVCA</b><br><br><br>______________________</div><div class='signature-block'><b>RADNIK</b><br><br><br>______________________</div></div>
    """

def generiraj_otkaz(poslodavac, radnik, podaci):
    return f"""<div class='header-doc'>ODLUKA O OTKAZU</div><div class='doc-body'>1. Otkazuje se ugovor radniku {radnik}.</div><div class='section-title'>Obrazloženje</div><div class='doc-body'>{podaci['tekst_obrazlozenja']}</div><br><br><table width="100%"><tr><td align="center"><b>POSLODAVAC</b><br>__________</td></tr></table>"""

def generiraj_tabularnu_doc(prod, kup, ko, cest, ul, opis, dat):
    return f"""<div class='header-doc'>TABULARNA IZJAVA<br><span style='font-size: 11pt; font-weight: normal;'>(Clausula Intabulandi)</span></div><div class='party-info'><b>PRODAVATELJ:</b><br>{prod}</div><div class='party-info'><b>KUPAC:</b><br>{kup}</div><div class='doc-body'>Temeljem Ugovora od {dat} za nekretninu u K.O. {ko}, k.č.br {cest}. {f'<br>Opis u naravi: {opis}' if opis else ''}</div><div class='doc-body clausula'>Ja, PRODAVATELJ, ovime izričito ovlašćujem KUPCA da zatraži uknjižbu prava vlasništva.</div><br><br><table width="100%"><tr><td width="40%"></td><td width="60%" align="center"><b>PRODAVATELJ</b><br>(Ovjera JB)<br><br>_________________</td></tr></table>"""

def generiraj_zk_prijedlog(sud, predlagatelj, protustranka, nekretnina, dokumenti, troskovi_dict):
    troskovnik_html = formatiraj_troskovnik(troskovi_dict)
    return f"""<div style="font-weight: bold; font-size: 14px;">{sud.upper()}</div><div style="font-size: 12px;">Zemljišnoknjižni odjel</div><br><br><div class='party-info'><b>PREDLAGATELJ:</b><br>{predlagatelj}</div><div class='party-info'><b>PROTUSTRANKA:</b><br>{protustranka}</div><br><div class='header-doc'>ZEMLJIŠNOKNJIŽNI PRIJEDLOG<br><span style='font-size: 12pt; font-weight: normal;'>za uknjižbu prava vlasništva</span></div><div class='doc-body'>Predlagatelj predlaže da naslovni sud, na temelju priloženih isprava, u zemljišnim knjigama za nekretninu upisanu kao:<br><br><b>Katastarska općina (k.o.):</b> {nekretnina['ko']}<br><b>Broj zk. uloška:</b> {nekretnina['ulozak']}<br><b>Broj čestice (k.č.br.):</b> {nekretnina['cestica']}{f", u naravi {nekretnina['opis']}" if nekretnina['opis'] else ""}<br><br>provede upis, odnosno dozvoli:</div><div class='section-title' style='text-align: center; border: 1px solid black; padding: 10px; margin: 20px 0;'>UKNJIŽBU PRAVA VLASNIŠTVA<br>u korist Predlagatelja (u cijelosti / 1/1 dijela).</div><div class='doc-body'>Predlagatelj prilaže izvornike/ovjerene preslike isprava koje su temelj za upis.</div><div class='section-title'>POPIS PRILOGA:</div><div class='doc-body'><ol><li>{dokumenti['ugovor']}</li><li>{dokumenti['tabularna']}</li><li>Dokaz o uplati sudske pristojbe</li><li>Dokaz o državljanstvu / OIB (preslika osobne iskaznice)</li></ol></div>{troskovnik_html}<br><br><table width="100%" border="0"><tr><td width="50%"></td><td width="50%" align="center"><b>PREDLAGATELJ</b><br>(potpis nije nužno ovjeravati)<br><br>______________________</td></tr></table>"""

def generiraj_brisovnu_tuzbu(sud, zastupanje, tuzitelj, tuzenik, nekretnina, podaci_spora, troskovi_dict):
    datum = date.today().strftime("%d.%m.%Y.")
    troskovnik_html = formatiraj_troskovnik(troskovi_dict)
    tekst_savjesnost = "Tuženik je prilikom stjecanja bio nesavjestan..." if podaci_spora['tuzenik_znao'] else "Tužba se podnosi u zakonskom roku..."
    return f"""<div style="font-weight: bold; font-size: 14px; text-align: left;">{sud.upper()}</div><div style="font-size: 12px; text-align: left;">{zastupanje}</div><br><div class='party-info'><b>PRAVNA STVAR:</b><br><b>TUŽITELJ:</b> {tuzitelj}<br><b>TUŽENIK:</b> {tuzenik}</div><div class='party-info'><b>Radi:</b> Brisanja uknjižbe i uspostave prijašnjeg ZK stanja<br><b>Vrijednost predmeta spora (VPS): {podaci_spora['vps']:,.2f} EUR</b></div><br><div class='header-doc'>BRISOVNA TUŽBA</div><div class='section-title'>I. ČINJENIČNI NAVODI</div><div class='doc-body'>Tužitelj je bio isključivi vlasnik nekretnine upisane u <b>zk.ul. {nekretnina['ulozak']}, k.o. {nekretnina['ko']}, k.č.br. {nekretnina['cestica']}</b>.<br><br>Dana {podaci_spora['datum_uknjizbe']}, u zemljišnim knjigama naslovnog suda, pod brojem <b>{podaci_spora['z_broj']}</b>, provedena je nevaljana uknjižba prava vlasništva u korist Tuženika na temelju isprave: {podaci_spora['isprava']}.<br><br>Tužitelj tvrdi da je navedena isprava ništetna iz sljedećih razloga:<br><i>{podaci_spora['razlog_nevaljanosti']}</i><br><br>{tekst_savjesnost}</div><div class='section-title'>DOKAZI:</div><div class='doc-body'>1. ZK izvadak.<br>2. Uvid u ZK spis broj {podaci_spora['z_broj']}.<br>3. {podaci_spora['isprava']}.</div><div class='section-title'>II. TUŽBENI ZAHTJEV</div><div class='doc-body'>Slijedom navedenog, Tužitelj predlaže da Sud donese sljedeću</div><div style="text-align: center; font-weight: bold; margin: 10px 0;">PRESUDU</div><div class='doc-body'><b>I. Utvrđuje se da je ništetan</b> {podaci_spora['isprava']}.<br><br><b>II. Utvrđuje se da je nevaljana uknjižba</b> prava vlasništva u korist tuženika, provedena pod brojem {podaci_spora['z_broj']}.<br><br><b>III. Nalaže se brisanje uknjižbe</b> i uspostava prijašnjeg stanja.<br><br><b>IV.</b> Nalaže se Tuženiku naknaditi trošak.</div>{troskovnik_html}<br><br><div style="text-align:right;">U {podaci_spora['mjesto']}, dana {datum}</div><table width="100%" border="0"><tr><td width="50%"></td><td width="50%" align="center"><b>TUŽITELJ</b><br><br><br>______________________</td></tr></table>"""

# -----------------------------------------------------------------------------
# 4. GLAVNA APLIKACIJA (GUI)
# -----------------------------------------------------------------------------

st.sidebar.title("NAVIGACIJA")
modul = st.sidebar.radio(
    "ODABERI USLUGU:",
    ["📝 Ugovori i Odluke", "⚖️ Tužbe", "🔨 Ovršni Prijedlog", "📜 Žalbe", "🏠 Zemljišne knjige", "🧮 Kamate"]
)

# --- 1. UGOVORI ---
if "Ugovori" in modul:
    st.header("Sastavljanje Ugovora i Odluka")
    
    # Prilagođena navigacija za Ugovore (NOVA OPCIJA PRVA)
    kategorija = st.radio("Kategorija prava:", ["Slobodna forma (Personalizirani ugovor)", "Građansko pravo (Predlošci)", "Radno pravo"], horizontal=True)
    
    # =================================================================
    # A) SLOBODNA FORMA - NOVI MODUL
    # =================================================================
    if kategorija == "Slobodna forma (Personalizirani ugovor)":
        st.subheader("Izrada Ugovora po mjeri")
        st.info("Ovaj modul omogućuje potpunu slobodu kreiranja članaka i poglavlja.")

        # Inicijalizacija stanja za dinamička polja
        if 'custom_contract' not in st.session_state:
            st.session_state.custom_contract = [
                {'naslov': 'Opći uvjeti', 'clanci': ['']} # Početno stanje
            ]

        # 1. ZAGLAVLJE
        with st.expander("1. Zaglavlje ugovora", expanded=True):
            col_naslov, col_urbroj = st.columns([2, 1])
            naslov_ugovora = col_naslov.text_input("Naslov Ugovora", "UGOVOR O POSLOVNOJ SURADNJI")
            urbroj = col_urbroj.text_input("UrBroj (Opcionalno)", placeholder="npr. 2024-01-01")
            
            c1, c2, c3 = st.columns(3)
            mjesto = c1.text_input("Mjesto sklapanja", "Zagreb")
            datum = c2.date_input("Datum sklapanja")
            rok_vazenja = c3.date_input("Vrijedi do (Opcionalno)", value=None)

        # 2. STRANKE (S ULOGAMA)
        with st.expander("2. Stranke", expanded=True):
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                st.markdown("### Prva strana")
                uloga1 = st.text_input("Uloga (npr. Naručitelj)", "Naručitelj")
                s1_tekst, _, _ = unos_stranke("Podaci prve strane", "cust_s1")
            
            with col_s2:
                st.markdown("### Druga strana")
                uloga2 = st.text_input("Uloga (npr. Izvođač)", "Izvođač")
                s2_tekst, _, _ = unos_stranke("Podaci druge strane", "cust_s2")

        # 3. DINAMIČKI SADRŽAJ (SRCE APLIKACIJE)
        st.markdown("---")
        st.subheader("3. Sadržaj Ugovora")
        
        # Iteracija kroz poglavlja (Rimski brojevi)
        for i, poglavlje in enumerate(st.session_state.custom_contract):
            oznaka = ["I", "II", "III", "IV", "V", "VI", "VII"][i] if i < 7 else f"{i+1}"
            st.markdown(f"#### Dio {i+1} (Rimski {oznaka})")
            
            # Naslov poglavlja i gumb za brisanje
            col_pog_naslov, col_pog_btn = st.columns([4, 1])
            novi_naslov = col_pog_naslov.text_input(f"Naslov dijela {i+1}", value=poglavlje['naslov'], key=f"naslov_{i}")
            poglavlje['naslov'] = novi_naslov # Ažuriranje
            
            if col_pog_btn.button("🗑️ Obriši dio", key=f"del_sec_{i}"):
                st.session_state.custom_contract.pop(i)
                st.rerun()

            # Iteracija kroz članke unutar poglavlja
            for j, clanak in enumerate(poglavlje['clanci']):
                cl_text = st.text_area(f"Članak (Dio {i+1})", value=clanak, height=100, key=f"cl_{i}_{j}", placeholder="Unesite tekst članka...")
                st.session_state.custom_contract[i]['clanci'][j] = cl_text # Ažuriranje
            
            # Gumb za dodavanje članka
            c_add, _ = st.columns([2, 4])
            if c_add.button(f"➕ Dodaj Članak u Dio {i+1}", key=f"add_art_{i}"):
                st.session_state.custom_contract[i]['clanci'].append("")
                st.rerun()
            
            st.divider()

        # Gumb za dodavanje novog dijela
        if st.button("➕ DODAJ NOVI DIO UGOVORA (npr. Naknada, Rokovi...)"):
            st.session_state.custom_contract.append({'naslov': '', 'clanci': ['']})
            st.rerun()

        # GENERIRANJE
        st.markdown("---")
        if st.button("Generiraj Personalizirani Ugovor", type="primary"):
            s1_data = {'uloga': uloga1, 'tekst': s1_tekst}
            s2_data = {'uloga': uloga2, 'tekst': s2_tekst}
            
            doc = generiraj_prilagodeni_ugovor(naslov_ugovora, mjesto, datum, rok_vazenja, s1_data, s2_data, urbroj, st.session_state.custom_contract)
            
            st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
            word = pripremi_za_word(doc)
            st.download_button("💾 Preuzmi Word (.doc)", word, "Moj_Ugovor.doc")

    # =================================================================
    # B) STANDARDNI UGOVORI (STARI KOD)
    # =================================================================
    elif kategorija == "Građansko pravo (Predlošci)":
        st.subheader("Građansko pravo")
        tip = st.selectbox("Odaberite vrstu ugovora:", ["Kupoprodaja", "Najam/Zakup", "Ugovor o djelu (Usluga)", "Zajam"])
        
        c1, c2 = st.columns(2)
        s1, _, _ = unos_stranke("PRVA STRANA", "u1")
        s2, _, _ = unos_stranke("DRUGA STRANA", "u2")
        opcije = {'kapara': st.checkbox("Kapara?"), 'solemnizacija': st.checkbox("Solemnizacija?")}
        if opcije['kapara']: opcije['iznos_kapare'] = st.number_input("Iznos kapare")
        
        data = {'mjesto': "Zagreb"}
        if tip == "Kupoprodaja":
            data['predmet_clanak'] = st.text_area("Predmet Ugovora", placeholder="Opišite predmet (npr. Vozilo marke BMW, šasija...)")
            data['cijena_clanak'] = f"Cijena: {st.number_input('Cijena')} EUR."
            data['rok_clanak'] = "Odmah po isplati cijene."
        elif tip == "Najam/Zakup":
            data['predmet_clanak'] = st.text_input("Prostor (Adresa i opis)")
            data['cijena_clanak'] = f"Mjesečna najamnina/zakupnina: {st.number_input('Mjesečni iznos')} EUR."
            data['rok_clanak'] = "Trajanje ugovora: 1 godina (ili upišite drugo)."
        elif tip == "Ugovor o djelu (Usluga)":
            data['predmet_clanak'] = st.text_area("Opis posla/usluge")
            data['cijena_clanak'] = f"Honorar (neto/bruto): {st.number_input('Iznos honorara')} EUR."
            data['rok_clanak'] = "Rok izvršenja posla: 30 dana."
        elif tip == "Zajam":
            data['predmet_clanak'] = "Predmet ugovora je novčani zajam."
            data['cijena_clanak'] = f"Glavnica zajma: {st.number_input('Iznos zajma')} EUR."
            data['rok_clanak'] = f"Rok povrata: {st.date_input('Datum povrata').strftime('%d.%m.%Y.')}"

        st.markdown("---")
        add_trosak = st.checkbox("Dodaj troškovnik sastava ugovora (za odvjetnike)")
        troskovi = None
        if add_trosak:
            col_t1, col_t2 = st.columns(2)
            sastav = col_t1.number_input("Cijena sastava", 0.0)
            pdv_ug = col_t1.checkbox("PDV?", value=True)
            pdv_iznos = sastav * 0.25 if pdv_ug else 0
            troskovi = {'stavka': sastav, 'pdv': pdv_iznos}

        if st.button("Generiraj Ugovor"):
            doc = generiraj_ugovor_standard(tip, s1, s2, data, opcije, troskovi)
            st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
            word = pripremi_za_word(doc)
            st.download_button("Preuzmi", word, f"{tip}.doc")

    elif kategorija == "Radno pravo":
        st.subheader("Radno pravo")
        tip = st.selectbox("Odaberite dokument:", ["Ugovor o radu", "Odluka o otkazu"])
        
        if tip == "Ugovor o radu":
            c1, c2 = st.columns(2)
            p, _, _ = unos_stranke("POSLODAVAC", "p")
            r, _, _ = unos_stranke("RADNIK", "r")
            
            col_d1, col_d2 = st.columns(2)
            datum_start = col_d1.date_input("Početak rada")
            mjesto_sklapanja = col_d2.text_input("Mjesto sklapanja", "Zagreb")
            
            podaci = {'vrsta': st.radio("Vrsta", ["Neodređeno", "Određeno"]), 'datum_do': None, 'razlog_odredeno': "", 'probni_rad': False}
            if podaci['vrsta'] == "Određeno": 
                d_do = st.date_input("Do (Datum)")
                podaci['datum_do'] = d_do.strftime('%d.%m.%Y.')
                podaci['razlog_odredeno'] = st.text_input("Razlog za određeno (npr. zamjena)")
            
            c_prob, c_go = st.columns(2)
            podaci['probni_rad'] = c_prob.checkbox("Probni rad")
            if podaci['probni_rad']: podaci['probni_rad_mj'] = c_prob.number_input("Trajanje (mjeseci)", 1, 6, 3)
            podaci['godisnji_odmor'] = c_go.number_input("Godišnji odmor (dana)", value=24)
            podaci['naziv_radnog_mjesta'] = st.text_input("Radno mjesto")
            podaci['opis_posla'] = st.text_area("Opis poslova (kratko)")
            podaci['mjesto_rada'] = st.text_input("Mjesto rada", "sjedište Poslodavca")
            c_sat, c_pla = st.columns(2)
            podaci['radno_vrijeme'] = c_sat.number_input("Tjedno radno vrijeme (sati)", value=40)
            podaci['bruto_placa'] = c_pla.number_input("Bruto plaća (EUR)")
            podaci['datum_start'] = datum_start.strftime('%d.%m.%Y.')
            podaci['mjesto_sklapanja'] = mjesto_sklapanja
            
            if st.button("Generiraj Ugovor o radu"):
                doc = generiraj_ugovor_o_radu(p, r, podaci)
                st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
                word = pripremi_za_word(doc)
                st.download_button("Preuzmi", word, "Ugovor_o_radu.doc")

        elif tip == "Odluka o otkazu":
            vrsta = st.selectbox("Vrsta otkaza", ["Poslovno uvjetovani", "Osobno uvjetovani", "Skrivljeno ponašanje", "Izvanredni otkaz"])
            c1, c2 = st.columns(2)
            p, _, _ = unos_stranke("POSLODAVAC", "po")
            r, _, _ = unos_stranke("RADNIK", "ro")
            podaci = {'vrsta_otkaza': vrsta, 'mjesto': "Zagreb", 'tekst_obrazlozenja': st.text_area("Obrazloženje otkaza (Obavezno detaljno)"), 'otkazni_rok': st.text_input("Otkazni rok")}
            if st.button("Generiraj Otkaz"):
                doc = generiraj_otkaz(p, r, podaci)
                st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
                word = pripremi_za_word(doc)
                st.download_button("Preuzmi", word, "Otkaz.doc")

# --- 2. TUŽBE ---
elif "Tužbe" in modul:
    st.header("Tužba (Parnični postupak)")
    st.info("Ispunite detalje za generiranje potpune tužbe s troškovnikom i petitumom.")
    zastupanje = zaglavlje_sastavljaca()
    col1, col2 = st.columns(2)
    with col1: t1, _, _ = unos_stranke("TUŽITELJ", "t1")
    with col2: t2, _, _ = unos_stranke("TUŽENIK", "t2")
    st.subheader("1. Predmet spora")
    sud = st.text_input("Naslovni sud", "OPĆINSKI GRAĐANSKI SUD U ZAGREBU")
    vps = st.number_input("Vrijednost spora (Glavnica duga)", min_value=0.0)
    datum_dospijeca = st.date_input("Datum dospijeća (Od kada teku kamate?)")
    vrsta = st.text_input("Radi (kratki opis)", "Isplate (Dugovanja)")
    st.subheader("2. Sadržaj (Obrazloženje)")
    cinjenice = st.text_area("I. Činjenice (Kronologija)", height=150, placeholder="Opišite nastanak duga...")
    dokazi = st.text_area("II. Dokazi", placeholder="- Ugovor o kupoprodaji\n- Račun broj 10/2023...")
    st.subheader("3. Troškovnik")
    col_tr1, col_tr2, col_tr3 = st.columns(3)
    trosak_sastav = col_tr1.number_input("Sastav tužbe (EUR)", 0.0)
    trosak_pdv = trosak_sastav * 0.25 if col_tr2.checkbox("Dodaj PDV (25%)", value=True) else 0.0
    trosak_pristojba = col_tr3.number_input("Sudska pristojba (EUR)", 0.0)
    if st.button("Generiraj Tužbu"):
        doc = generiraj_tuzbu_pro(sud, zastupanje, t1, t2, vps, vrsta, {'cinjenice': cinjenice, 'dokazi': dokazi, 'datum_dospijeca': datum_dospijeca.strftime('%d.%m.%Y.')}, {'stavka': trosak_sastav, 'pdv': trosak_pdv, 'pristojba': trosak_pristojba})
        st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
        word = pripremi_za_word(doc)
        st.download_button("Preuzmi Word", word, "Tuzba.doc")

# --- 3. OVRHE ---
elif "Ovršni" in modul:
    st.header("Prijedlog za Ovrhu (Vjerodostojna isprava)")
    jb = st.text_input("Javni bilježnik (Ime, Prezime, Grad)", placeholder="Ivan Horvat, Zagreb")
    col1, col2 = st.columns(2)
    with col1: o1, _, _ = unos_stranke("OVRHOVODITELJ (Vjerovnik)", "o1")
    with col2: o2, _, _ = unos_stranke("OVRŠENIK (Dužnik)", "o2")
    st.subheader("1. Dugovanje")
    c1, c2, c3 = st.columns(3)
    opis_isprave = c1.text_input("Vjerodostojna isprava", placeholder="Račun br. 100-2024")
    dat_racuna = c2.date_input("Datum izdavanja računa")
    glavnica = c3.number_input("Glavnica duga (EUR)", min_value=0.0)
    dospjece = st.date_input("Datum dospijeća")
    st.subheader("2. Troškovnik")
    ct1, ct2, ct3 = st.columns(3)
    trosak_odvjetnik = ct1.number_input("Odvjetnik", 0.0)
    trosak_jb_nagrada = ct2.number_input("JB Nagrada", 0.0)
    trosak_pdv = (trosak_odvjetnik + trosak_jb_nagrada) * 0.25 if ct3.checkbox("Obračunaj PDV?") else 0.0
    if st.button("Generiraj Ovršni Prijedlog"):
        doc = generiraj_ovrhu_pro(jb, o1, o2, {'glavnica': glavnica, 'datum_racuna': dat_racuna.strftime('%d.%m.%Y.'), 'dospjece': dospjece.strftime('%d.%m.%Y.')}, opis_isprave, {'stavka': trosak_odvjetnik, 'materijalni': trosak_jb_nagrada, 'pdv': trosak_pdv, 'pristojba': 0})
        st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
        word = pripremi_za_word(doc)
        st.download_button("Preuzmi Word", word, "Ovrha.doc")

# --- 4. ŽALBE ---
elif "Žalbe" in modul:
    st.header("Pravni lijekovi: Žalba na presudu")
    with st.expander("1. Podaci o sudu i presudi", expanded=True):
        col_s1, col_s2 = st.columns(2)
        sud_prvi = col_s1.text_input("Prvostupanjski sud", value="OPĆINSKI GRAĐANSKI SUD U ZAGREBU")
        sud_drugi = col_s2.text_input("Drugostupanjski sud", value="ŽUPANIJSKI SUD U ...")
        c1, c2 = st.columns(2)
        broj_presude = c1.text_input("Poslovni broj presude")
        datum_presude = c2.text_input("Datum donošenja presude")
        mjesto = st.text_input("Mjesto sastava žalbe", value="Zagreb")
    with st.expander("2. Stranke", expanded=False):
        col_tuz, col_tuzen = st.columns(2)
        stranke = {'tuzitelj': col_tuz.text_input("Tužitelj"), 'tuzenik': col_tuzen.text_input("Tuženik")}
    with st.expander("3. Sadržaj žalbe", expanded=True):
        opseg = st.radio("Pobijate li presudu:", ["u cijelosti", "u dijelu odluke o trošku", "u dosuđujućem dijelu"], horizontal=True)
        st.markdown("**Žalbeni razlozi:**")
        r1 = st.checkbox("Bitna povreda odredaba parničnog postupka")
        r2 = st.checkbox("Pogrešno ili nepotpuno utvrđeno činjenično stanje")
        r3 = st.checkbox("Pogrešna primjena materijalnog prava")
        razlozi_lista = [r for r, checked in [("Zbog bitne povrede odredaba parničnog postupka", r1), ("Zbog pogrešno ili nepotpuno utvrđenog činjeničnog stanja", r2), ("Zbog pogrešne primjene materijalnog prava", r3)] if checked]
        if not razlozi_lista: razlozi_lista.append("(Navesti razloge)")
        obrazlozenje = st.text_area("OBRAZLOŽENJE", height=300)
    with st.expander("4. Troškovnik žalbe", expanded=False):
        troskovnik_data = {'stavka': 0.0, 'pdv': 0.0, 'pristojba': 0.0}
        if st.checkbox("Potražujem trošak", value=True):
            col_tr1, col_tr2 = st.columns(2)
            troskovnik_data['stavka'] = col_tr1.number_input("Cijena sastava", min_value=0.0)
            if col_tr1.checkbox("Dodaj PDV"): troskovnik_data['pdv'] = troskovnik_data['stavka'] * 0.25
            troskovnik_data['pristojba'] = col_tr2.number_input("Sudska pristojba", min_value=0.0)
    if st.button("Generiraj Žalbu"):
        doc_html = generiraj_zalbu_pro(sud_prvi, sud_drugi, stranke, {'broj': broj_presude, 'datum': datum_presude, 'opseg': opseg, 'mjesto': mjesto}, razlozi_lista, obrazlozenje, troskovnik_data)
        st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
        st.download_button("💾 Preuzmi Žalbu", pripremi_za_word(doc_html), "Zalba.doc")

# --- 5. ZEMLJIŠNE KNJIGE ---
elif "Zemljišne" in modul:
    st.header("Zemljišne knjige")
    zk_usluga = st.selectbox("Odaberite ZK uslugu:", ["Tabularna isprava", "ZK Prijedlog (Uknjižba)", "Brisovna tužba"])
    
    if zk_usluga == "Tabularna isprava":
        c1, c2 = st.columns(2)
        prod, _, _ = unos_stranke("PRODAVATELJ", "tp")
        kup, _, _ = unos_stranke("KUPAC", "tk")
        c1, c2, c3 = st.columns(3)
        ko = c1.text_input("K.O.")
        cest = c2.text_input("Čestica")
        ul = c3.text_input("Uložak")
        opis = st.text_area("Opis u naravi")
        dat = st.date_input("Datum ugovora")
        if st.button("Generiraj Tabularnu"):
            doc = generiraj_tabularnu_doc(prod, kup, ko, cest, ul, opis, dat.strftime('%d.%m.%Y.'))
            st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
            st.download_button("Preuzmi", pripremi_za_word(doc), "Tabularna.doc")

    elif zk_usluga == "ZK Prijedlog (Uknjižba)":
        sud = st.text_input("Sud", "OPĆINSKI SUD U ZAGREBU")
        c1, c2, c3 = st.columns(3)
        ko = c1.text_input("K.O.", "Centar")
        ulozak = c2.text_input("ZK uložak")
        cestica = c3.text_input("Čestica")
        opis = st.text_area("Opis u naravi")
        c1, c2 = st.columns(2)
        pred, _, _ = unos_stranke("PREDLAGATELJ", "zk_p")
        prot, _, _ = unos_stranke("PROTUSTRANKA", "zk_pr")
        ug = st.text_input("Ugovor info")
        tab = st.text_input("Tabularna info")
        pristojba = st.number_input("ZK pristojba", 0.0)
        if st.button("Generiraj Prijedlog"):
            doc = generiraj_zk_prijedlog(sud, pred, prot, {'ko': ko, 'ulozak': ulozak, 'cestica': cestica, 'opis': opis}, {'ugovor': ug, 'tabularna': tab}, {'pristojba': pristojba})
            st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
            st.download_button("Preuzmi", pripremi_za_word(doc), "ZK_Prijedlog.doc")

    elif zk_usluga == "Brisovna tužba":
        zastupanje = zaglavlje_sastavljaca()
        sud = st.text_input("Nadležni sud")
        c1, c2 = st.columns(2)
        tuzitelj, _, _ = unos_stranke("TUŽITELJ", "bt_t")
        tuzenik, _, _ = unos_stranke("TUŽENIK", "bt_tu")
        c1, c2, c3 = st.columns(3)
        ko = c1.text_input("K.O.")
        ulozak = c2.text_input("Uložak")
        cestica = c3.text_input("Čestica")
        opis = st.text_area("Opis u naravi")
        c1, c2 = st.columns(2)
        z_broj = c1.text_input("Z-broj")
        dat_uknj = c2.date_input("Datum uknjižbe")
        razlog = st.text_area("Razlog nevaljanosti")
        tuzenik_znao = st.radio("Je li tuženik znao?", ["DA", "NE"])
        vps = st.number_input("VPS", 10000.0)
        sastav = st.number_input("Cijena sastava", 0.0)
        pdv = sastav * 0.25
        pristojba = st.number_input("Pristojba", 0.0)
        if st.button("Generiraj Tužbu"):
            doc = generiraj_brisovnu_tuzbu(sud, zastupanje, tuzitelj, tuzenik, {'ko': ko, 'ulozak': ulozak, 'cestica': cestica, 'opis': opis}, {'vps': vps, 'z_broj': z_broj, 'datum_uknjizbe': dat_uknj.strftime('%d.%m.%Y.'), 'isprava': "Ugovor", 'datum_isprave': "...", 'razlog_nevaljanosti': razlog, 'tuzenik_znao': "DA" in tuzenik_znao, 'mjesto': "Zagreb"}, {'stavka': sastav, 'pdv': pdv, 'pristojba': pristojba})
            st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
            st.download_button("Preuzmi", pripremi_za_word(doc), "Brisovna.doc")

# --- 6. KAMATE ---
elif "Kamate" in modul:
    st.header("Kalkulator Kamata")
    iznos = st.number_input("Glavnica")
    stopa = st.number_input("Stopa (%)", value=12.0)
    # ISPRAVAK: Maknuto slovo 'A' s kraja linije
    d1 = st.date_input("Dospijeće")
    d2 = st.date_input("Obračun")
    if st.button("Izračunaj"):
        dana = (d2-d1).days
        if dana > 0:
            kamata = (iznos * stopa * dana)/36500
            st.success(f"Kamata: {kamata:.2f} EUR (za {dana} dana)")
            st.metric("Ukupno dugovanje", f"{iznos + kamata:.2f} EUR")
        else: st.error("Datum obračuna mora biti poslije dospijeća.")
