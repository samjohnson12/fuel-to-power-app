
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from fuel2power.tech import TECH_SPECS

from fuel2power.units import (
    FuelDefaults,
    diesel_gal_per_day_to_btu_per_day,
    mmbtu_per_day_to_btu_per_day,
    dth_per_day_to_mmbtu_per_day,
    mcf_per_day_to_mmbtu_per_day,
    btu_per_day_to_mmbtu_per_day,
    btu_per_day_to_diesel_gal_per_day,
    btu_per_day_to_dth_per_day,
    btu_per_day_to_mcf_per_day,
)
from fuel2power.calc import compute_power, compute_required_fuel_energy


st.set_page_config(page_title="Fuel → Power (kW) Calculator", layout="wide")

st.title("Fuel → Power (kW) Calculator")
st.caption("Convert available diesel or natural gas fuel per day into electrical power using technology heat rates.")

# Sidebar: scenario inputs
st.sidebar.header("Scenario Inputs")

fuel_type = st.sidebar.selectbox("Fuel type", ["Natural Gas", "Diesel"])

defaults = FuelDefaults()

# Heating value / conversion defaults (editable)
with st.sidebar.expander("Fuel property assumptions (editable)", expanded=False):
    diesel_btu_per_gal = st.number_input("Diesel BTU/gal", min_value=50_000.0, max_value=200_000.0, value=float(defaults.diesel_btu_per_gal), step=500.0)
    ng_btu_per_scf = st.number_input("Natural gas BTU/scf", min_value=700.0, max_value=1_400.0, value=float(defaults.ng_btu_per_scf), step=1.0)
    dth_to_mmbtu = st.number_input("Dekatherm → MMBtu factor", min_value=0.90, max_value=1.10, value=float(defaults.dth_to_mmbtu), step=0.001)
    st.caption("Conversion factors sourced from [EIA Energy Conversion Calculators](https://www.eia.gov/energyexplained/units-and-calculators/energy-conversion-calculators.php)")

# Fuel quantity input
st.sidebar.subheader("Fuel available (per day)")
if fuel_type == "Diesel":
    diesel_gal_per_day = st.sidebar.number_input("Diesel gallons/day", min_value=0.0, value=0.0, step=10.0)
    btu_per_day = diesel_gal_per_day_to_btu_per_day(diesel_gal_per_day, diesel_btu_per_gal)
    fuel_display = f"{diesel_gal_per_day:,.2f} gal/day"
else:
    ng_unit = st.sidebar.selectbox("Natural gas input units", ["MMBtu/day", "Dekatherms/day", "MCF/day"])
    ng_value = st.sidebar.number_input(f"Natural gas ({ng_unit})", min_value=0.0, value=0.0, step=10.0)

    if ng_unit == "MMBtu/day":
        btu_per_day = mmbtu_per_day_to_btu_per_day(ng_value)
        fuel_display = f"{ng_value:,.2f} MMBtu/day"
    elif ng_unit == "Dekatherms/day":
        mmbtu_day = dth_per_day_to_mmbtu_per_day(ng_value, dth_to_mmbtu)
        btu_per_day = mmbtu_per_day_to_btu_per_day(mmbtu_day)
        fuel_display = f"{ng_value:,.2f} Dth/day"
    else:  # MCF/day
        mmbtu_day = mcf_per_day_to_mmbtu_per_day(ng_value, ng_btu_per_scf)
        btu_per_day = mmbtu_per_day_to_btu_per_day(mmbtu_day)
        fuel_display = f"{ng_value:,.2f} MCF/day"

st.sidebar.subheader("Operating Profile")
hours_per_day = st.sidebar.slider("Hours of operation per day", min_value=1, max_value=24, value=24, step=1)

st.sidebar.subheader("Technology")
tech_names = list(TECH_SPECS.keys())
selected_techs = st.sidebar.multiselect(
    "Select one or more technologies to compare",
    options=tech_names,
    default=[tech_names[0]],
)

# Heat rate overrides
heat_rate_overrides = {}
with st.sidebar.expander("Heat rate assumptions (editable)", expanded=False):
    for tech_key in selected_techs:
        spec = TECH_SPECS[tech_key]
        heat_rate_overrides[tech_key] = st.number_input(
            f"{spec.name} heat rate (BTU/kWh)",
            min_value=1_000.0,
            max_value=30_000.0,
            value=float(spec.default_heat_rate_btu_per_kwh),
            step=50.0,
            key=f"hr_{tech_key}",
        )

# Main panel
st.subheader("Results")

if selected_techs:
    results = []
    for tech_key in selected_techs:
        spec = TECH_SPECS[tech_key]
        hr = heat_rate_overrides[tech_key]

        pr = compute_power(btu_per_day=btu_per_day, heat_rate_btu_per_kwh=hr, hours_per_day=hours_per_day)
        results.append(
            {
                "Technology": spec.name,
                "Heat rate used (BTU/kWh)": hr,
                "kWh/day": pr.kwh_per_day,
                "Avg kW (24h basis)": pr.avg_kw_24h,
                f"Operating kW ({hours_per_day} h/day)": pr.operating_kw,
            }
        )

    df = pd.DataFrame(results)
    st.dataframe(
        df.style.format(
            {
                "Heat rate used (BTU/kWh)": "{:,.0f}",
                "kWh/day": "{:,.0f}",
                "Avg kW (24h basis)": "{:,.0f}",
                f"Operating kW ({hours_per_day} h/day)": "{:,.0f}",
            }
        ),
        use_container_width=True,
    )

    # Operating kW comparison chart
    col1, col2 = st.columns([1, 1])

    # Prepare data for charts
    chart_df_heat = df[["Technology", "Heat rate used (BTU/kWh)"]].rename(columns={"Heat rate used (BTU/kWh)": "Value"})
    chart_df_kw = df[["Technology", f"Operating kW ({hours_per_day} h/day)"]].rename(columns={f"Operating kW ({hours_per_day} h/day)": "Value"})

    with col1:
        st.subheader("Heat Rate Comparison")
        chart1 = alt.Chart(chart_df_heat).mark_bar(size=40).encode(
            x=alt.X("Technology:N", axis=alt.Axis(labelAngle=0)),
            y="Value:Q",
            tooltip=["Technology", "Value:Q"]
        ).interactive()
        st.altair_chart(chart1, use_container_width=True)

    with col2:
        st.subheader("Operating kW Comparison")
        chart2 = alt.Chart(chart_df_kw).mark_bar(size=40).encode(
            x=alt.X("Technology:N", axis=alt.Axis(labelAngle=0)),
            y="Value:Q",
            tooltip=["Technology", "Value:Q"]
        ).interactive()
        st.altair_chart(chart2, use_container_width=True)

    # Inverse calculation: required fuel for target operating kW
    st.divider()
    st.subheader("Fuel required to meet a target operating level")

    with st.expander("Compute required fuel/day from target operating kW", expanded=True):
        tech_for_target = st.selectbox(
            "Technology for sizing fuel requirement",
            options=selected_techs if selected_techs else tech_names,
            index=0,
        )

        # Use the same heat rate override you already set in the sidebar
        hr_target = heat_rate_overrides.get(
            tech_for_target,
            float(TECH_SPECS[tech_for_target].default_heat_rate_btu_per_kwh),
        )

        target_operating_kw = st.number_input(
            f"Target operating kW (during the {hours_per_day} h/day run window)",
            min_value=0.0,
            value=10_000.0,
            step=500.0,
        )

        req = compute_required_fuel_energy(
            target_operating_kw=target_operating_kw,
            hours_per_day=hours_per_day,
            heat_rate_btu_per_kwh=hr_target,
        )

        st.write(
            {
                "Technology": TECH_SPECS[tech_for_target].name,
                "Heat rate used (BTU/kWh)": f"{hr_target:,.0f}",
                "Target operating kW": f"{target_operating_kw:,.0f}",
                "Hours/day": hours_per_day,
                "Required kWh/day": f"{req.required_kwh_per_day:,.0f}",
                "Required BTU/day": f"{req.required_btu_per_day:,.0f}",
            }
        )

        out_fuel_type = st.selectbox("Fuel type for output", ["Natural Gas", "Diesel"], index=0)

        if out_fuel_type == "Diesel":
            req_gal_day = btu_per_day_to_diesel_gal_per_day(req.required_btu_per_day, diesel_btu_per_gal)
            st.metric("Required diesel", f"{req_gal_day:,.0f} gal/day")
            
        else:
            out_ng_unit = st.selectbox(
                "Output NG units",
                ["MMBtu/day", "Dekatherms/day", "MCF/day"],
                index=0,
                key="out_ng_unit"   # recommended: prevents Streamlit widget collisions
            )

            if out_ng_unit == "MMBtu/day":
                req_val = btu_per_day_to_mmbtu_per_day(req.required_btu_per_day)
                st.metric("Required natural gas", f"{req_val:,.2f} MMBtu/day")

            elif out_ng_unit == "Dekatherms/day":
                req_val = btu_per_day_to_dth_per_day(req.required_btu_per_day, dth_to_mmbtu)
                st.metric("Required natural gas", f"{req_val:,.2f} Dth/day")

            else:  # "MCF/day"
                req_val = btu_per_day_to_mcf_per_day(req.required_btu_per_day, ng_btu_per_scf)
                st.metric("Required natural gas", f"{req_val:,.2f} MCF/day")

else:
    st.info("Please select at least one technology to see results and comparisons.")
