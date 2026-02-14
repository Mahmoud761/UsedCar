import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Used Car Sales Analysis Dashboard",
    layout="wide"
)

# ---------------- Header ----------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("AdobeStock_320079603.webp", width=650)

st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:10px;">
        🚗 Car Sales Exploratory Data Analysis
    </h1>

    <h4 style="text-align:center; font-weight: normal; color: gray;">
        Data Insights | Sales Trends | Customer Behavior Analysis
    </h4>
    """,
    unsafe_allow_html=True
)

# ---------------- Load Data ----------------
df = pd.read_csv("updated_used_car.csv")

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "📌 Data Overview",
        "📊 Univariate Analysis (Histograms)",
        "📈 Bivariate Analysis",
        "🧾 Data Explorer (Filters)",

    ],
    index=0
)

# ---------------- Page 1: Overview ----------------
if page == "📌 Data Overview":
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", f"{df.shape[1]:,}")
    c3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")

    st.subheader("Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Describe (Categorical)")
    st.dataframe(df.select_dtypes(include='object').describe(), use_container_width=True)

    st.subheader("Describe (Numeric)")
    st.dataframe(df.select_dtypes(include='number').describe(), use_container_width=True)

# ---------------- Page 2: Univariate (Histogram) ----------------
elif page == "📊 Univariate Analysis (Histograms)":
    st.subheader("Visuals (Histograms)")

    skip_cols = {"Car_id", "Date", "Dealer_No", "Customer Name"}
    cols_to_plot = [c for c in df.columns if c not in skip_cols]

    selected_col = st.selectbox("Choose a column to view histogram", cols_to_plot)
    if selected_col:
        fig = px.histogram(data_frame=df, x=selected_col, title=selected_col)
        st.plotly_chart(fig, use_container_width=True)

# ---------------- Page 3: 📈 Bivariate Analysis ----------------
elif page == "📈 Bivariate Analysis":
    st.subheader("Top 10 Most Expensive Brands")
    if "Brand" in df.columns and "Price" in df.columns:
        top10_brand = (
            df.groupby("Brand")["Price"]
              .mean()
              .sort_values(ascending=False)
              .head(10)
              .reset_index()
        )
        fig = px.bar(top10_brand, x="Brand", y="Price", title="Top 10 Most Expensive Brands")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Missing columns: Brand and/or Price")

    st.subheader("Bottom 10 Most Expensive Brands")
    if "Brand" in df.columns and "Price" in df.columns:
        bottom10_brand = (
            df.groupby("Brand")["Price"]
              .mean()
              .sort_values(ascending=True)
              .head(10)
              .reset_index()
        )
        fig = px.bar(bottom10_brand, x="Brand", y="Price", title="Bottom 10 Most Expensive Brands")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Brand vs Dealer Region (Count Heatmap)")
    if {"Dealer_Region", "Brand", "Car_id"}.issubset(df.columns):
        brand_region = df.groupby(["Dealer_Region", "Brand"])["Car_id"].count().reset_index(name="count")
        fig = px.density_heatmap(
            data_frame=brand_region,
            x="Brand",
            y="Dealer_Region",
            z="count",
            color_continuous_scale="Blues",
            title="Brand x Dealer Region (Sales Count)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Missing required columns for heatmap: Dealer_Region, Brand, Car_id")

    st.divider()

    st.subheader("Price Category")
    if "Price_category" in df.columns:
        cat_counts = df["Price_category"].value_counts().reset_index()
        cat_counts.columns = ["Price_category", "count"]

        fig = px.pie(
            cat_counts,
            names="Price_category",
            values="count",
            title="Price Category Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Price_category column not found.")

    st.divider()

    st.subheader("Top Selling Brand in Each Region")
    if {"Dealer_Region", "Brand", "Car_id"}.issubset(df.columns):
        top_brand_per_region = (
            df.groupby(['Dealer_Region', 'Brand'])['Car_id']
              .count()
              .reset_index(name='count')
              .sort_values(['Dealer_Region', 'count'], ascending=[True, False])
              .drop_duplicates('Dealer_Region')
        )

        fig = px.bar(
            top_brand_per_region,
            x='Dealer_Region',
            y='count',
            color='Brand',
            title='Top Selling Brand in Each Region'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Missing required columns: Dealer_Region, Brand, Car_id")

    st.divider()

    st.subheader("Body Style Distribution")
    if "Body Style" in df.columns:
        body_style = df['Body Style'].value_counts().reset_index(name='count')
        body_style.columns = ['Body Style', 'count']

        fig = px.pie(
            data_frame=body_style,
            names='Body Style',
            values='count',
            title='Distribution of Body Styles',
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("This chart shows the market share of each body style based on sales volume.")
    else:
        st.warning("Column 'Body Style' not found.")

    st.divider()

    st.subheader("Top Selling Body Style in Top 10 Brands")
    if {"Brand", "Body Style", "Car_id"}.issubset(df.columns):
        top10_brands = (
            df.groupby('Brand')['Car_id']
              .count()
              .sort_values(ascending=False)
              .head(10)
              .index
        )

        df_top10 = df[df['Brand'].isin(top10_brands)]

        top_Body_Style_per_Brand = (
            df_top10.groupby(['Brand', 'Body Style'])['Car_id']
                    .count()
                    .reset_index(name='count')
                    .sort_values(['Brand', 'count'], ascending=[True, False])
                    .drop_duplicates('Brand')
        )

        fig = px.bar(
            top_Body_Style_per_Brand,
            x='Brand',
            y='count',
            color='Body Style',
            title='Top Selling Body Style in Top 10 Brands'
        )

        st.plotly_chart(fig, use_container_width=True)
        st.caption("Showing only the top 10 brands by total sales to reduce visual clutter.")
    else:
        st.warning("Missing required columns: Brand, Body Style, Car_id")

elif page == "🧾 Data Explorer (Filters)":
    st.subheader("🧾 Data Explorer (Filters & Table)")
    st.caption("Use the filters from the sidebar to slice the data, then explore the table below.")

    # ---------- Sidebar Filters ----------
    st.sidebar.markdown("### 🔎 Table Filters")

    # Brand filter
    if "Brand" in df.columns:
        brand_list = sorted(df["Brand"].dropna().unique().tolist())
        brand_sel = st.sidebar.multiselect("Brand", options=brand_list, default=[])
    else:
        brand_sel = []

    # Region filter
    if "Dealer_Region" in df.columns:
        region_list = sorted(df["Dealer_Region"].dropna().unique().tolist())
        region_sel = st.sidebar.multiselect("Dealer Region", options=region_list, default=[])
    else:
        region_sel = []

    # Body Style filter
    if "Body Style" in df.columns:
        body_list = sorted(df["Body Style"].dropna().unique().tolist())
        body_sel = st.sidebar.multiselect("Body Style", options=body_list, default=[])
    else:
        body_sel = []

    # Transmission filter
    if "Transmission" in df.columns:
        trans_list = sorted(df["Transmission"].dropna().unique().tolist())
        trans_sel = st.sidebar.multiselect("Transmission", options=trans_list, default=[])
    else:
        trans_sel = []

    # Price range filter
    if "Price" in df.columns:
        min_p = int(df["Price"].min())
        max_p = int(df["Price"].max())
        price_range = st.sidebar.slider("Price Range", min_value=min_p, max_value=max_p, value=(min_p, max_p))
    else:
        price_range = None

    # Search box (optional)
    search_text = st.sidebar.text_input("Search (any text in row)", value="").strip().lower()

    # ---------- Apply Filters ----------
    fdf = df.copy()

    if brand_sel:
        fdf = fdf[fdf["Brand"].isin(brand_sel)]

    if region_sel:
        fdf = fdf[fdf["Dealer_Region"].isin(region_sel)]

    if body_sel:
        fdf = fdf[fdf["Body Style"].isin(body_sel)]

    if trans_sel:
        fdf = fdf[fdf["Transmission"].isin(trans_sel)]

    if price_range and "Price" in fdf.columns:
        fdf = fdf[(fdf["Price"] >= price_range[0]) & (fdf["Price"] <= price_range[1])]

    if search_text:
        # search across all columns as string
        mask = fdf.astype(str).apply(lambda row: row.str.lower().str.contains(search_text, na=False)).any(axis=1)
        fdf = fdf[mask]

    # ---------- Table Controls ----------
    st.markdown("### 📌 Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Filtered Rows", f"{len(fdf):,}")
    c2.metric("Filtered Columns", f"{fdf.shape[1]:,}")
    if "Price" in fdf.columns:
        c3.metric("Avg Price (Filtered)", f"{fdf['Price'].mean():,.0f}")

    # Choose columns to show
    st.markdown("### 🧱 Table View")
    cols_show = st.multiselect("Choose columns to display", options=fdf.columns.tolist(), default=fdf.columns.tolist())
    view_df = fdf[cols_show] if cols_show else fdf

    # Pagination-like control
    max_rows = st.slider("Rows to display", min_value=50, max_value=1000, value=200, step=50)
    st.dataframe(view_df.head(max_rows), use_container_width=True)

    # Download filtered data
    csv_bytes = view_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name="filtered_used_car_data.csv",
        mime="text/csv"
    )





