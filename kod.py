import streamlit as st

primary_color = "#00AADB"


st.set_page_config(
    page_title="Total Reach 360°",
    page_icon=":bar_chart:",
    layout="wide",
)

st.markdown(f"""<style> .reportview-container {{ background-color: {primary_color}; }} </style>""", unsafe_allow_html=True)



import pandas as pd

pd.set_option('display.float_format', '{:.0f}'.format)

df = pd.read_excel('TBR_9m.xlsx')
tematyka = pd.read_excel('kat.xlsx')

tematyka_lista = tematyka['kat'].unique()
wskaźniki_lista = ['Druk+e-wydania', 'www PC', 'www Mobile', 'www', 'Total Reach 360°']
miesiące_lista = [1, 2, 3, 4, 5, 6, 7, 8, 9]

strony = pd.read_excel('strony.xlsx')
tematyka_legenda_dict = dict(zip(strony['Pismo'], strony['Strona']))
wydawca_legenda_dict = dict(zip(tematyka['tytuł'], tematyka['wydawca']))

st.markdown("<h1 style='margin-top: -80px; text-align: center;'>Total Reach 360°</h1>", unsafe_allow_html=True)

selected_kwartaly = st.multiselect(
    "Wybierz kwartały:",
    ["I kwartał 2023", "II kwartał 2023", "III kwartał 2023"],
    default=["I kwartał 2023", "II kwartał 2023", "III kwartał 2023"]
)

# Mapowanie wybranych kwartałów na odpowiadające im miesiące
miesiace_mapping = {"I kwartał 2023": [1, 2, 3], "II kwartał 2023": [4, 5, 6], "III kwartał 2023": [7, 8, 9]}
selected_miesiace = [item for kwartal in selected_kwartaly for item in miesiace_mapping[kwartal]]

selected_tematyki = st.multiselect("Określ grupy pism:", tematyka_lista, default=tematyka_lista)

estymacja = st.radio("Określ sposób prezentowania danych:", ['Estymacja na populację', 'Zasięg (%)'], horizontal=True, index = 0)
www_option = st.radio("Określ zakres danych www:", ['www PC oraz www Mobile', 'www'], horizontal=True, index =0 )

show_wspolczytelnictwo = st.checkbox("Pokaż współczytelnictwo", value=False)

wyniki = pd.DataFrame()

for i in selected_tematyki:
    pisma_lista = tematyka[tematyka['kat'] == i]['tytuł'].to_list()
    for j in pisma_lista:
        for k in wskaźniki_lista:
            if k != 'Total Reach 360°':
                wyniki.loc[j, k] = df[(df['tytuł'] == j) & (df['wskaźnik'] == k) & (df['miesiąc'].between(selected_miesiace[0], selected_miesiace[1]))]['wynik'].mean()
            else:
                wyniki.loc[j, k] = max(wyniki.loc[j, 'Druk+e-wydania'], (1 - float(df[(df['tytuł'] == j) & (df['wskaźnik'] == 'współczytelnictwo')]['wynik'])) * wyniki.loc[j, 'Druk+e-wydania'] + wyniki.loc[j, 'www'])

wyniki = wyniki.sort_values('Total Reach 360°', ascending=False)

if estymacja == 'Zasięg (%)':
    wyniki = wyniki / 29545225 * 100
    wyniki = wyniki.round(2)

if show_wspolczytelnictwo:
    wyniki['Współczytelnictwo'] = wyniki['Druk+e-wydania'] + wyniki['www'] - wyniki['Total Reach 360°']

wyniki_sformatowane = wyniki.applymap(lambda x: '{:,.2f}%'.format(x).replace('.', ',') if not pd.isna(x) and estymacja == 'Zasięg (%)' else '{:,.0f}'.format(x).replace(',', ' ') if not pd.isna(x) else x)
wyniki_sformatowane = wyniki_sformatowane.astype('object').fillna('-')
wyniki_sformatowane = wyniki_sformatowane.reset_index()
wyniki_sformatowane.columns = ['Marka prasowa'] + list(wyniki_sformatowane.columns[1:])
wyniki_sformatowane['Wydawca'] = wyniki_sformatowane['Marka prasowa'].map(wydawca_legenda_dict)
new_column_order = ['Marka prasowa', 'Wydawca'] + list(wyniki_sformatowane.columns[1:-1])
wyniki_sformatowane = wyniki_sformatowane[new_column_order]
wyniki_sformatowane.index+=1

if www_option == 'www':
    del wyniki_sformatowane['www PC']
    del wyniki_sformatowane['www Mobile']
else:
    del wyniki_sformatowane['www']
 

wyniki_sformatowane_styled = wyniki_sformatowane.style.set_table_styles([
    {'selector': 'table', 'props': [('text-align', 'center')]},
    {'selector': 'th', 'props': [('text-align', 'center')]},
    {'selector': 'td', 'props': [('text-align', 'center')]},
    {'selector': 'th.col0, td.col0', 'props': [('text-align', 'left')]}  # Wyrównaj pierwszą kolumnę do lewej
]).set_properties(
    subset=['Total Reach 360°'], 
    **{'font-weight': 'bold'}
)


# Przekształć stylizowaną ramkę danych do formatu HTML
html_table = wyniki_sformatowane_styled.to_html()


# Dodaj styl CSS, aby umieścić tabelę na środku
html_table = f"<div style='margin: auto;'>{html_table}</div>"

# Wyświetl tabelę
st.markdown(html_table, unsafe_allow_html=True)



tekst = 'Badane marki:'
for pismo in wyniki.index.unique():
    try:
        tekst = f'{tekst} {pismo} : {tematyka_legenda_dict[pismo]},'
    except:
        pass

st.markdown("""<div style="font-size:12px">Statystyki: Zasięg CCS i estymacja na populację, populacja 29 545 225</div>""", unsafe_allow_html=True)

if estymacja == 'Zasieg':
    st.markdown("""<div style="font-size:12px; margin-left: 2px">Zasięg (w %)</div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div style="font-size:12px; margin-left: 2px">Estymacja na populację</div>""", unsafe_allow_html=True)

st.markdown("""<div style="font-size:12px">Fale:</div>""", unsafe_allow_html=True)


st.markdown(f"""<div style="font-size:12px; margin-left: 2px">{min(selected_miesiace)}-{max(selected_miesiace)}/2023:</div>""", unsafe_allow_html=True)


st.markdown("""<div style="font-size:12px">Dane CCS: Druk+e-wydania –  Badanie PBC „Zanagażowanie w reklamę” , www, www PC, www mobile – PBI/Gemius/</div>""", unsafe_allow_html=True)
            
st.markdown(f"""<div style="font-size:12px">{tekst}</div>""", unsafe_allow_html=True)

przyp = "PRZYPOMINAMY UŻYTKOWNIKOM, ŻE ZGODNIE Z ZALECENIAMI PBC NIE NALEŻY POSŁUGIWAĆ SIĘ WYNIKAMI TEGO BADANIA BEZ ZACHOWANIA REGUŁ WNIOSKOWANIA STATYSTYCZNEGO. SZCZEGÓLNIE POWAŻNY BŁĄD MOŻE ZOSTAĆ POPEŁNIONY W PRZYPADKU, KIEDY NIEISTOTNA STATYSTYCZNIE RÓŻNICA MIĘDZY DWOMA WSKAŹNIKAMI CZYTELNICTWA JEST INTERPRETOWANA JAKO RÓŻNICA W POZIOMIE CZYTELNICTWA MIMO, IŻ MIEŚCI SIĘ ONA W GRANICACH BŁĘDU NA POZIOMIE UFNOŚCI 95%."


st.markdown(f"""<div style="font-size:12px; margin-top: 2px; margin-bottom: 0px">{przyp}</div>""", unsafe_allow_html=True)

st.markdown("""<div style="font-size:12px">Definicje: www.pbc.pl/wskazniki/</div>""", unsafe_allow_html=True)
