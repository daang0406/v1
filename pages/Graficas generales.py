import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.graph_objects as go 
import plotly.express as px

st.title('Graficas generales')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
icono = Image.open("KIW_icono.ico")
st.set_page_config(page_title="Graficas generales", page_icon=icono, layout="wide", )

# drive
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credenciales = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
cliente = gspread.authorize(credenciales)
sheet = cliente.open("Base de datos").sheet1
# ---------------------------------------------------------------------------------------------------

datos= sheet.get_all_records()
df = pd.DataFrame(datos)

mon = df['Mon.']
filas_a_eliminar = df[df['Mon.'].isin(['Total PEN', 'Total USD','Total EUR', 'Total general'])].index
df_sin_totales = df.drop(filas_a_eliminar)

proveedor= df_sin_totales['Nombre del Proveedor']
importe= df_sin_totales['Total general']
fecha= df_sin_totales['Fecha']
mon = df_sin_totales['Mon.']
mon2 = list(set(mon))

df_sin_totales['Fecha'] = pd.to_datetime(df_sin_totales['Fecha'])

col1, col2 = st.columns((2))

with col1:
    inicio= st.date_input('Fecha de inicio',format="DD/MM/YYYY")

with col2:
    final= st.date_input('Fecha final', format="DD/MM/YYYY")

inicio = pd.to_datetime(inicio)
final = pd.to_datetime(final)

filtro_fechas = (df_sin_totales['Fecha'] >= inicio) & (df_sin_totales['Fecha'] <= final)

df_filtrado = df_sin_totales[(df_sin_totales['Fecha'] >= inicio) & (df_sin_totales['Fecha'] <= final)]

moneda_general = st.multiselect("Escoge la moneda:", mon2, key='moneda_general')
grafica_general = st.multiselect("Escoge el tipo de gráfica:",['PIE', 'linea de tendencia', 'Barras'],key='grafica_general')

if 'PEN' in moneda_general:
    mon_soles= df_filtrado[df_filtrado["Mon."] == "PEN"]["Mon."].tolist()
    importe_soles_general= df_filtrado[df_filtrado["Mon."] == "PEN"]["Total general"].tolist()   
    proveedor_general= df_filtrado[df_filtrado["Mon."] == "PEN"]["Nombre del Proveedor"].tolist()   
    if 'linea de tendencia' in grafica_general:
            fig = px.line(y=importe_soles_general, x=proveedor_general,
                            title='Distribución de saldo en soles por Banco'
                            , markers=True)
            fig.update_traces(marker_color='red')
            fig.update_layout(
                                    xaxis_title='Proveedor',
                                    yaxis_title='Monto',
                                    barmode='group'  # Agrupa las barras
                                )
            st.plotly_chart(fig, use_container_width=True)
    if 'Barras' in grafica_general:
                                
                                fig = px.bar(y=importe_soles_general, x=proveedor_general,
                                                title='Distribución de saldo en soles por Banco', )
                                fig.update_traces(marker_color='red')
                                fig.update_layout(
                                    xaxis_title='Proveedor',
                                    yaxis_title='Monto',
                                    barmode='group'  # Agrupa las barras
                                )
                                st.plotly_chart(fig, use_container_width=True)
    else:
         st.warning('No se ha seleccionado')
