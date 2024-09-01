import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Uber pickups en NYC",
    page_icon="🚕",
    layout="wide"
)

def load_data(n_rows):
    return (
        pd.read_csv("https://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz", nrows=n_rows)
        .rename(columns=lambda x: x.lower())
        .assign(
            datetime=lambda df: pd.to_datetime(df["date/time"]),
            weekday=lambda df: df.datetime.dt.day_name()
        )
    )

with st.sidebar:
    st.title("App UBER")
    # Logo de CIDAEN
    st.image("https://www.cidaen.es/assets/img/cidaen.png", use_column_width=True, caption="CIDAEN")
    # Filtro para introducir el número de filas a leer
    row_selected = st.slider("Seleccionar número de filas", 0, 100000, 10000, step=1000)
    df = load_data(n_rows=row_selected)
    # Filtro para seleccionar un día de la semana
    weekday_selected = st.selectbox("Seleccionar día de la semana", df.weekday.unique())
    # Filtro para seleccionar una hora del días
    hour_selected = st.slider("Seleccionar la hora", 0, 23, 12)

st.title("Uber pickups en NYC")

# Checkbox que si está activado muestre la tabla en crudo (las primeras 5 filas)
show_raw = st.checkbox("Mostrar datos en crudo")
if show_raw:
    st.write("## Datos crudos")
    st.dataframe(df.head(5))

# Crear dos columnas
cols = st.columns(2)

with cols[0]:
    # Col1: KPI con la media de recogidas por día de la semana seleccionado
    # Mostrando si es mayor o menor que la media global entre todos los días de la semana
    mean_pickups_weekday = (
        df
        .loc[lambda df: df.weekday == weekday_selected]
        .assign(
            date=lambda df: df.datetime.dt.date
        )
        .groupby("date")
        .agg(
            total_pickups=("base", "count")
        )
        .total_pickups
        .mean()
    )

    mean_pickups_total = (
        df
        .assign(
            date=lambda df: df.datetime.dt.date
        )
        .groupby(["date", "weekday"])
        .agg(
            total_pickups=("base", "count")
        )
        .reset_index()
        .groupby("weekday")
        .agg(
            total_pickups=("total_pickups", "mean")
        )
        .total_pickups
        .mean()
    )

    st.metric(f"Pickups {weekday_selected}", mean_pickups_weekday, f"{mean_pickups_weekday/mean_pickups_total-1:.2%}")

with cols[1]:
    # Col2: KPI con la media de recogidas por hora seleccionada
    # Mostrando si es mayor o menos que la media global entre todas las horas de la semana
    mean_pickups_hour = (
        df
        .assign(
            date=lambda df: df.datetime.dt.date,
            hour=lambda df: df.datetime.dt.hour
        )
        .loc[lambda df: df.hour == hour_selected]
        .groupby(["date", "hour"])
        .agg(
            total_pickups=("base", "count")
        )
        .total_pickups
        .mean()
    )

    mean_pickups_total_hour = (
        df
        .assign(
            date=lambda df: df.datetime.dt.date,
            hour=lambda df: df.datetime.dt.hour
        )
        .groupby(["date", "hour"])
        .agg(
            total_pickups=("base", "count")
        )
        .reset_index()
        .groupby("hour")
        .agg(
            total_pickups=("total_pickups", "mean")
        )
        .total_pickups
        .mean()
    )

    st.metric(f"Pickups {hour_selected}", mean_pickups_hour, f"{mean_pickups_hour/mean_pickups_total_hour-1:.2%}")

st.map((
    df
    .loc[lambda df: df.weekday == weekday_selected]
    .loc[lambda df: df.datetime.dt.hour == hour_selected]
    )
)
