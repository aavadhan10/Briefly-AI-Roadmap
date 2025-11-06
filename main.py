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

# Beautiful CSS
st.markdown("""
<style>
    .main {
        background: #f5f5f5;
    }
    h1 {
        color: #2c3e50 !important;
        font-family: 'Arial Black', sans-serif !important;
        text-align: center;
        padding: 2rem 0;
    }
    .stSelectbox > div > div {
        border: 2px solid #3498db;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

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
# DATA LOADING & PROCESSING
# ============================================================================
def extract_tasks_from_roadmap(df, company_name):
    """Extract tasks from company roadmap"""
    tasks = []
    task_row_idx = None
    
    for idx, row in df.iterrows():
        if pd.notna(row.iloc[0]) and 'task' in str(row.iloc[0]).lower():
            task_row_idx = idx
            break
    
    if task_row_idx is None:
        return tasks
    
    task_row = df.iloc[task_row_idx]
    
    for col_idx in range(1, len(task_row), 2):
        task_desc = task_row.iloc[col_idx]
        ai_benefit = task_row.iloc[col_idx + 1] if col_idx + 1 < len(task_row) else None
        
        if pd.notna(task_desc) and str(task_desc).strip() and len(str(task_desc)) > 10:
            area_num = (col_idx // 2) + 1
            
            tasks.append({
                'Company': company_name,
                'Area': f'Area #{area_num}',
                'Task': str(task_desc).strip(),
                'AI_Benefit': str(ai_benefit).strip() if pd.notna(ai_benefit) else None,
                'Priority': None,
                'Quarter': None,
                'Stage': None
            })
    
    return tasks

def prioritize_tasks(tasks):
    """Smart prioritization"""
    high_priority_words = ['manual', 'time-consuming', 'error', 'repetitive', 'copy', 'paste', 'spreadsheet']
    medium_priority_words = ['report', 'update', 'review', 'tracking']
    automation_words = ['automat', 'ai', 'reduce time', 'efficiency']
    
    for task in tasks:
        task_lower = task['Task'].lower()
        benefit_lower = task['AI_Benefit'].lower() if task['AI_Benefit'] else ''
        
        score = 0
        for word in high_priority_words:
            if word in task_lower:
                score += 3
        for word in automation_words:
            if word in benefit_lower:
                score += 2
        for word in medium_priority_words:
            if word in task_lower:
                score += 1
        
        if score >= 6:
            task['Priority'] = 'P0'
        elif score >= 4:
            task['Priority'] = 'P1'
        elif score >= 2:
            task['Priority'] = 'P2'
        else:
            task['Priority'] = 'P3'
        
        if any(word in task_lower for word in ['evaluate', 'compare', 'choose']):
            task['Stage'] = 'Strategy'
        elif any(word in task_lower for word in ['test', 'trial', 'poc', 'demo']):
            task['Stage'] = 'Planning'
        elif any(word in task_lower for word in ['pilot', 'beta']):
            task['Stage'] = 'Development'
        elif any(word in task_lower for word in ['implement', 'rollout', 'deploy']):
            task['Stage'] = 'Launch'
        else:
            task['Stage'] = 'Planning'
    
    return tasks

def assign_quarters(tasks):
    """Assign quarters based on priority"""
    quarters = ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
    
    p0_tasks = [t for t in tasks if t['Priority'] == 'P0']
    p1_tasks = [t for t in tasks if t['Priority'] == 'P1']
    p2_tasks = [t for t in tasks if t['Priority'] == 'P2']
    p3_tasks = [t for t in tasks if t['Priority'] == 'P3']
    
    for i, task in enumerate(p0_tasks):
        task['Quarter'] = 'Q1 2025' if i % 2 == 0 else 'Q2 2025'
    
    for i, task in enumerate(p1_tasks):
        task['Quarter'] = 'Q2 2025' if i % 2 == 0 else 'Q3 2025'
    
    for i, task in enumerate(p2_tasks):
        task['Quarter'] = 'Q3 2025' if i % 2 == 0 else 'Q4 2025'
    
    for i, task in enumerate(p3_tasks):
        task['Quarter'] = quarters[4 + (i % 4)]
    
    return tasks

def load_tool_requests(filepath):
    """Load tool requests"""
    try:
        df = pd.read_excel(filepath, header=1)
        df = df.rename(columns={
            df.columns[0]: 'Name',
            df.columns[2]: 'Stakeholder',
            df.columns[3]: 'Department',
            df.columns[5]: 'Target_Quarter',
            df.columns[8]: 'Phase',
            df.columns[9]: 'Priority'
        })
        
        df = df[df['Name'].notna()]
        df = df[~df['Name'].astype(str).str.contains('Name|Subitems|📥|🧭|💰|📈|💻', na=False)]
        
        for idx, row in df.iterrows():
            phase = str(row.get('Phase', '')).lower()
            if 'pilot' in phase:
                df.at[idx, 'Stage'] = 'Development'
            elif 'demo' in phase or 'poc' in phase:
                df.at[idx, 'Stage'] = 'Planning'
            elif 'implement' in phase:
                df.at[idx, 'Stage'] = 'Launch'
            else:
                df.at[idx, 'Stage'] = 'Strategy'
            
            if pd.isna(row.get('Target_Quarter')) or row['Target_Quarter'] == 'Not Assigned Yet':
                priority = str(row.get('Priority', 'P2')).upper()
                if priority == 'P0':
                    df.at[idx, 'Target_Quarter'] = 'Q1 2025'
                elif priority == 'P1':
                    df.at[idx, 'Target_Quarter'] = 'Q2 2025'
                elif priority == 'P2':
                    df.at[idx, 'Target_Quarter'] = 'Q3 2025'
                else:
                    df.at[idx, 'Target_Quarter'] = 'Q4 2025'
        
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"Error loading: {e}")
        return None

@st.cache_data
def load_all_data():
    """Load all data"""
    data = {'tool_requests': None, 'companies': {}}
    
    pipeline_files = ['AI_Tool_Request_Pipeline_1762382492.xlsx', 'AI_Tool_Request_Pipeline_1762381302.xlsx']
    for f in pipeline_files:
        if os.path.exists(f):
            data['tool_requests'] = load_tool_requests(f)
            if data['tool_requests'] is not None:
                break
    
    roadmap_files = ['AI_Roadmap_-_Accounting_-_Updated_10_1_2025.xlsx']
    for f in roadmap_files:
        if os.path.exists(f):
            try:
                xl = pd.ExcelFile(f)
                for sheet_name in xl.sheet_names:
                    company_name = sheet_name.strip()
                    df = pd.read_excel(f, sheet_name=sheet_name)
                    tasks = extract_tasks_from_roadmap(df, company_name)
                    if tasks:
                        tasks = prioritize_tasks(tasks)
                        tasks = assign_quarters(tasks)
                        data['companies'][company_name] = {'tasks': tasks}
                break
            except:
                pass
    
    return data

# ============================================================================
# TIMELINE ROADMAP VISUALIZATION
# ============================================================================
def create_timeline_roadmap(company_name, tasks, tool_requests):
    """Create timeline-style roadmap like your example"""
    
    quarters = ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
    stages = ['Strategy', 'Planning', 'Development', 'Launch']
    
    # Colors for each stage
    stage_colors = {
        'Strategy': '#E8B04B',   # Gold/Yellow
        'Planning': '#5DADE2',   # Blue
        'Development': '#82C785', # Green  
        'Launch': '#C594C5'       # Purple
    }
    
    # Quarter colors for headers
    quarter_header_colors = ['#82C785', '#82C785', '#82C785', '#82C785', '#C594C5', '#C594C5', '#C594C5', '#C594C5']
    
    fig = go.Figure()
    
    # Collect all items
    all_items = {}
    for stage in stages:
        all_items[stage] = {q: [] for q in quarters}
    
    # Add tasks
    for task in tasks:
        if task['Quarter'] in quarters and task['Stage'] in stages:
            all_items[task['Stage']][task['Quarter']].append({
                'text': task['Task'][:60] + '...' if len(task['Task']) > 60 else task['Task'],
                'full_text': task['Task'],
                'priority': task['Priority'],
                'type': 'Task',
                'area': task.get('Area', '')
            })
    
    # Add tool requests
    if tool_requests is not None:
        for _, row in tool_requests.iterrows():
            quarter = row['Target_Quarter']
            stage = row.get('Stage', 'Planning')
            if quarter in quarters and stage in stages:
                all_items[stage][quarter].append({
                    'text': row['Name'][:60] + '...' if len(row['Name']) > 60 else row['Name'],
                    'full_text': row['Name'],
                    'priority': row.get('Priority', 'P2'),
                    'type': 'Tool',
                    'dept': row.get('Department', '')
                })
    
    # Create grid with boxes
    y_position = len(stages) - 1
    
    for stage_idx, stage in enumerate(stages):
        for q_idx, quarter in enumerate(quarters):
            items = all_items[stage][quarter]
            
            # Draw cell background
            fig.add_shape(
                type='rect',
                x0=q_idx,
                x1=q_idx + 1,
                y0=y_position - 0.45,
                y1=y_position + 0.45,
                fillcolor='#f8f9fa',
                line=dict(color='#ddd', width=1),
                layer='below'
            )
            
            # Add items as boxes in the cell
            for item_idx, item in enumerate(items[:3]):  # Max 3 items per cell
                box_y = y_position + 0.3 - (item_idx * 0.25)
                box_height = 0.2
                
                # Box color based on priority
                if item['priority'] == 'P0':
                    box_color = stage_colors[stage]
                    box_opacity = 1.0
                else:
                    box_color = stage_colors[stage]
                    box_opacity = 0.7
                
                # Add box
                fig.add_shape(
                    type='rect',
                    x0=q_idx + 0.05,
                    x1=q_idx + 0.95,
                    y0=box_y - box_height/2,
                    y1=box_y + box_height/2,
                    fillcolor=box_color,
                    opacity=box_opacity,
                    line=dict(color='white', width=2)
                )
                
                # Add text
                fig.add_annotation(
                    x=q_idx + 0.5,
                    y=box_y,
                    text=f"<b>{item['text'][:35]}</b>",
                    showarrow=False,
                    font=dict(size=9, color='white', family='Arial'),
                    xanchor='center',
                    yanchor='middle',
                    hoverlabel=dict(bgcolor='white')
                )
        
        y_position -= 1
    
    # Layout
    fig.update_layout(
        title={
            'text': f"<b style='font-size:36px'>PRODUCT ROADMAP</b><br><span style='font-size:18px'>{company_name} - 2025-2026</span>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'color': 'white'}
        },
        xaxis=dict(
            tickmode='array',
            tickvals=[i + 0.5 for i in range(len(quarters))],
            ticktext=[f'<b>{q}</b>' for q in quarters],
            tickfont=dict(size=12, color='white'),
            showgrid=False,
            range=[0, len(quarters)],
            showline=False,
            zeroline=False
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(stages))),
            ticktext=[f'<b>{s}</b>' for s in stages[::-1]],
            tickfont=dict(size=14, color='white', family='Arial Black'),
            showgrid=False,
            range=[-0.5, len(stages) - 0.5],
            showline=False,
            zeroline=False
        ),
        height=700,
        plot_bgcolor='#6B9E78',
        paper_bgcolor='#6B9E78',
        margin=dict(l=150, r=50, t=150, b=80),
        hovermode='closest'
    )
    
    # Add quarter color headers
    for i, (q, color) in enumerate(zip(quarters, quarter_header_colors)):
        fig.add_shape(
            type='rect',
            x0=i,
            x1=i+1,
            y0=len(stages) - 0.5,
            y1=len(stages) + 0.3,
            fillcolor=color,
            line=dict(width=0),
            layer='below'
        )
    
    return fig

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    if not check_password():
        return
    
    st.title("🚀 Briefly AI 2025-2026 Roadmap")
    st.markdown("---")
    
    with st.spinner("📊 Loading data..."):
        data = load_all_data()
    
    if not data['companies'] and data['tool_requests'] is None:
        st.error("❌ No data found")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"✅ {len(data['companies'])} Companies")
    with col2:
        total_tasks = sum(len(c['tasks']) for c in data['companies'].values())
        st.success(f"✅ {total_tasks} Tasks")
    with col3:
        if data['tool_requests'] is not None:
            st.success(f"✅ {len(data['tool_requests'])} Tools")
    
    st.markdown("---")
    
    companies = list(data['companies'].keys())
    view_options = ['📊 All Companies'] + [f'🏢 {c}' for c in companies]
    selected_view = st.selectbox("**Select View:**", view_options, index=0)
    
    st.markdown("---")
    
    if selected_view == '📊 All Companies':
        all_tasks = []
        for company_data in data['companies'].values():
            all_tasks.extend(company_data['tasks'])
        
        fig = create_timeline_roadmap('All Companies', all_tasks, data['tool_requests'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        company_name = selected_view.replace('🏢 ', '')
        if company_name in data['companies']:
            company_data = data['companies'][company_name]
            
            company_tools = None
            if data['tool_requests'] is not None and 'Stakeholder' in data['tool_requests'].columns:
                company_tools = data['tool_requests'][
                    data['tool_requests']['Stakeholder'].astype(str).str.contains(company_name, case=False, na=False)
                ]
            
            fig = create_timeline_roadmap(company_name, company_data['tasks'], company_tools)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
