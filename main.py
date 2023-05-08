import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import folium
import streamlit_folium
from folium.features import CustomIcon, DivIcon

def importar_coordenadas(file):
    df = pd.read_excel(file)
    return df

def crear_mapa(latitud_inicial, longitud_inicial, zoom, width, height):
    mapa = folium.Map(location=[latitud_inicial, longitud_inicial], zoom_start=zoom, width=width, height=height, max_zoom=50, tiles='CartoDB Positron')
    return mapa

def ajustar_tamaño_numero_poste(tamaño_fuente):
    return f'<div style="font-size: {tamaño_fuente}pt; font-weight: bold;">'

def st_folium(m, width=1500, height=1200):
    streamlit_folium.folium_static(m, width=width, height=height)


def marcar_postes(mapa, df, icono_url, icon_size, tamaño_fuente):
    for index, row in df.iterrows():
        latitud = row['Latitud']
        longitud = row['Longitud']
        numero_poste = row['Numero']

        if pd.isna(latitud) or pd.isna(longitud) or pd.isna(numero_poste):
            continue

        icono_personalizado = folium.CustomIcon(
            icon_image=icono_url,
            icon_size=icon_size
        )

        folium.Marker(
            location=[latitud, longitud],
            icon=icono_personalizado
        ).add_to(mapa)

        folium.Marker(
            location=[latitud, longitud],
            icon=DivIcon(
                icon_size=(150, 36),
                icon_anchor=(icon_size[0] // 2, -10),
                html=ajustar_tamaño_numero_poste(tamaño_fuente) + f'{numero_poste}</div>',
            ),
        ).add_to(mapa)

def main():
    st.title('Americasolar Herramienta de Mapa para Postes')

    archivo_cargado = st.file_uploader("Cargar archivo de Excel con coordenadas de postes:", type=['xlsx'])

    if archivo_cargado:
        df = importar_coordenadas(archivo_cargado)

        if not df.empty:
            latitud_inicial = df['Latitud'].mean()
            longitud_inicial = df['Longitud'].mean()
            zoom = 15
            
            mapa_modes = ('Normal', 'Wide')
            mapa_mode = st.selectbox("Selecciona el modo de visualización del mapa:", mapa_modes)

            width = '50%'
            height = 600

            if mapa_mode == "Wide":
                width = '100%'
                height = '100%'

            mapa = crear_mapa(latitud_inicial, longitud_inicial, zoom, width, height)


            icono_url = st.text_input('Link del icono:', 'https://cdn-icons-png.flaticon.com/512/89/89069.png')
            icono_ancho = st.slider('Ancho del icono (px):', min_value=5, max_value=50, value=20)
            icono_alto = st.slider('Alto del icono (px):', min_value=5, max_value=50, value=20)
            tamaño_fuente = st.slider('Tamaño del número de poste (pt):', min_value=1, max_value=24, value=10)

            marcar_postes(mapa, df, icono_url, (icono_ancho, icono_alto), tamaño_fuente)

            st.markdown('Haga clic en el mapa para agregar marcadores:')
            st_folium(mapa)
            
            indice = st.number_input('Ingrese el numero del poste para editar las coordenadas:', min_value=0, value=0)
            if 0 <= indice < len(df):
                latitud_edit = st.number_input('Nueva latitud:', value=df.at[indice, 'Latitud'], step=1e-8, format="%.8f")
                longitud_edit = st.number_input('Nueva longitud:', value=df.at[indice, 'Longitud'], step=1e-8, format="%.8f")
                if st.button('Actualizar coordenadas'):
                    df.at[indice, 'Latitud'] = latitud_edit
                    df.at[indice, 'Longitud'] = longitud_edit
                    mapa = crear_mapa(latitud_inicial, longitud_inicial, zoom)
                    marcar_postes(mapa, df, icono_url, (icono_ancho, icono_alto))
                    streamlit_folium.folium_static(mapa)
        else:
            st.error('El archivo no contiene datos.')
    else:
        st.warning('Por favor, cargue un archivo de Excel.')


if __name__ == "__main__":
    main()