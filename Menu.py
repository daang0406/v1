import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.graph_objects as go # para mayor cantidad de graficos saldo vs Egresos
from PIL import Image

icono = Image.open("KIW_icono.ico")
st.set_page_config(page_title="Flujo de caja", page_icon=icono, layout="wide")



# drive
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credenciales = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
cliente = gspread.authorize(credenciales)
#sheet = cliente.open("Base de datos").sheet1
# ---------------------------------------------------------------------------------------------------

st.title(":bar_chart: Flujo de caja")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Fecha actual
fecha_actual = datetime.now().date().strftime('%d/%m/%Y')
hora_actual = datetime.now().time().strftime('%H:%M')

col1, col2 = st.columns((2))

with col1:
        st.header("Subir Saldo de Bancos")
        saldo_file = st.file_uploader("Selecciona un archivo", type=["xlsx", "xls"], key="saldo_file")

        if saldo_file is not None:
                saldo_df = pd.read_excel(saldo_file, engine='openpyxl')
                st.success("Archivo cargado exitosamente.")
                #fila_titulo = saldo_df[saldo_df.apply(lambda row: 'BANCO' in str(row.values), axis=1)].index[0]
                saldo_df = pd.read_excel(saldo_file, engine='openpyxl')
                saldo_df.fillna('', inplace=True)

                edited_saldo = st.data_editor(saldo_df, num_rows="dynamic")

                moneda2 = list(set(saldo_df["Moneda"]))
                moneda2 = [elem for elem in moneda2 if elem != "" or None]

                moneda_soles_saldo = saldo_df[saldo_df["Moneda"] == "Soles"]["Moneda"].tolist()
                importe_soles_saldo = saldo_df[saldo_df["Moneda"] == "Soles"]["Importe Soles"].tolist()

                banco = saldo_df[saldo_df["Moneda"] == "Soles"]["BANCO"].tolist()

                moneda_usd_saldo = saldo_df[saldo_df["Moneda"] == "Usd"]["Moneda"].tolist()
                importe_usd_saldo = saldo_df[saldo_df["Moneda"] == "Usd"]["Importe USD"].tolist()

                banco2 = saldo_df[saldo_df["Moneda"] == "Usd"]["BANCO"].tolist()
                if st.button("subir",key="Boton_ingresos"):
                        sheet=cliente.open("Base de datos").get_worksheet(1)
                        df = saldo_df
                        df['fecha'] = fecha_actual
                        sheet.append_rows(df.values.tolist())
                
                moneda_saldo = st.multiselect("Escoge la moneda:", moneda2, key='moneda_saldo')
                grafica_saldo = st.multiselect("Escoge el tipo de gráfica:",
                                                ['PIE', 'linea de tendencia', 'Barras'],
                                                key='grafica_saldo')

                if 'Soles' in moneda_saldo:
                        if 'PIE' in grafica_saldo:
                                fig = px.pie(values=importe_soles_saldo, names=banco,
                                                title='Distribución de saldo en soles por Banco')
                                st.plotly_chart(fig)
                        if 'linea de tendencia' in grafica_saldo:
                                fig = px.line(y=importe_soles_saldo, x=banco,
                                                title='Distribución de saldo en soles por Banco')
                                st.plotly_chart(fig)
                        if 'Barras' in grafica_saldo:
                                fig = px.bar(y=importe_soles_saldo, x=banco,
                                                title='Distribución de saldo en soles por Banco', )
                                # fig.update_traces(marker_color='red')
                                st.plotly_chart(fig)
                if 'Usd' in moneda_saldo:
                        if 'PIE' in grafica_saldo:
                                fig = px.pie(values=importe_usd_saldo, names=banco2,
                                                title='Distribución de saldo en dolares por Banco')
                                st.plotly_chart(fig)
                        if 'linea de tendencia' in grafica_saldo:
                                fig = px.line(y=importe_usd_saldo, x=banco2,
                                                title='Distribución de saldo en dolares por Banco')
                                st.plotly_chart(fig)
                        if 'Barras' in grafica_saldo:
                                fig = px.bar(y=importe_usd_saldo, x=banco2,
                                                title='Distribución de saldo en dolares por Banco', )
                                # fig.update_traces(marker_color='red')
                                st.plotly_chart(fig) 
                else:
                        st.warning("No se ha seleccionado ningún archivo. ")

        else:
                st.warning("No se ha seleccionado ningún archivo. ")

with col2:
        st.header("Subir Propuesta de Pago")
        pago_file = st.file_uploader("Selecciona un archivo", type=["xlsx", "xls"], key="pago_file")

        if pago_file is not None:
                pago_df = pd.read_excel(pago_file, engine='openpyxl')
                # ------------------------------------------------------
                # Encontrar el índice y las columnas donde comienza y termina la selección
                mon_index = pago_df.index[pago_df['Mon.'] == 'Mon.'].tolist()
                total_general_index = pago_df.index[pago_df['Mon.'] == 'Total general'].tolist()

                if mon_index and total_general_index:
                        start_row = min(mon_index) + 1  # Sumar 1 para ir a la siguiente fila
                        end_row = max(total_general_index)

                        start_col = pago_df.columns.get_loc('Mon.')
                        end_col = pago_df.columns.get_loc(
                                'Total general') + 1  # Sumar 1 para incluir la columna 'Total general'

                        # Seleccionar la parte del DataFrame
                        pago_df = pago_df.iloc[start_row:end_row, start_col:end_col]
                # -----------------------------------------------------
                st.success("Archivo cargado exitosamente.")
                pago_df.fillna('', inplace=True)

                edited_pago = st.data_editor(pago_df, num_rows="dynamic")

                moneda1 = list(set(pago_df["Mon."]))
                moneda1 = [elem for elem in moneda1 if (elem != "" or None) and len(elem) == 3]

                # Importes en distintas divisas

                importe_soles_pago = pago_df['Total general'].tolist()[
                                        :pago_df[pago_df['Mon.'] == 'Total PEN'].index[0]]
                importe_dolares_pago = pago_df['Total general'].tolist()[
                                        pago_df[pago_df['Mon.'] == 'USD'].index[0]:
                                        pago_df[pago_df['Mon.'] == 'Total USD'].index[
                                                0]
                                        ]
                
                # Listas de proveedores cada divisa
                proveedor_soles = pago_df['Nombre del Proveedor'].tolist()[
                                        :pago_df[pago_df['Mon.'] == 'Total PEN'].index[0]]
                proveedor_dolares = pago_df['Nombre del Proveedor'].tolist()[
                                        pago_df[pago_df['Mon.'] == 'USD'].index[0]:
                                        pago_df[pago_df['Mon.'] == 'Total USD'].index[0]
                                        ]
                try:
                    importe_euros_pago = pago_df['Total general'].tolist()[
                        pago_df[pago_df['Mon.'] == 'EUR'].index[0]:
                        pago_df[pago_df['Mon.'] == 'Total EUR'].index[0]
                    ]
                    proveedor_euros = pago_df['Nombre del Proveedor'].tolist()[
                        pago_df[pago_df['Mon.'] == 'EUR'].index[0]:
                        pago_df[pago_df['Mon.'] == 'Total EUR'].index[0]
                    ]
                except IndexError:
                    pass

                if st.button("subir",key="boton_egresos"):
                        df = pago_df
                        df['Mon.'] = df['Mon.'].replace(['', ' '], np.nan)
                        df['Mon.'].fillna(method='ffill', inplace=True)
                        df.dropna(axis=1, how='all', inplace=True)
                        df.drop(df.columns[3], axis=1, inplace=True)
                        df['fecha'] = fecha_actual
                        sheet.append_rows(df.values.tolist())
                else:
                        st.warning("No se esta subiendo ningun archivo ")

                moneda_pago = st.multiselect("Escoge la moneda:", moneda1, key='moneda_pago')
                grafica_pago = st.multiselect("Escoge el tipo de gráfica:",
                                                ['PIE', 'linea de tendencia', 'Barras'],
                                                key='grafica_pago')

                if 'PEN' in moneda_pago:
                        if 'PIE' in grafica_pago:
                                absolutos = []
                                for num in importe_soles_pago:
                                        absolutos.append(num * -1)
                                fig = px.pie(values=absolutos, names=proveedor_soles,
                                                title='Distribución de saldo en soles por Banco')
                                st.plotly_chart(fig)
                        if 'linea de tendencia' in grafica_pago:
                                fig = px.line(y=importe_soles_pago, x=proveedor_soles,
                                                title='Distribución de saldo en soles por Banco'
                                                , markers=True)
                                fig.update_traces(marker_color='red')
                                st.plotly_chart(fig)
                        if 'Barras' in grafica_pago:
                                fig = px.bar(y=importe_soles_pago, x=proveedor_soles,
                                                title='Distribución de saldo en soles por Banco', )
                                fig.update_traces(marker_color='red')
                                st.plotly_chart(fig)

                if 'USD' in moneda_pago:
                        if 'PIE' in grafica_pago:
                                absolutos = []
                                for num in importe_dolares_pago:
                                        absolutos.append(num * -1)
                                fig = px.pie(values=absolutos, names=proveedor_dolares,
                                                title='Distribución de saldo en dolares por Banco')
                                st.plotly_chart(fig)
                        if 'linea de tendencia' in grafica_pago:
                                fig = px.line(y=importe_dolares_pago, x=proveedor_dolares,
                                                title='Distribución de saldo en dolares por Banco'
                                                , markers=True)
                                fig.update_traces(marker_color='red')
                                st.plotly_chart(fig)
                        if 'Barras' in grafica_pago:
                                fig = px.bar(y=importe_dolares_pago, x=proveedor_dolares,
                                                title='Distribución de saldo en dolares por Banco', )
                                fig.update_traces(marker_color='red')
                                st.plotly_chart(fig)

                if 'EUR' in moneda_pago:
                        if 'PIE' in grafica_pago:
                                absolutos = []
                                for num in importe_euros_pago:
                                        absolutos.append(num * -1)
                                fig = px.pie(values=absolutos, names=proveedor_euros,
                                                title='Distribución de saldo en euros por Banco')
                                st.plotly_chart(fig)
                        if 'linea de tendencia' in grafica_pago:
                                fig = px.line(y=importe_euros_pago, x=proveedor_euros,
                                                title='Distribución de saldo en euros por Banco'
                                                , markers=True)
                                fig.update_traces(marker_color='red')
                                # fig.up
                                st.plotly_chart(fig)
                        if 'Barras' in grafica_pago:
                                fig = px.bar(y=importe_euros_pago, x=proveedor_euros,
                                                title='Distribución de saldo en euros por Banco', )
                                fig.update_traces(marker_color='red')
                                st.plotly_chart(fig)
                else:
                        st.warning("No se ha seleccionado ningún archivo. ")

        else:
                st.warning("No se ha seleccionado ningún archivo. Se usará el archivo por defecto.")

# -----------------------------------------------------------------------------------------------------------------
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
st.markdown('<div style="width:100%;font-size: 50px;">Gráfico semanal de liquidez              '
                f'      fecha actual {fecha_actual}</div>', unsafe_allow_html=True)

st.markdown(f'<div style="width:100%;font-size: 30px;">Saldo en el Banco</div>', unsafe_allow_html=True)
monto_en_soles = 14000000  # usare esto para el grafico final luego deberemos actualizarlo con un archivo correcto

if saldo_file is not None and pago_file is not None:
        divisa = st.multiselect("Escoge la moneda:", moneda1, key='divisa_saldo')
        col3, col4 = st.columns((2))
        if 'PEN' in divisa:
                # Saldo en el Banco en soles
                col3.write(f'<div style="width:100%;font-size: 20px;">Calculado: S/.'
                                f' {sum(importe_soles_saldo)}</div>', unsafe_allow_html=True)
                col4.write(f'<div style="width:100%;font-size: 20px;">Obtenido: S/.'
                                f' {sum(importe_soles_saldo)}</div>', unsafe_allow_html=True)

st.markdown(f'<div style="width:100%;font-size: 30px;">Propuesta de Pago</div>', unsafe_allow_html=True)

if saldo_file is not None and pago_file is not None:
        divisa = st.multiselect("Escoge la moneda:", moneda1, key='divisa_pago')
        col5, col6 = st.columns((2))
        if 'PEN' in divisa:
                # valor obtenido en soles del pago total
                obtenido_pago_soles = \
                pago_df['Total general'].tolist()[:pago_df[pago_df['Mon.'] == 'USD'].index[0]][-1]

                # Saldo en el Banco en soles
                col5.write(f'<div style="width:100%;font-size: 20px;">Calculado: S/.'
                                f' {sum(importe_soles_pago)}</div>', unsafe_allow_html=True)
                col6.write(f'<div style="width:100%;font-size: 20px;">Obtenido: S/.'
                                f' {obtenido_pago_soles}</div>', unsafe_allow_html=True)
        if 'USD' in divisa:
                # valor obtenido en soles del pago total
                obtenido_pago_dolares = pago_df['Total general'].tolist()[
                                        pago_df[pago_df['Mon.'] == 'USD'].index[0]:
                                        pago_df[pago_df['Mon.'] == 'EUR'].index[
                                                0]
                                        ][-1]

                # Saldo en el Banco en dolares
                col5.write(f'<div style="width:100%;font-size: 20px;">Calculado: $'
                                f' {sum(importe_dolares_pago)}</div>', unsafe_allow_html=True)
                col6.write(f'<div style="width:100%;font-size: 20px;">Obtenido: $'
                                f' {obtenido_pago_dolares}</div>', unsafe_allow_html=True)
                # pass
        if 'EUR' in divisa:
                # €
                obtenido_pago_euros = pago_df['Total general'].tolist()[
                                        pago_df[pago_df['Mon.'] == 'EUR'].index[0]:
                                        pago_df[pago_df['Mon.'] == 'Total general'].index[
                                                0]][-1]
                # Saldo en el Banco en euros
                col5.write(f'<div style="width:100%;font-size: 20px;">Calculado: €'
                                f' {sum(importe_euros_pago)}</div>', unsafe_allow_html=True)
                col6.write(f'<div style="width:100%;font-size: 20px;">Obtenido: €'
                                f' {obtenido_pago_euros}</div>', unsafe_allow_html=True)
                pass

# -----------------------------------------------------------------------------------------------------------------
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

grafica_final = st.multiselect("Escoge el tipo de gráfica:",
                                ['linea de tendencia', 'Barras'],
                                key='grafica_final')
if pago_file is not None and saldo_file is not None:
        valores_nuevos = []
        i = monto_en_soles
        for elemnto in importe_soles_pago:
                i += elemnto
                valores_nuevos.append(i)

        col7, col8 = st.columns((2))

        if 'linea de tendencia' in grafica_final:
                with col7:
                        fig = px.line(y=valores_nuevos, x=proveedor_soles,
                                        title='Distribución de saldo en soles por Banco')  # width=1400
                        fig.update_traces(marker_color='white')
                        st.plotly_chart(fig)
        if 'Barras' in grafica_final:
                with col8:
                        fig = px.bar(y=valores_nuevos, x=proveedor_soles,
                                        title='Distribución de saldo en soles por Banco', )
                        fig.update_traces(marker_color='green')
                        st.plotly_chart(fig)

# ------------------------------------------------------------------------------------------------------------------
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

st.markdown(f'<div style="width:100%;font-size: 30px;">Ingresos vs Egresos</div>', unsafe_allow_html=True)

if pago_file is not None and saldo_file is not None:
        # seleccion de divisa
        divisa_final = st.multiselect("Escoge la moneda:", moneda1, key='divisa_comparacion')

        if 'PEN' in divisa_final:
                # Crear la figura de Plotly
                fig = go.Figure()

                # Agregar barras de gastos en rojo
                fig.add_trace(go.Bar(
                        x=proveedor_soles,
                        y=importe_soles_pago,
                        name='Egresos',
                        marker_color='red'
                ))

                # Agregar barras de egresos en azul
                fig.add_trace(go.Bar(
                        x=banco,
                        y=importe_soles_saldo,
                        name='Ingresos',
                        marker_color='blue'
                ))

                # Configurar el diseño del gráfico
                fig.update_layout(
                        xaxis_title='Categoría',
                        yaxis_title='Monto',
                        barmode='group'  # Agrupa las barras
                )

                # Mostrar el gráfico
                st.plotly_chart(fig, use_container_width=True)





