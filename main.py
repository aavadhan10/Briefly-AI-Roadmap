import streamlit as st
import pandas as pd
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
# DATA PROCESSING
# ============================================================================
def extract_tasks_from_roadmap(df, company_name):
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
                'AI_Benefit': str(ai_benefit).strip() if pd.notna(ai_benefit) else None
            })
    
    return tasks

def prioritize_and_assign(tasks):
    """Prioritize and assign quarters and stages"""
    high_words = ['manual', 'time-consuming', 'error', 'repetitive', 'copy', 'paste', 'spreadsheet']
    
    quarters = ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
    stages = ['Planning', 'Strategy', 'Strategy', 'Strategy']
    
    for idx, task in enumerate(tasks):
        task_lower = task['Task'].lower()
        
        score = sum(1 for word in high_words if word in task_lower)
        
        if score >= 3:
            task['Priority'] = 'P0'
        elif score >= 2:
            task['Priority'] = 'P1'
        else:
            task['Priority'] = 'P2'
        
        # Assign quarter
        task['Quarter'] = quarters[idx % len(quarters)]
        
        # Assign stage
        task['Stage'] = stages[idx % len(stages)]
    
    return tasks

def load_tool_requests(filepath):
    try:
        df = pd.read_excel(filepath, header=1)
        df = df.rename(columns={
            df.columns[0]: 'Name',
            df.columns[2]: 'Stakeholder',
            df.columns[5]: 'Target_Quarter',
            df.columns[9]: 'Priority'
        })
        
        df = df[df['Name'].notna()]
        df = df[~df['Name'].astype(str).str.contains('Name|Subitems|📥', na=False)]
        
        for idx, row in df.iterrows():
            if pd.isna(row.get('Target_Quarter')) or str(row['Target_Quarter']) == 'Not Assigned Yet':
                df.at[idx, 'Target_Quarter'] = 'Q1 2025'
            df.at[idx, 'Stage'] = 'Planning'
        
        return df.reset_index(drop=True)
    except:
        return None

@st.cache_data
def load_all_data():
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
                        tasks = prioritize_and_assign(tasks)
                        data['companies'][company_name] = {'tasks': tasks}
                break
            except:
                pass
    
    return data

# ============================================================================
# HTML ROADMAP GENERATOR
# ============================================================================
def create_html_roadmap(company_name, tasks, tool_requests):
    """Create beautiful HTML roadmap"""
    
    quarters_2025 = ['Quarter 1', 'Quarter 2', 'Quarter 3', 'Quarter 4']
    quarters_2026 = ['Quarter 1', 'Quarter 2', 'Quarter 3', 'Quarter 4']
    quarter_map = {
        'Q1 2025': 'Quarter 1', 'Q2 2025': 'Quarter 2', 'Q3 2025': 'Quarter 3', 'Q4 2025': 'Quarter 4',
        'Q1 2026': 'Quarter 1', 'Q2 2026': 'Quarter 2', 'Q3 2026': 'Quarter 3', 'Q4 2026': 'Quarter 4'
    }
    
    stages = ['Planning', 'Strategy', 'Strategy', 'Strategy']
    stage_colors = {
        'Planning': '#5B7EBD',
        'Strategy': ['#D4A574', '#82B366', '#B17FB8']
    }
    
    # Organize data
    roadmap_data = {
        'Planning': {q: [] for q in quarters_2025 + quarters_2026},
        'Strategy 1': {q: [] for q in quarters_2025 + quarters_2026},
        'Strategy 2': {q: [] for q in quarters_2025 + quarters_2026},
        'Strategy 3': {q: [] for q in quarters_2025 + quarters_2026}
    }
    
    # Add tasks
    strategy_counters = [0, 0, 0]
    for task in tasks:
        q_name = quarter_map.get(task['Quarter'])
        if not q_name:
            continue
        
        if task['Stage'] == 'Planning':
            roadmap_data['Planning'][q_name].append(task)
        elif task['Stage'] == 'Strategy':
            # Distribute across 3 strategy rows
            idx = strategy_counters[0] % 3
            roadmap_data[f'Strategy {idx+1}'][q_name].append(task)
            strategy_counters[0] += 1
    
    # Add tool requests
    if tool_requests is not None:
        for _, row in tool_requests.iterrows():
            q_name = quarter_map.get(row['Target_Quarter'])
            if q_name:
                roadmap_data['Planning'][q_name].append({
                    'Task': row['Name'],
                    'Priority': row.get('Priority', 'P2'),
                    'Stage': 'Planning'
                })
    
    # Generate HTML
    html = f"""
    <style>
        .roadmap-container {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #6B9080 0%, #7A9E8F 100%);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}
        .roadmap-header {{
            background: rgba(107, 144, 128, 0.95);
            color: white;
            padding: 25px;
            border-radius: 8px 8px 0 0;
            margin-bottom: 2px;
        }}
        .roadmap-title {{
            font-size: 36px;
            font-weight: bold;
            margin: 0;
            letter-spacing: 2px;
        }}
        .roadmap-subtitle {{
            font-size: 16px;
            margin: 8px 0 0 0;
            opacity: 0.9;
        }}
        .roadmap-grid {{
            display: table;
            width: 100%;
            background: white;
            border-collapse: collapse;
        }}
        .roadmap-row {{
            display: table-row;
        }}
        .roadmap-cell {{
            display: table-cell;
            border: 2px solid #e0e0e0;
            padding: 15px;
            vertical-align: top;
            background: #fafafa;
            min-height: 150px;
            position: relative;
        }}
        .roadmap-cell.year-header {{
            background: linear-gradient(135deg, #82B366 0%, #6B9E78 100%);
            color: white;
            font-weight: bold;
            font-size: 18px;
            text-align: center;
            padding: 15px;
            border: none;
        }}
        .roadmap-cell.year-header.year2 {{
            background: linear-gradient(135deg, #B17FB8 0%, #9B6BA3 100%);
        }}
        .roadmap-cell.quarter-header {{
            background: #f0f0f0;
            font-weight: 600;
            font-size: 13px;
            text-align: center;
            padding: 10px;
            color: #666;
        }}
        .roadmap-cell.quarter-goal {{
            background: #FFF9E6;
            font-size: 11px;
            font-style: italic;
            text-align: center;
            padding: 8px;
            color: #888;
            min-height: 40px;
        }}
        .roadmap-cell.stage-label {{
            background: linear-gradient(135deg, #5B7EBD 0%, #4A6BA8 100%);
            color: white;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            padding: 20px;
            border: none;
            writing-mode: horizontal-tb;
            min-width: 140px;
        }}
        .roadmap-cell.stage-label.strategy1 {{
            background: linear-gradient(135deg, #D4A574 0%, #C19563 100%);
        }}
        .roadmap-cell.stage-label.strategy2 {{
            background: linear-gradient(135deg, #82B366 0%, #6B9E78 100%);
        }}
        .roadmap-cell.stage-label.strategy3 {{
            background: linear-gradient(135deg, #B17FB8 0%, #9B6BA3 100%);
        }}
        .task-card {{
            background: #5B7EBD;
            color: white;
            padding: 12px;
            margin: 8px 0;
            border-radius: 6px;
            font-size: 12px;
            line-height: 1.4;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: transform 0.2s;
        }}
        .task-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .task-card.strategy1 {{
            background: #D4A574;
        }}
        .task-card.strategy2 {{
            background: #82B366;
        }}
        .task-card.strategy3 {{
            background: #B17FB8;
        }}
        .task-card.priority-p0 {{
            border: 3px solid #E74C3C;
            font-weight: bold;
        }}
    </style>
    
    <div class="roadmap-container">
        <div class="roadmap-header">
            <div class="roadmap-title">Product Roadmap</div>
            <div class="roadmap-subtitle">Map out the timeline of {company_name}'s project</div>
        </div>
        
        <div class="roadmap-grid">
            <!-- Year Headers -->
            <div class="roadmap-row">
                <div class="roadmap-cell" style="border:none; background:transparent;"></div>
                <div class="roadmap-cell year-header" colspan="4">YEAR 1 - 2025</div>
                <div class="roadmap-cell year-header year2" colspan="4">YEAR 2 - 2026</div>
            </div>
            
            <!-- Quarter Headers -->
            <div class="roadmap-row">
                <div class="roadmap-cell" style="border:none; background:transparent;"></div>
                {''.join(f'<div class="roadmap-cell quarter-header">{q}</div>' for q in quarters_2025)}
                {''.join(f'<div class="roadmap-cell quarter-header">{q}</div>' for q in quarters_2026)}
            </div>
            
            <!-- Quarter Goals -->
            <div class="roadmap-row">
                <div class="roadmap-cell" style="border:none; background:transparent;"></div>
    """
    
    # Add quarter goal cells
    for _ in range(8):
        html += '<div class="roadmap-cell quarter-goal">Insert your team\'s goal for this quarter</div>'
    
    html += """
            </div>
            
            <!-- Planning Row -->
            <div class="roadmap-row">
                <div class="roadmap-cell stage-label">Planning</div>
    """
    
    # Add Planning cells
    for q in quarters_2025 + quarters_2026:
        items = roadmap_data['Planning'][q]
        html += '<div class="roadmap-cell">'
        for item in items[:2]:  # Max 2 per cell
            task_text = item['Task'][:50] + '...' if len(item['Task']) > 50 else item['Task']
            priority_class = f"priority-{item.get('Priority', 'P2').lower()}"
            html += f'<div class="task-card {priority_class}">{task_text}</div>'
        html += '</div>'
    
    html += '</div>'
    
    # Strategy rows
    for i in range(3):
        stage_name = f'Strategy {i+1}'
        html += f'''
            <div class="roadmap-row">
                <div class="roadmap-cell stage-label strategy{i+1}">Strategy</div>
        '''
        
        for q in quarters_2025 + quarters_2026:
            items = roadmap_data[stage_name][q]
            html += '<div class="roadmap-cell">'
            for item in items[:2]:
                task_text = item['Task'][:50] + '...' if len(item['Task']) > 50 else item['Task']
                priority_class = f"priority-{item.get('Priority', 'P2').lower()}"
                html += f'<div class="task-card strategy{i+1} {priority_class}">{task_text}</div>'
            html += '</div>'
        
        html += '</div>'
    
    html += '''
        </div>
    </div>
    '''
    
    return html

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    if not check_password():
        return
    
    with st.spinner("📊 Loading data..."):
        data = load_all_data()
    
    if not data['companies']:
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
        
        html = create_html_roadmap('All Companies', all_tasks, data['tool_requests'])
        st.markdown(html, unsafe_allow_html=True)
    else:
        company_name = selected_view.replace('🏢 ', '')
        if company_name in data['companies']:
            company_data = data['companies'][company_name]
            
            company_tools = None
            if data['tool_requests'] is not None and 'Stakeholder' in data['tool_requests'].columns:
                company_tools = data['tool_requests'][
                    data['tool_requests']['Stakeholder'].astype(str).str.contains(company_name, case=False, na=False)
                ]
            
            html = create_html_roadmap(company_name, company_data['tasks'], company_tools)
            st.markdown(html, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

if __name__ == "__main__":
    main()
