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
    """
    Univerzalna funkcija za generiranje tablice troškova.
    """
    if not troskovi: return ""
    
    # Sigurna provjera ključeva
    stavka = troskovi.get('stavka', 0.0)
    pdv = troskovi.get('pdv', 0.0)
    materijalni = troskovi.get('materijalni', 0.0)
    pristojba = troskovi.get('pristojba', 0.0)
    
    ukupno = stavka + pdv + materijalni + pristojba
    
    html = f"""
    <div class='section-title' style='margin-top: 30px;'>POPIS TROŠKOVA POSTUPKA:</div>
    <table class='cost-table'>
        <tr>
            <td width="70%">1. Sastav podneska/isprave (Tbr. Tarife):</td>
            <td width="30%" align="right">{stavka:.2f} EUR</td>
        </tr>
    """
    
    if pdv > 0:
        html += f"""
        <tr>
            <td>2. PDV (25%) na stavku 1.:</td>
            <td align="right">{pdv:.2f} EUR</td>
        </tr>
        """
        
    if materijalni > 0:
        html += f"""
        <tr>
            <td>3. Materijalni troškovi / JB Nagrada:</td>
            <td align="right">{materijalni:.2f} EUR</td>
        </tr>
        """

    if pristojba > 0:
        html += f"""
        <tr>
            <td>4. Sudska pristojba:</td>
            <td align="right">{pristojba:.2f} EUR</td>
        </tr>
        """
        
    html += f"""
        <tr style='font-weight: bold; background-color: #f0f0f0;'>
            <td style='padding: 10px;'>UKUPNO:</td>
            <td style='padding: 10px;' align="right">{ukupno:.2f} EUR</td>
        </tr>
    </table>
    """
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

# === TUŽBA PRO ===
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
    <div class='justified'>
    {format_text(data['cinjenice'])}
    </div>

    <div class='section-title'>II. DOKAZI</div>
    <div class='justified'>
    Predlaže se izvođenje sljedećih dokaza:
    <br>
    {format_text(data['dokazi'])}
    </div>

    <div class='section-title'>III. TUŽBENI ZAHTJEV</div>
    <div class='justified'>
    Slijedom navedenog, budući da Tuženik nije podmirio svoju dospjelu obvezu, Tužitelj predlaže da naslovni Sud donese sljedeću
    <br><br>
    <div style="text-align: center; font-weight: bold;">PRESUDU</div>
    <br>
    <b>I. Nalaže se Tuženiku</b> da Tužitelju isplati iznos od <b>{vps:,.2f} EUR</b> zajedno sa zakonskom zateznom kamatom koja teče od dana dospijeća {data['datum_dospijeca']} pa do isplate, po stopi određenoj zakonom.
    <br><br>
    <b>II. Nalaže se Tuženiku</b> da Tužitelju naknadi troškove ovog parničnog postupka, u roku od 15 dana, zajedno sa zateznom kamatom od dana donošenja presude do isplate.
    </div>

    {troskovnik_html}

    <br><br>
    <div class='signature-row'>
        <div style='display:inline-block; width: 50%;'>
            <b>PRILOZI:</b><br>
            1. Punomoć<br>
            2. Dokaz o uplati pristojbe<br>
            3. Dokazi navedeni u točki II.
        </div> 
        <div class='signature-block'>
            <b>TUŽITELJ</b>
            <br>(po punomoćniku)<br><br>
            ______________________
        </div>
    </div>
    """

# === OVRHA PRO ===
def generiraj_ovrhu_pro(jb, ovrhovoditelj, ovrsenik, trazbina, isprava, troskovi_dict):
    troskovnik_html = formatiraj_troskovnik(troskovi_dict)
    
    # Izračun ukupnog troška za izreku rješenja
    ukupno_trosak = troskovi_dict.get('stavka', 0) + troskovi_dict.get('pdv', 0) + troskovi_dict.get('materijalni', 0) + troskovi_dict.get('pristojba', 0)

    return f"""
    <div style="font-weight: bold;">JAVNOM BILJEŽNIKU {jb.upper()}</div>
    <br>
    
    <div class='justified'>
    <b>OVRHOVODITELJ:</b> {ovrhovoditelj}<br>
    <b>OVRŠENIK:</b> {ovrsenik}
    <br><br>
    <b>Radi:</b> Ovrhe na temelju vjerodostojne isprave<br>
    <b>Vrijednost tražbine: {trazbina['glavnica']:,.2f} EUR</b>
    </div>
    <br>
    <div class='header-doc'>PRIJEDLOG ZA OVRHU<br><span style='font-size:11pt; font-weight:normal'>na temelju vjerodostojne isprave</span></div>

    <div class='justified'>
    Na temelju vjerodostojne isprave – <b>{isprava}</b> od dana {trazbina['datum_racuna']}, iz koje proizlazi dospjela tražbina Ovrhovoditelja prema Ovršeniku, Ovrhovoditelj predlaže da Javni bilježnik donese sljedeće:
    </div>

    <div style='border: 2px solid black; padding: 15px; margin: 20px 0;'>
        <div class='header-doc' style='margin:0;'>RJEŠENJE O OVRSI</div>
        <div style='text-align:center; font-size:10pt;'>(na temelju vjerodostojne isprave)</div>
        <br>
        <div class='justified'>
        <b>I. NALAŽE SE Ovršeniku</b> da Ovrhovoditelju u roku od osam dana od dana dostave ovog rješenja namiri tražbinu u iznosu od <b>{trazbina['glavnica']:,.2f} EUR</b>, zajedno sa zakonskim zateznim kamatama koje teku od dana dospijeća <b>{trazbina['dospjece']}</b> pa do isplate, kao i da mu naknadi troškove ovog postupka u iznosu od <b>{ukupno_trosak:.2f} EUR</b>.
        <br><br>
        <b>II. ODREĐUJE SE OVRHA</b> radi naplate tražbine iz točke I. ovog rješenja i troškova postupka. Ovrha će se provesti na novčanim sredstvima Ovršenika po svim računima kod banaka, te na cjelokupnoj imovini Ovršenika.
        </div>
    </div>

    {troskovnik_html}

    <br><br>
    <div class='signature-row'>
        <div style='display:inline-block; width: 50%;'></div>
        <div class='signature-block'>
            <b>OVRHOVODITELJ</b>
            <br><br><br>
            ______________________
        </div>
    </div>
    """

# === ŽALBA PRO ===
def generiraj_zalbu_pro(sud_prvi, sud_drugi, stranke, podaci_o_presudi, razlozi, tekst_obrazlozenja, troskovnik):
    troskovnik_html = formatiraj_troskovnik(troskovnik)
    danas = date.today().strftime("%d.%m.%Y.")
    
    razlozi_html = "<ul>"
    for razlog in razlozi:
        razlozi_html += f"<li>{razlog}</li>"
    razlozi_html += "</ul>"

    return f"""
    <div style="font-weight: bold; font-size: 14px;">{sud_drugi.upper()}</div>
    <div>(kao drugostupanjskom sudu)</div>
    <br>
    <div>putem</div>
    <br>
    <div style="font-weight: bold;">{sud_prvi.upper()}</div>
    <div>(kao prvostupanjskog suda)</div>
    <br><br>
    
    <div class='justified'>
    <b>PRAVNA STVAR:</b><br>
    <b>TUŽITELJ:</b> {stranke['tuzitelj']}<br>
    <b>TUŽENIK:</b> {stranke['tuzenik']}<br>
    <b>Poslovni broj: {podaci_o_presudi['broj']}</b>
    </div>
    <br>
    
    <div class='header-doc'>ŽALBA</div>
    <div style="text-align: center;">
    protiv presude {sud_prvi} poslovni broj {podaci_o_presudi['broj']} od dana {podaci_o_presudi['datum']}
    </div>
    <br>

    <div class='justified'>
    Žalitelj ovime pravovremeno, u otvorenom zakonskom roku, podnosi žalbu protiv navedene presude {podaci_o_presudi['opseg']} zbog sljedećih zakonskih razloga (čl. 353. ZPP):
    </div>
    
    {razlozi_html}

    <div class='section-title'>I. OBRAZLOŽENJE</div>
    <div class='justified'>
    {format_text(tekst_obrazlozenja)}
    </div>

    <div class='section-title'>II. PRIJEDLOG</div>
    <div class='justified'>
    Slijedom navedenog, predlaže se da naslovni drugostupanjski sud ovu žalbu uvaži, pobijanu presudu ukine i predmet vrati prvostupanjskom sudu na ponovno suđenje.
    </div>

    {troskovnik_html}

    <br><br>
    <div style="text-align: right;">U {podaci_o_presudi['mjesto']}, dana {danas}</div>
    <table width="100%">
        <tr>
            <td width="50%"></td>
            <td width="50%" align="center">
                <b>ŽALITELJ</b>
                <br>(po punomoćniku)<br><br>
                ______________________
            </td>
        </tr>
    </table>
    """

# === OSTALI GENERATORI (Standardni) ===
def generiraj_ugovor_standard(tip_ugovora, stranka1, stranka2, podaci, opcije, troskovi_dict=None):
    datum = date.today().strftime("%d.%m.%Y.")
    dodatni_tekst = ""
    if opcije.get('kapara'):
        dodatni_tekst += f"<br><b>Kapara:</b> Ugovorne strane potvrđuju da je Kupac isplatio kaparu u iznosu od {opcije['iznos_kapare']} EUR."
    
    solemnizacija_clanak = ""
    if opcije.get('solemnizacija'):
        solemnizacija_clanak = """<div class='section-title'>Članak (Solemnizacija)</div><div class='doc-body'>Ugovorne strane suglasne su da se ovaj Ugovor solemnizira (potvrdi) kod Javnog bilježnika.</div>"""

    titles = {"Kupoprodaja": ("UGOVOR O KUPOPRODAJI", "PRODAVATELJ", "KUPAC"), "Najam/Zakup": ("UGOVOR O NAJMU", "NAJMODAVAC", "NAJMOPRIMAC"), "Ugovor o djelu (Usluga)": ("UGOVOR O DJELU", "NARUČITELJ", "IZVOĐAČ"), "Zajam": ("UGOVOR O ZAJMU", "ZAJMODAVAC", "ZAJMOPRIMAC")}
    naslov, u1, u2 = titles[tip_ugovora]
    
    trosak_prikaz = formatiraj_troskovnik(troskovi_dict) if troskovi_dict else ""

    return f"""<div class='header-doc'>{naslov}</div><div class='doc-body'>Sklopljen u {podaci['mjesto']}, dana {datum}, između:</div><div class='party-info'>1. <b>{u1}:</b><br>{stranka1}<br><br>2. <b>{u2}:</b><br>{stranka2}</div><div class='section-title'>Članak 1.</div><div class='doc-body'>{format_text(podaci['predmet_clanak'])}</div><div class='section-title'>Članak 2.</div><div class='doc-body'>{format_text(podaci['cijena_clanak'])}{dodatni_tekst}</div><div class='section-title'>Članak 3.</div><div class='doc-body'>{format_text(podaci['rok_clanak'])}</div>{solemnizacija_clanak}<br><br>{trosak_prikaz}<br><table width="100%"><tr><td width="50%" align="center"><b>{u1}</b><br><br>__________</td><td width="50%" align="center"><b>{u2}</b><br><br>__________</td></tr></table>"""

def generiraj_ugovor_o_radu(poslodavac, radnik, podaci):
    vrsta_tekst = "NA NEODREĐENO" if podaci['vrsta'] != "Određeno" else "NA ODREĐENO"
    return f"""<div class='header-doc'>UGOVOR O RADU<br>{vrsta_tekst}</div><div class='party-info'>1. <b>POSLODAVAC:</b><br>{poslodavac}<br>2. <b>RADNIK:</b><br>{radnik}</div><div class='section-title'>Radno mjesto</div><div class='doc-body'>{podaci['naziv_radnog_mjesta']}</div><div class='section-title'>Plaća</div><div class='doc-body'>{podaci['bruto_placa']} EUR</div><br><br><table width="100%"><tr><td width="50%" align="center"><b>POSLODAVAC</b><br>__________</td><td width="50%" align="center"><b>RADNIK</b><br>__________</td></tr></table>"""

def generiraj_otkaz(poslodavac, radnik, podaci):
    return f"""<div class='header-doc'>ODLUKA O OTKAZU</div><div class='doc-body'>1. Otkazuje se ugovor radniku {radnik}.</div><div class='section-title'>Obrazloženje</div><div class='doc-body'>{podaci['tekst_obrazlozenja']}</div><br><br><table width="100%"><tr><td align="center"><b>POSLODAVAC</b><br>__________</td></tr></table>"""

def generiraj_tabularnu_doc(prod, kup, ko, cest, ul, opis, dat):
    return f"""
    <div class='header-doc'>TABULARNA IZJAVA<br><span style='font-size: 11pt; font-weight: normal;'>(Clausula Intabulandi)</span></div>
    <div class='party-info'><b>PRODAVATELJ:</b><br>{prod}</div>
    <div class='party-info'><b>KUPAC:</b><br>{kup}</div>
    <div class='doc-body'>Temeljem Ugovora od {dat} za nekretninu u K.O. {ko}, k.č.br {cest}.
    {f'<br>Opis u naravi: {opis}' if opis else ''}
    </div>
    <div class='doc-body clausula'>Ja, PRODAVATELJ, ovime izričito ovlašćujem KUPCA da zatraži uknjižbu prava vlasništva.</div>
    <br><br><table width="100%"><tr><td width="40%"></td><td width="60%" align="center"><b>PRODAVATELJ</b><br>(Ovjera JB)<br><br>_________________</td></tr></table>
    """

def generiraj_zk_prijedlog(sud, predlagatelj, protustranka, nekretnina, dokumenti, troskovi_dict):
    troskovnik_html = formatiraj_troskovnik(troskovi_dict)
    return f"""
    <div style="font-weight: bold; font-size: 14px;">{sud.upper()}</div>
    <div style="font-size: 12px;">Zemljišnoknjižni odjel</div>
    <br><br>
    
    <div class='party-info'>
    <b>PREDLAGATELJ:</b><br>
    {predlagatelj}
    </div>
    
    <div class='party-info'>
    <b>PROTUSTRANKA:</b><br>
    {protustranka}
    </div>
    
    <div class='party-info'>
    <b>RADI:</b> Uknjižbe prava vlasništva
    </div>
    
    <br>
    <div class='header-doc'>ZEMLJIŠNOKNJIŽNI PRIJEDLOG<br><span style='font-size: 12pt; font-weight: normal;'>za uknjižbu prava vlasništva</span></div>

    <div class='doc-body'>
    Predlagatelj predlaže da naslovni sud, na temelju priloženih isprava, u zemljišnim knjigama za nekretninu upisanu kao:
    <br><br>
    <b>Katastarska općina (k.o.):</b> {nekretnina['ko']}<br>
    <b>Broj zk. uloška:</b> {nekretnina['ulozak']}<br>
    <b>Broj čestice (k.č.br.):</b> {nekretnina['cestica']}
    {f", u naravi {nekretnina['opis']}" if nekretnina['opis'] else ""}
    <br><br>
    provede upis, odnosno dozvoli:
    </div>

    <div class='section-title' style='text-align: center; border: 1px solid black; padding: 10px; margin: 20px 0;'>
    UKNJIŽBU PRAVA VLASNIŠTVA<br>
    u korist Predlagatelja (u cijelosti / 1/1 dijela).
    </div>

    <div class='doc-body'>
    Predlagatelj prilaže izvornike/ovjerene preslike isprava koje su temelj za upis.
    </div>

    <div class='section-title'>POPIS PRILOGA:</div>
    <div class='doc-body'>
    <ol>
        <li>{dokumenti['ugovor']}</li>
        <li>{dokumenti['tabularna']}</li>
        <li>Dokaz o uplati sudske pristojbe</li>
        <li>Dokaz o državljanstvu / OIB (preslika osobne iskaznice)</li>
    </ol>
    </div>

    {troskovnik_html}

    <br><br>
    <table width="100%" border="0">
        <tr>
            <td width="50%"></td>
            <td width="50%" align="center">
                <b>PREDLAGATELJ</b>
                <br>(potpis nije nužno ovjeravati)<br><br>
                ______________________
            </td>
        </tr>
    </table>
    """

def generiraj_brisovnu_tuzbu(sud, zastupanje, tuzitelj, tuzenik, nekretnina, podaci_spora, troskovi_dict):
    datum = date.today().strftime("%d.%m.%Y.")
    troskovnik_html = formatiraj_troskovnik(troskovi_dict)
    
    tekst_savjesnost = ""
    if podaci_spora['tuzenik_znao']:
        tekst_savjesnost = "Tuženik je prilikom stjecanja bio nesavjestan (u zloj vjeri) jer je znao, odnosno morao znati, da je temeljni pravni posao nevaljan, te se stoga ne može pozivati na načelo povjerenja u zemljišne knjige."
    else:
        tekst_savjesnost = "Tužba se podnosi u zakonskom roku propisanom člankom 129. ZZK za stjecatelje u dobroj vjeri."

    return f"""
    <div style="font-weight: bold; font-size: 14px; text-align: left;">{sud.upper()}</div>
    <div style="font-size: 12px; text-align: left;">{zastupanje}</div>
    <br>
    <div class='party-info'>
    <b>PRAVNA STVAR:</b><br>
    <b>TUŽITELJ:</b> {tuzitelj}<br>
    <b>TUŽENIK:</b> {tuzenik}
    </div>
    
    <div class='party-info'>
    <b>Radi:</b> Brisanja uknjižbe i uspostave prijašnjeg ZK stanja<br>
    <b>Vrijednost predmeta spora (VPS): {podaci_spora['vps']:,.2f} EUR</b>
    </div>
    <br>
    <div class='header-doc'>BRISOVNA TUŽBA</div>

    <div class='section-title'>I. ČINJENIČNI NAVODI</div>
    <div class='doc-body'>
    Tužitelj je bio isključivi vlasnik nekretnine upisane u <b>zk.ul. {nekretnina['ulozak']}, k.o. {nekretnina['ko']}, k.č.br. {nekretnina['cestica']}</b>{f", u naravi {nekretnina['opis']}" if nekretnina['opis'] else ""}.
    <br><br>
    Dana {podaci_spora['datum_uknjizbe']}, u zemljišnim knjigama naslovnog suda, pod brojem <b>{podaci_spora['z_broj']}</b>, provedena je nevaljana uknjižba prava vlasništva u korist Tuženika.
    <br><br>
    Navedena uknjižba temelji se na ispravi: {podaci_spora['isprava']} od dana {podaci_spora['datum_isprave']}.
    <br><br>
    Tužitelj tvrdi da je navedena isprava (temeljni pravni posao) ništetna/nevaljana iz sljedećih razloga:
    <br>
    <i>{podaci_spora['razlog_nevaljanosti']}</i>
    <br><br>
    S obzirom na to da je temeljni pravni posao ništetan, ništetna je i sama uknjižba koja je na temelju njega provedena (načelo kauzalnosti).
    <br><br>
    {tekst_savjesnost}
    </div>

    <div class='section-title'>DOKAZI:</div>
    <div class='doc-body'>
    1. ZK izvadak (povijesni i trenutni).<br>
    2. Uvid u ZK spis broj {podaci_spora['z_broj']}.<br>
    3. {podaci_spora['isprava']} (predmet pobijanja).<br>
    4. Saslušanje stranaka.<br>
    5. Po potrebi grafološko ili drugo vještačenje.
    </div>

    <div class='section-title'>II. TUŽBENI ZAHTJEV</div>
    <div class='doc-body'>
    Slijedom navedenog, Tužitelj predlaže da Sud donese sljedeću
    </div>
    <div style="text-align: center; font-weight: bold; margin: 10px 0;">PRESUDU</div>
    <div class='doc-body'>
    <b>I. Utvrđuje se da je ništetan i bez pravnog učinka</b> {podaci_spora['isprava']} od dana {podaci_spora['datum_isprave']}, sklopljen između stranaka (ili prednika).
    <br><br>
    <b>II. Utvrđuje se da je nevaljana uknjižba</b> prava vlasništva u korist tuženika, provedena u zemljišnim knjigama {sud}, u zk.ul. {nekretnina['ulozak']}, k.o. {nekretnina['ko']}, na k.č.br. {nekretnina['cestica']}, pod poslovnim brojem {podaci_spora['z_broj']}.
    <br><br>
    <b>III. Nalaže se brisanje uknjižbe</b> prava vlasništva upisanog u korist Tuženika na nekretnini iz točke II. izreke, te <b>uspostava prijašnjeg zemljišnoknjižnog stanja</b> kakvo je bilo prije provedbe nevaljanog upisa, na način da se ponovno upiše pravo vlasništva u korist Tužitelja.
    <br><br>
    <b>IV.</b> Nalaže se Tuženiku naknaditi Tužitelju parnični trošak u roku od 15 dana.
    </div>

    {troskovnik_html}

    <br><br>
    <div style="text-align:right;">U {podaci_spora['mjesto']}, dana {datum}</div>
    <table width="100%" border="0">
        <tr>
            <td width="50%"></td>
            <td width="50%" align="center">
                <b>TUŽITELJ</b><br><br><br>
                ______________________
            </td>
        </tr>
    </table>
    <br><br>
    <div style="font-size: 10pt;">
    <b>PRILOZI:</b><br>
    1. Dokaz o uplati sudske pristojbe.<br>
    2. ZK izvadak.<br>
    3. Preslika osporene isprave.<br>
    4. Punomoć za zastupanje.
    </div>
    """

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
    
    kategorija = st.radio("Kategorija prava:", ["Građansko pravo (Obvezno)", "Radno pravo"], horizontal=True)
    
    if kategorija == "Građansko pravo (Obvezno)":
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

        # Troškovnik za ugovor (opcionalno)
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
            podaci = {'vrsta': st.radio("Vrsta", ["Neodređeno", "Određeno"]), 'datum_do': None, 'razlog_odredeno': "", 'probni_rad': False}
            if podaci['vrsta'] == "Određeno": 
                podaci['datum_do'] = st.date_input("Do")
                podaci['razlog_odredeno'] = st.text_input("Razlog za određeno")
            podaci['probni_rad'] = st.checkbox("Probni rad")
            podaci['naziv_radnog_mjesta'] = st.text_input("Radno mjesto")
            podaci['bruto_placa'] = st.number_input("Bruto plaća (EUR)")
            
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

# --- 2. TUŽBE (UPDATED) ---
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
    cinjenice = st.text_area("I. Činjenice (Kronologija)", height=150, placeholder="Opišite nastanak duga. Npr. Dana X stranke su sklopile ugovor. Tužitelj je isporučio robu. Tuženik nije platio račun br. Y u iznosu od Z...")
    dokazi = st.text_area("II. Dokazi", placeholder="- Ugovor o kupoprodaji\n- Račun broj 10/2023\n- Opomena pred tužbu\n- Izvod iz poslovnih knjiga")
    
    st.subheader("3. Troškovnik (Odvjetnička tarifa)")
    st.markdown("Ovdje unesite troškove koje tražite od suda.")
    col_tr1, col_tr2, col_tr3 = st.columns(3)
    trosak_sastav = col_tr1.number_input("Sastav tužbe (EUR)", 0.0)
    trosak_pdv = 0.0
    if col_tr2.checkbox("Dodaj PDV (25%)", value=True):
        trosak_pdv = trosak_sastav * 0.25
    trosak_pristojba = col_tr3.number_input("Sudska pristojba (EUR)", 0.0)
    
    if st.button("Generiraj Tužbu"):
        troskovi_dict = {'stavka': trosak_sastav, 'pdv': trosak_pdv, 'pristojba': trosak_pristojba}
        data_tuzba = {'cinjenice': cinjenice, 'dokazi': dokazi, 'datum_dospijeca': datum_dospijeca.strftime('%d.%m.%Y.')}
        
        doc = generiraj_tuzbu_pro(sud, zastupanje, t1, t2, vps, vrsta, data_tuzba, troskovi_dict)
        
        st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
        word = pripremi_za_word(doc)
        st.download_button("Preuzmi Word", word, "Tuzba.doc")

# --- 3. OVRHE (UPDATED) ---
elif "Ovršni" in modul:
    st.header("Prijedlog za Ovrhu (Vjerodostojna isprava)")
    st.info("Podnosi se Javnom bilježniku. Sadrži Prijedlog + Rješenje o ovrsi.")
    
    jb = st.text_input("Javni bilježnik (Ime, Prezime, Grad)", placeholder="Ivan Horvat, Zagreb")
    
    col1, col2 = st.columns(2)
    with col1: o1, _, _ = unos_stranke("OVRHOVODITELJ (Vjerovnik)", "o1")
    with col2: o2, _, _ = unos_stranke("OVRŠENIK (Dužnik)", "o2")
    
    st.subheader("1. Dugovanje")
    c1, c2, c3 = st.columns(3)
    opis_isprave = c1.text_input("Vjerodostojna isprava (Izvor duga)", placeholder="Račun br. 100-2024")
    dat_racuna = c2.date_input("Datum izdavanja računa")
    glavnica = c3.number_input("Glavnica duga (EUR)", min_value=0.0)
    dospjece = st.date_input("Datum dospijeća (Kamate teku od...)")
    
    st.subheader("2. Troškovnik (Nužno za Rješenje!)")
    st.markdown("Morate predvidjeti i trošak bilježnika kako bi ga on mogao dosuditi.")
    
    ct1, ct2, ct3 = st.columns(3)
    trosak_odvjetnik = ct1.number_input("Odvjetnik (Sastav prijedloga)", 0.0)
    trosak_jb_nagrada = ct2.number_input("JB Nagrada (Materijalni)", 0.0, help="Provjerite tarifu JB prema visini duga.")
    trosak_pdv = 0.0
    
    if ct3.checkbox("Obračunaj PDV na sve?"):
        trosak_pdv = (trosak_odvjetnik + trosak_jb_nagrada) * 0.25
        
    ukupno_trosak = trosak_odvjetnik + trosak_jb_nagrada + trosak_pdv
    st.write(f"**Ukupno trošak postupka:** {ukupno_trosak:.2f} EUR")
    
    if st.button("Generiraj Ovršni Prijedlog"):
        trazbina_data = {
            'glavnica': glavnica,
            'datum_racuna': dat_racuna.strftime('%d.%m.%Y.'),
            'dospjece': dospjece.strftime('%d.%m.%Y.')
        }
        
        # 'materijalni' ovdje koristimo za JB nagradu radi prikaza u tablici
        troskovi_dict = {
            'stavka': trosak_odvjetnik, 
            'materijalni': trosak_jb_nagrada, 
            'pdv': trosak_pdv,
            'pristojba': 0,
        }
        
        doc = generiraj_ovrhu_pro(jb, o1, o2, trazbina_data, opis_isprave, troskovi_dict)
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
        broj_presude = c1.text_input("Poslovni broj presude (npr. P-1234/2023)")
        datum_presude = c2.text_input("Datum donošenja presude", placeholder="dd.mm.gggg.")
        mjesto = st.text_input("Mjesto sastava žalbe", value="Zagreb")

    with st.expander("2. Stranke", expanded=False):
        col_tuz, col_tuzen = st.columns(2)
        tuzitelj_ime = col_tuz.text_input("Tužitelj")
        tuzenik_ime = col_tuzen.text_input("Tuženik")
        stranke = {'tuzitelj': tuzitelj_ime, 'tuzenik': tuzenik_ime}

    with st.expander("3. Sadržaj žalbe", expanded=True):
        opseg = st.radio("Pobijate li presudu:", ["u cijelosti", "u dijelu odluke o trošku", "u dosuđujućem dijelu"], horizontal=True)
        
        st.markdown("**Žalbeni razlozi:**")
        r1 = st.checkbox("Bitna povreda odredaba parničnog postupka")
        r2 = st.checkbox("Pogrešno ili nepotpuno utvrđeno činjenično stanje")
        r3 = st.checkbox("Pogrešna primjena materijalnog prava")
        
        razlozi_lista = []
        if r1: razlozi_lista.append("Zbog bitne povrede odredaba parničnog postupka")
        if r2: razlozi_lista.append("Zbog pogrešno ili nepotpuno utvrđenog činjeničnog stanja")
        if r3: razlozi_lista.append("Zbog pogrešne primjene materijalnog prava")
        if not razlozi_lista: razlozi_lista.append("(Navesti razloge)")

        obrazlozenje = st.text_area("OBRAZLOŽENJE (Argumentacija)", height=300)

    with st.expander("4. Troškovnik žalbe", expanded=False):
        trazi_trosak = st.checkbox("Potražujem trošak sastava ove žalbe", value=True)
        cijena_sastav = 0.0
        pristojba = 0.0
        pdv = 0.0
        if trazi_trosak:
            col_tr1, col_tr2 = st.columns(2)
            cijena_sastav = col_tr1.number_input("Cijena sastava žalbe (EUR)", min_value=0.0)
            if col_tr1.checkbox("Dodaj PDV (25%)"):
                pdv = cijena_sastav * 0.25
            pristojba = col_tr2.number_input("Sudska pristojba", min_value=0.0)

        troskovnik_data = {'stavka': cijena_sastav, 'pdv': pdv, 'pristojba': pristojba}

    if st.button("Generiraj Žalbu"):
        podaci_presuda = {'broj': broj_presude, 'datum': datum_presude, 'opseg': opseg, 'mjesto': mjesto}
        doc_html = generiraj_zalbu_pro(sud_prvi, sud_drugi, stranke, podaci_presuda, razlozi_lista, obrazlozenje, troskovnik_data)
        st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
        word_data = pripremi_za_word(doc_html)
        st.download_button("💾 Preuzmi Žalbu", data=word_data, file_name="Zalba.doc")

# --- 5. ZEMLJIŠNE KNJIGE (UPDATED) ---
elif "Zemljišne" in modul:
    st.header("Zemljišne knjige")
    
    zk_usluga = st.selectbox("Odaberite ZK uslugu:", ["Tabularna isprava", "ZK Prijedlog (Uknjižba)", "Brisovna tužba"])
    
    # A) TABULARNA
    if zk_usluga == "Tabularna isprava":
        st.warning("⚠️ Potpisuje samo PRODAVATELJ (ovjera kod JB).")
        c1, c2 = st.columns(2)
        prod, _, valid1 = unos_stranke("PRODAVATELJ", "tp")
        kup, _, valid2 = unos_stranke("KUPAC", "tk")
        
        c1, c2, c3 = st.columns(3)
        ko = c1.text_input("K.O.")
        cest = c2.text_input("Čestica")
        ul = c3.text_input("Uložak")
        opis = st.text_area("Opis u naravi (Opcionalno)")
        dat = st.date_input("Datum ugovora")
        
        if st.button("Generiraj Tabularnu"):
            doc = generiraj_tabularnu_doc(prod, kup, ko, cest, ul, opis, dat.strftime('%d.%m.%Y.'))
            st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
            word = pripremi_za_word(doc)
            st.download_button("Preuzmi", word, "Tabularna.doc")

    # B) ZK PRIJEDLOG
    elif zk_usluga == "ZK Prijedlog (Uknjižba)":
        sud = st.text_input("Sud", "OPĆINSKI SUD U ZAGREBU")
        c1, c2, c3 = st.columns(3)
        ko = c1.text_input("K.O.", "Centar")
        ulozak = c2.text_input("ZK uložak")
        cestica = c3.text_input("Čestica")
        opis = st.text_area("Opis u naravi")
        c1, c2 = st.columns(2)
        pred, _, _ = unos_stranke("PREDLAGATELJ (Kupac)", "zk_p")
        prot, _, _ = unos_stranke("PROTUSTRANKA (Prodavatelj)", "zk_pr")
        ug = st.text_input("Ugovor info", "Ugovor o kupoprodaji od...")
        tab = st.text_input("Tabularna info", "(u ugovoru)")
        
        st.subheader("Troškovnik")
        pristojba = st.number_input("ZK pristojba", 0.0)
        troskovi_dict = {'pristojba': pristojba}

        if st.button("Generiraj Prijedlog"):
            doc = generiraj_zk_prijedlog(sud, pred, prot, {'ko': ko, 'ulozak': ulozak, 'cestica': cestica, 'opis': opis}, {'ugovor': ug, 'tabularna': tab}, troskovi_dict)
            st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
            word = pripremi_za_word(doc)
            st.download_button("Preuzmi", word, "ZK_Prijedlog.doc")

    # C) BRISOVNA TUŽBA
    elif zk_usluga == "Brisovna tužba":
        zastupanje = zaglavlje_sastavljaca()
        sud = st.text_input("Nadležni sud", "OPĆINSKI GRAĐANSKI SUD U ZAGREBU")
        c1, c2 = st.columns(2)
        tuzitelj, _, _ = unos_stranke("TUŽITELJ", "bt_t")
        tuzenik, _, _ = unos_stranke("TUŽENIK", "bt_tu")
        
        c1, c2, c3 = st.columns(3)
        ko = c1.text_input("K.O.")
        ulozak = c2.text_input("Uložak")
        cestica = c3.text_input("Čestica")
        opis = st.text_area("Opis u naravi")
        
        c1, c2 = st.columns(2)
        z_broj = c1.text_input("Z-broj nevaljanog upisa")
        dat_uknj = c2.date_input("Datum nevaljane uknjižbe")
        
        razlog = st.text_area("Razlog nevaljanosti")
        tuzenik_znao = st.radio("Je li tuženik znao?", ["DA (Nesavjestan)", "NE (Pošten)"])
        vps = st.number_input("VPS (Vrijednost)", 10000.0)
        
        st.subheader("Troškovnik")
        sastav = st.number_input("Cijena sastava", 0.0)
        pdv = sastav * 0.25
        pristojba = st.number_input("Pristojba", 0.0)
        troskovi_dict = {'stavka': sastav, 'pdv': pdv, 'pristojba': pristojba}

        if st.button("Generiraj Tužbu"):
            spora_data = {
                'vps': vps, 'z_broj': z_broj, 
                'datum_uknjizbe': dat_uknj.strftime('%d.%m.%Y.'),
                'isprava': "Ugovor/Isprava", 'datum_isprave': "...",
                'razlog_nevaljanosti': razlog, 'tuzenik_znao': "DA" in tuzenik_znao,
                'mjesto': "Zagreb"
            }
            nekretnina = {'ko': ko, 'ulozak': ulozak, 'cestica': cestica, 'opis': opis}
            doc = generiraj_brisovnu_tuzbu(sud, zastupanje, tuzitelj, tuzenik, nekretnina, spora_data, troskovi_dict)
            st.markdown(f"<div class='legal-doc'>{doc}</div>", unsafe_allow_html=True)
            word = pripremi_za_word(doc)
            st.download_button("Preuzmi Tužbu", word, "Brisovna_tuzba.doc")

# --- 6. KAMATE ---
elif "Kamate" in modul:
    st.header("Kalkulator Kamata")
    st.info("Ovaj modul služi samo za izračun, ne generira dokument. Podatke koristite u tužbi/ovrsi.")
    iznos = st.number_input("Glavnica")
    stopa = st.number_input("Stopa (%)", value=12.0)
    d1 = st.date_input("Dospijeće")
    d2 = st.date_input("Obračun")
    
    if st.button("Izračunaj"):
        dana = (d2-d1).days
        if dana > 0:
            kamata = (iznos * stopa * dana)/36500
            st.success(f"Kamata: {kamata:.2f} EUR (za {dana} dana)")
            st.metric("Ukupno dugovanje", f"{iznos + kamata:.2f} EUR")
        else:
            st.error("Datum obračuna mora biti poslije dospijeća.")
