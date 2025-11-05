import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import io

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Briefly AI 2025-2026 Roadmap",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# AUTHENTICATION
# ============================================================================
def check_password():
    """Password protection - BrieflyAI2026"""
    def password_entered():
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == hashlib.sha256("BrieflyAI2026".encode()).hexdigest():
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔐 Password", type="password", on_change=password_entered, key="password")
        st.info("Enter password to access the Briefly AI Roadmap")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔐 Password", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect password")
        return False
    else:
        return True

# ============================================================================
# CUSTOM STYLING
# ============================================================================
st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #e0e0e0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: 600;
        color: #555;
        border-radius: 8px 8px 0 0;
        transition: all 0.3s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f2f6;
        color: #1f77b4;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white !important;
    }
    
    /* Headers */
    h1 {
        color: #1f77b4;
        padding-bottom: 1rem;
        font-size: 3rem !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    h2 {
        color: #2c3e50;
        padding-top: 1.5rem;
        font-weight: 600;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    h3 {
        color: #34495e;
        font-weight: 600;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
    }
    
    /* Cards */
    .roadmap-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Stage badges */
    .stage-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    /* Priority indicators */
    .priority-p0 { color: #e74c3c; font-weight: 700; }
    .priority-p1 { color: #f39c12; font-weight: 600; }
    .priority-p2 { color: #3498db; font-weight: 500; }
    .priority-p3 { color: #95a5a6; font-weight: 400; }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 2px solid #ecf0f1;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'tool_requests' not in st.session_state:
    st.session_state.tool_requests = None
if 'roadmap_data' not in st.session_state:
    st.session_state.roadmap_data = None
if 'quarters' not in st.session_state:
    st.session_state.quarters = [
        'Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025',
        'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026'
    ]
if 'stage_order' not in st.session_state:
    st.session_state.stage_order = [
        'Discovery',
        'Build vs Buy',
        'Initial Demo',
        'Piloting',
        'Implementation'
    ]
if 'changes_made' not in st.session_state:
    st.session_state.changes_made = False

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================
def load_tool_requests(file):
    """
    Load and process tool request pipeline data
    Handles various Excel formats automatically
    """
    try:
        # Try reading the file
        df = pd.read_excel(file, header=1)
        
        # Smart column mapping - handles variations in column names
        col_mapping = {}
        for col in df.columns:
            col_str = str(col).lower()
            if 'name' in col_str and 'tool' not in col_str and 'Name' not in col_mapping.values():
                col_mapping[col] = 'Name'
            elif 'department' in col_str:
                col_mapping[col] = 'Department'
            elif 'quarter' in col_str or 'target' in col_str and 'Quarter' not in col_str:
                col_mapping[col] = 'Target_Quarter'
            elif 'stage' in col_str or 'phase' in col_str:
                col_mapping[col] = 'Phase'
            elif 'priorit' in col_str and 'score' not in col_str:
                col_mapping[col] = 'Priority'
            elif 'tool' in col_str and 'potential' in col_str:
                col_mapping[col] = 'Tool'
            elif 'budget' in col_str:
                col_mapping[col] = 'Budget'
            elif 'stakeholder' in col_str or 'requesting' in col_str:
                col_mapping[col] = 'Stakeholder'
            elif 'status' in col_str and 'evaluation' in col_str:
                col_mapping[col] = 'Status'
            elif 'review' in col_str:
                col_mapping[col] = 'Reviewed_By'
            elif 'note' in col_str:
                col_mapping[col] = 'Notes'
            elif 'score' in col_str:
                col_mapping[col] = 'Score'
        
        df = df.rename(columns=col_mapping)
        
        # Ensure all required columns exist
        required_columns = {
            'Name': None,
            'Department': 'Not Assigned',
            'Target_Quarter': 'Not Assigned',
            'Phase': 'Discovery',
            'Priority': 'P2',
            'Stage': 'Discovery'
        }
        
        for col, default in required_columns.items():
            if col not in df.columns:
                df[col] = default
        
        # Clean the data
        df = df[df['Name'].notna()].copy()
        
        # Remove header/label rows
        df = df[~df['Name'].astype(str).str.contains(
            'Name|Subitems|📥|🧭|💰|📈|💻|New Requests|Operations|Accounting|Sales|Marketing|IT|Back Office',
            case=False,
            na=False
        )]
        
        df = df.reset_index(drop=True)
        
        # Standardize and clean values
        df['Target_Quarter'] = df['Target_Quarter'].fillna('Not Assigned')
        df['Target_Quarter'] = df['Target_Quarter'].replace('Not Assigned Yet', 'Not Assigned')
        df['Priority'] = df['Priority'].fillna('P2')
        df['Priority'] = df['Priority'].astype(str).str.upper()
        
        # Create Stage column from Phase if needed
        if 'Stage' not in df.columns or df['Stage'].isna().all():
            df['Stage'] = df['Phase'].apply(categorize_stage)
        else:
            df['Stage'] = df['Stage'].apply(lambda x: categorize_stage(x) if pd.notna(x) else 'Discovery')
        
        # Add ID column for tracking
        df['ID'] = range(len(df))
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading tool requests: {str(e)}")
        st.error("Please ensure your Excel file has the correct format.")
        return None

def categorize_stage(phase):
    """
    Intelligently categorize phase text into standard stages
    """
    if pd.isna(phase):
        return 'Discovery'
    
    phase_lower = str(phase).lower()
    
    # Check for each stage keyword
    if any(word in phase_lower for word in ['discovery', 'intake', 'new', 'exploring', 'initial']):
        return 'Discovery'
    elif any(word in phase_lower for word in ['budget', 'evaluation', 'buy', 'build', 'compare', 'vendor']):
        return 'Build vs Buy'
    elif any(word in phase_lower for word in ['demo', 'poc', 'proof', 'concept', 'test']):
        return 'Initial Demo'
    elif any(word in phase_lower for word in ['pilot', 'trial', 'beta']):
        return 'Piloting'
    elif any(word in phase_lower for word in ['implement', 'rollout', 'deploy', 'production', 'launch']):
        return 'Implementation'
    else:
        return 'Discovery'

def load_roadmap_data(file):
    """
    Load company-specific roadmap data from multi-sheet Excel
    """
    try:
        xl = pd.ExcelFile(file)
        roadmaps = {}
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet_name)
            roadmaps[sheet_name.strip()] = df
        
        return roadmaps
        
    except Exception as e:
        st.error(f"❌ Error loading roadmap data: {str(e)}")
        return None

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================
def create_gantt_chart(df):
    """
    Create an advanced interactive Gantt chart with beautiful styling
    """
    valid_df = df[(df['Target_Quarter'].notna()) & (df['Target_Quarter'] != 'Not Assigned')].copy()
    
    if valid_df.empty:
        return None
    
    # Create quarter mapping
    quarter_order = {q: i for i, q in enumerate(st.session_state.quarters)}
    
    # Prepare Gantt data
    gantt_data = []
    for idx, row in valid_df.iterrows():
        quarter = row['Target_Quarter']
        if quarter in quarter_order:
            gantt_data.append({
                'Task': row['Name'][:50] + ('...' if len(row['Name']) > 50 else ''),
                'Full_Name': row['Name'],
                'Start': quarter_order[quarter],
                'Duration': 1,
                'Department': row.get('Department', 'Unknown'),
                'Stage': row.get('Stage', 'Discovery'),
                'Priority': row.get('Priority', 'P2'),
                'Quarter': quarter,
                'Tool': row.get('Tool', 'TBD'),
                'Stakeholder': row.get('Stakeholder', 'N/A')
            })
    
    if not gantt_data:
        return None
    
    gantt_df = pd.DataFrame(gantt_data)
    
    # Beautiful stage colors
    stage_colors = {
        'Discovery': '#FF6B9D',          # Pink
        'Build vs Buy': '#4ECDC4',      # Turquoise
        'Initial Demo': '#95E1D3',      # Mint
        'Piloting': '#C7CEEA',          # Lavender
        'Implementation': '#FFA07A'     # Coral
    }
    
    # Create figure
    fig = go.Figure()
    
    # Add bars for each stage
    for stage in st.session_state.stage_order:
        stage_data = gantt_df[gantt_df['Stage'] == stage]
        if len(stage_data) > 0:
            fig.add_trace(go.Bar(
                name=stage,
                y=stage_data['Task'],
                x=stage_data['Duration'],
                base=stage_data['Start'],
                orientation='h',
                marker=dict(
                    color=stage_colors.get(stage, '#CCCCCC'),
                    line=dict(color='rgba(255,255,255,0.8)', width=3),
                    pattern_shape=""
                ),
                text=stage_data['Priority'],
                textposition='inside',
                textfont=dict(size=11, color='white', family='Arial Black'),
                hovertemplate=(
                    '<b>%{customdata[0]}</b><br><br>' +
                    '<b>Stage:</b> ' + stage + '<br>' +
                    '<b>Quarter:</b> %{customdata[1]}<br>' +
                    '<b>Priority:</b> %{customdata[2]}<br>' +
                    '<b>Department:</b> %{customdata[3]}<br>' +
                    '<b>Tool:</b> %{customdata[4]}<br>' +
                    '<b>Stakeholder:</b> %{customdata[5]}<br>' +
                    '<extra></extra>'
                ),
                customdata=stage_data[['Full_Name', 'Quarter', 'Priority', 'Department', 'Tool', 'Stakeholder']].values
            ))
    
    # Layout with beautiful styling
    fig.update_layout(
        title={
            'text': '<b>🗓️ Product Roadmap Timeline 2025-2026</b>',
            'font': {'size': 28, 'color': '#1f77b4', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title='<b>Quarter</b>',
            titlefont=dict(size=16, color='#2c3e50'),
            tickmode='array',
            tickvals=list(range(len(st.session_state.quarters))),
            ticktext=st.session_state.quarters,
            tickfont=dict(size=12, color='#34495e'),
            gridcolor='rgba(200,200,200,0.3)',
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            title='',
            autorange='reversed',
            tickfont=dict(size=11, color='#2c3e50'),
            showgrid=True,
            gridcolor='rgba(200,200,200,0.2)'
        ),
        barmode='stack',
        height=max(600, len(gantt_df) * 40),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#bdc3c7',
            borderwidth=2,
            font=dict(size=12, color='#2c3e50')
        ),
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='white',
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='white',
            font_size=13,
            font_family='Arial'
        )
    )
    
    return fig

def create_stage_funnel(df):
    """
    Create a beautiful stage funnel showing pipeline progression
    """
    stage_counts = df['Stage'].value_counts()
    
    funnel_data = []
    for stage in st.session_state.stage_order:
        count = stage_counts.get(stage, 0)
        funnel_data.append({'Stage': stage, 'Count': count})
    
    funnel_df = pd.DataFrame(funnel_data)
    
    colors = ["#FF6B9D", "#4ECDC4", "#95E1D3", "#C7CEEA", "#FFA07A"]
    
    fig = go.Figure(go.Funnel(
        y=funnel_df['Stage'],
        x=funnel_df['Count'],
        textinfo="value+percent initial",
        textfont=dict(size=14, color='white', family='Arial Black'),
        marker={
            "color": colors,
            "line": {"width": 3, "color": "white"}
        },
        connector={"line": {"color": "#7f8c8d", "width": 3, "dash": "dot"}}
    ))
    
    fig.update_layout(
        title={
            'text': '<b>📊 Tool Request Pipeline</b>',
            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=500,
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='white',
        font=dict(size=13, color='#2c3e50')
    )
    
    return fig

def create_department_chart(df):
    """
    Create a beautiful department distribution pie chart
    """
    dept_counts = df['Department'].value_counts()
    
    colors = px.colors.qualitative.Set3
    
    fig = px.pie(
        values=dept_counts.values,
        names=dept_counts.index,
        title='<b>🏢 Requests by Department</b>',
        hole=0.45,
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont=dict(size=13, color='white', family='Arial'),
        marker=dict(line=dict(color='white', width=3))
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=12)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font=dict(size=20, color='#2c3e50', family='Arial Black'),
        title_x=0.5
    )
    
    return fig

def create_priority_chart(df):
    """
    Create a beautiful priority distribution bar chart
    """
    priority_counts = df['Priority'].value_counts().sort_index()
    
    colors_map = {
        'P0': '#e74c3c',  # Red
        'P1': '#f39c12',  # Orange
        'P2': '#3498db',  # Blue
        'P3': '#95a5a6'   # Gray
    }
    
    colors = [colors_map.get(p, '#bdc3c7') for p in priority_counts.index]
    
    fig = go.Figure(data=[
        go.Bar(
            x=priority_counts.index,
            y=priority_counts.values,
            marker=dict(
                color=colors,
                line=dict(color='white', width=2)
            ),
            text=priority_counts.values,
            textposition='auto',
            textfont=dict(size=16, color='white', family='Arial Black'),
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': '<b>🔥 Priority Distribution</b>',
            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title='<b>Priority Level</b>',
            titlefont=dict(size=14),
            tickfont=dict(size=13, color='#2c3e50')
        ),
        yaxis=dict(
            title='<b>Number of Requests</b>',
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        ),
        height=500,
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='white',
        showlegend=False,
        hoverlabel=dict(
            bgcolor='white',
            font_size=13
        )
    )
    
    return fig

def create_quarter_distribution(df):
    """
    Create quarter distribution chart
    """
    quarter_counts = df[df['Target_Quarter'] != 'Not Assigned']['Target_Quarter'].value_counts()
    quarter_counts = quarter_counts.reindex(st.session_state.quarters, fill_value=0)
    
    fig = go.Figure(data=[
        go.Bar(
            x=quarter_counts.index,
            y=quarter_counts.values,
            marker=dict(
                color=quarter_counts.values,
                colorscale='Viridis',
                line=dict(color='white', width=2),
                showscale=True,
                colorbar=dict(title='Count')
            ),
            text=quarter_counts.values,
            textposition='auto',
            textfont=dict(size=14, color='white', family='Arial Black')
        )
    ])
    
    fig.update_layout(
        title={
            'text': '<b>📅 Tools Assigned by Quarter</b>',
            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title='<b>Quarter</b>',
            titlefont=dict(size=14),
            tickfont=dict(size=12, color='#2c3e50')
        ),
        yaxis=dict(
            title='<b>Number of Tools</b>',
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        ),
        height=450,
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='white'
    )
    
    return fig

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    # Check password
    if not check_password():
        return
    
    # Header
    st.markdown('<h1>🚀 Briefly AI 2025-2026 Roadmap</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.3rem; color: #7f8c8d; margin-top: -1rem; margin-bottom: 2rem;"><b>Product Planning & Tool Request Management Dashboard</b></p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # ========================================================================
    # SIDEBAR - DATA UPLOAD & FILTERS
    # ========================================================================
    with st.sidebar:
        st.markdown("## 📁 Data Upload")
        st.markdown("---")
        
        pipeline_file = st.file_uploader(
            "**Tool Request Pipeline**",
            type=['xlsx', 'xls'],
            help="Upload your tool request Excel file"
        )
        
        roadmap_file = st.file_uploader(
            "**Company Roadmaps** (Optional)",
            type=['xlsx', 'xls'],
            help="Upload company-specific roadmap file"
        )
        
        # Load pipeline data
        if pipeline_file:
            with st.spinner("🔄 Loading pipeline data..."):
                st.session_state.tool_requests = load_tool_requests(pipeline_file)
                if st.session_state.tool_requests is not None:
                    st.success(f"✅ Loaded **{len(st.session_state.tool_requests)}** tool requests")
                    st.session_state.changes_made = False
        
        # Load roadmap data
        if roadmap_file:
            with st.spinner("🔄 Loading roadmap data..."):
                st.session_state.roadmap_data = load_roadmap_data(roadmap_file)
                if st.session_state.roadmap_data is not None:
                    st.success(f"✅ Loaded **{len(st.session_state.roadmap_data)}** company roadmaps")
        
        st.markdown("---")
        
        # Filters
        if st.session_state.tool_requests is not None:
            st.markdown("## 🔍 Filters")
            st.markdown("---")
            
            df = st.session_state.tool_requests
            
            # Department filter
            departments = ['All'] + sorted(df['Department'].dropna().unique().tolist())
            selected_dept = st.multiselect(
                "**Department**",
                departments,
                default=['All'],
                help="Filter by department"
            )
            
            # Stage filter
            stages = ['All'] + st.session_state.stage_order
            selected_stage = st.multiselect(
                "**Stage**",
                stages,
                default=['All'],
                help="Filter by current stage"
            )
            
            # Priority filter
            priorities = ['All'] + sorted(df['Priority'].dropna().unique().tolist())
            selected_priority = st.multiselect(
                "**Priority**",
                priorities,
                default=['All'],
                help="Filter by priority level"
            )
            
            # Quarter filter
            quarters_filter = ['All', 'Not Assigned'] + st.session_state.quarters
            selected_quarters = st.multiselect(
                "**Quarter**",
                quarters_filter,
                default=['All'],
                help="Filter by target quarter"
            )
            
            st.markdown("---")
            
            # Quick stats in sidebar
            if st.checkbox("📊 Show Quick Stats", value=True):
                st.markdown("### Summary")
                st.metric("Total Tools", len(df))
                st.metric("P0 Critical", len(df[df['Priority'] == 'P0']))
                st.metric("In Piloting", len(df[df['Stage'] == 'Piloting']))
                st.metric("Unassigned", len(df[df['Target_Quarter'] == 'Not Assigned']))
    
    # ========================================================================
    # MAIN CONTENT AREA
    # ========================================================================
    
    # Show welcome message if no data loaded
    if st.session_state.tool_requests is None:
        st.info("👆 **Please upload the Tool Request Pipeline file to begin**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            ### 📊 Features
            - Interactive Gantt timeline
            - Visual pipeline funnel
            - Department analytics
            - Priority tracking
            """)
        with col2:
            st.markdown("""
            ### 📅 Planning
            - Assign to quarters
            - Update stages
            - Track progress
            - Export data
            """)
        with col3:
            st.markdown("""
            ### 🏢 Companies
            - Multi-company support
            - Separate roadmaps
            - Consolidated view
            - Custom tracking
            """)
        
        st.markdown("---")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 12px; color: white; text-align: center;'>
            <h2 style='color: white; margin-bottom: 1rem;'>Getting Started</h2>
            <p style='font-size: 1.1rem;'>
                1. Click <b>Browse files</b> in the sidebar<br>
                2. Upload your Excel file with tool requests<br>
                3. Optionally upload company roadmap file<br>
                4. Use filters to focus on specific items<br>
                5. Assign tools to quarters and update stages
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Get data and apply filters
    df = st.session_state.tool_requests.copy()
    
    # Apply filters
    if 'selected_dept' in locals() and 'All' not in selected_dept and selected_dept:
        df = df[df['Department'].isin(selected_dept)]
    
    if 'selected_stage' in locals() and 'All' not in selected_stage and selected_stage:
        df = df[df['Stage'].isin(selected_stage)]
    
    if 'selected_priority' in locals() and 'All' not in selected_priority and selected_priority:
        df = df[df['Priority'].isin(selected_priority)]
    
    if 'selected_quarters' in locals() and 'All' not in selected_quarters and selected_quarters:
        df = df[df['Target_Quarter'].isin(selected_quarters)]
    
    # ========================================================================
    # KEY METRICS ROW
    # ========================================================================
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📊 Total Requests", len(df), delta=f"{len(df)} in view")
    
    with col2:
        assigned = len(df[(df['Target_Quarter'] != 'Not Assigned') & (df['Target_Quarter'].notna())])
        pct = (assigned/len(df)*100) if len(df) > 0 else 0
        st.metric("📅 Assigned", assigned, delta=f"{pct:.0f}%")
    
    with col3:
        p0_count = len(df[df['Priority'] == 'P0'])
        st.metric("🔥 P0 Critical", p0_count, delta="High Priority" if p0_count > 0 else "None")
    
    with col4:
        in_pilot = len(df[df['Stage'] == 'Piloting'])
        st.metric("🧪 In Piloting", in_pilot)
    
    with col5:
        implemented = len(df[df['Stage'] == 'Implementation'])
        st.metric("✅ Implemented", implemented)
    
    st.markdown("---")
    
    # ========================================================================
    # MAIN TABS
    # ========================================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "📅 Quarter Planning",
        "🏢 Company Roadmaps",
        "📋 Data Explorer",
        "📈 Analytics"
    ])
    
    # ========================================================================
    # TAB 1: DASHBOARD
    # ========================================================================
    with tab1:
        st.markdown("## 📊 Dashboard Overview")
        
        # Gantt Chart - Full Width
        st.markdown("### 🗓️ Timeline View")
        gantt_fig = create_gantt_chart(df)
        if gantt_fig:
            st.plotly_chart(gantt_fig, use_container_width=True)
        else:
            st.info("💡 **Tip:** Assign tools to quarters in the 'Quarter Planning' tab to see the timeline visualization")
        
        st.markdown("---")
        
        # Charts Grid
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_stage_funnel(df), use_container_width=True)
            st.plotly_chart(create_priority_chart(df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_department_chart(df), use_container_width=True)
            st.plotly_chart(create_quarter_distribution(df), use_container_width=True)
        
        # Summary Table
        st.markdown("---")
        st.markdown("### 📋 Summary by Stage")
        
        summary_data = []
        for stage in st.session_state.stage_order:
            stage_df = df[df['Stage'] == stage]
            p0_count = len(stage_df[stage_df['Priority'] == 'P0'])
            summary_data.append({
                'Stage': stage,
                'Total Tools': len(stage_df),
                'P0 Priority': p0_count,
                'Avg Assigned': f"{(len(stage_df[stage_df['Target_Quarter'] != 'Not Assigned'])/len(stage_df)*100) if len(stage_df) > 0 else 0:.0f}%"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # TAB 2: QUARTER PLANNING
    # ========================================================================
    with tab2:
        st.markdown("## 📅 Quarter Planning & Assignment")
        st.markdown("**Assign tools to specific quarters and update their development stages**")
        
        if st.session_state.changes_made:
            st.warning("⚠️ You have unsaved changes. Don't forget to export your updated data!")
        
        st.markdown("---")
        
        # Group by quarter
        for quarter in ['Not Assigned'] + st.session_state.quarters:
            quarter_tools = df[df['Target_Quarter'] == quarter]
            
            if len(quarter_tools) > 0:
                # Color code based on quarter
                if quarter == 'Not Assigned':
                    header_color = "🔴"
                elif '2025' in quarter:
                    header_color = "🟢"
                else:
                    header_color = "🔵"
                
                with st.expander(
                    f"{header_color} **{quarter}** - {len(quarter_tools)} tools",
                    expanded=(quarter == 'Not Assigned')
                ):
                    for idx, row in quarter_tools.iterrows():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            # Priority emoji
                            priority_emoji = {
                                'P0': '🔴',
                                'P1': '🟡',
                                'P2': '🟢',
                                'P3': '⚪'
                            }.get(row['Priority'], '⚪')
                            
                            st.markdown(f"{priority_emoji} **{row['Name']}**")
                            st.caption(f"📦 {row['Department']} | 🎯 {row['Stage']}")
                            
                            # Show tool if available
                            if pd.notna(row.get('Tool')):
                                st.caption(f"🛠️ Tool: {row['Tool']}")
                        
                        with col2:
                            # Quarter selector
                            new_quarter = st.selectbox(
                                "Assign to Quarter",
                                ['Not Assigned'] + st.session_state.quarters,
                                index=(['Not Assigned'] + st.session_state.quarters).index(quarter),
                                key=f"quarter_{idx}",
                                label_visibility="collapsed"
                            )
                            
                            if new_quarter != quarter:
                                st.session_state.tool_requests.at[idx, 'Target_Quarter'] = new_quarter
                                st.session_state.changes_made = True
                                st.rerun()
                        
                        with col3:
                            # Stage selector
                            current_stage = row['Stage'] if row['Stage'] in st.session_state.stage_order else 'Discovery'
                            new_stage = st.selectbox(
                                "Update Stage",
                                st.session_state.stage_order,
                                index=st.session_state.stage_order.index(current_stage),
                                key=f"stage_{idx}",
                                label_visibility="collapsed"
                            )
                            
                            if new_stage != row['Stage']:
                                st.session_state.tool_requests.at[idx, 'Stage'] = new_stage
                                st.session_state.changes_made = True
                                st.rerun()
                        
                        with col4:
                            # Info button
                            if st.button("ℹ️", key=f"info_{idx}", help="View details"):
                                st.info(f"""
                                **Full Name:** {row['Name']}
                                
                                **Department:** {row.get('Department', 'N/A')}
                                
                                **Stakeholder:** {row.get('Stakeholder', 'N/A')}
                                
                                **Tool:** {row.get('Tool', 'N/A')}
                                
                                **Budget:** {row.get('Budget', 'N/A')}
                                
                                **Status:** {row.get('Status', 'N/A')}
                                
                                **Notes:** {row.get('Notes', 'None')}
                                """)
                        
                        st.markdown("<hr style='margin: 0.5rem 0; border: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
        
        # Export Section
        st.markdown("---")
        st.markdown("### 💾 Export Updated Roadmap")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = st.session_state.tool_requests.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"briefly_roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_buffer = io.BytesIO()
            st.session_state.tool_requests.to_excel(excel_buffer, index=False, sheet_name='Tool Requests')
            st.download_button(
                label="📥 Download as Excel",
                data=excel_buffer.getvalue(),
                file_name=f"briefly_roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            json_data = st.session_state.tool_requests.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_data,
                file_name=f"briefly_roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    # ========================================================================
    # TAB 3: COMPANY ROADMAPS
    # ========================================================================
    with tab3:
        st.markdown("## 🏢 Company-Specific Roadmaps")
        
        if st.session_state.roadmap_data is None:
            st.info("📤 Upload the Company Roadmap Excel file in the sidebar to view company-specific details")
            
            # Show which companies have tool requests
            st.markdown("### 📊 Tool Requests by Stakeholder")
            if 'Stakeholder' in df.columns:
                stakeholder_counts = df['Stakeholder'].value_counts()
                
                for stakeholder, count in stakeholder_counts.items():
                    if pd.notna(stakeholder):
                        st.markdown(f"**{stakeholder}:** {count} tool requests")
        else:
            companies = list(st.session_state.roadmap_data.keys())
            
            st.markdown(f"**{len(companies)} company roadmaps loaded**")
            st.markdown("---")
            
            # Create tabs for each company
            company_tabs = st.tabs([f"🏢 {company}" for company in companies])
            
            for i, company in enumerate(companies):
                with company_tabs[i]:
                    st.markdown(f"### {company} Roadmap")
                    
                    # Display company roadmap data
                    company_df = st.session_state.roadmap_data[company]
                    st.dataframe(company_df, use_container_width=True, height=400)
                    
                    st.markdown("---")
                    
                    # Show tools related to this company
                    if 'Stakeholder' in df.columns:
                        company_tools = df[
                            df['Stakeholder'].astype(str).str.contains(company, case=False, na=False)
                        ]
                        
                        if len(company_tools) > 0:
                            st.markdown(f"### 🛠️ {len(company_tools)} Tool Requests from {company}")
                            
                            # Group by stage
                            for stage in st.session_state.stage_order:
                                stage_tools = company_tools[company_tools['Stage'] == stage]
                                if len(stage_tools) > 0:
                                    st.markdown(f"**{stage}** ({len(stage_tools)})")
                                    for _, tool in stage_tools.iterrows():
                                        priority_color = {
                                            'P0': '🔴',
                                            'P1': '🟡',
                                            'P2': '🟢',
                                            'P3': '⚪'
                                        }.get(tool['Priority'], '⚪')
                                        st.markdown(
                                            f"  {priority_color} {tool['Name']} - "
                                            f"**{tool['Target_Quarter']}** "
                                            f"({tool.get('Tool', 'TBD')})"
                                        )
                        else:
                            st.info(f"No tool requests found for {company}")
                    
                    # Export company-specific data
                    st.markdown("---")
                    if st.button(f"📥 Export {company} Roadmap", key=f"export_{company}"):
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            company_df.to_excel(writer, sheet_name=company, index=False)
                            if 'Stakeholder' in df.columns:
                                company_tools.to_excel(writer, sheet_name='Tool Requests', index=False)
                        
                        st.download_button(
                            label=f"Download {company} Data",
                            data=excel_buffer.getvalue(),
                            file_name=f"{company}_roadmap_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
    
    # ========================================================================
    # TAB 4: DATA EXPLORER
    # ========================================================================
    with tab4:
        st.markdown("## 📋 Data Explorer")
        
        # Display options
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"Showing **{len(df)}** of **{len(st.session_state.tool_requests)}** total requests")
        
        with col2:
            show_all_cols = st.checkbox("Show all columns", value=False)
        
        with col3:
            page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=2)
        
        st.markdown("---")
        
        # Select columns to display
        if show_all_cols:
            display_df = df
        else:
            key_cols = ['Name', 'Department', 'Stage', 'Target_Quarter', 'Priority', 'Tool', 'Status', 'Stakeholder']
            display_cols = [col for col in key_cols if col in df.columns]
            display_df = df[display_cols]
        
        # Pagination
        total_pages = (len(display_df) - 1) // page_size + 1
        
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                page = st.selectbox(
                    "Page",
                    range(1, total_pages + 1),
                    format_func=lambda x: f"Page {x} of {total_pages}"
                )
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(display_df))
            paginated_df = display_df.iloc[start_idx:end_idx]
        else:
            paginated_df = display_df
        
        # Display dataframe
        st.dataframe(
            paginated_df,
            use_container_width=True,
            height=500
        )
        
        # Search functionality
        st.markdown("---")
        st.markdown("### 🔍 Search Tools")
        search_term = st.text_input("Search by name, department, or tool", "")
        
        if search_term:
            search_results = df[
                df['Name'].str.contains(search_term, case=False, na=False) |
                df.get('Department', pd.Series()).str.contains(search_term, case=False, na=False) |
                df.get('Tool', pd.Series()).str.contains(search_term, case=False, na=False)
            ]
            
            st.markdown(f"**Found {len(search_results)} results:**")
            st.dataframe(search_results, use_container_width=True)
        
        # Export options
        st.markdown("---")
        st.markdown("### 📥 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = display_df.to_csv(index=False)
            st.download_button(
                "📄 Download CSV",
                csv,
                f"briefly_data_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_buffer = io.BytesIO()
            display_df.to_excel(excel_buffer, index=False)
            st.download_button(
                "📊 Download Excel",
                excel_buffer.getvalue(),
                f"briefly_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            json_data = display_df.to_json(orient='records', indent=2)
            st.download_button(
                "📋 Download JSON",
                json_data,
                f"briefly_data_{datetime.now().strftime('%Y%m%d')}.json",
                "application/json",
                use_container_width=True
            )
    
    # ========================================================================
    # TAB 5: ANALYTICS
    # ========================================================================
    with tab5:
        st.markdown("## 📈 Advanced Analytics")
        
        # Timeline analysis
        st.markdown("### 📅 Timeline Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tools per quarter
            quarter_data = df[df['Target_Quarter'] != 'Not Assigned'].groupby('Target_Quarter').size()
            fig = px.bar(
                x=quarter_data.index,
                y=quarter_data.values,
                title='<b>Tools per Quarter</b>',
                labels={'x': 'Quarter', 'y': 'Number of Tools'},
                color=quarter_data.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Stage progression over quarters
            stage_quarter = df[df['Target_Quarter'] != 'Not Assigned'].groupby(['Target_Quarter', 'Stage']).size().unstack(fill_value=0)
            fig = px.bar(
                stage_quarter,
                title='<b>Stage Distribution by Quarter</b>',
                labels={'value': 'Count', 'Target_Quarter': 'Quarter'},
                barmode='stack',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Department analysis
        st.markdown("### 🏢 Department Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Department vs Priority
            dept_priority = pd.crosstab(df['Department'], df['Priority'])
            fig = px.bar(
                dept_priority,
                title='<b>Priority Distribution by Department</b>',
                labels={'value': 'Count', 'Department': 'Department'},
                barmode='group',
                color_discrete_sequence=['#e74c3c', '#f39c12', '#3498db', '#95a5a6']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Department vs Stage
            dept_stage = pd.crosstab(df['Department'], df['Stage'])
            fig = px.bar(
                dept_stage,
                title='<b>Stage Distribution by Department</b>',
                labels={'value': 'Count', 'Department': 'Department'},
                barmode='stack',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Key Insights
        st.markdown("### 💡 Key Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🎯 Most Active Department")
            top_dept = df['Department'].value_counts().iloc[0] if len(df) > 0 else "N/A"
            top_dept_count = df['Department'].value_counts().values[0] if len(df) > 0 else 0
            st.markdown(f"**{top_dept}** with **{top_dept_count}** requests")
        
        with col2:
            st.markdown("#### 📅 Busiest Quarter")
            quarter_counts = df[df['Target_Quarter'] != 'Not Assigned']['Target_Quarter'].value_counts()
            if len(quarter_counts) > 0:
                busiest_q = quarter_counts.iloc[0]
                busiest_q_name = quarter_counts.index[0]
                st.markdown(f"**{busiest_q_name}** with **{busiest_q}** tools")
            else:
                st.markdown("No quarters assigned yet")
        
        with col3:
            st.markdown("#### ⚠️ Attention Needed")
            unassigned = len(df[df['Target_Quarter'] == 'Not Assigned'])
            p0_unassigned = len(df[(df['Target_Quarter'] == 'Not Assigned') & (df['Priority'] == 'P0')])
            st.markdown(f"**{unassigned}** unassigned tools")
            if p0_unassigned > 0:
                st.markdown(f"⚠️ **{p0_unassigned}** are P0 priority!")
        
        # Completion metrics
        st.markdown("---")
        st.markdown("### ✅ Completion Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = len(df)
            assigned = len(df[df['Target_Quarter'] != 'Not Assigned'])
            pct = (assigned/total*100) if total > 0 else 0
            st.metric("Assignment Rate", f"{pct:.1f}%", delta=f"{assigned}/{total}")
        
        with col2:
            in_progress = len(df[df['Stage'].isin(['Build vs Buy', 'Initial Demo', 'Piloting'])])
            pct = (in_progress/total*100) if total > 0 else 0
            st.metric("In Progress", f"{pct:.1f}%", delta=f"{in_progress}/{total}")
        
        with col3:
            implemented = len(df[df['Stage'] == 'Implementation'])
            pct = (implemented/total*100) if total > 0 else 0
            st.metric("Implemented", f"{pct:.1f}%", delta=f"{implemented}/{total}")
        
        with col4:
            discovery = len(df[df['Stage'] == 'Discovery'])
            pct = (discovery/total*100) if total > 0 else 0
            st.metric("Early Stage", f"{pct:.1f}%", delta=f"{discovery}/{total}")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    st.markdown("---")
    st.markdown("""
    <div class='footer'>
        <p><b>Briefly AI 2025-2026 Roadmap Dashboard</b></p>
        <p>Built with Streamlit • Last updated: {}</p>
        <p>🔒 Secure • 📊 Real-time • 🚀 Interactive</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    main()
