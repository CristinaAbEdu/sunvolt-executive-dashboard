import pandas as pd
import streamlit as st
import plotly.express as px

# Section 1: Streamlit dashboard setup

# Page setup
st.set_page_config(
    page_title="SunVolt Executive Dashboard",
    page_icon="☀️",
    layout="wide"
)

# Dashboard colours
NAVY = "#1F4E5F"
TEAL = "#4F89A8"
GOLD = "#F4C95D"
CORAL = "#D96C75"
LIGHT_BG = "#F7F9FB"


# I chose light, professional dashboard styling
st.markdown(
    """
    <style>
        p, li, label {
            color: #1F2937 !important;
        }

        h1, h2, h3 {
            color: #1F4E5F !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Load the Excel dataset
@st.cache_data
def load_data():
    return pd.read_excel("SunVolt Solar Customer Data.xlsx")

df = load_data()

# Main dashboard heading
st.title("☀️ SunVolt Energy: Executive Solar Adoption Dashboard")

st.caption(
    "Decision support for the CEO, investors and management team | "
    
)

st.markdown(
    "This dashboard highlights where SunVolt Energy can increase solar-system "
    "adoption, strengthen conversion and improve long-term profitability."
)




# Section 2: Executive Snapshot 

# Convert Yes/No purchases into 1/0 where needed
if "Purchase Flag" not in df.columns:
    df["Purchase Flag"] = (
        df["Purchased Solar System"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"yes": 1, "no": 0})
    )

# Calculate the key figures
total_customers = len(df)
total_purchases = int(df["Purchase Flag"].sum())
overall_rate = df["Purchase Flag"].mean()

regional_summary = (
    df.groupby("Region", as_index=False)
    .agg(
        Customers=("Customer ID", "count"),
        Purchases=("Purchase Flag", "sum"),
        Purchase_Rate=("Purchase Flag", "mean")
    )
)

top_region = regional_summary.loc[
    regional_summary["Purchase_Rate"].idxmax(), "Region"
]

top_region_rate = regional_summary["Purchase_Rate"].max()

# Display the KPI cards
st.subheader("Executive Snapshot")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Customers Analysed", f"{total_customers:,}")
col2.metric("Solar Systems Purchased", f"{total_purchases:,}")
col3.metric("Overall Purchase Rate", f"{overall_rate:.1%}")
col4.metric("Highest Adoption Region", top_region, f"{top_region_rate:.1%}")

st.divider()




# SECTION 3: REGIONAL PERFORMANCE

st.subheader("1. Regional Performance: Sales Volume vs Adoption Rate")

regional_volume = regional_summary.sort_values("Purchases", ascending=False)
regional_rate = regional_summary.sort_values("Purchase_Rate", ascending=False)

left_col, right_col = st.columns(2)

with left_col:
    fig_volume = px.bar(
        regional_volume,
        x="Region",
        y="Purchases",
        text="Purchases",
        title="Total Solar-System Purchases by Region",
        color="Region",
        color_discrete_map={
            "North America": GOLD,
            "Europe": TEAL,
            "Pacific": TEAL
        }
    )

    fig_volume.update_traces(textposition="outside")

    fig_volume.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_x=0.02,
        xaxis_title="",
        yaxis_title="Number of systems purchased"
    )

    st.plotly_chart(fig_volume, use_container_width=True)

with right_col:
    fig_region_rate = px.bar(
        regional_rate,
        x="Region",
        y="Purchase_Rate",
        text="Purchase_Rate",
        title="Solar-System Purchase Rate by Region",
        color="Region",
        color_discrete_map={
            "Pacific": GOLD,
            "Europe": TEAL,
            "North America": CORAL
        }
    )

    fig_region_rate.update_traces(
        texttemplate="%{text:.1%}",
        textposition="outside"
    )

    fig_region_rate.add_hline(
    y=overall_rate,
    line_dash="dash",
    line_color=NAVY
)

    fig_region_rate.update_layout(
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    title_x=0.02,
    xaxis_title="",
    yaxis_title="Purchase rate",
    yaxis_tickformat=".0%",
    yaxis_range=[0, 0.70],
    margin=dict(t=70, r=120)
)

    st.plotly_chart(fig_region_rate, use_container_width=True)
    
    st.caption("Dashed horizontal line = overall purchase rate of 48.2%.")

st.info(
    "Key insight: North America produces the largest number of purchases, but "
    "has the lowest purchase rate. Pacific has the strongest adoption rate and "
    "should be supported with sufficient installation capacity."
)

st.divider()



# SECTION 4: CUSTOMER OPPORTUNITIES

st.subheader("2. Customer Opportunities: Who Should SunVolt Target?")

# Create age and income categories if they are not already in the dataset
if "Age Group" not in df.columns:
    df["Age Group"] = pd.cut(
        df["Age"],
        bins=[0, 29, 39, 49, 59, 150],
        labels=["Under 30", "30-39", "40-49", "50-59", "60+"]
    )

if "Income Band" not in df.columns:
    df["Income Band"] = pd.cut(
        df["Annual Income"],
        bins=[0, 29999, 49999, 69999, 99999, float("inf")],
        labels=["<30k", "30k-49k", "50k-69k", "70k-99k", "100k+"]
    )

age_order = ["Under 30", "30-39", "40-49", "50-59", "60+"]
income_order = ["<30k", "30k-49k", "50k-69k", "70k-99k", "100k+"]

age_summary = (
    df.groupby("Age Group", observed=False)["Purchase Flag"]
    .mean()
    .reindex(age_order)
    .reset_index()
)

income_summary = (
    df.groupby("Income Band", observed=False)["Purchase Flag"]
    .mean()
    .reindex(income_order)
    .reset_index()
)

left_col, right_col = st.columns(2)

with left_col:
    age_summary["Opportunity"] = age_summary["Age Group"].apply(
        lambda group: "Priority segment" if group == "30-39" else "Other segment"
    )

    fig_age = px.bar(
        age_summary,
        x="Age Group",
        y="Purchase Flag",
        text="Purchase Flag",
        title="Purchase Rate by Age Group",
        color="Opportunity",
        color_discrete_map={
    "Priority segment": GOLD,
    "Other segment": TEAL
},
category_orders={"Age Group": age_order}
    )

    fig_age.update_traces(
        texttemplate="%{text:.1%}",
        textposition="outside"
    )

    fig_age.add_hline(
    y=overall_rate,
    line_dash="dash",
    line_color=NAVY
)

    fig_age.update_layout(
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    title_x=0.02,
    xaxis_title="",
    yaxis_title="Purchase rate",
    yaxis_tickformat=".0%",
    yaxis_range=[0, 0.70],
    margin=dict(t=70, r=120)
)

    st.plotly_chart(fig_age, use_container_width=True)

with right_col:
    income_summary["Opportunity"] = income_summary["Income Band"].apply(
        lambda band: "Priority segment" if band == "30k-49k" else "Other segment"
    )

    fig_income = px.bar(
        income_summary,
        x="Income Band",
        y="Purchase Flag",
        text="Purchase Flag",
        title="Purchase Rate by Annual Income Band",
        color="Opportunity",
        color_discrete_map={
    "Priority segment": GOLD,
    "Other segment": TEAL
},
category_orders={"Income Band": income_order}
    )

    fig_income.update_traces(
        texttemplate="%{text:.1%}",
        textposition="outside"
    )

    fig_income.add_hline(
    y=overall_rate,
    line_dash="dash",
    line_color=NAVY
)

    fig_income.update_layout(
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    title_x=0.02,
    xaxis_title="",
    yaxis_title="Purchase rate",
    yaxis_tickformat=".0%",
    yaxis_range=[0, 0.70],
    margin=dict(t=70, r=120)
)

    st.plotly_chart(fig_income, use_container_width=True)
    
    st.caption("Dashed horizontal line = overall purchase rate of 48.2%.")

st.info(
    "Priority audience: customers aged 30–39 and those earning R30k–R49k show "
    "the highest observed purchase rates. These groups should receive focused "
    "campaigns, while lower-adoption groups may respond better to affordable "
    "packages, flexible payment options and clearer product information."
)

st.divider()





# SECTION 5: INSTALLER ACCESS

st.subheader("3. Installation Access: Where Is Distance Reducing Adoption?")

# Standardise distance labels 
df["Distance Band"] = (
    df["Distance from Nearest Installer"]
    .astype(str)
    .str.replace(" ", "", regex=False)
    .str.replace("kms", "km", regex=False)
)

distance_mapping = {
    "0-1km": "0-1 km",
    "1-2km": "1-2 km",
    "2-5km": "2-5 km",
    "5-10km": "5-10 km",
    "10+km": "10+ km"
}

df["Distance Band"] = df["Distance Band"].replace(distance_mapping)

distance_order = ["0-1 km", "1-2 km", "2-5 km", "5-10 km", "10+ km"]

distance_summary = (
    df.groupby("Distance Band", observed=False)["Purchase Flag"]
    .mean()
    .reindex(distance_order)
    .reset_index()
)

distance_summary["Access Status"] = distance_summary["Distance Band"].apply(
    lambda band: (
        "Strongest access segment" if band == "2-5 km"
        else "Access risk" if band == "10+ km"
        else "Other distance"
    )
)

fig_distance = px.bar(
    distance_summary,
    x="Distance Band",
    y="Purchase Flag",
    text="Purchase Flag",
    title="Purchase Rate by Access to Installation Services",
    color="Access Status",
    color_discrete_map={
        "Strongest access segment": GOLD,
        "Access risk": CORAL,
        "Other distance": TEAL
    },
    category_orders={"Distance Band": distance_order}
)

fig_distance.update_traces(
    texttemplate="%{text:.1%}",
    textposition="outside"
)

fig_distance.add_hline(
    y=overall_rate,
    line_dash="dash",
    line_color=NAVY
)

fig_distance.update_layout(
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    title_x=0.02,
    xaxis_title="Distance from nearest installer",
    yaxis_title="Purchase rate",
    yaxis_tickformat=".0%",
    yaxis_range=[0, 0.70],
    margin=dict(t=70, r=40)
)

st.plotly_chart(fig_distance, use_container_width=True)

st.caption("Dashed horizontal line = overall purchase rate of 48.2%.")

st.info(
    "Access matters: purchase rates are strongest within 5 km of an installer, "
    "but fall sharply beyond this point. SunVolt should reduce this barrier "
    "through mobile installation teams, local installer partnerships and "
    "remote consultations for customers further away."
)

st.divider()



# SECTION 6: MANAGEMENT ACTION PLAN

st.subheader("4. Management Action Plan")

st.markdown(
    "The dashboard findings point to three practical priorities for increasing "
    "solar-system adoption and using resources more effectively."
)

action_1, action_2, action_3 = st.columns(3)

with action_1:
    st.markdown(
        f"""
        <div style="
            background-color: white;
            border-left: 7px solid {GOLD};
            border-radius: 10px;
            padding: 22px;
            min-height: 240px;">
            <h3 style="color: {NAVY};">01. Focus growth investment</h3>
            <p><b>Priority:</b> Target customers aged 30–39 and those earning R30k–R49k.</p>
            <p><b>Action:</b> Use targeted digital campaigns and tailored package offers for these high-adoption groups.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with action_2:
    st.markdown(
        f"""
        <div style="
            background-color: white;
            border-left: 7px solid {CORAL};
            border-radius: 10px;
            padding: 22px;
            min-height: 240px;">
            <h3 style="color: {NAVY};">02. Improve conversion</h3>
            <p><b>Priority:</b> North America has the highest sales volume but the lowest purchase rate.</p>
            <p><b>Action:</b> Test local promotions, flexible financing and personalised consultations to improve conversion.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with action_3:
    st.markdown(
        f"""
        <div style="
            background-color: white;
            border-left: 7px solid {TEAL};
            border-radius: 10px;
            padding: 22px;
            min-height: 240px;">
            <h3 style="color: {NAVY};">03. Reduce access barriers</h3>
            <p><b>Priority:</b> Adoption falls substantially for customers living more than 5 km from an installer.</p>
            <p><b>Action:</b> Use mobile installation teams, local partners and remote consultations in distant areas.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
f"""<div style="background-color: #E8F2F5; border-left: 8px solid {GOLD}; border-radius: 14px; padding: 28px 32px; margin-top: 20px; box-shadow: 0 8px 20px rgba(31, 78, 95, 0.12);">
<div style="font-size: 14px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 10px;">EXECUTIVE TAKEAWAY · NEXT 90 DAYS</div>
<div style="font-size: 27px; font-weight: 700; line-height: 1.3; margin-bottom: 18px;">Convert North America, scale Pacific and remove installation-access barriers.</div>
<div style="font-size: 17px; line-height: 1.6; margin-bottom: 22px;">SunVolt should direct investment towards high-adoption customer groups, test conversion-focused offers in North America, and expand service access for customers located further from installers.</div>
<div>
<span style="background-color: #FFF5D6; border: 1px solid {GOLD}; border-radius: 20px; padding: 7px 13px; font-size: 14px; margin-right: 8px;">Pacific: sustain capacity</span>
<span style="background-color: #FBE7E9; border: 1px solid {CORAL}; border-radius: 20px; padding: 7px 13px; font-size: 14px; margin-right: 8px;">North America: improve conversion</span>
<span style="background-color: #DCECF3; border: 1px solid {TEAL}; border-radius: 20px; padding: 7px 13px; font-size: 14px;">Distant areas: improve access</span>
</div>
</div>""",
unsafe_allow_html=True
)