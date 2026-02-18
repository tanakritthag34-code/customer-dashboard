import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(layout="wide")
sns.set_style("whitegrid")
sns.set_palette("Set2")

st.title("📊 Executive Customer Purchase Behavior Dashboard")

# =============================
# LOAD DATA
# =============================
FILE_NAME = "customer_data.csv"

if not os.path.exists(FILE_NAME):
    st.error("❌ customer_data.csv not found")
    st.stop()

df = pd.read_csv(FILE_NAME)
df.columns = df.columns.str.strip().str.lower()

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("🔎 Filter Options")

region_filter = st.sidebar.multiselect(
    "Select Region",
    options=df["region"].unique(),
    default=df["region"].unique()
)

age_range = st.sidebar.slider(
    "Select Age Range",
    int(df["age"].min()),
    int(df["age"].max()),
    (int(df["age"].min()), int(df["age"].max()))
)

loyalty_range = st.sidebar.slider(
    "Select Loyalty Score",
    float(df["loyalty_score"].min()),
    float(df["loyalty_score"].max()),
    (float(df["loyalty_score"].min()), float(df["loyalty_score"].max()))
)

filtered_df = df[
    (df["region"].isin(region_filter)) &
    (df["age"].between(age_range[0], age_range[1])) &
    (df["loyalty_score"].between(loyalty_range[0], loyalty_range[1]))
]

if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()

# Create Age Group
bins = [20,30,40,50,60]
labels = ["20-29","30-39","40-49","50+"]
filtered_df["age_group"] = pd.cut(filtered_df["age"], bins=bins, labels=labels, right=False)

# =============================
# KPI SECTION
# =============================
st.markdown("## 🔹 Key Business Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", len(filtered_df))
col2.metric("Total Revenue", f"${filtered_df['purchase_amount'].sum():,.2f}")
col3.metric("Avg Purchase", f"${filtered_df['purchase_amount'].mean():,.2f}")
col4.metric("Avg Frequency", round(filtered_df["purchase_frequency"].mean(),2))

st.markdown("---")

# =============================
# VISUALIZATION SECTION
# =============================

# Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("Purchase Distribution")
    fig, ax = plt.subplots()
    sns.histplot(filtered_df["purchase_amount"], kde=True)
    st.pyplot(fig)

with col2:
    st.subheader("Average Purchase by Region")
    fig, ax = plt.subplots()
    filtered_df.groupby("region")["purchase_amount"].mean().sort_values().plot(kind="bar")
    st.pyplot(fig)

# Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("Purchase Spread by Region")
    fig, ax = plt.subplots()
    sns.boxplot(data=filtered_df, x="region", y="purchase_amount")
    st.pyplot(fig)

with col2:
    st.subheader("Income vs Purchase (Loyalty Colored)")
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=filtered_df,
        x="annual_inc",
        y="purchase_amount",
        hue="loyalty_score",
        palette="viridis"
    )
    st.pyplot(fig)

# Row 3
col1, col2 = st.columns(2)

with col1:
    st.subheader("Frequency by Loyalty Segment")
    fig, ax = plt.subplots()
    filtered_df.groupby(pd.cut(filtered_df["loyalty_score"], bins=4))["purchase_frequency"].mean().plot(kind="bar")
    st.pyplot(fig)

with col2:
    st.subheader("Average Purchase by Age Group")
    fig, ax = plt.subplots()
    filtered_df.groupby("age_group")["purchase_amount"].mean().plot(kind="bar")
    st.pyplot(fig)

# =============================
# TOP 10% HIGH VALUE CUSTOMERS
# =============================
st.markdown("---")
st.markdown("## 🏆 Top 10% High Value Customers")

threshold = filtered_df["purchase_amount"].quantile(0.90)
top_10 = filtered_df[filtered_df["purchase_amount"] >= threshold]
others = filtered_df[filtered_df["purchase_amount"] < threshold]

col1, col2, col3 = st.columns(3)
col1.metric("Top 10% Customers", len(top_10))
col2.metric("Avg Purchase (Top 10%)", f"${top_10['purchase_amount'].mean():,.2f}")
col3.metric("Revenue Contribution %",
            f"{(top_10['purchase_amount'].sum()/filtered_df['purchase_amount'].sum())*100:.1f}%")

fig, ax = plt.subplots()
sns.histplot(top_10["purchase_amount"], color="gold")
st.pyplot(fig)

# =============================
# CORRELATION HEATMAP
# =============================
st.markdown("---")
st.subheader("Correlation Heatmap")

fig, ax = plt.subplots()
sns.heatmap(
    filtered_df[["age","annual_inc","purchase_amount","loyalty_score","purchase_frequency"]].corr(),
    annot=True,
    cmap="coolwarm"
)
st.pyplot(fig)

# =============================
# BUSINESS QUESTION ANALYSIS
# =============================
st.markdown("---")
st.markdown("## 📊 Business Question Analysis")

# Q1
st.markdown("### 1️⃣ ลูกค้ากลุ่มใดมีแนวโน้มซื้อสินค้าสูง?")

top_region = filtered_df.groupby("region")["purchase_amount"].mean().idxmax()
top_age = filtered_df.groupby("age_group")["purchase_amount"].mean().idxmax()

st.write(f"""
• Region ที่มีค่าเฉลี่ยการซื้อสูงสุดคือ **{top_region}**  
• Age Group ที่ใช้จ่ายสูงสุดคือ **{top_age}**  
• ลูกค้าที่มี Loyalty Score สูงมีแนวโน้มซื้อสูงกว่า
""")

# Q2
st.markdown("### 2️⃣ ปัจจัยใดทำให้ลูกค้ากลับมาซื้อซ้ำ?")

loyalty_corr = filtered_df["loyalty_score"].corr(filtered_df["purchase_frequency"])
income_corr = filtered_df["annual_inc"].corr(filtered_df["purchase_frequency"])
age_corr = filtered_df["age"].corr(filtered_df["purchase_frequency"])

st.write(f"""
• Loyalty vs Frequency correlation = **{loyalty_corr:.2f}**  
• Income vs Frequency correlation = **{income_corr:.2f}**  
• Age vs Frequency correlation = **{age_corr:.2f}**

👉 Loyalty Score เป็นปัจจัยหลักที่ส่งผลต่อการซื้อซ้ำ
""")

# Q3
st.markdown("### 3️⃣ สามารถจำแนกลูกค้าตามพฤติกรรมได้หรือไม่?")

high_value = filtered_df[
    (filtered_df["purchase_amount"] > filtered_df["purchase_amount"].quantile(0.75)) &
    (filtered_df["loyalty_score"] > filtered_df["loyalty_score"].quantile(0.75))
]

low_engagement = filtered_df[
    (filtered_df["purchase_amount"] < filtered_df["purchase_amount"].quantile(0.25)) &
    (filtered_df["loyalty_score"] < filtered_df["loyalty_score"].quantile(0.25))
]

st.write(f"""
🏆 High Value Loyal Customers: **{len(high_value)} คน**  
⚠ Low Engagement Customers: **{len(low_engagement)} คน**

ลูกค้าสามารถแบ่งกลุ่มตามพฤติกรรมการซื้อและระดับ Loyalty ได้อย่างชัดเจน
""")

