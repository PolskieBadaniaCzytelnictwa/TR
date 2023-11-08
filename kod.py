import streamlit as st

primary_color = "#00AADB"


st.set_page_config(
    page_title="Total Reach 360°",
    page_icon=":bar_chart:",
    layout="wide",
)




import pandas as pd

pd.set_option('display.float_format', '{:.0f}'.format)

df = pd.read_excel('TBR_9m.xlsx')
tematyka = pd.read_excel('kat.xlsx')

tematyka_lista = tematyka['kat'].unique()
wskaźniki_lista = ['Druk i E-wydania', 'www PC', 'www Mobile', 'www', 'Total Reach 360°']
miesiące_lista = [1, 2, 3, 4, 5, 6, 7, 8, 9]

strony = pd.read_excel('strony.xlsx')
tematyka_legenda_dict = dict(zip(strony['Pismo'], strony['Strona']))
wydawca_legenda_dict = dict(zip(tematyka['tytuł'], tematyka['wydawca']))

st.markdown("<h1 style='margin-top: -80px; text-align: center;'>Total Reach 360°</h1>", unsafe_allow_html=True)

selected_miesiace = [1,2,3,4,5,6,7,8,9]

selected_tematyki = st.multiselect("Określ grupy pism:", tematyka_lista, default=tematyka_lista)

estymacja = st.radio("Określ sposób prezentowania danych:", ['Estymacja na populację', 'Zasięg (%)'], horizontal=True, index = 0)
www_option = st.radio("Określ zakres danych www:", ['Total Reach 360° (Druk i E-Wydania, www PC oraz www Mobile)', 'Total Reach 360° (Druk i E-Wydania, www)',
                                                    'Druk i E-wydania', 'www', 'www PC', 'www Mobile'], horizontal=True, index =0)

if www_option == 'Total Reach 360° (Druk i E-Wydania, www PC oraz www Mobile)' or www_option == 'Total Reach 360° (Druk i E-Wydania, www)': 
    show_wspolczytelnictwo = st.checkbox("Pokaż współczytelnictwo", value=False)
else:
    show_wspolczytelnictwo = False

wyniki = pd.DataFrame()

for i in selected_tematyki:
    pisma_lista = tematyka[tematyka['kat'] == i]['tytuł'].to_list()
    for j in pisma_lista:
        for k in wskaźniki_lista:
            if k != 'Total Reach 360°':
                wyniki.loc[j, k] = df[(df['tytuł'] == j) & (df['wskaźnik'] == k) & (df['miesiąc'].between(selected_miesiace[0], selected_miesiace[-1]))]['wynik'].mean()
            else:
                wyniki.loc[j, k] = max(wyniki.loc[j, 'Druk i E-wydania'], (1 - float(df[(df['tytuł'] == j) & (df['wskaźnik'] == 'współczytelnictwo')]['wynik'])) * wyniki.loc[j, 'Druk i E-wydania'] + wyniki.loc[j, 'www'])

if www_option == 'Druk i E-wydania':
    wyniki = wyniki.sort_values('Druk i E-wydania', ascending=False)
elif www_option == 'www':
    wyniki = wyniki.sort_values('www', ascending=False)
elif www_option == 'www PC':
    wyniki = wyniki.sort_values('www PC', ascending=False)
elif www_option == 'www Mobile':
    wyniki = wyniki.sort_values('www Mobile', ascending=False)
else:
    wyniki = wyniki.sort_values('Total Reach 360°', ascending=False)


if estymacja == 'Zasięg (%)':
    wyniki = wyniki / 29545225 * 100
    wyniki = wyniki.round(2)

if show_wspolczytelnictwo:
    wyniki['Współczytelnictwo'] = wyniki['Druk i E-wydania'] + wyniki['www'] - wyniki['Total Reach 360°']

wyniki_sformatowane = wyniki.applymap(lambda x: '{:,.2f}%'.format(x).replace('.', ',') if not pd.isna(x) and estymacja == 'Zasięg (%)' else '{:,.0f}'.format(x).replace(',', ' ') if not pd.isna(x) else x)

if www_option ==  'Total Reach 360° (Druk i E-Wydania, www)' or www_option == 'Total Reach 360° (Druk i E-Wydania, www PC oraz www Mobile)':
    wyniki_sformatowane = wyniki_sformatowane.astype('object').fillna('-')
elif www_option ==  'www':
    wyniki_sformatowane.dropna(subset = ['www'], inplace=True)
elif www_option ==  'www PC':
    wyniki_sformatowane.dropna(subset = ['www PC'], inplace=True)
elif www_option ==  'www Mobile':
    wyniki_sformatowane.dropna(subset = ['www Mobile'], inplace=True)


wyniki_sformatowane = wyniki_sformatowane.reset_index()
wyniki_sformatowane.columns = ['Marka prasowa'] + list(wyniki_sformatowane.columns[1:])
wyniki_sformatowane['Wydawca'] = wyniki_sformatowane['Marka prasowa'].map(wydawca_legenda_dict)
new_column_order = ['Marka prasowa', 'Wydawca'] + list(wyniki_sformatowane.columns[1:-1])
wyniki_sformatowane = wyniki_sformatowane[new_column_order]
wyniki_sformatowane.index+=1

if www_option ==  'Total Reach 360° (Druk i E-Wydania, www)':
    del wyniki_sformatowane['www PC']
    del wyniki_sformatowane['www Mobile']
elif www_option == 'Total Reach 360° (Druk i E-Wydania, www PC oraz www Mobile)':
    del wyniki_sformatowane['www']
else:
    del wyniki_sformatowane['Total Reach 360°']
    if www_option ==  'Druk i E-wydania':
        del wyniki_sformatowane['www PC']
        del wyniki_sformatowane['www Mobile']
        del wyniki_sformatowane['www']
    elif www_option ==  'www':
        del wyniki_sformatowane['www PC']
        del wyniki_sformatowane['www Mobile']
        del wyniki_sformatowane['Druk i E-wydania']
    elif www_option ==  'www PC':
        del wyniki_sformatowane['www']
        del wyniki_sformatowane['www Mobile']
        del wyniki_sformatowane['Druk i E-wydania']
    elif www_option ==  'www Mobile':
        del wyniki_sformatowane['www PC']
        del wyniki_sformatowane['www']
        del wyniki_sformatowane['Druk i E-wydania']

del wyniki_sformatowane['Wydawca']

if 'Total Reach 360°' in wyniki_sformatowane.columns :
    wyniki_sformatowane_styled = wyniki_sformatowane.style.set_table_styles([
    {'selector': 'table', 'props': [('text-align', 'center')]},
    {'selector': 'th', 'props': [('text-align', 'center')]},
    {'selector': 'td', 'props': [('text-align', 'center')]},
    {'selector': 'th.col0, td.col0', 'props': [('text-align', 'left')]}  # Wyrównaj pierwszą kolumnę do lewej
]).set_properties(
    subset=['Total Reach 360°'], 
    **{'font-weight': 'bold'})

else:
    wyniki_sformatowane_styled = wyniki_sformatowane.style.set_table_styles([
    {'selector': 'table', 'props': [('text-align', 'center')]},
    {'selector': 'th', 'props': [('text-align', 'center')]},
    {'selector': 'td', 'props': [('text-align', 'center')]},
    {'selector': 'th.col0, td.col0', 'props': [('text-align', 'left')]}  # Wyrównaj pierwszą kolumnę do lewej
])


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

st.markdown("""<div style="font-size:12px">Statystyki: Zasięg CCS i Estymacja na populację, populacja 29 545 225</div>""", unsafe_allow_html=True)



st.markdown("""<div style="font-size:12px">Fale: 1-9/2023</div>""", unsafe_allow_html=True)




st.markdown("""<div style="font-size:12px">Dane CCS: Druk, E-wydania, Współczytelnictwo –  Badanie PBC „Zanagażowanie w reklamę” , www, www PC, www mobile – PBI/Gemius</div>""", unsafe_allow_html=True)
            
st.markdown(f"""<div style="font-size:12px">{tekst}</div>""", unsafe_allow_html=True)

st.markdown("""<div style="font-size:12px">Definicje: www.pbc.pl/wskazniki/</div>""", unsafe_allow_html=True)
