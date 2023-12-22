import streamlit as st
import pandas as pd

primary_color = "#00AADB"

st.set_page_config(
    page_title="Total Reach 360°",
    page_icon=":bar_chart:",
    layout="wide",
)

pd.set_option('display.float_format', '{:.0f}'.format)

df = pd.read_excel('TBR360_g.xlsx')
tematyka = pd.read_excel('kat.xlsx')

tematyka_lista = tematyka['kat'].unique()
wskaźniki_lista = ['Druk i E-wydania', 'www', 'Total Reach 360°']
miesiące_lista = [1, 2, 3, 4, 5, 6, 7, 8, 9]

strony = pd.read_excel('strony.xlsx')
tematyka_legenda_dict = dict(zip(strony['Pismo'], strony['Strona']))
wydawca_legenda_dict = dict(zip(tematyka['tytuł'], tematyka['wydawca']))

st.markdown("<h1 style='margin-top: -80px; text-align: center;'>Total Reach 360°</h1>", unsafe_allow_html=True)

selected_miesiace = [341,342,343,344,345,346,347,348,349]

selected_tematyki = st.multiselect("Określ grupy pism:", tematyka_lista, default=tematyka_lista)
if selected_tematyki == []:
    selected_tematyki = tematyka_lista

estymacja = st.radio("Określ sposób prezentowania danych:", ['Estymacja na populację', 'Zasięg (%)'], horizontal=True, index = 0)
www_option = st.radio("Określ zakres danych www:", [ 'Total Reach 360° (Druk i E-Wydania, www)',
                                                    'Druk i E-wydania', 'www'], horizontal=True, index =0)

def display_image(color):
    image_url = f"https://via.placeholder.com/150/{color[1:]}/000000?text={'Kobieta' if color == '00AADB' else 'Mężczyzna'}"
    st.image(image_url, caption=f"Obrazek - {'Kobieta' if color == '00AADB' else 'Mężczyzna'}", use_column_width=True)

Płeć = st.radio("Wybierz płeć:", ['Wszyscy', 'Kobiety', 'Mężczyźni'], horizontal=True, index =0)

Wiek = st.multiselect("Wybierz grupę wiekową:", ['15-24', '25-34', '35-44', '45-59', '60-75'], default=['15-24', '25-34', '35-44', '45-59', '60-75'])



if www_option == 'Total Reach 360° (Druk i E-Wydania, www)': 
    show_wspolczytelnictwo = st.checkbox("Pokaż współczytelnictwo", value=False)
else:
    show_wspolczytelnictwo = False


wyszukiwarka = st.text_input("Wyszukaj markę prasową:",  "", key="placeholder")


wyniki = pd.DataFrame()

for i in selected_tematyki:
    pisma_lista = tematyka[tematyka['kat'] == i]['tytuł'].to_list()
    for j in pisma_lista:
        for k in wskaźniki_lista:
            if k != 'Total Reach 360°':
                df_g = df.copy()
                if Płeć == 'Kobiety':
                    df_g = df_g[df_g['P']=='K']
                if Płeć == 'Mężczyźni':
                    df_g = df_g[df_g['P']=='M']
                wartosci_numeryczne = {'15-24': 1, '25-34': 2, '35-44': 3, '45-59': 4, '60-75': 5}
                Wiek_num = [wartosci_numeryczne[grupa] for grupa in Wiek]
                df_g = df_g[df_g['W'].isin(Wiek_num)]
               
                
                wyniki.loc[j, k] = df_g[(df_g['tytuł'] == j) & (df_g['WSKAŹNIK'] == k) & (df_g['WAVE'].between(selected_miesiace[0], selected_miesiace[-1]))]['WYNIK'].sum()
            else:
                wyniki.loc[j, k] = max(wyniki.loc[j, 'Druk i E-wydania'], (1 - float(df[(df['tytuł'] == j) & (df['WSKAŹNIK'] == 'współczytelnictwo')]['WYNIK'])) * wyniki.loc[j, 'Druk i E-wydania'] + wyniki.loc[j, 'www'])

wyniki = wyniki[wyniki.index.str.contains(wyszukiwarka, case=False, na=False)]


if www_option == 'Druk i E-wydania':
    wyniki = wyniki.sort_values('Druk i E-wydania', ascending=False)
elif www_option == 'www':
    wyniki = wyniki.sort_values('www', ascending=False)
else:
    wyniki = wyniki.sort_values('Total Reach 360°', ascending=False)

suma = 0 
if (Płeć == 'Kobiety' or Płeć == 'Wszyscy') and 1 in Wiek_num:
    suma += 1812738
if (Płeć == 'Mężczyźni' or Płeć == 'Wszyscy') and 1 in Wiek_num:
    suma += 1893705
if (Płeć == 'Kobiety' or Płeć == 'Wszyscy') and 2 in Wiek_num:
    suma += 2387225
if (Płeć == 'Mężczyźni' or Płeć == 'Wszyscy') and 2 in Wiek_num:
    suma += 2440240
if (Płeć == 'Kobiety' or Płeć == 'Wszyscy') and 3 in Wiek_num:
    suma += 3054633
if (Płeć == 'Mężczyźni' or Płeć == 'Wszyscy') and 3 in Wiek_num:
    suma += 3054845
if (Płeć == 'Kobiety' or Płeć == 'Wszyscy') and 4 in Wiek_num:
    suma += 3762817
if (Płeć == 'Mężczyźni' or Płeć == 'Wszyscy') and 4 in Wiek_num:
    suma += 3596251
if (Płeć == 'Kobiety' or Płeć == 'Wszyscy') and 5 in Wiek_num:
    suma += 4205663
if (Płeć == 'Mężczyźni' or Płeć == 'Wszyscy') and 5 in Wiek_num:
    suma += 3337109

if estymacja == 'Zasięg (%)':
    wyniki = wyniki / suma * 100
    wyniki = wyniki.round(2)

if show_wspolczytelnictwo:
    wyniki['Współczytelnictwo'] = wyniki['Druk i E-wydania'] + wyniki['www'] - wyniki['Total Reach 360°']


wyniki_sformatowane = wyniki.applymap(lambda x: '{:,.2f}%'.format(x).replace('.', ',') if not pd.isna(x) and estymacja == 'Zasięg (%)' else '{:,.0f}'.format(x).replace(',', ' ') if not pd.isna(x) else x)


if www_option ==  'Total Reach 360° (Druk i E-Wydania, www)':
    wyniki_sformatowane = wyniki_sformatowane.astype('object').fillna('-')
elif www_option ==  'www':
    wyniki_sformatowane.dropna(subset = ['www'], inplace=True)


wyniki_sformatowane = wyniki_sformatowane.reset_index()
wyniki_sformatowane.columns = ['Marka prasowa'] + list(wyniki_sformatowane.columns[1:])
wyniki_sformatowane['Wydawca'] = wyniki_sformatowane['Marka prasowa'].map(wydawca_legenda_dict)
new_column_order = ['Marka prasowa', 'Wydawca'] + list(wyniki_sformatowane.columns[1:-1])
#wyniki_sformatowane['Marka prasowa'] = wyniki_sformatowane['Marka prasowa'].apply(lambda x: f"[{x}](https://www.pbc.pl/badany-tytul/{x.lower().replace(' ', '-')}/)")


wyniki_sformatowane = wyniki_sformatowane[new_column_order]
wyniki_sformatowane.index+=1


if www_option !=  'Total Reach 360° (Druk i E-Wydania, www)':
    del wyniki_sformatowane['Total Reach 360°']
    if www_option ==  'Druk i E-wydania':
        del wyniki_sformatowane['www']
    elif www_option ==  'www':
        del wyniki_sformatowane['Druk i E-wydania']
    elif www_option ==  'www PC':
        del wyniki_sformatowane['www']
        del wyniki_sformatowane['Druk i E-wydania']
    elif www_option ==  'www Mobile':
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

def make_clickable(tytul):
    link = f"https://www.pbc.pl/badany-tytul/{tytul.lower().replace(' ', '-')}/"
    return f'<a target="_blank" href="{link}">{tytul}</a>'

wyniki_sformatowane['Marka prasowa'] = wyniki_sformatowane['Marka prasowa'].apply(make_clickable)


html_table = wyniki_sformatowane_styled.to_html(escape=False)


html_table = f"<div style='margin: auto;'>{html_table}</div>"

# Wyświetl tabelę
st.markdown(html_table, unsafe_allow_html=True)


tekst = 'Badane marki:'
for pismo in wyniki.index.unique():
    try:
        tekst = f'{tekst} {pismo} i {tematyka_legenda_dict[pismo]},'
    except:
        pass

st.markdown(f"""<div style="font-size:12px">Statystyki: Zasięg CCS i Estymacja na populację, Populacja w wybranej grupie celowej =  {suma}</div>""", unsafe_allow_html=True)



st.markdown("""<div style="font-size:12px">Fale: 1-9/2023</div>""", unsafe_allow_html=True)




st.markdown("""<div style="font-size:12px">Dane CCS: Druk, E-wydania, Współczytelnictwo –  Badanie PBC „Zanagażowanie w reklamę” , www, www PC, www mobile – PBI/Gemius</div>""", unsafe_allow_html=True)
            
st.markdown(f"""<div style="font-size:12px">{tekst}</div>""", unsafe_allow_html=True)

st.markdown("""<div style="font-size:12px">Definicje: www.pbc.pl/wskazniki/</div>""", unsafe_allow_html=True)
