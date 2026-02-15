import streamlit as st
from datetime import date

# -----------------------------------------------------------------------------
# 1. KONFIGURACIJA I CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="LegalTech Suite v15.0 (Radno Pravo)", page_icon="⚖️", layout="wide")

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
    
    /* Isticanje klauzule */
    .clausula {
        font-weight: bold;
        font-style: italic;
        background-color: #f9f9f9;
        padding: 10px;
        border-left: 3px solid #333;
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
    # Vraća tuple (html_tekst, tip_osobe, ima_oib_bool)
    tip = st.radio(f"Tip osobe ({oznaka})", ["Fizička osoba", "Pravna osoba"], key=f"{key_prefix}_tip", horizontal=True, label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    has_valid_data = False
    
    if tip == "Fizička osoba":
        ime = col1.text_input(f"Ime i Prezime", key=f"{key_prefix}_ime")
        oib = col2.text_input(f"OIB", max_chars=11, key=f"{key_prefix}_oib")
        adresa = st.text_input(f"Adresa (Ulica, Grad)", key=f"{key_prefix}_adresa")
        
        if ime and oib and adresa:
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
# 3. GENERATORI DOKUMENATA (RADNO PRAVO - NOVO!)
# -----------------------------------------------------------------------------

def generiraj_ugovor_o_radu(poslodavac, radnik, podaci):
    datum = date.today().strftime("%d.%m.%Y.")
    
    vrsta_tekst = "NA NEODREĐENO VRIJEME"
    clanak_trajanje = "Ugovor se sklapa na neodređeno vrijeme."
    
    if podaci['vrsta'] == "Određeno":
        vrsta_tekst = "NA ODREĐENO VRIJEME"
        datum_do_str = podaci['datum_do'].strftime("%d.%m.%Y.")
        clanak_trajanje = f"Ugovor se sklapa na određeno vrijeme do <b>{datum_do_str}</b>, zbog: {podaci['razlog_odredeno']}."

    probni_rad_txt = ""
    if podaci['probni_rad']:
        probni_rad_txt = f"<br>Ugovara se probni rad u trajanju od {podaci['probni_rad_mj']} mjeseci. Za vrijeme probnog rada otkazni rok je 7 dana."

    datum_start_str = podaci['datum_start'].strftime("%d.%m.%Y.")

    return f"""
    <div class='header-doc'>UGOVOR O RADU<br><span style='font-size: 12pt; font-weight: normal;'>{vrsta_tekst}</span></div>

    <div class='doc-body'>
    Sklopljen u {podaci['mjesto_sklapanja']}, dana {datum} godine, između:
    </div>

    <div class='party-info'>
    1. <b>POSLODAVAC:</b><br>{poslodavac}
    <br><br>
    2. <b>RADNIK:</b><br>{radnik}
    </div>

    <div class='section-title'>Članak 1. (Početak i trajanje rada)</div>
    <div class='doc-body'>
    Radnik počinje s radom dana <b>{datum_start_str}</b>.
    <br>
    {clanak_trajanje}
    {probni_rad_txt}
    </div>

    <div class='section-title'>Članak 2. (Mjesto i vrsta rada)</div>
    <div class='doc-body'>
    Radnik će obavljati poslove radnog mjesta: <b>{podaci['naziv_radnog_mjesta']}</b>.
    <br>
    Opis poslova: {format_text(podaci['opis_posla'])}
    <br>
    Mjesto rada je: {podaci['mjesto_rada']}.
    </div>

    <div class='section-title'>Članak 3. (Radno vrijeme)</div>
    <div class='doc-body'>
    Radno vrijeme određuje se kao {podaci['radno_vrijeme']} sati tjedno (puno/nepuno radno vrijeme).
    Raspored radnog vremena utvrđuje se odlukom poslodavca ili rasporedom rada.
    </div>

    <div class='section-title'>Članak 4. (Plaća)</div>
    <div class='doc-body'>
    Za obavljeni rad Poslodavac će Radniku isplaćivati osnovnu bruto plaću u iznosu od <b>{podaci['bruto_placa']:.2f} EUR</b> mjesečno.
    Plaća se isplaćuje do 15. u mjesecu za prethodni mjesec.
    </div>

    <div class='section-title'>Članak 5. (Godišnji odmor)</div>
    <div class='doc-body'>
    Radnik ima pravo na godišnji odmor u trajanju od najmanje {podaci['godisnji_odmor']} radnih dana (zakonski minimum: 4 tjedna), sukladno Zakonu o radu.
    </div>

    <div class='section-title'>Članak 6. (Otkazni rok)</div>
    <div class='doc-body'>
    U slučaju redovitog otkaza ugovora o radu, primjenjuju se otkazni rokovi utvrđeni Zakonom o radu.
    </div>

    <br><br>
    <table width="100%" border="0">
        <tr>
            <td width="50%" align="center" valign="top">
                <b>POSLODAVAC</b><br><br><br>______________________
            </td>
            <td width="50%" align="center" valign="top">
                <b>RADNIK</b><br><br><br>______________________
            </td>
        </tr>
    </table>
    """

def generiraj_otkaz(poslodavac, radnik, podaci):
    datum = date.today().strftime("%d.%m.%Y.")
    
    naslov = "ODLUKA O OTKAZU UGOVORA O RADU"
    podnaslov = ""
    pravna_osnova = ""
    obrazlozenje_uvod = ""
    
    if podaci['vrsta_otkaza'] == "Redoviti (Poslovno uvjetovani)":
        podnaslov = "(Poslovno uvjetovani otkaz)"
        pravna_osnova = "Temeljem članka 115. stavka 1. podstavka 1. Zakona o radu,"
        obrazlozenje_uvod = "Zbog gospodarskih, tehnoloških i organizacijskih razloga prestala je potreba za obavljanjem poslova koje obavlja radnik."
        
    elif podaci['vrsta_otkaza'] == "Redoviti (Osobno uvjetovani)":
        podnaslov = "(Osobno uvjetovani otkaz)"
        pravna_osnova = "Temeljem članka 115. stavka 1. podstavka 2. Zakona o radu,"
        obrazlozenje_uvod = "Radnik nije u mogućnosti uredno izvršavati svoje obveze iz radnog odnosa zbog određenih trajnih osobina ili sposobnosti."

    elif podaci['vrsta_otkaza'] == "Redoviti (Skrivljeno ponašanje)":
        podnaslov = "(Otkaz uvjetovan skrivljenim ponašanjem)"
        pravna_osnova = "Temeljem članka 115. stavka 1. podstavka 3. Zakona o radu,"
        obrazlozenje_uvod = "Radnik je prekršio obveze iz radnog odnosa."
        
        if podaci.get('prethodna_opomena'):
            datum_op_str = podaci['datum_opomene'].strftime("%d.%m.%Y.")
            obrazlozenje_uvod += f"<br>Radnik je prethodno pismeno upozoren na kršenje obveza dana {datum_op_str}, ali je nastavio s kršenjem."
        else:
            obrazlozenje_uvod += "<br>Poslodavac nije bio dužan prethodno upozoriti radnika zbog okolnosti slučaja."

    elif podaci['vrsta_otkaza'] == "Izvanredni otkaz":
        naslov = "ODLUKA O IZVANREDNOM OTKAZU"
        pravna_osnova = "Temeljem članka 116. Zakona o radu,"
        obrazlozenje_uvod = "Zbog osobito teške povrede obveze iz radnog odnosa, nastavak radnog odnosa nije moguć niti do isteka otkaznog roka."

    if podaci['vrsta_otkaza'] == "Izvanredni otkaz":
        clanak_rok = "Radni odnos prestaje danom dostave ove Odluke radniku, <b>bez obveze poštivanja otkaznog roka</b>."
    else:
        clanak_rok = f"Radni odnos prestaje istekom otkaznog roka u trajanju od <b>{podaci['otkazni_rok']}</b> (sukladno ZOR-u i stažu radnika), koji počinje teći danom dostave ove Odluke."

    datum_ug_str = podaci['datum_ugovora'].strftime("%d.%m.%Y.")

    return f"""
    <div style="text-align: left; font-weight: bold;">{poslodavac.split(',')[0]}</div>
    <div style="text-align: left;">(Poslodavac)</div>
    <br>
    <div style="text-align: right;">U {podaci['mjesto']}, dana {datum}</div>
    <br><br>
    <div class='header-doc'>{naslov}<br><span style='font-size: 12pt; font-weight: normal;'>{podnaslov}</span></div>

    <div class='doc-body'>
    {pravna_osnova} Poslodavac donosi sljedeću
    </div>

    <div class='section-title' style='text-align:center'>ODLUKU</div>

    <div class='doc-body'>
    1. Radniku <b>{radnik.split(',')[0]}</b> (u daljnjem tekstu: Radnik) otkazuje se Ugovor o radu sklopljen dana {datum_ug_str}.
    <br><br>
    2. {clanak_rok}
    <br><br>
    3. Do isteka otkaznog roka radnik je dužan raditi / oslobođen je obveze rada (prekrižiti nepotrebno).
    </div>

    <div class='section-title'>OBRAZLOŽENJE</div>
    <div class='doc-body'>
    {obrazlozenje_uvod}
    <br><br>
    <b>Činjenice i razlozi:</b>
    <br>
    {format_text(podaci['tekst_obrazlozenja'])}
    </div>

    <div class='section-title'>UPUTA O PRAVNOM LIJEKU</div>
    <div class='doc-body'>
    Protiv ove Odluke radnik može podnijeti Zahtjev za zaštitu prava poslodavcu u roku od 15 dana od dana dostave ove Odluke.
    </div>

    <br><br>
    <table width="100%" border="0">
        <tr>
            <td width="50%" valign="top">
                Dostavljeno radniku dana:<br>__________________
                <br><br>
                Potpis radnika:<br>__________________
            </td>
            <td width="50%" align="center" valign="top">
                <b>POSLODAVAC</b>
                <br><br><br>
                ______________________
            </td>
        </tr>
    </table>
    """

# -----------------------------------------------------------------------------
# 4. OSTALI GENERATORI (STARI)
# -----------------------------------------------------------------------------

def generiraj_ugovor_standard(tip_ugovora, stranka1, stranka2, podaci, opcije):
    datum = date.today().strftime("%d.%m.%Y.")
    
    dodatni_tekst = ""
    if opcije.get('kapara'):
        dodatni_tekst += f"<br><b>Kapara:</b> Ugovorne strane potvrđuju da je Kupac isplatio kaparu u iznosu od {opcije['iznos_kapare']} EUR. U slučaju odustanka Kupca kapara se zadržava."
    
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
    <div class='doc-body'>Sklopljen u {podaci['mjesto']}, dana {datum} godine, između:</div>
    <div class='party-info'>1. <b>{u1}:</b><br>{stranka1}<br><br>2. <b>{u2}:</b><br>{stranka2}</div>
    <div class='section-title'>Članak 1. (Predmet)</div>
    <div class='doc-body'>{format_text(podaci['predmet_clanak'])}</div>
    <div class='section-title'>Članak 2. (Cijena)</div>
    <div class='doc-body'>{format_text(podaci['cijena_clanak'])}{dodatni_tekst}</div>
    <div class='section-title'>Članak 3. (Rokovi)</div>
    <div class='doc-body'>{format_text(podaci['rok_clanak'])}</div>
    {solemnizacija_clanak}
    <div class='section-title'>Završne odredbe</div>
    <div class='doc-body'>Nadležan sud: {podaci['sud']}.</div>
    <br><br>
    <table width="100%" border="0"><tr>
    <td width="50%" align="center"><b>{u1}</b><br><br>_________________</td>
    <td width="50%" align="center"><b>{u2}</b><br><br>_________________</td>
    </tr></table>
    """

def generiraj_tuzbu(sud, zastupanje, tuzitelj, tuzenik, vps, vrsta, data, troskovi, dospijece_kamata):
    datum_dospijeca_str = dospijece_kamata.strftime('%d.%m.%Y.')
    return f"""
    <div style="font-weight: bold; font-size: 14px; text-align: left;">{sud.upper()}</div>
    <div style="font-size: 12px; text-align: left;">{zastupanje}</div>
    <br><div class='party-info'><b>TUŽITELJ:</b><br>{tuzitelj}<br><br><b>TUŽENIK:</b><br>{tuzenik}</div>
    <div class='party-info'><b>Radi:</b> {vrsta}<br><b>VPS: {vps:,.2f} EUR</b></div>
    <br><div class='header-doc'>TUŽBA</div>
    <div class='section-title'>I. ČINJENIČNI NAVODI</div><div class='doc-body'>{format_text(data['cinjenice'])}</div>
    <div class='section-title'>II. DOKAZI</div><div class='doc-body'>{format_text(data['dokazi'])}</div>
    <div class='section-title'>III. TUŽBENI ZAHTJEV</div>
    <div class='doc-body'>Tužitelj predlaže da Sud donese sljedeću</div>
    <div style="text-align: center; font-weight: bold;">PRESUDU</div>
    <div class='doc-body'>1. Nalaže se Tuženiku isplatiti {vps:,.2f} EUR sa zateznim kamatama od {datum_dospijeca_str}.</div>
    <br><br><table width="100%"><tr><td width="50%"></td><td width="50%" align="center"><b>TUŽITELJ</b><br>_________________</td></tr></table>
    """

def generiraj_ovrhu(jb, ovrhovoditelj, ovrsenik, trazbina, isprava, troskovi):
    return f"""
    <div style="font-weight: bold;">JAVNOM BILJEŽNIKU {jb.upper()}</div>
    <br><div class='party-info'><b>OVRHOVODITELJ:</b><br>{ovrhovoditelj}<br><br><b>OVRŠENIK:</b><br>{ovrsenik}</div>
    <div class='header-doc'>PRIJEDLOG ZA OVRHU</div>
    <div class='doc-body'>Temeljem vjerodostojne isprave {isprava} predlaže se donijeti:</div>
    <div class='header-doc' style='border:1px solid black; padding:10px;'>RJEŠENJE O OVRSI</div>
    <div class='doc-body'>Nalaže se Ovršeniku platiti {trazbina['glavnica']:,.2f} EUR s kamatama od {trazbina['dospjece']}.</div>
    <br><br><table width="100%"><tr><td width="50%"></td><td width="50%" align="center"><b>OVRHOVODITELJ</b><br>_________________</td></tr></table>
    """

def generiraj_zalbu(sud1, sud2, broj, razlozi, tekst, troskovi):
    return f"""
    <div style="font-weight: bold;">{sud2.upper()}</div><div>putem {sud1.upper()}</div>
    <div class='header-doc'>ŽALBA</div>
    <div class='doc-body'>Protiv presude {broj} zbog: {razlozi}</div>
    <div class='section-title'>Obrazloženje</div><div class='doc-body'>{format_text(tekst)}</div>
    <br><br><table width="100%"><tr><td width="50%"></td><td width="50%" align="center"><b>ŽALITELJ</b><br>_________________</td></tr></table>
    """

def generiraj_tabularnu(prodavatelj, kupac, ko, cestica, ulozak, opis, datum_ugovora):
    return f"""
    <div class='header-doc'>TABULARNA IZJAVA<br><span style='font-size: 11pt; font-weight: normal;'>(Clausula Intabulandi)</span></div>
    <div class='party-info'><b>PRODAVATELJ:</b><br>{prodavatelj}</div>
    <div class='party-info'><b>KUPAC:</b><br>{kupac}</div>
    <div class='doc-body'>Temeljem Ugovora od {datum_ugovora} za nekretninu u K.O. {ko}, k.č.br {cestica}.</div>
    <div class='doc-body clausula'>Ja, PRODAVATELJ, ovime izričito ovlašćujem KUPCA da zatraži uknjižbu prava vlasništva.</div>
    <br><br><table width="100%"><tr><td width="40%"></td><td width="60%" align="center"><b>PRODAVATELJ</b><br>(Ovjera JB)<br><br>_________________</td></tr></table>
    """

# -----------------------------------------------------------------------------
# 4. GLAVNA APLIKACIJA (GUI)
# -----------------------------------------------------------------------------

st.sidebar.title("NAVIGACIJA")
modul = st.sidebar.radio(
    "ODABERI USLUGU:",
    ["📝 Ugovori i Odluke", "⚖️ Tužbe", "🔨 Ovršni Prijedlog", "📜 Žalbe", "🔐 Tabularna Izjava", "🧮 Kamate"]
)
st.sidebar.info("v15.0: Radno pravo (ZOR).")

# --- 1. UGOVORI I ODLUKE ---
if "Ugovori" in modul:
    st.header("Sastavljanje Ugovora i Odluka")
    
    # Proširena lista dokumenata
    tip_dokumenta = st.selectbox(
        "Odaberite dokument:", 
        [
            "Kupoprodaja", 
            "Najam/Zakup", 
            "Ugovor o djelu (Usluga)", 
            "Zajam",
            "--- RADNO PRAVO ---",
            "Ugovor o radu",
            "Odluka o otkazu"
        ]
    )
    
    if "---" in tip_dokumenta:
        st.stop() # Samo separator

    st.markdown("---")
    
    # === A) LOGIKA ZA STANDARDNE UGOVORE ===
    if tip_dokumenta in ["Kupoprodaja", "Najam/Zakup", "Ugovor o djelu (Usluga)", "Zajam"]:
        col_opt1, col_opt2 = st.columns(2)
        ima_kapara = col_opt1.checkbox("Ugovorena Kapara?")
        ima_solemnizacija = col_opt2.checkbox("Solemnizacija (Ovršnost)?")
        iznos_kapare = 0.0
        if ima_kapara:
            iznos_kapare = st.number_input("Iznos kapare (EUR)", min_value=0.0)
        opcije = {'kapara': ima_kapara, 'iznos_kapare': iznos_kapare, 'solemnizacija': ima_solemnizacija}
        
        c1, c2 = st.columns(2)
        s1_txt, _, _ = unos_stranke("PRVA STRANA", "u1")
        s2_txt, _, _ = unos_stranke("DRUGA STRANA", "u2")
        
        mjesto = st.text_input("Mjesto", value="Zagreb")
        sud = st.text_input("Sud", value="Stvarno nadležni sud u Zagrebu")
        data = {'mjesto': mjesto, 'sud': sud}
        
        # Pojednostavljena polja za standardne ugovore
        if tip_dokumenta == "Kupoprodaja":
            data['predmet_clanak'] = st.text_area("Predmet", placeholder="Opis nekretnine...")
            cijena = st.number_input("Cijena")
            data['cijena_clanak'] = f"Cijena: <b>{cijena} EUR</b>."
            data['rok_clanak'] = "Odmah po isplati."
        elif tip_dokumenta == "Najam/Zakup":
            data['predmet_clanak'] = st.text_input("Prostor")
            cijena = st.number_input("Najamnina")
            data['cijena_clanak'] = f"Mjesečno: <b>{cijena} EUR</b>."
            data['rok_clanak'] = "1 godina."
        elif tip_dokumenta == "Ugovor o djelu (Usluga)":
            data['predmet_clanak'] = st.text_area("Opis posla")
            cijena = st.number_input("Honorar")
            data['cijena_clanak'] = f"Honorar: <b>{cijena} EUR</b>."
            data['rok_clanak'] = "30 dana."
        elif tip_dokumenta == "Zajam":
            data['predmet_clanak'] = "Zajam novca."
            iznos = st.number_input("Iznos")
            data['cijena_clanak'] = f"Glavnica: <b>{iznos} EUR</b>."
            data['rok_clanak'] = f"Do: {st.date_input('Rok')}"

        if st.button("Generiraj Ugovor"):
            doc_html = generiraj_ugovor_standard(tip_dokumenta, s1_txt, s2_txt, data, opcije)
            st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
            word_data = pripremi_za_word(doc_html)
            st.download_button("💾 Preuzmi Word", data=word_data, file_name=f"{tip_dokumenta}.doc", mime="application/msword")

    # === B) LOGIKA ZA UGOVOR O RADU ===
    elif tip_dokumenta == "Ugovor o radu":
        st.info("Sukladno Zakonu o radu (NN 93/14, 127/17, 98/19, 151/22, 64/23)")
        
        # Izbornik za vrstu rada
        vrsta_rada = st.radio("Vrsta ugovora:", ["Neodređeno", "Određeno"], horizontal=True)
        
        col_zor1, col_zor2 = st.columns(2)
        datum_do = None
        razlog_odredeno = ""
        
        if vrsta_rada == "Određeno":
            datum_do = col_zor1.date_input("Vrijedi do:")
            razlog_odredeno = col_zor2.text_input("Razlog (npr. zamjena, povećanje opsega posla)")
        
        probni_rad = st.checkbox("Ugovori probni rad?")
        probni_rad_mj = 0
        if probni_rad:
            probni_rad_mj = st.slider("Trajanje probnog rada (mjeseci)", 1, 6, 3)

        st.markdown("---")
        c1, c2 = st.columns(2)
        poslodavac, _, _ = unos_stranke("POSLODAVAC", "posl")
        radnik, _, _ = unos_stranke("RADNIK", "radn")
        
        st.subheader("Uvjeti rada")
        col_uvjeti1, col_uvjeti2 = st.columns(2)
        naziv_radnog_mjesta = col_uvjeti1.text_input("Naziv radnog mjesta")
        mjesto_rada = col_uvjeti2.text_input("Mjesto rada (Adresa)")
        bruto_placa = col_uvjeti1.number_input("Bruto plaća (EUR)", min_value=0.0)
        radno_vrijeme = col_uvjeti2.number_input("Sati tjedno", value=40)
        godisnji_odmor = col_uvjeti1.number_input("Dana godišnjeg odmora", value=20)
        otkazni_rok = col_uvjeti2.text_input("Minimalni otkazni rok (npr. 15 dana)")
        
        opis_posla = st.text_area("Kratki opis poslova")
        
        podaci_rad = {
            'vrsta': vrsta_rada,
            'datum_do': datum_do,
            'razlog_odredeno': razlog_odredeno,
            'probni_rad': probni_rad,
            'probni_rad_mj': probni_rad_mj,
            'datum_start': st.date_input("Datum početka rada"),
            'mjesto_sklapanja': st.text_input("Mjesto sklapanja", value="Zagreb"),
            'naziv_radnog_mjesta': naziv_radnog_mjesta,
            'mjesto_rada': mjesto_rada,
            'bruto_placa': bruto_placa,
            'radno_vrijeme': radno_vrijeme,
            'godisnji_odmor': godisnji_odmor,
            'otkazni_rok': otkazni_rok,
            'opis_posla': opis_posla
        }

        if st.button("Generiraj Ugovor o Radu"):
            doc_html = generiraj_ugovor_o_radu(poslodavac, radnik, podaci_rad)
            st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
            word_data = pripremi_za_word(doc_html)
            st.download_button("💾 Preuzmi Word", data=word_data, file_name="Ugovor_o_radu.doc", mime="application/msword")

    # === C) LOGIKA ZA OTKAZ ===
    elif tip_dokumenta == "Odluka o otkazu":
        st.error("PAŽNJA: Otkaz mora biti pismeno obrazložen i dostavljen radniku!")
        
        vrsta_otkaza = st.selectbox("Vrsta otkaza:", [
            "Redoviti (Poslovno uvjetovani)",
            "Redoviti (Osobno uvjetovani)",
            "Redoviti (Skrivljeno ponašanje)",
            "Izvanredni otkaz"
        ])
        
        prethodna_opomena = False
        datum_opomene = None
        
        if vrsta_otkaza == "Redoviti (Skrivljeno ponašanje)":
            prethodna_opomena = st.checkbox("Jeste li radniku prethodno dali pismenu opomenu?")
            if prethodna_opomena:
                datum_opomene = st.date_input("Datum prethodne opomene")
            else:
                st.warning("Za otkaz uvjetovan skrivljenim ponašanjem obično je potrebna prethodna opomena, osim ako su okolnosti izuzetno teške.")

        c1, c2 = st.columns(2)
        poslodavac, _, _ = unos_stranke("POSLODAVAC", "posl_otkaz")
        radnik, _, _ = unos_stranke("RADNIK", "radn_otkaz")
        
        st.subheader("Detalji")
        datum_ugovora = st.date_input("Datum ugovora koji se otkazuje")
        tekst_obrazlozenja = st.text_area("Detaljno obrazloženje (Zašto se daje otkaz?)", height=150)
        
        otkazni_rok = "Nema (Izvanredni otkaz)"
        if "Redoviti" in vrsta_otkaza:
            otkazni_rok = st.text_input("Trajanje otkaznog roka (npr. 1 mjesec i 2 tjedna)")
        
        podaci_otkaz = {
            'vrsta_otkaza': vrsta_otkaza,
            'prethodna_opomena': prethodna_opomena,
            'datum_opomene': datum_opomene,
            'mjesto': st.text_input("Mjesto donošenja odluke", value="Zagreb"),
            'datum_ugovora': datum_ugovora,
            'tekst_obrazlozenja': tekst_obrazlozenja,
            'otkazni_rok': otkazni_rok
        }

        if st.button("Generiraj Odluku o Otkazu"):
            doc_html = generiraj_otkaz(poslodavac, radnik, podaci_otkaz)
            st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
            word_data = pripremi_za_word(doc_html)
            st.download_button("💾 Preuzmi Word", data=word_data, file_name="Otkaz.doc", mime="application/msword")

# --- 2. TUŽBE ---
elif "Tužbe" in modul:
    st.header("Tužba sa Troškovnikom")
    # (Ovaj dio ostaje isti kao u v13/v14, skraćen radi preglednosti - kopiraj ga iz v14 ako trebaš puni tekst)
    # ... Ovdje ide kod za tužbe iz prethodne verzije ...
    # Zbog limita znakova, ako trebaš cijeli kod, reci, ali gore je integriran novi dio.
    # Da kod bude potpun, evo copy-paste dijela za tužbe:
    zastupanje = zaglavlje_sastavljaca()
    c1, c2 = st.columns(2)
    tuz_txt, tuz_tip, _ = unos_stranke("TUŽITELJ", "t1")
    tuzen_txt, tuzen_tip, _ = unos_stranke("TUŽENIK", "t2")
    
    suggested_sud = "OPĆINSKI SUD U..."
    if tuz_tip == "Pravna" and tuzen_tip == "Pravna":
        suggested_sud = "TRGOVAČKI SUD U ZAGREBU"
        st.info("💡 Detektirano da su obje stranke pravne osobe -> Predložen Trgovački sud.")
    
    sud = st.text_input("Sud", value=suggested_sud)
    vrsta = st.text_input("Radi", value="Isplate")
    vps = st.number_input("VPS (EUR)", min_value=0.0)
    dospijece_kamata = st.date_input("Datum dospijeća tražbine")
    cinjenice = st.text_area("I. Činjenice")
    dokazi = st.text_area("II. Dokazi")
    
    troskovi = {'sastav': "100.00", 'pdv': "25.00", 'pristojba': "50.00", 'ukupno': "175.00"} # Placeholder
    
    if st.button("Generiraj Tužbu"):
        data = {'cinjenice': cinjenice, 'dokazi': dokazi}
        doc_html = generiraj_tuzbu(sud, zastupanje, tuz_txt, tuzen_txt, vps, vrsta, data, troskovi, dospijece_kamata)
        st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
        word_data = pripremi_za_word(doc_html)
        st.download_button("💾 Preuzmi Word", data=word_data, file_name="Tuzba.doc", mime="application/msword")

# --- 3. OVRHE (Skraćeno - isto kao v14) ---
elif "Ovršni" in modul:
    st.header("Ovršni Prijedlog")
    # ... kod za ovrhe ...
    st.info("Koristi kod iz v14 za ovaj dio, ovdje je samo placeholder da skripta radi.")

# --- 4. ŽALBE (Skraćeno - isto kao v14) ---
elif "Žalbe" in modul:
    st.header("Žalba")
    # ... kod za žalbe ...

# --- 5. TABULARNA (Skraćeno - isto kao v14) ---
elif "Tabularna" in modul:
    st.header("Tabularna Izjava")
    c1, c2 = st.columns(2)
    prod, _, prod_valid = unos_stranke("PRODAVATELJ", "tp")
    kup, _, kup_valid = unos_stranke("KUPAC", "tk")
    col_k1, col_k2 = st.columns(2)
    ko = col_k1.text_input("K.O.")
    cestica = col_k2.text_input("Čestica")
    datum_ug = st.date_input("Datum ugovora")
    
    if st.button("Kreiraj Tabularnu"):
        if prod_valid and kup_valid and ko and cestica:
            doc_html = generiraj_tabularnu(prod, kup, ko, cestica, "", "", datum_ug.strftime('%d.%m.%Y.'))
            st.markdown(f"<div class='legal-doc'>{doc_html}</div>", unsafe_allow_html=True)
            word_data = pripremi_za_word(doc_html)
            st.download_button("💾 Preuzmi Word", data=word_data, file_name="Tabularna.doc", mime="application/msword")
        else:
            st.error("Fale podaci.")


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
