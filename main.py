import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import os

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Briefly AI 2025-2026 Roadmap",
    page_icon="🚀",
    layout="wide"
)

# ============================================================================
# PASSWORD
# ============================================================================
def check_password():
    def password_entered():
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == hashlib.sha256("BrieflyAI2026".encode()).hexdigest():
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔐 Password", type="password", on_change=password_entered, key="password")
        st.info("Enter password: BrieflyAI2026")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔐 Password", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect password")
        return False
    return True

# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data
def load_all_data():
    """Load all Excel files from repo"""
    data = {}
    
    # Load pipeline
    pipeline_files = [
        'AI_Tool_Request_Pipeline_1762382492.xlsx',
        'AI_Tool_Request_Pipeline_1762381302.xlsx'
    ]
    
    for f in pipeline_files:
        if os.path.exists(f):
            try:
                df = pd.read_excel(f, header=1)
                # Clean and process
                df = df.rename(columns={
                    df.columns[0]: 'Name',
                    df.columns[2]: 'Stakeholder',
                    df.columns[3]: 'Department',
                    df.columns[5]: 'Target_Quarter',
                    df.columns[7]: 'Tool',
                    df.columns[8]: 'Phase',
                    df.columns[9]: 'Priority'
                })
                df = df[df['Name'].notna()]
                df = df[~df['Name'].astype(str).str.contains('Name|Subitems|📥|🧭|💰|📈|💻', na=False)]
                data['pipeline'] = df.reset_index(drop=True)
                break
            except:
                pass
    
    # Load company roadmaps
    roadmap_files = [
        'AI_Roadmap_-_Accounting_-_Updated_10_1_2025.xlsx',
        'AI Roadmap - Accounting - Updated 10.1.2025.xlsx'
    ]
    
    for f in roadmap_files:
        if os.path.exists(f):
            try:
                xl = pd.ExcelFile(f)
                data['companies'] = {}
                for sheet in xl.sheet_names:
                    data['companies'][sheet.strip()] = pd.read_excel(f, sheet_name=sheet)
            except:
                pass
            break
    
    return data

def categorize_stage(phase):
    """Map phase to stage"""
    if pd.isna(phase):
        return 'Discovery'
    phase = str(phase).lower()
    if any(x in phase for x in ['discovery', 'intake']):
        return 'Discovery'
    elif any(x in phase for x in ['budget', 'buy', 'evaluation']):
        return 'Build vs Buy'
    elif any(x in phase for x in ['demo', 'poc']):
        return 'Initial Demo'
    elif 'pilot' in phase:
        return 'Piloting'
    elif any(x in phase for x in ['implement', 'rollout']):
        return 'Implementation'
    return 'Discovery'

def assign_quarter(row, idx, total):
    """Smart quarter assignment based on priority and stage"""
    if pd.notna(row.get('Target_Quarter')) and row['Target_Quarter'] != 'Not Assigned Yet':
        return row['Target_Quarter']
    
    stage = categorize_stage(row.get('Phase'))
    priority = str(row.get('Priority', 'P2')).upper()
    
    # P0 items go to Q1-Q2 2025
    if priority == 'P0':
        if stage in ['Discovery', 'Build vs Buy']:
            return 'Q1 2025'
        else:
            return 'Q2 2025'
    # P1 items go to Q2-Q3 2025
    elif priority == 'P1':
        if stage in ['Discovery', 'Build vs Buy']:
            return 'Q2 2025'
        else:
            return 'Q3 2025'
    # P2 items go to Q3-Q4 2025
    elif priority == 'P2':
        return 'Q3 2025' if idx % 2 == 0 else 'Q4 2025'
    # P3 items go to 2026
    else:
        return 'Q1 2026'

# ============================================================================
# VISUAL ROADMAP GENERATOR
# ============================================================================
def create_visual_roadmap(company_name, tools_df, roadmap_df):
    """Create visual roadmap with swimlanes like the example image"""
    
    quarters = ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
    quarter_positions = {q: i for i, q in enumerate(quarters)}
    
    # Define swimlanes (categories)
    swimlanes = [
        'Strategy & Planning',
        'Build vs Buy',
        'Initial Demo/POC',
        'Piloting',
        'Implementation',
        'Operations'
    ]
    
    # Color scheme
    colors = {
        'Strategy & Planning': '#3498db',
        'Build vs Buy': '#e74c3c',
        'Initial Demo/POC': '#f39c12',
        'Piloting': '#9b59b6',
        'Implementation': '#2ecc71',
        'Operations': '#1abc9c'
    }
    
    fig = go.Figure()
    
    # Process tools and assign to swimlanes
    for idx, row in tools_df.iterrows():
        stage = categorize_stage(row.get('Phase'))
        quarter = assign_quarter(row, idx, len(tools_df))
        
        if quarter not in quarter_positions:
            continue
        
        # Map stage to swimlane
        if stage == 'Discovery':
            swimlane = 'Strategy & Planning'
        elif stage == 'Build vs Buy':
            swimlane = 'Build vs Buy'
        elif stage == 'Initial Demo':
            swimlane = 'Initial Demo/POC'
        elif stage == 'Piloting':
            swimlane = 'Piloting'
        elif stage == 'Implementation':
            swimlane = 'Implementation'
        else:
            swimlane = 'Operations'
        
        y_pos = swimlanes.index(swimlane)
        x_start = quarter_positions[quarter]
        
        # Determine bar length based on stage
        if stage in ['Discovery', 'Build vs Buy']:
            duration = 1  # 1 quarter
        elif stage in ['Initial Demo', 'Piloting']:
            duration = 1.5  # 1.5 quarters
        else:
            duration = 2  # 2 quarters
        
        # Add bar
        fig.add_trace(go.Bar(
            name=row['Name'][:30],
            x=[duration],
            y=[swimlane],
            base=x_start,
            orientation='h',
            marker=dict(
                color=colors[swimlane],
                line=dict(color='white', width=2)
            ),
            text=row['Name'][:25],
            textposition='inside',
            textfont=dict(size=10, color='white'),
            hovertemplate=(
                f"<b>{row['Name']}</b><br>" +
                f"Stage: {stage}<br>" +
                f"Quarter: {quarter}<br>" +
                f"Priority: {row.get('Priority', 'N/A')}<br>" +
                f"Tool: {row.get('Tool', 'TBD')}<br>" +
                "<extra></extra>"
            ),
            showlegend=False
        ))
    
    # Layout
    fig.update_layout(
        title={
            'text': f'<b>{company_name} - AI Roadmap 2025-2026</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2c3e50'}
        },
        xaxis=dict(
            title='<b>Timeline</b>',
            tickmode='array',
            tickvals=list(range(len(quarters))),
            ticktext=quarters,
            gridcolor='rgba(200,200,200,0.3)',
            showgrid=True,
            range=[-0.5, len(quarters) - 0.5]
        ),
        yaxis=dict(
            title='',
            categoryorder='array',
            categoryarray=swimlanes[::-1],  # Reverse for top-to-bottom
            gridcolor='rgba(200,200,200,0.3)',
            showgrid=True
        ),
        barmode='overlay',
        height=600,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        hovermode='closest',
        margin=dict(l=200, r=50, t=100, b=50)
    )
    
    return fig

def create_summary_table(company_name, tools_df):
    """Create summary table for the company"""
    
    # Assign quarters if not set
    for idx, row in tools_df.iterrows():
        if pd.isna(row.get('Target_Quarter')) or row.get('Target_Quarter') == 'Not Assigned Yet':
            tools_df.at[idx, 'Target_Quarter'] = assign_quarter(row, idx, len(tools_df))
        if pd.isna(row.get('Stage')):
            tools_df.at[idx, 'Stage'] = categorize_stage(row.get('Phase'))
    
    summary = {
        'Quarter': [],
        'Stage': [],
        'Tool/Initiative': [],
        'Priority': [],
        'Status': []
    }
    
    for _, row in tools_df.iterrows():
        summary['Quarter'].append(row.get('Target_Quarter', 'TBD'))
        summary['Stage'].append(categorize_stage(row.get('Phase')))
        summary['Tool/Initiative'].append(row['Name'][:50])
        summary['Priority'].append(row.get('Priority', 'P2'))
        summary['Status'].append(row.get('Phase', 'Discovery'))
    
    return pd.DataFrame(summary)

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    if not check_password():
        return
    
    # Header
    st.title("🚀 Briefly AI 2025-2026 Roadmap")
    st.markdown("**Visual Product Roadmaps by Company**")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data from repository..."):
        data = load_all_data()
    
    if 'pipeline' not in data:
        st.error("❌ No pipeline data found. Please add Excel files to the repository.")
        return
    
    pipeline_df = data['pipeline']
    companies_data = data.get('companies', {})
    
    st.success(f"✅ Loaded {len(pipeline_df)} tool requests")
    
    # Get unique companies from pipeline
    if 'Stakeholder' in pipeline_df.columns:
        companies = pipeline_df['Stakeholder'].dropna().unique()
    else:
        companies = ['Caravel', 'Rimon', 'OGC', 'Scale', 'Briefly']
    
    # Add "All Companies" view
    view_options = ['📊 All Companies Overview'] + [f'🏢 {c}' for c in companies]
    selected_view = st.selectbox("Select View", view_options, index=0)
    
    st.markdown("---")
    
    # ========================================================================
    # ALL COMPANIES OVERVIEW
    # ========================================================================
    if selected_view == '📊 All Companies Overview':
        st.header("All Companies - Consolidated Roadmap")
        
        # Assign quarters and stages to all tools
        for idx, row in pipeline_df.iterrows():
            if pd.isna(row.get('Target_Quarter')) or row.get('Target_Quarter') == 'Not Assigned Yet':
                pipeline_df.at[idx, 'Target_Quarter'] = assign_quarter(row, idx, len(pipeline_df))
            if pd.isna(row.get('Stage')):
                pipeline_df.at[idx, 'Stage'] = categorize_stage(row.get('Phase'))
        
        # Create consolidated roadmap
        fig = create_visual_roadmap('All Companies', pipeline_df, None)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Initiatives", len(pipeline_df))
        with col2:
            p0_count = len(pipeline_df[pipeline_df['Priority'].astype(str).str.upper() == 'P0'])
            st.metric("P0 Critical", p0_count)
        with col3:
            q1_count = len(pipeline_df[pipeline_df['Target_Quarter'] == 'Q1 2025'])
            st.metric("Q1 2025", q1_count)
        with col4:
            companies_count = pipeline_df['Stakeholder'].nunique() if 'Stakeholder' in pipeline_df.columns else len(companies)
            st.metric("Companies", companies_count)
        
        st.markdown("---")
        st.subheader("📋 All Tools by Quarter")
        
        summary_df = create_summary_table('All Companies', pipeline_df)
        summary_df = summary_df.sort_values(['Quarter', 'Priority'])
        
        st.dataframe(summary_df, use_container_width=True, height=400)
        
        # Export
        csv = summary_df.to_csv(index=False)
        st.download_button(
            "📥 Download Full Roadmap (CSV)",
            csv,
            f"briefly_all_companies_roadmap_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
    
    # ========================================================================
    # INDIVIDUAL COMPANY VIEW
    # ========================================================================
    else:
        company_name = selected_view.replace('🏢 ', '')
        st.header(f"{company_name} - AI Roadmap 2025-2026")
        
        # Filter tools for this company
        if 'Stakeholder' in pipeline_df.columns:
            company_tools = pipeline_df[
                pipeline_df['Stakeholder'].astype(str).str.contains(company_name, case=False, na=False)
            ].copy()
        else:
            # Distribute tools if no stakeholder info
            company_tools = pipeline_df[pipeline_df.index % len(companies) == list(companies).index(company_name)].copy()
        
        if len(company_tools) == 0:
            st.warning(f"No tools assigned to {company_name} yet")
            return
        
        # Assign quarters and stages
        for idx, row in company_tools.iterrows():
            if pd.isna(row.get('Target_Quarter')) or row.get('Target_Quarter') == 'Not Assigned Yet':
                company_tools.at[idx, 'Target_Quarter'] = assign_quarter(row, idx, len(company_tools))
            if pd.isna(row.get('Stage')):
                company_tools.at[idx, 'Stage'] = categorize_stage(row.get('Phase'))
        
        # Get company-specific roadmap data if available
        company_roadmap = companies_data.get(company_name, None)
        
        # Create visual roadmap
        fig = create_visual_roadmap(company_name, company_tools, company_roadmap)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Company stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tools", len(company_tools))
        with col2:
            p0_count = len(company_tools[company_tools['Priority'].astype(str).str.upper() == 'P0'])
            st.metric("P0 Priority", p0_count)
        with col3:
            stages = company_tools['Stage'].nunique()
            st.metric("Active Stages", stages)
        with col4:
            q1_count = len(company_tools[company_tools['Target_Quarter'] == 'Q1 2025'])
            st.metric("Q1 2025", q1_count)
        
        st.markdown("---")
        
        # Detailed table
        st.subheader(f"📋 {company_name} Tools by Quarter")
        
        summary_df = create_summary_table(company_name, company_tools)
        summary_df = summary_df.sort_values(['Quarter', 'Priority'])
        
        st.dataframe(summary_df, use_container_width=True, height=400)
        
        # Company roadmap details if available
        if company_roadmap is not None:
            st.markdown("---")
            st.subheader(f"📄 {company_name} Detailed Roadmap")
            with st.expander("View Full Roadmap Details", expanded=False):
                st.dataframe(company_roadmap, use_container_width=True, height=400)
        
        # Export
        csv = summary_df.to_csv(index=False)
        st.download_button(
            f"📥 Download {company_name} Roadmap (CSV)",
            csv,
            f"briefly_{company_name}_roadmap_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

if __name__ == "__main__":
    main()
