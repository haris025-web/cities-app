import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page Config
st.set_page_config(page_title="Global Cities Dashboard", layout="wide")


# Load Data Function
@st.cache_data
def load_data():

    columns = [
        "geonameid", "name", "asciiname", "alternatenames",
        "latitude", "longitude", "feature_class", "feature_code",
        "country_code", "cc2", "admin1_code", "admin2_code",
        "admin3_code", "admin4_code", "population",
        "elevation", "dem", "timezone", "modification_date"
    ]

    df = pd.read_csv(
        "data/cities500.txt",
        sep="\t",
        header=None,
        names=columns,
        low_memory=False
    )

    # Convert numeric columns safely
    numeric_cols = ["latitude", "longitude", "population", "elevation", "dem"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clean population column
    df["population"] = df["population"].fillna(0)
    df["population"] = df["population"].astype(float)

    return df


# Load Dataset
df = load_data()
df["population"] = pd.to_numeric(df["population"], errors="coerce")
df["population"] = df["population"].fillna(0)
# Dashboard Title
st.title("🌍 Global Cities Data Visualization Dashboard")
st.markdown(
    "Professional interactive dashboard built with Streamlit, Pandas, Matplotlib, and Seaborn."
)

# Sidebar Filters
st.sidebar.header("Dashboard Filters")

# Country Filter
countries = sorted(df["country_code"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    countries,
    default=countries[:5]
)

# Population Filter
min_pop = 0
max_pop = int(pd.to_numeric(df["population"], errors="coerce").fillna(0).max())

population_range = st.sidebar.slider(
    "Population Range",
    min_pop,
    max_pop,
    (0, int(df["population"].quantile(0.95)))
)

# Search Box
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
        filtered_df["name"].str.contains(search_city, case=False, na=False)
    ]

# KPI Cards
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Records", f"{len(filtered_df):,}")
k2.metric("Average Population", f"{filtered_df['population'].mean():,.0f}")
k3.metric("Max Population", f"{filtered_df['population'].max():,.0f}")
k4.metric("Countries", filtered_df["country_code"].nunique())

st.markdown("---")

# Charts
c1, c2 = st.columns(2)

# Bar Chart
with c1:
    st.subheader("Bar Chart - Top Countries by City Count")

    fig, ax = plt.subplots(figsize=(7, 5))

    filtered_df["country_code"].value_counts().head(10).plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Country")
    ax.set_ylabel("City Count")

    st.pyplot(fig)

# Pie Chart
with c2:
    st.subheader("Pie Chart - Population Distribution")

    pie_data = filtered_df.groupby("country_code")["population"].sum().head(5)

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.pie(
        pie_data,
        labels=pie_data.index,
        autopct="%1.1f%%"
    )

    st.pyplot(fig)

# Histogram and Scatter Plot
c3, c4 = st.columns(2)

with c3:
    st.subheader("Histogram - Population Distribution")

    fig, ax = plt.subplots(figsize=(7, 5))

    sns.histplot(
        filtered_df["population"].dropna(),
        bins=30,
        ax=ax
    )

    st.pyplot(fig)

with c4:
    st.subheader("Scatter Plot - Latitude vs Longitude")

    fig, ax = plt.subplots(figsize=(7, 5))

    sample_size = min(2000, len(filtered_df))

    sns.scatterplot(
        data=filtered_df.sample(sample_size),
        x="longitude",
        y="latitude",
        size="population",
        legend=False,
        ax=ax
    )

    st.pyplot(fig)

# Boxplot and Violin Plot
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

# Heatmap
st.subheader("Heatmap - Correlation Matrix")

numeric_df = filtered_df.select_dtypes(include=["float64", "int64"])

fig, ax = plt.subplots(figsize=(8, 6))

sns.heatmap(
    numeric_df.corr(numeric_only=True),
    annot=True,
    cmap="coolwarm",
    ax=ax
)

st.pyplot(fig)

# Line Chart
st.subheader("Line Chart - Population Trend")

line_data = filtered_df.groupby("country_code")["population"].mean().head(15)

fig, ax = plt.subplots(figsize=(10, 5))

line_data.plot(
    kind="line",
    marker="o",
    ax=ax
)

ax.set_ylabel("Average Population")

st.pyplot(fig)

# Area Chart
st.subheader("Area Chart - Population by Country")

area_data = filtered_df.groupby("country_code")["population"].sum().head(10)

fig, ax = plt.subplots(figsize=(10, 5))

area_data.plot(
    kind="area",
    ax=ax
)

st.pyplot(fig)

# Count Plot
st.subheader("Count Plot - Feature Class")

fig, ax = plt.subplots(figsize=(10, 5))

sns.countplot(
    data=filtered_df,
    x="feature_class",
    ax=ax
)

st.pyplot(fig)

# Success Message
st.success("Dashboard Loaded Successfully")
