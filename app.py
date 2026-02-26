import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="GPS Positional Report")

# --- HEADER (NO LOGOS, NO TENNESSEE) ---
st.markdown(f"""
<style>
.main {{ background-color: #0E1117; }}
.block-container {{ padding-top: 2rem !important; }}
.header-title {{ 
    color: #FFFFFF; 
    font-family: 'Arial Black'; 
    font-size: 34px; 
    text-transform: uppercase; 
    text-align: center;
    margin-top: 20px;
}}
.header-subtitle {{ 
    color: #818589; 
    font-size: 20px; 
    text-align: center; 
    margin-top: 10px; 
    font-weight: bold; 
}}
th, td {{ 
    text-align: center !important; 
    vertical-align: middle !important; 
    border: 1px solid #444; 
}}
div[data-testid="stMetricValue"] {{ 
    font-size: 34px !important; 
    font-weight: bold; 
}}
</style>

<h1 class="header-title">Daily GPS Performance Report</h1>
""", unsafe_allow_html=True)

# --- SESSION CONFIGURATION ---
st.markdown("###Session Intensity")
c_set1, c_set2 = st.columns([1, 2])
with c_set1:
    intensity_choice = st.selectbox("Select Session Intensity", ["High Intensity", "Medium Intensity", "Low Intensity"])
with c_set2:
    practice_label = st.text_input("Practice Label", "Session Summary")

intensity_config = {
    "High Intensity": {"vel_target": 90, "color": "#FF8200", "low_color": "#58595B"},
    "Medium Intensity": {"vel_target": 90, "color": "#D4A017", "low_color": "#58595B"},
    "Low Intensity": {"vel_target": 90, "color": "#2E7D32", "low_color": "#58595B"}
}
conf = intensity_config[intensity_choice]

# --- FINAL TARGET LOGIC ---
def get_targets(pos_name, intensity):
    speed_pos_group = ['CB', 'WR']
    
    if intensity == "High Intensity":
        return (500, 400) if pos_name in ['CB', 'S', 'WR'] else (450, 300)
    elif intensity == "Medium Intensity":
        return (450, 175) if pos_name in speed_pos_group else (400, 175)
    else: 
        return (400, 100) if pos_name in speed_pos_group else (350, 100)

st.markdown(
    f"<div class='header-subtitle'>{practice_label} - <span style='color:{conf['color']}'>{intensity_choice}</span></div>", 
    unsafe_allow_html=True
)

# --- SIDEBAR ---
print_all = st.sidebar.checkbox("Prepare All Positions for Printing")
uploaded_file = st.file_uploader("Upload Excel Export", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file).round(1)
    df.columns = df.columns.str.strip()

    # --- NAME FORMATTING ---
    def generate_smart_label(name, all_names):
        try:
            parts = str(name).split()
            first, last = parts[0], parts[-1]
            same_last = [n for n in all_names if str(n).split()[-1] == last and n != name]
            return f"{last}, {first[:2]}." if len(same_last) > 0 else f"{last}, {first[0]}."
        except:
            return str(name)

    df['Display Name'] = df['Name'].apply(lambda x: generate_smart_label(x, df['Name'].tolist()))

    # --- CALCULATIONS ---
    hsd_cols = ['60-75% Dist', '82%+ Distance Tempo1 (y)', '82-90% Dist']
    df['HSD (60%+)'] = df[[c for c in hsd_cols if c in df.columns]].fillna(0).sum(axis=1)

    accel_cols = ['Acceleration B1 Efforts (Gen 2)', 'Acceleration B2 Efforts (Gen 2)', 'Acceleration B3 Efforts (Gen 2)']
    decel_cols = ['Deceleration B1 Efforts (Gen 2)', 'Deceleration B2 Efforts (Gen 2)', 'Deceleration B3 Efforts (Gen 2)']
    df['Accel Efforts'] = df[[c for c in accel_cols if c in df.columns]].fillna(0).sum(axis=1)
    df['Decel Efforts'] = df[[c for c in decel_cols if c in df.columns]].fillna(0).sum(axis=1)
    df['Total Explosive Work'] = df['Accel Efforts'] + df['Decel Efforts']

    # --- POSITION REPORT ---
    def render_position_report(pos_name):
        pos_df = df[df['Position Name'] == pos_name].copy().sort_values('Display Name')
        t_load, t_hsd = get_targets(pos_name, intensity_choice)

        st.header(f"{pos_name} Performance")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Avg Load", f"{round(pos_df['Total Player Load'].mean(), 1)} / {t_load}")
        m2.metric("Avg HSD", f"{round(pos_df['HSD (60%+)'].mean(), 1)}y")
        m3.metric("Avg Explosive", int(pos_df['Total Explosive Work'].mean()))
        m4.metric(f"{conf['vel_target']}% Compliance", f"{len(pos_df[pos_df['Max Vel (% Max)'] >= conf['vel_target']])} Athletes")

        # Elite/Grinder Lists
        hi_vol_speed = pos_df[(pos_df['Max Vel (% Max)'] >= conf['vel_target']) & (pos_df['Total Player Load'] >= t_load)]
        hi_vol_grinders = pos_df[(pos_df['Max Vel (% Max)'] < conf['vel_target']) & (pos_df['Total Player Load'] >= t_load)]

        qc1, qc2 = st.columns(2)
        with qc1:
            st.subheader("High Intensity / High Volume")
            st.write(", ".join(hi_vol_speed['Display Name'].astype(str).tolist()) if not hi_vol_speed.empty else "None")
        with qc2:
            st.subheader("High Volume Grinders")
            st.write(", ".join(hi_vol_grinders['Display Name'].astype(str).tolist()) if not hi_vol_grinders.empty else "None")
        st.divider()

        # Scatter Plot
        s_colors = [conf['color'] if (r['Max Vel (% Max)'] >= conf['vel_target'] and r['Total Player Load'] >= t_load) else conf['low_color'] for i, r in pos_df.iterrows()]
        fig_speed = go.Figure(go.Scatter(
            x=pos_df['Total Player Load'] + np.random.uniform(-0.3, 0.3, size=len(pos_df)), 
            y=pos_df['Max Vel (% Max)'], mode='markers+text', text=pos_df['Display Name'], textposition='top center',
            marker=dict(size=14, color=s_colors, line=dict(width=1, color='white')), showlegend=False
        ))
        fig_speed.add_vline(x=t_load, line_dash="dot", line_color=conf['color'])
        fig_speed.add_hline(y=conf['vel_target'], line_dash="dot", line_color=conf['color'])
        fig_speed.update_layout(title="Volume vs Top Speed", template='plotly_dark', xaxis_title="Total Player Load", yaxis_title="Max Velocity (% Max)", height=450)
        st.plotly_chart(fig_speed, use_container_width=True)

        # HSD / Explosive Plots
        c1, c2 = st.columns(2)
        with c1:
            h_colors = [conf['color'] if y >= t_hsd else conf['low_color'] for y in pos_df['HSD (60%+)']]
            st.plotly_chart(go.Figure(go.Bar(x=pos_df['Display Name'], y=pos_df['HSD (60%+)'], marker_color=h_colors)).update_layout(title="HSD (60%+)", template='plotly_dark', xaxis_title="", height=400), use_container_width=True)
        with c2:
            fig_exp = go.Figure()
            exp_map = {'Band 1': '#E5E5E5', 'Band 2': '#FF8200', 'Band 3': '#212121'}
            for b in [1, 2, 3]:
                fig_exp.add_trace(go.Bar(x=pos_df['Display Name'], y=pos_df[f'Acceleration B{b} Efforts (Gen 2)'], name=f'Band {b}', marker_color=exp_map[f'Band {b}'], offsetgroup=0, legendgroup=f'Band {b}'))
                fig_exp.add_trace(go.Bar(x=pos_df['Display Name'], y=pos_df[f'Deceleration B{b} Efforts (Gen 2)'], name=f'Band {b}', marker_color=exp_map[f'Band {b}'], offsetgroup=1, legendgroup=f'Band {b}', showlegend=False))
            st.plotly_chart(fig_exp.update_layout(title="Explosive Split (A/D)", barmode='stack', template='plotly_dark', height=400, xaxis_title="", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)), use_container_width=True)

        # Roster Table
        display_metrics = ['Display Name', 'Total Player Load', 'HSD (60%+)', 'Accel Efforts', 'Decel Efforts', 'Total Explosive Work', 'Maximum Velocity (mph)', 'Max Vel (% Max)']
        def final_styling(row):
            styles = [''] * len(row)
            for col, target, idx in [('Total Player Load', t_load, 1), ('HSD (60%+)', t_hsd, 2)]:
                val = row[col]
                if val > target:
                    styles[idx] = 'background-color: #990000; color: white; font-weight: bold'
                elif target * 0.85 <= val <= target:
                    styles[idx] = 'background-color: #006600; color: white; font-weight: bold' 
                elif val < target * 0.85:
                    styles[idx] = 'background-color: #CC9900; color: black; font-weight: bold' 
            if row['Max Vel (% Max)'] >= 90:
                styles[7] = 'background-color: #006600; color: white; font-weight: bold'
            return styles
        st.table(pos_df[display_metrics].reset_index(drop=True).style.apply(final_styling, axis=1).format(precision=1))

    # --- TEAM OVERVIEW ---
    tabs = st.tabs(["Team Overview"] + sorted(df['Position Name'].unique()))
    with tabs[0]:
        st.header(f"Team Summary - {intensity_choice}")
        tc1, tc2, tc3 = st.columns(3)
        tc1.metric("Avg Player Load", round(df['Total Player Load'].mean(), 1))
        tc2.metric("Avg HSD", f"{round(df['HSD (60%+)'].mean(), 1)}y")
        tc3.metric("Avg Explosive Efforts", int(df['Total Explosive Work'].mean()))
        st.divider()
        team_summary = df.groupby('Position Name')[['Total Player Load', 'HSD (60%+)']].mean().reset_index()
        team_h_colors = [conf['color'] if r['HSD (60%+)'] >= get_targets(r['Position Name'], intensity_choice)[1] else conf['low_color'] for _, r in team_summary.iterrows()]
        team_l_colors = [conf['color'] if r['Total Player Load'] >= get_targets(r['Position Name'], intensity_choice)[0] else conf['low_color'] for _, r in team_summary.iterrows()]
        st.plotly_chart(go.Figure(go.Bar(x=team_summary['Position Name'], y=team_summary['HSD (60%+)'], marker_color=team_h_colors)).update_layout(title="Avg. HSD by Position", template='plotly_dark', height=400), use_container_width=True)
        st.plotly_chart(go.Figure(go.Bar(x=team_summary['Position Name'], y=team_summary['Total Player Load'], marker_color=team_l_colors)).update_layout(title="Avg. Player Load by Position", template='plotly_dark', height=400), use_container_width=True)

    for i, pos in enumerate(sorted(df['Position Name'].unique())):
        with tabs[i + 1]:
            render_position_report(pos)
else:
    st.info("Awaiting Data...")
