import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Page Config
st.set_page_config(page_title="Global Cities Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    columns = [
        "geonameid", "name", "asciiname", "alternatenames",
        "latitude", "longitude", "feature_class", "feature_code",
        "country_code", "cc2", "admin1_code", "admin2_code",
        "admin3_code", "admin4_code", "population",
        "elevation", "dem", "timezone", "modification_date"
    ]

    try:
        df = pd.read_csv(
            "data/cities500.txt",
            sep="\t",
            header=None,
            names=columns,
            low_memory=False
        )

        numeric_cols = [
            "latitude",
            "longitude",
            "population",
            "elevation",
            "dem"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["population"] = df["population"].fillna(0)

        return df

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=columns)

# Load Dataset
df = load_data()

if df.empty:
    st.error("Dataset could not be loaded. Check that data/cities500.txt exists in GitHub.")
    st.stop()

# Dashboard Title
st.title("🌍 Global Cities Data Visualization Dashboard")
tab1, tab2, tab3 = st.tabs([
    "📊 Dashboard",
    "🌍 Map",
    "📈 Statistics"
])
st.markdown(
    "Professional interactive dashboard built with Streamlit, Pandas, Matplotlib, and Seaborn."
)

# Sidebar
st.sidebar.header("Dashboard Filters")

countries = sorted(df["country_code"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    countries,
    default=countries[:5] if len(countries) >= 5 else countries
)

population_series = pd.to_numeric(
    df["population"],
    errors="coerce"
).fillna(0)

max_pop = int(population_series.max()) if len(population_series) > 0 else 1000000

if max_pop <= 0:
    max_pop = 1000000

population_range = st.sidebar.slider(
    "Population Range",
    0,
    max_pop,
    (
        0,
        int(population_series.quantile(0.95))
        if len(population_series) > 0
        else max_pop
    )
)

search_city = st.sidebar.text_input("Search City")

# Filter Data
filtered_df = df.copy()

if selected_countries:
    filtered_df = filtered_df[
        filtered_df["country_code"].isin(selected_countries)
    ]

filtered_df = filtered_df[
    (filtered_df["population"] >= population_range[0]) &
    (filtered_df["population"] <= population_range[1])
]

if search_city:
    filtered_df = filtered_df[
        filtered_df["name"].astype(str).str.contains(
            search_city,
            case=False,
            na=False
        )
    ]

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# KPI Cards
with tab1:
    k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "🏙️ Cities",
    f"{len(filtered_df):,}"
)

k2.metric(
    "👥 Avg Population",
    f"{filtered_df['population'].mean():,.0f}"
)

k3.metric(
    "🚀 Largest Population",
    f"{filtered_df['population'].max():,.0f}"
)

k4.metric(
    "🌍 Countries",
    filtered_df["country_code"].nunique()
)
st.metric(
    "🏆 Largest City",
    filtered_df.loc[
        filtered_df["population"].idxmax(),
        "name"
    ]
)

st.markdown("---")
with tab2:
    st.subheader("🌍 Interactive World Map")

map_df = filtered_df.dropna(
    subset=["latitude", "longitude"]
)

fig = px.scatter_geo(
    map_df,
    lat="latitude",
    lon="longitude",
    hover_name="name",
    color="country_code",
    size="population",
    projection="natural earth"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
st.subheader("🏆 Top 10 Most Populated Cities")

top10 = (
    filtered_df
    .sort_values("population", ascending=False)
    [["name", "country_code", "population"]]
    .head(10)
)

st.dataframe(
    top10,
    use_container_width=True
)
st.subheader("📥 Export Data")

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Cities CSV",
    data=csv,
    file_name="filtered_cities.csv",
    mime="text/csv"
)
# Charts
with tab3:
    c1, c2 = st.columns(2)

with c1:
    st.subheader("Bar Chart - Top Countries by City Count")

    fig, ax = plt.subplots(figsize=(7, 5))

    filtered_df["country_code"].value_counts().head(10).plot(
        kind="bar",
        ax=ax
    )

    st.pyplot(fig)

with c2:
    st.subheader("Pie Chart - Population Distribution")

    pie_data = (
        filtered_df.groupby("country_code")["population"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    fig, ax = plt.subplots(figsize=(7, 5))

    if len(pie_data) > 0:
        ax.pie(
            pie_data,
            labels=pie_data.index,
            autopct="%1.1f%%"
        )

    st.pyplot(fig)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Histogram - Population Distribution")

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.histplot(
        filtered_df["population"],
        bins=30,
        ax=ax
    )

    st.pyplot(fig)

with c4:
    st.subheader("Scatter Plot - Latitude vs Longitude")

    fig, ax = plt.subplots(figsize=(7, 5))

    sample_size = min(2000, len(filtered_df))

    if sample_size > 0:
        sns.scatterplot(
            data=filtered_df.sample(sample_size),
            x="longitude",
            y="latitude",
            size="population",
            legend=False,
            ax=ax
        )

    st.pyplot(fig)

c5, c6 = st.columns(2)

with c5:
    st.subheader("Box Plot - Population")

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.boxplot(
        y=filtered_df["population"],
        ax=ax
    )

    st.pyplot(fig)

with c6:
    st.subheader("Violin Plot - Population")

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.violinplot(
        y=filtered_df["population"],
        ax=ax
    )

    st.pyplot(fig)

st.subheader("Heatmap - Correlation Matrix")

numeric_df = filtered_df.select_dtypes(
    include=["float64", "int64"]
)

if len(numeric_df.columns) > 1:
    fig, ax = plt.subplots(figsize=(8, 6))

    sns.heatmap(
        numeric_df.corr(),
        annot=True,
        cmap="coolwarm",
        ax=ax
    )

    st.pyplot(fig)

st.subheader("Line Chart - Population Trend")

line_data = (
    filtered_df.groupby("country_code")["population"]
    .mean()
    .head(15)
)

fig, ax = plt.subplots(figsize=(10, 5))

line_data.plot(
    kind="line",
    marker="o",
    ax=ax
)

st.pyplot(fig)

st.subheader("Area Chart - Population by Country")

area_data = (
    filtered_df.groupby("country_code")["population"]
    .sum()
    .head(10)
)

fig, ax = plt.subplots(figsize=(10, 5))

area_data.plot(
    kind="area",
    ax=ax
)

st.pyplot(fig)

st.subheader("Count Plot - Feature Class")

fig, ax = plt.subplots(figsize=(10, 5))

sns.countplot(
    data=filtered_df,
    x="feature_class",
    ax=ax
)

st.pyplot(fig)

st.success("Dashboard Loaded Successfully")
