import streamlit as st
from datetime import date

# -----------------------------------------------------------------------------
# 1. KONFIGURACIJA I CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="LegalTech Suite v13.0 (Trgovački Sud Fix)", page_icon="⚖️", layout="wide")

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
        padding: 50px; 
        color: black;
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

    .section-title {
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
        font-family: 'Times New Roman', serif;
    }
    
    .cost-table {
        margin-top: 20px;
        border-top: 1px solid black;
        padding-top: 10px;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
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

def unos_stranke(oznaka, key_prefix):
    st.markdown(f"**{oznaka}**")
    # Vraća tuple (tekst, tip_osobe)
    tip = st.radio(f"Tip osobe ({oznaka})", ["Fizička osoba", "Pravna osoba"], key=f"{key_prefix}_tip", horizontal=True, label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    if tip == "Fizička osoba":
        ime = col1.text_input(f"Ime i Prezime", key=f"{key_prefix}_ime")
        oib = col2.text_input(f"OIB", max_chars=11, key=f"{key_prefix}_oib")
        adresa = st.text_input(f"Adresa (Ulica, Grad)", key=f"{key_prefix}_adresa")
        if ime and oib and adresa:
            return f"<b>{ime}</b><br>Adresa: {adresa}<br>OIB: {oib}", "Fizička"
        return "____________________ (ime), OIB: ____________________", "Fizička"
    else: 
        tvrtka = col1.text_input(f"Tvrtka", key=f"{key_prefix}_tvrtka")
        oib = col2.text_input(f"OIB", max_chars=11, key=f"{key_prefix}_oib_pravna")
        mbs = col1.text_input(f"MBS", key=f"{key_prefix}_mbs")
        zastupnik = col2.text_input(f"Zastupan po", key=f"{key_prefix}_zastupnik")
        sjediste = st.text_input(f"Sjedište", key=f"{key_prefix}_sjediste")
        if tvrtka and oib:
            return f"<b>{tvrtka}</b><br>Sjedište: {sjediste}<br>OIB: {oib}, MBS: {mbs}<br>Zastupana po: {zastupnik}", "Pravna"
        return "____________________ (tvrtka), OIB: ____________________", "Pravna"

def zaglavlje_sastavljaca():
    with st.expander("ℹ️ PODACI O ZASTUPANJU (Punomoćnik)", expanded=False):
        status = st.radio("Dokument sastavlja:", ["Stranka osobno", "Odvjetnik po punomoći"], horizontal=True)
        if status == "Odvjetnik po punomoći":
            odvjetnik = st.text_input("Podaci o odvjetniku/uredu")
            return f"<br>Zastupan po punomoćniku: {odvjetnik}<br>"
        return ""

# -----------------------------------------------------------------------------
# 3. GENERATORI DOKUMENATA
# -----------------------------------------------------------------------------

def generiraj_ugovor(tip_ugovora, stranka1, stranka2, podaci, opcije):
    datum = date.today().strftime("%d.%m.%Y.")
    
    dodatni_tekst = ""
    if opcije.get('kapara'):
        dodatni_tekst += f"<br><b>Kapara:</b> Ugovorne strane potvrđuju da je Kupac isplatio kaparu u iznosu od {opcije['iznos_kapare']} EUR. U slučaju odustanka Kupca kapara se zadržava, a u slučaju odustanka Prodavatelja vraća se u dvostrukom iznosu.<br>"
    
    solemnizacija_clanak = ""
    if opcije.get('solemnizacija'):
        solemnizacija_clanak = """
        <div class='section-title'>Članak (Solemnizacija)</div>
        <div class='doc-body'>
        Ugovorne strane suglasne su da se ovaj Ugovor solemnizira (potvrdi) kod Javnog bilježnika kako bi stekao svojstvo ovršne isprave.
        </div>
        """

    titles = {
        "Kupoprodaja": ("UGOVOR O KUPOPRODAJI", "PRODAVATELJ", "KUPAC"),
        "Najam/Zakup": ("UGOVOR O NAJMU/ZAKUPU", "NAJMODAVAC/ZAKUPODAVAC", "NAJMOPRIMAC/ZAKUPNIK"),
        "Ugovor o djelu (Usluga)": ("UGOVOR O DJELU", "NARUČITELJ", "IZVOĐAČ"),
        "Zajam": ("UGOVOR O ZAJMU", "ZAJMODAVAC", "ZAJMOPRIMAC")
    }
    naslov, u1, u2 = titles[tip_ugovora]

    return f"""
    <div class='header-doc'>{naslov}</div>

    <div class='doc-body'>
    Sklopljen u {podaci['mjesto']}, dana {datum} godine, između ugovornih strana:
    </div>

    <div class='party-info'>
    1. <b>{u1}:</b><br>{stranka1}
    <br><br>
    2. <b>{u2}:</b><br>{stranka2}
    </div>

    <div class='doc-body'>
    Stranke su suglasno ugovorile sljedeće:
    </div>

    <div class='section-title'>Članak 1. (Predmet)</div>
    <div class='doc-body'>{format_text(podaci['predmet_clanak'])}</div>

    <div class='section-title'>Članak 2. (Cijena i plaćanje)</div>
    <div class='doc-body'>
    {format_text(podaci['cijena_clanak'])}
    {dodatni_tekst}
    </div>

    <div class='section-title'>Članak 3. (Rokovi)</div>
    <div class='doc-body'>{format_text(podaci['rok_clanak'])}</div>

    <div class='section-title'>Članak 4. (Jamstva)</div>
    <div class='doc-body'>
    Stranke jamče da su podaci istiniti. {u1} jamči da je isključivi nositelj prava i da nema tereta.
    </div>
    
    {solemnizacija_clanak}

    <div class='section-title'>Članak 5. (Završne odredbe)</div>
    <div class='doc-body'>
    Izmjene ovog Ugovora valjane su samo u pisanom obliku. Nadležan sud: {podaci['sud']}.
    </div>

    <br><br>
    <table width="100%" border="0">
        <tr>
            <td width="50%" align="center" valign="top">
                <b>{u1}</b><br><br><br>______________________
            </td>
            <td width="50%" align="center" valign="top">
                <b>{u2}</b><br><br><br>______________________
            </td>
        </tr>
    </table>
    """

def generiraj_tuzbu(sud, zastupanje, tuzitelj, tuzenik, vps, vrsta, data, troskovi, dospijece_kamata):
    datum_dospijeca_str = dospijece_kamata.strftime('%d.%m.%Y.')
    
    return f"""
    <div style="font-weight: bold; font-size: 14px; text-align: left;">{sud.upper()}</div>
    <div style="font-size: 12px; text-align: left;">{zastupanje}</div>
    <br>
    
    <div class='party-info'>
    <b>TUŽITELJ:</b><br>{tuzitelj}<br><br>
    <b>TUŽENIK:</b><br>{tuzenik}
    </div>
    
    <div class='party-info'>
    <b>Radi:</b> {vrsta}<br>
    <b>VPS: {vps:,.2f} EUR</b>
    </div>

    <br>
    <div class='header-doc'>TUŽBA</div>

    <div class='section-title'>I. ČINJENIČNI NAVODI</div>
    <div class='doc-body'>
    {format_text(data['cinjenice'])} 
    </div>

    <div class='section-title'>II. DOKAZI</div>
    <div class='doc-body'>
    {format_text(data['dokazi'])}
    </div>

    <div class='section-title'>III. TUŽBENI ZAHTJEV</div>
    <div class='doc-body'>
    Tužitelj predlaže da Sud donese sljedeću
    </div>
    <div style="text-align: center; font-weight: bold; margin: 10px 0;">PRESUDU</div>
    <div class='doc-body'>
    1. Nalaže se Tuženiku da Tužitelju isplati iznos od <b>{vps:,.2f} EUR</b> zajedno sa zakonskom zateznom kamatom koja teče od <b>{datum_dospijeca_str}</b> pa do isplate, po stopi određenoj zakonom.
    <br>
    2. Nalaže se Tuženiku da Tužitelju nadoknadi parnični trošak u roku od 15 dana.
    </div>

    <div class='section-title'>IV. POPIS PRILOGA</div>
    <div class='doc-body'>
    {format_text(data['dokazi'])} (u preslici)
    </div>

    <div class='cost-table'>
    <b>TROŠKOVNIK:</b><br>
    - Sastav tužbe (Tbr. 7.): {troskovi['sastav']} EUR<br>
    - PDV (25%): {troskovi['pdv']} EUR<br>
    - Sudska pristojba na tužbu: {troskovi['pristojba']} EUR<br>
    <b>UKUPNO: {troskovi['ukupno']} EUR</b>
    </div>

    <br><br>
    <table width="100%" border="0">
        <tr>
            <td width="50%"></td>
            <td width="50%" align="center">
                <b>TUŽITELJ</b><br>
                ______________________
            </td>
        </tr>
    </table>
    """

def generiraj_ovrhu(jb, ovrhovoditelj, ovrsenik, trazbina, isprava, troskovi):
    return f"""
    <div style="font-weight: bold; text-align:left;">JAVNOM BILJEŽNIKU {jb.upper()}</div>
    <br>
    
    <div class='party-info'>
    <b>OVRHOVODITELJ:</b><br>{ovrhovoditelj}<br><br>
    <b>OVRŠENIK:</b><br>{ovrsenik}
    </div>

    <div class='party-info'>
    <b>Radi:</b> Ovrhe na temelju vjerodostojne isprave<br>
    <b>Tražbina: {trazbina['glavnica']:,.2f} EUR</b>
    </div>

    <br>
    <div class='header-doc'>PRIJEDLOG ZA OVRHU</div>

    <div class='doc-body'>
    Na temelju vjerodostojne isprave – {isprava}, Ovrhovoditelj predlaže donijeti:
    </div>

    <div class='header-doc' style='margin-top: 20px; border: 1px solid black; padding: 10px;'>RJEŠENJE O OVRSI</div>

    <div class='doc-body'>
    <b>I. NALAŽE SE Ovršeniku</b> da Ovrhovoditelju u roku od 8 dana plati <b>{trazbina['glavnica']:,.2f} EUR</b>, sa zateznim kamatama od {trazbina['dospjece']} do isplate, te troškove postupka.
    <br>
    <b>II. ODREĐUJE SE OVRHA</b> na cjelokupnoj imovini Ovršenika.
    </div>

    <div class='cost-table'>
    <b>SPECIFIKACIJA TROŠKA:</b><br>
    - Javnobilježnička nagrada: {troskovi['jb_nagrada']} EUR<br>
    - Materijalni troškovi JB: {troskovi['jb_trosak']} EUR<br>
    - Sastav prijedloga (Odvjetnik): {troskovi['odvjetnik']} EUR<br>
    - PDV: {troskovi['pdv']} EUR<br>
    <b>UKUPNO: {troskovi['ukupno']} EUR</b>
    </div>

    <br><br>
    <table width="100%" border="0">
        <tr>
            <td width="50%"></td>
            <td width="50%" align="center">
                <b>OVRHOVODITELJ</b><br>______________________
            </td>
        </tr>
    </table>
    """

def generiraj_zalbu(sud1, sud2, broj, razlozi, tekst, troskovi):
    return f"""
    <div style="font-weight: bold; text-align:left;">{sud2.upper()}</div>
    <div style="text-align:left;">putem: {sud1.upper()}</div>
    <br>
    <div class='party-info'>
    <b>Poslovni broj:</b> {broj}
    </div>
    <br>
    <div class='header-doc'>ŽALBA</div>
    <div style="text-align: center;">protiv presude {sud1} posl. br. {broj}</div>
    <br>
    <div class='doc-body'>
    Žalitelj izjavljuje žalbu zbog (čl. 353. ZPP):<br>
    {razlozi}
    </div>

    <div class='section-title'>OBRAZLOŽENJE</div>
    <div class='doc-body'>
    {format_text(tekst)}
    </div>

    <div class='section-title'>PRIJEDLOG</div>
    <div class='doc-body'>
    Predlaže se presudu ukinuti i vratiti na ponovno suđenje ili preinačiti. Traži se trošak žalbe.
    </div>

    <div class='cost-table'>
    <b>TROŠKOVNIK ŽALBE:</b><br>
    - Sastav žalbe (Tbr. 10.): {troskovi['sastav']} EUR<br>
    - PDV: {troskovi['pdv']} EUR<br>
    - Sudska pristojba na žalbu: {troskovi['pristojba']} EUR<br>
    <b>UKUPNO: {troskovi['ukupno']} EUR</b>
    </div>

    <br><br>
    <table width="100%" border="0">
        <tr>
            <td width="50%"></td>
            <td width="50%" align="center">
                <b>ŽALITELJ</b><br>______________________
            </td>
        </tr>
    </table>
    """

def generiraj_tabularnu(prodavatelj, kupac, ko, cestica, ulozak):
    return f"""
    <div class='header-doc'>TABULARNA IZJAVA<br><span style='font-size: 12pt; font-weight: normal;'>(Clausula Intabulandi)</span></div>
    
    <div class='doc-body'>
    Ja, <b>PRODAVATELJ:</b>
    </div>
    
    <div class='party-info'>
    {prodavatelj}
    </div>

    <div class='doc-body'>
    izjavljujem da sam od <b>KUPCA:</b>
    </div>

    <div class='party-info'>
    {kupac}
    </div>

    <div class='doc-body'>
    primio cjelokupnu cijenu te ga ovlašćujem da bez mog daljnjeg pitanja ishodi uknjižbu prava vlasništva na nekretnini:<br>
    <b>K.O. {ko}, čestica {cestica}</b> {f', ZK uložak {ulozak}' if ulozak else ''}.
    </div>
    
    <br><br>
    <table width="100%" border="0">
        <tr>
            <td width="40%"></td>
            <td width="60%" align="center">
                <b>PRODAVATELJ</b><br>(Ovjera potpisa JB)<br><br>______________________
            </td>
        </tr>
    </table>
    """

# -----------------------------------------------------------------------------
# 4. GLAVNA APLIKACIJA (GUI)
# -----------------------------------------------------------------------------

st.sidebar.title("NAVIGACIJA")
modul = st.sidebar.radio(
    "ODABERI USLUGU:",
    ["📝 Ugovori (+Kapara/Solemn.)", "⚖️ Tužbe (+Troškovnik)", "🔨 Ovršni Prijedlog", "📜 Žalbe", "🔐 Tabularna Izjava", "🧮 Kamate"]
)
st.sidebar.info("v13.0: Automatski Trgovački sud.")

# --- 1. UGOVORI ---
if "Ugovori" in modul:
    st.header("Sastavljanje Ugovora (Advanced)")
    tip = st.selectbox("Vrsta:", ["Kupoprodaja", "Najam/Zakup", "Ugovor o djelu (Usluga)", "Zajam"])
    
    st.markdown("---")
    col_opt1, col_opt2 = st.columns(2)
    ima_kapara = col_opt1.checkbox("Ugovorena Kapara?")
    ima_solemnizacija = col_opt2.checkbox("Solemnizacija (Ovršnost)?")
    
    iznos_kapare = 0.0
    if ima_kapara:
        iznos_kapare = st.number_input("Iznos kapare (EUR)", min_value=0.0)
    
    opcije = {'kapara': ima_kapara, 'iznos_kapare': iznos_kapare, 'solemnizacija': ima_solemnizacija}
    st.markdown("---")

    c1, c2 = st.columns(2)
    # Bitno: hvatamo i 'tip_osobe' (drugi dio tuple-a)
    s1_txt, s1_tip = unos_stranke("PRVA STRANA", "u1")
    s2_txt, s2_tip = unos_stranke("DRUGA STRANA", "u2")
    
    mjesto = st.text_input("Mjesto", value="Zagreb")
    sud = st.text_input("Sud", value="Stvarno nadležni sud u Zagrebu")
    data = {'mjesto': mjesto, 'sud': sud}
    
    if tip == "Kupoprodaja":
        predmet = st.text_area("Predmet", placeholder="Nekretnina/Pokretnina...")
        cijena = st.number_input("Cijena (EUR)")
        data['predmet_clanak'] = f"Prodavatelj prodaje: {predmet}"
        data['cijena_clanak'] = f"Cijena: <b>{cijena:,.2f} EUR</b>."
        data['rok_clanak'] = "Posjed odmah po isplati."
    elif tip == "Najam/Zakup":
        predmet = st.text_input("Prostor")
        cijena = st.number_input("Najamnina")
        data['predmet_clanak'] = f"Prostor: {predmet}"
        data['cijena_clanak'] = f"Mjesečno: <b>{cijena:,.2f} EUR</b>."
        data['rok_clanak'] = "1 godina."
    elif tip == "Ugovor o djelu (Usluga)":
        opis = st.text_area("Opis")
        cijena = st.number_input("Honorar")
        data['predmet_clanak'] = f"Posao: {opis}"
        data['cijena_clanak'] = f"Honorar: <b>{cijena:,.2f} EUR</b>."
        data['rok_clanak'] = "30 dana."
    elif tip == "Zajam":
        iznos = st.number_input("Iznos")
        rok = st.date_input("Rok")
        data['predmet_clanak'] = "Zajam novca."
        data['cijena_clanak'] = f"Glavnica: <b>{iznos:,.2f} EUR</b>."
        data['rok_clanak'] = f"Do: {rok}"

    if st.button("Generiraj Ugovor"):
        doc_html = generiraj_ugovor(tip, s1_txt, s2_txt, data, opcije)
        st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
        word_data = pripremi_za_word(doc_html)
        st.download_button("💾 Preuzmi Word", data=word_data, file_name=f"{tip}.doc", mime="application/msword")

# --- 2. TUŽBE ---
elif "Tužbe" in modul:
    st.header("Tužba sa Troškovnikom")
    zastupanje = zaglavlje_sastavljaca()
    c1, c2 = st.columns(2)
    # Hvatamo i tip osobe (Fizička/Pravna)
    tuz_txt, tuz_tip = unos_stranke("TUŽITELJ", "t1")
    tuzen_txt, tuzen_tip = unos_stranke("TUŽENIK", "t2")
    
    # --- AUTOMATSKA DETEKCIJA TRGOVAČKOG SUDA ---
    suggested_sud = "OPĆINSKI SUD U..."
    if tuz_tip == "Pravna" and tuzen_tip == "Pravna":
        suggested_sud = "TRGOVAČKI SUD U ZAGREBU"
        st.info("💡 Detektirano da su obje stranke pravne osobe -> Predložen Trgovački sud.")
    
    sud = st.text_input("Sud", value=suggested_sud)
    vrsta = st.text_input("Radi", value="Isplate")
    vps = st.number_input("VPS (EUR)", min_value=0.0)
    
    st.warning("⚠️ Kamate se računaju od dospijeća, a ne od presude!")
    dospijece_kamata = st.date_input("Datum dospijeća tražbine (npr. dospijeće računa)")

    cinjenice = st.text_area("I. Činjenice (Svaki novi red je Shift+Enter u Wordu)")
    dokazi = st.text_area("II. Dokazi")
    
    st.markdown("---")
    st.subheader("💰 Troškovnik")
    ct1, ct2 = st.columns(2)
    tr_sastav = ct1.number_input("Cijena sastava tužbe (EUR)", value=0.0)
    tr_pdv = ct2.number_input("PDV na odvjetnika", value=0.0)
    tr_pristojba = st.number_input("Sudska pristojba", value=0.0)
    tr_ukupno = tr_sastav + tr_pdv + tr_pristojba
    
    troskovi = {'sastav': f"{tr_sastav:.2f}", 'pdv': f"{tr_pdv:.2f}", 'pristojba': f"{tr_pristojba:.2f}", 'ukupno': f"{tr_ukupno:.2f}"}

    if st.button("Generiraj Tužbu"):
        data = {'cinjenice': cinjenice, 'dokazi': dokazi}
        doc_html = generiraj_tuzbu(sud, zastupanje, tuz_txt, tuzen_txt, vps, vrsta, data, troskovi, dospijece_kamata)
        st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
        word_data = pripremi_za_word(doc_html)
        st.download_button("💾 Preuzmi Word", data=word_data, file_name="Tuzba.doc", mime="application/msword")

# --- 3. OVRHE ---
elif "Ovršni" in modul:
    st.header("Ovrha + Troškovnik")
    jb = st.text_input("Javni bilježnik")
    c1, c2 = st.columns(2)
    ov1, _ = unos_stranke("OVRHOVODITELJ", "ov1")
    ov2, _ = unos_stranke("OVRŠENIK", "ov2")
    
    isprava = st.text_input("Vjerodostojna isprava")
    glavnica = st.number_input("Glavnica (EUR)")
    dospijece = st.date_input("Dospijeće")

    st.markdown("---")
    st.subheader("💰 Troškovi postupka")
    co1, co2 = st.columns(2)
    tr_jb_nagrada = co1.number_input("JB Nagrada", value=0.0)
    tr_jb_mat = co2.number_input("JB Materijalni", value=0.0)
    tr_odv = co1.number_input("Odvjetnik", value=0.0)
    tr_pdv = co2.number_input("PDV", value=0.0)
    tr_ukupno = tr_jb_nagrada + tr_jb_mat + tr_odv + tr_pdv

    troskovi = {'jb_nagrada': f"{tr_jb_nagrada:.2f}", 'jb_trosak': f"{tr_jb_mat:.2f}", 'odvjetnik': f"{tr_odv:.2f}", 'pdv': f"{tr_pdv:.2f}", 'ukupno': f"{tr_ukupno:.2f}"}

    if st.button("Kreiraj Ovrhu"):
        trazbina = {'glavnica': glavnica, 'dospjece': dospijece.strftime('%d.%m.%Y.')}
        doc_html = generiraj_ovrhu(jb, ov1, ov2, trazbina, isprava, troskovi)
        st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
        word_data = pripremi_za_word(doc_html)
        st.download_button("💾 Preuzmi Word", data=word_data, file_name="Ovrha.doc", mime="application/msword")

# --- 4. ŽALBE ---
elif "Žalbe" in modul:
    st.header("Žalba + Troškovnik")
    sud1 = st.text_input("Prvostupanjski")
    sud2 = st.text_input("Drugostupanjski")
    broj = st.text_input("Poslovni broj")
    
    razlozi = st.text_area("Razlozi žalbe")
    tekst = st.text_area("Obrazloženje")
    
    st.subheader("💰 Trošak žalbe")
    ct1, ct2 = st.columns(2)
    tr_sastav = ct1.number_input("Sastav žalbe", value=0.0)
    tr_pdv = ct2.number_input("PDV", value=0.0)
    tr_pristojba = st.number_input("Pristojba", value=0.0)
    tr_ukupno = tr_sastav + tr_pdv + tr_pristojba
    
    troskovi = {'sastav': f"{tr_sastav:.2f}", 'pdv': f"{tr_pdv:.2f}", 'pristojba': f"{tr_pristojba:.2f}", 'ukupno': f"{tr_ukupno:.2f}"}

    if st.button("Generiraj Žalbu"):
        doc_html = generiraj_zalbu(sud1, sud2, broj, razlozi, tekst, troskovi)
        st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
        word_data = pripremi_za_word(doc_html)
        st.download_button("💾 Preuzmi Word", data=word_data, file_name="Zalba.doc", mime="application/msword")

# --- 5. TABULARNA ---
elif "Tabularna" in modul:
    st.header("Tabularna Izjava")
    c1, c2 = st.columns(2)
    prod, _ = unos_stranke("PRODAVATELJ", "tp")
    kup, _ = unos_stranke("KUPAC", "tk")
    ko = st.text_input("K.O.")
    cestica = st.text_input("Čestica")
    ulozak = st.text_input("ZK Uložak")

    if st.button("Kreiraj"):
        doc_html = generiraj_tabularnu(prod, kup, ko, cestica, ulozak)
        st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
        word_data = pripremi_za_word(doc_html)
        st.download_button("💾 Preuzmi Word", data=word_data, file_name="Tabularna.doc", mime="application/msword")

# --- 6. KAMATE ---
elif "Kamate" in modul:
    st.header("Kalkulator Kamata")
    iznos = st.number_input("Glavnica")
    stopa = st.number_input("Stopa (%)", value=12.0)
    d1 = st.date_input("Dospijeće")
    d2 = st.date_input("Obračun")
    if st.button("Izračunaj"):
        dana = (d2-d1).days
        if dana > 0:
            kamata = (iznos * stopa * dana)/36500
            st.success(f"Kamata: {kamata:.2f} EUR (za {dana} dana)")
        else:
            st.error("Datum obračuna mora biti poslije dospijeća.")
