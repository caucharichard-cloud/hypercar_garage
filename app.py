import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import requests
from io import BytesIO

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Hypercar Garage",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Estilos CSS (Tema Oscuro/Racing) ---
def local_css():
    st.markdown(
        """
        <style>
        /* Fondo principal */
        .stApp {
            background-color: #121212;
            color: #E0E0E0;
            font-family: 'Inter', sans-serif;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1A1A24;
            border-right: 2px solid #FF3333;
        }
        
        /* Títulos */
        h1, h2, h3 {
            color: #FFFFFF;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 800;
        }
        
        h1 {
            border-bottom: 3px solid #FF3333;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        
        /* Tarjetas de Vehículos */
        .car-card {
            background-color: #1E1E2C;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #FF3333;
            transition: transform 0.3s ease;
        }
        .car-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(255, 51, 51, 0.2);
        }
        
        /* Metricas */
        [data-testid="stMetricValue"] {
            color: #FF3333;
            font-weight: bold;
        }
        
        /* Botones */
        .stButton>button {
            background-color: transparent;
            color: #FF3333;
            border: 2px solid #FF3333;
            border-radius: 5px;
            text-transform: uppercase;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #FF3333;
            color: #FFFFFF;
            border-color: #FF3333;
        }
        
        /* Dataframes/Tablas */
        .stDataFrame {
            border: 1px solid #333;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

local_css()

# --- Datos de Ejemplo (Base de Datos en Memoria) ---
@st.cache_data
def load_data():
    data = {
        'ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Marca': ['Bugatti', 'Koenigsegg', 'Ferrari', 'McLaren', 'Porsche', 'Pagani', 'Aston Martin', 'Lamborghini', 'Rimac', 'Hennessey'],
        'Modelo': ['Chiron Super Sport', 'Jesko Absolut', 'SF90 Stradale', 'Speedtail', '918 Spyder', 'Huayra BC', 'Valkyrie', 'Revuelto', 'Nevera', 'Venom F5'],
        'Potencia_HP': [1578, 1600, 986, 1036, 887, 791, 1139, 1001, 1914, 1817],
        'Velocidad_Max_kmh': [440, 531, 340, 403, 345, 380, 402, 350, 412, 500],
        'Aceleracion_0_100_s': [2.4, 2.5, 2.5, 2.9, 2.6, 2.8, 2.5, 2.5, 1.85, 2.6],
        'Peso_kg': [1995, 1390, 1570, 1430, 1634, 1218, 1030, 1772, 2150, 1360],
        'Precio_USD': [3900000, 3000000, 520000, 2250000, 845000, 2500000, 3200000, 608000, 2200000, 2100000],
        'Motor': ['8.0L Quad-Turbo W16', '5.0L Twin-Turbo V8', '4.0L Twin-Turbo V8 Hybrid', '4.0L Twin-Turbo V8 Hybrid', '4.6L V8 Hybrid', '6.0L Twin-Turbo V12', '6.5L V12 Hybrid', '6.5L V12 Plug-in Hybrid', '4 Motores Eléctricos', '6.6L Twin-Turbo V8'],
        'Traccion': ['AWD', 'RWD', 'AWD', 'RWD', 'AWD', 'RWD', 'RWD', 'AWD', 'AWD', 'RWD'],
        'Imagen_URL': [
            'https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?auto=format&fit=crop&q=80&w=1000', # Bugatti (Generic Supercar)
            'https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?auto=format&fit=crop&q=80&w=1000', # Koenigsegg (Generic Supercar)
            'https://images.unsplash.com/photo-1592198084033-aade902d1aae?auto=format&fit=crop&q=80&w=1000', # Ferrari (Generic)
            'https://images.unsplash.com/photo-1620882814836-932b137f8f90?auto=format&fit=crop&q=80&w=1000', # McLaren (Generic)
            'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&q=80&w=1000', # Porsche
            'https://images.unsplash.com/photo-1580273916550-e323be2ae537?auto=format&fit=crop&q=80&w=1000', # Pagani (Generic)
            'https://images.unsplash.com/photo-1603386329225-868f9b1ee6c9?auto=format&fit=crop&q=80&w=1000', # Aston Martin (Generic)
            'https://images.unsplash.com/photo-1511919884226-fd3cad34687c?auto=format&fit=crop&q=80&w=1000', # Lamborghini
            'https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&q=80&w=1000', # Rimac (EV Generic)
            'https://images.unsplash.com/photo-1544636331-e26879cd3d92?auto=format&fit=crop&q=80&w=1000'  # Hennessey (Generic)
        ]
    }
    return pd.DataFrame(data)

df = load_data()

# --- Funciones de Utilidad ---
def format_currency(value):
    return f"${value:,.0f}"

def render_image(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        st.image(img, use_column_width=True)
    except Exception as e:
        st.warning("No se pudo cargar la imagen del vehículo.")
        # Placeholder
        st.image("https://via.placeholder.com/800x400.png?text=Hypercar+Image+Not+Found", use_column_width=True)

# --- Navegación ---
st.sidebar.title("🏁 Menú")
menu_options = ["🏠 Garage Principal", "📊 Comparador de Hypercars", "🏆 Ranking y Estadísticas"]
choice = st.sidebar.radio("Navegación", menu_options)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Hypercar Garage**\n\n"
    "Explora los vehículos más rápidos y exclusivos del planeta."
)

# --- Lógica de Vistas ---

if choice == "🏠 Garage Principal":
    st.title("Garage Principal")
    st.markdown("Explora el catálogo de hipercoches por marca.")

    # Filtro de Marcas
    marcas_disponibles = sorted(df['Marca'].unique().tolist())
    marcas_disponibles.insert(0, "Todas")
    
    col_filtro, _ = st.columns([1, 2])
    with col_filtro:
        selected_brand = st.selectbox("Selecciona una Marca", marcas_disponibles)

    if selected_brand == "Todas":
        df_filtered = df
    else:
        df_filtered = df[df['Marca'] == selected_brand]

    st.markdown("---")

    # Mostrar Vehículos en Grid
    cols = st.columns(2)
    for index, row in df_filtered.iterrows():
        col = cols[index % 2]
        with col:
            with st.container():
                st.markdown(f'<div class="car-card">', unsafe_allow_html=True)
                st.subheader(f"{row['Marca']} {row['Modelo']}")
                render_image(row['Imagen_URL'])
                
                mcol1, mcol2, mcol3 = st.columns(3)
                mcol1.metric("Potencia", f"{row['Potencia_HP']} HP")
                mcol2.metric("Vel. Máx", f"{row['Velocidad_Max_kmh']} km/h")
                mcol3.metric("0-100 km/h", f"{row['Aceleracion_0_100_s']} s")
                
                with st.expander("Ver Ficha Técnica Completa"):
                    st.write(f"**Motor:** {row['Motor']}")
                    st.write(f"**Tracción:** {row['Traccion']}")
                    st.write(f"**Peso:** {row['Peso_kg']} kg")
                    st.write(f"**Precio Estimado:** {format_currency(row['Precio_USD'])}")
                
                st.markdown('</div>', unsafe_allow_html=True)


elif choice == "📊 Comparador de Hypercars":
    st.title("Head-to-Head: Comparador")
    st.markdown("Selecciona dos vehículos para comparar sus prestaciones.")

    modelos_disponibles = [f"{row['Marca']} {row['Modelo']}" for index, row in df.iterrows()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        car1_name = st.selectbox("Vehículo 1", modelos_disponibles, index=0)
        car1_data = df[df['Marca'] + ' ' + df['Modelo'] == car1_name].iloc[0]
        
    with col2:
        car2_name = st.selectbox("Vehículo 2", modelos_disponibles, index=1)
        car2_data = df[df['Marca'] + ' ' + df['Modelo'] == car2_name].iloc[0]

    st.markdown("---")
    
    # Renderizar imágenes lado a lado
    img_col1, img_col2 = st.columns(2)
    with img_col1:
        render_image(car1_data['Imagen_URL'])
        st.markdown(f"<h3 style='text-align: center;'>{car1_name}</h3>", unsafe_allow_html=True)
    with img_col2:
        render_image(car2_data['Imagen_URL'])
        st.markdown(f"<h3 style='text-align: center;'>{car2_name}</h3>", unsafe_allow_html=True)

    st.markdown("### Especificaciones")
    
    # Tabla comparativa
    comparative_df = pd.DataFrame({
        'Especificación': ['Potencia (HP)', 'Velocidad Máxima (km/h)', '0-100 km/h (s)', 'Peso (kg)', 'Motor', 'Precio (USD)'],
        car1_name: [car1_data['Potencia_HP'], car1_data['Velocidad_Max_kmh'], car1_data['Aceleracion_0_100_s'], car1_data['Peso_kg'], car1_data['Motor'], format_currency(car1_data['Precio_USD'])],
        car2_name: [car2_data['Potencia_HP'], car2_data['Velocidad_Max_kmh'], car2_data['Aceleracion_0_100_s'], car2_data['Peso_kg'], car2_data['Motor'], format_currency(car2_data['Precio_USD'])]
    })
    
    st.dataframe(comparative_df, use_container_width=True, hide_index=True)

    # Gráfico de Radar (Araña) para comparación visual
    st.markdown("### Gráfico de Radar")
    
    # Normalizar datos para el radar (escala 0-100 para visualizar mejor las diferencias relativas)
    def normalize(val, min_val, max_val, inverse=False):
        if max_val == min_val: return 100
        norm = ((val - min_val) / (max_val - min_val)) * 100
        return 100 - norm if inverse else norm

    max_hp = df['Potencia_HP'].max()
    max_speed = df['Velocidad_Max_kmh'].max()
    min_accel = df['Aceleracion_0_100_s'].min()
    max_accel = df['Aceleracion_0_100_s'].max()
    min_weight = df['Peso_kg'].min()
    max_weight = df['Peso_kg'].max()

    categories = ['Potencia', 'Velocidad Max', 'Aceleración (Inversa)', 'Ligereza (Inversa)']
    
    car1_stats = [
        normalize(car1_data['Potencia_HP'], 0, max_hp),
        normalize(car1_data['Velocidad_Max_kmh'], 0, max_speed),
        normalize(car1_data['Aceleracion_0_100_s'], min_accel, max_accel, inverse=True), # Menos es mejor
        normalize(car1_data['Peso_kg'], min_weight, max_weight, inverse=True) # Menos es mejor
    ]
    
    car2_stats = [
        normalize(car2_data['Potencia_HP'], 0, max_hp),
        normalize(car2_data['Velocidad_Max_kmh'], 0, max_speed),
        normalize(car2_data['Aceleracion_0_100_s'], min_accel, max_accel, inverse=True),
        normalize(car2_data['Peso_kg'], min_weight, max_weight, inverse=True)
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=car1_stats,
        theta=categories,
        fill='toself',
        name=car1_name,
        line_color='#FF3333'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=car2_stats,
        theta=categories,
        fill='toself',
        name=car2_name,
        line_color='#33B5E5'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False
            )),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0')
    )
    
    st.plotly_chart(fig, use_container_width=True)


elif choice == "🏆 Ranking y Estadísticas":
    st.title("Leaderboard")
    st.markdown("Clasificación de los hipercoches según diferentes métricas.")

    sort_option = st.selectbox(
        "Clasificar por:",
        ("Velocidad Máxima (Mayor a Menor)", "Potencia (Mayor a Menor)", "Aceleración 0-100 (Menor a Mayor)", "Precio (Mayor a Menor)", "Peso (Menor a Mayor)")
    )

    if sort_option == "Velocidad Máxima (Mayor a Menor)":
        df_sorted = df.sort_values(by='Velocidad_Max_kmh', ascending=False)
        y_col = 'Velocidad_Max_kmh'
        title = 'Velocidad Máxima (km/h)'
    elif sort_option == "Potencia (Mayor a Menor)":
        df_sorted = df.sort_values(by='Potencia_HP', ascending=False)
        y_col = 'Potencia_HP'
        title = 'Potencia (HP)'
    elif sort_option == "Aceleración 0-100 (Menor a Mayor)":
        df_sorted = df.sort_values(by='Aceleracion_0_100_s', ascending=True)
        y_col = 'Aceleracion_0_100_s'
        title = 'Aceleración 0-100 km/h (s)'
    elif sort_option == "Precio (Mayor a Menor)":
        df_sorted = df.sort_values(by='Precio_USD', ascending=False)
        y_col = 'Precio_USD'
        title = 'Precio (USD)'
    elif sort_option == "Peso (Menor a Mayor)":
        df_sorted = df.sort_values(by='Peso_kg', ascending=True)
        y_col = 'Peso_kg'
        title = 'Peso (kg)'

    df_sorted['Vehículo'] = df_sorted['Marca'] + ' ' + df_sorted['Modelo']

    # Gráfico de Barras
    fig_bar = px.bar(
        df_sorted, 
        x='Vehículo', 
        y=y_col, 
        color='Marca',
        title=f'Ranking: {title}',
        color_discrete_sequence=px.colors.qualitative.Set1,
        template='plotly_dark'
    )
    
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

    # Mostrar Datos Tabulares del Ranking
    st.markdown("### Datos Crudos")
    display_cols = ['Marca', 'Modelo', 'Potencia_HP', 'Velocidad_Max_kmh', 'Aceleracion_0_100_s', 'Peso_kg', 'Precio_USD']
    df_display = df_sorted[display_cols].copy()
    
    # Formatear precio para la tabla
    df_display['Precio_USD'] = df_display['Precio_USD'].apply(format_currency)
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)