import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import os
import re

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
# TASK EXTRACTION & PRIORITIZATION
# ============================================================================
def extract_tasks_from_roadmap(df, company_name):
    """Extract tasks from company roadmap Excel sheet"""
    tasks = []
    
    # Look for "Tasks" row
    task_row_idx = None
    for idx, row in df.iterrows():
        if pd.notna(row.iloc[0]) and 'task' in str(row.iloc[0]).lower():
            task_row_idx = idx
            break
    
    if task_row_idx is None:
        return tasks
    
    # Extract tasks from the row
    task_row = df.iloc[task_row_idx]
    
    for col_idx in range(1, len(task_row), 2):  # Every other column (Finance Now vs AI columns)
        task_desc = task_row.iloc[col_idx]
        ai_benefit = task_row.iloc[col_idx + 1] if col_idx + 1 < len(task_row) else None
        
        if pd.notna(task_desc) and str(task_desc).strip() and len(str(task_desc)) > 10:
            # Determine area number
            area_num = (col_idx // 2) + 1
            
            tasks.append({
                'Company': company_name,
                'Area': f'Area #{area_num}',
                'Task': str(task_desc).strip(),
                'AI_Benefit': str(ai_benefit).strip() if pd.notna(ai_benefit) else None,
                'Priority': None,  # Will assign later
                'Quarter': None,
                'Stage': None
            })
    
    return tasks

def prioritize_tasks(tasks):
    """Smart prioritization based on task characteristics"""
    
    # Priority keywords
    high_priority_words = ['manual', 'time-consuming', 'error', 'repetitive', 'copy', 'paste', 'spreadsheet']
    medium_priority_words = ['report', 'update', 'review', 'tracking']
    automation_words = ['automat', 'ai', 'reduce time', 'efficiency']
    
    for task in tasks:
        task_lower = task['Task'].lower()
        benefit_lower = task['AI_Benefit'].lower() if task['AI_Benefit'] else ''
        
        score = 0
        
        # High priority if lots of manual work
        for word in high_priority_words:
            if word in task_lower:
                score += 3
        
        # Automation benefit adds priority
        for word in automation_words:
            if word in benefit_lower:
                score += 2
        
        # Medium priority work
        for word in medium_priority_words:
            if word in task_lower:
                score += 1
        
        # Assign priority based on score
        if score >= 6:
            task['Priority'] = 'P0'
        elif score >= 4:
            task['Priority'] = 'P1'
        elif score >= 2:
            task['Priority'] = 'P2'
        else:
            task['Priority'] = 'P3'
        
        # Assign stage based on keywords
        if any(word in task_lower for word in ['evaluate', 'compare', 'choose']):
            task['Stage'] = 'Build vs Buy'
        elif any(word in task_lower for word in ['test', 'trial', 'poc', 'demo']):
            task['Stage'] = 'Initial Demo'
        elif any(word in task_lower for word in ['pilot', 'beta']):
            task['Stage'] = 'Piloting'
        elif any(word in task_lower for word in ['implement', 'rollout', 'deploy']):
            task['Stage'] = 'Implementation'
        else:
            task['Stage'] = 'Discovery'
    
    return tasks

def assign_quarters(tasks):
    """Assign quarters based on priority and stage"""
    
    quarters = ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
    
    # Group by priority
    p0_tasks = [t for t in tasks if t['Priority'] == 'P0']
    p1_tasks = [t for t in tasks if t['Priority'] == 'P1']
    p2_tasks = [t for t in tasks if t['Priority'] == 'P2']
    p3_tasks = [t for t in tasks if t['Priority'] == 'P3']
    
    # Assign P0 to Q1-Q2 2025
    for i, task in enumerate(p0_tasks):
        if task['Stage'] in ['Discovery', 'Build vs Buy']:
            task['Quarter'] = 'Q1 2025'
        else:
            task['Quarter'] = 'Q1 2025' if i % 2 == 0 else 'Q2 2025'
    
    # Assign P1 to Q2-Q3 2025
    for i, task in enumerate(p1_tasks):
        if task['Stage'] in ['Discovery', 'Build vs Buy']:
            task['Quarter'] = 'Q2 2025'
        else:
            task['Quarter'] = 'Q2 2025' if i % 2 == 0 else 'Q3 2025'
    
    # Assign P2 to Q3-Q4 2025
    for i, task in enumerate(p2_tasks):
        task['Quarter'] = 'Q3 2025' if i % 2 == 0 else 'Q4 2025'
    
    # Assign P3 to 2026
    for i, task in enumerate(p3_tasks):
        task['Quarter'] = quarters[4 + (i % 4)]  # Spread across 2026
    
    return tasks

# ============================================================================
# TOOL REQUESTS PROCESSING
# ============================================================================
def load_tool_requests(filepath):
    """Load and process tool requests"""
    try:
        df = pd.read_excel(filepath, header=1)
        
        # Rename columns
        df = df.rename(columns={
            df.columns[0]: 'Name',
            df.columns[2]: 'Stakeholder',
            df.columns[3]: 'Department',
            df.columns[5]: 'Target_Quarter',
            df.columns[7]: 'Tool',
            df.columns[8]: 'Phase',
            df.columns[9]: 'Priority'
        })
        
        # Clean
        df = df[df['Name'].notna()]
        df = df[~df['Name'].astype(str).str.contains('Name|Subitems|📥|🧭|💰|📈|💻', na=False)]
        
        # Process each row
        for idx, row in df.iterrows():
            # Assign stage
            phase = str(row.get('Phase', '')).lower()
            if 'discovery' in phase or 'intake' in phase:
                df.at[idx, 'Stage'] = 'Discovery'
            elif 'budget' in phase or 'buy' in phase:
                df.at[idx, 'Stage'] = 'Build vs Buy'
            elif 'demo' in phase or 'poc' in phase:
                df.at[idx, 'Stage'] = 'Initial Demo'
            elif 'pilot' in phase:
                df.at[idx, 'Stage'] = 'Piloting'
            elif 'implement' in phase:
                df.at[idx, 'Stage'] = 'Implementation'
            else:
                df.at[idx, 'Stage'] = 'Discovery'
            
            # Assign quarter if not set
            if pd.isna(row.get('Target_Quarter')) or row['Target_Quarter'] == 'Not Assigned Yet':
                priority = str(row.get('Priority', 'P2')).upper()
                stage = df.at[idx, 'Stage']
                
                if priority == 'P0':
                    df.at[idx, 'Target_Quarter'] = 'Q1 2025' if stage in ['Discovery', 'Build vs Buy'] else 'Q2 2025'
                elif priority == 'P1':
                    df.at[idx, 'Target_Quarter'] = 'Q2 2025' if stage in ['Discovery', 'Build vs Buy'] else 'Q3 2025'
                elif priority == 'P2':
                    df.at[idx, 'Target_Quarter'] = 'Q3 2025'
                else:
                    df.at[idx, 'Target_Quarter'] = 'Q4 2025'
        
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"Error loading tool requests: {e}")
        return None

# ============================================================================
# VISUAL ROADMAP CREATION
# ============================================================================
def create_visual_roadmap(company_name, tasks, tool_requests):
    """Create visual swimlane roadmap"""
    
    quarters = ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']
    quarter_positions = {q: i for i, q in enumerate(quarters)}
    
    # Define swimlanes
    swimlanes = [
        'Strategy & Planning',
        'Build vs Buy',
        'Initial Demo/POC',
        'Piloting',
        'Implementation',
        'Operations'
    ]
    
    # Color scheme - matching your example
    colors = {
        'Strategy & Planning': '#3498db',      # Blue
        'Build vs Buy': '#e74c3c',            # Red
        'Initial Demo/POC': '#f39c12',        # Orange
        'Piloting': '#9b59b6',                # Purple
        'Implementation': '#2ecc71',          # Green
        'Operations': '#1abc9c'               # Teal
    }
    
    priority_colors = {
        'P0': '#8B0000',  # Dark red
        'P1': '#FF4500',  # Orange red
        'P2': '#FFA500',  # Orange
        'P3': '#FFD700'   # Gold
    }
    
    fig = go.Figure()
    
    all_items = []
    
    # Add roadmap tasks
    for task in tasks:
        if task['Quarter'] not in quarter_positions:
            continue
        
        # Map stage to swimlane
        stage_to_lane = {
            'Discovery': 'Strategy & Planning',
            'Build vs Buy': 'Build vs Buy',
            'Initial Demo': 'Initial Demo/POC',
            'Piloting': 'Piloting',
            'Implementation': 'Implementation'
        }
        
        swimlane = stage_to_lane.get(task['Stage'], 'Operations')
        
        all_items.append({
            'name': task['Task'][:40] + ('...' if len(task['Task']) > 40 else ''),
            'full_name': task['Task'],
            'swimlane': swimlane,
            'quarter': task['Quarter'],
            'priority': task['Priority'],
            'type': 'Roadmap Task',
            'area': task.get('Area', 'N/A'),
            'benefit': task.get('AI_Benefit', 'N/A')
        })
    
    # Add tool requests
    if tool_requests is not None:
        for _, row in tool_requests.iterrows():
            if row['Target_Quarter'] not in quarter_positions:
                continue
            
            stage_to_lane = {
                'Discovery': 'Strategy & Planning',
                'Build vs Buy': 'Build vs Buy',
                'Initial Demo': 'Initial Demo/POC',
                'Piloting': 'Piloting',
                'Implementation': 'Implementation'
            }
            
            swimlane = stage_to_lane.get(row['Stage'], 'Operations')
            
            all_items.append({
                'name': row['Name'][:40] + ('...' if len(row['Name']) > 40 else ''),
                'full_name': row['Name'],
                'swimlane': swimlane,
                'quarter': row['Target_Quarter'],
                'priority': row.get('Priority', 'P2'),
                'type': 'Tool Request',
                'tool': row.get('Tool', 'TBD'),
                'department': row.get('Department', 'N/A')
            })
    
    # Create bars
    for item in all_items:
        x_start = quarter_positions[item['quarter']]
        swimlane = item['swimlane']
        
        # Determine duration based on stage
        if swimlane in ['Strategy & Planning', 'Build vs Buy']:
            duration = 1
        elif swimlane in ['Initial Demo/POC', 'Piloting']:
            duration = 1.5
        else:
            duration = 2
        
        # Color based on priority
        base_color = colors[swimlane]
        if item['priority'] == 'P0':
            # Make P0 darker/more saturated
            bar_color = priority_colors['P0']
        else:
            bar_color = base_color
        
        fig.add_trace(go.Bar(
            name=item['name'],
            x=[duration],
            y=[swimlane],
            base=x_start,
            orientation='h',
            marker=dict(
                color=bar_color,
                line=dict(color='white', width=2),
                opacity=0.9 if item['priority'] == 'P0' else 0.8
            ),
            text=f"{item['priority']}" if item['priority'] == 'P0' else '',
            textposition='inside',
            textfont=dict(size=10, color='white', family='Arial Black'),
            hovertemplate=(
                f"<b>{item['full_name']}</b><br>" +
                f"Type: {item['type']}<br>" +
                f"Quarter: {item['quarter']}<br>" +
                f"Priority: {item['priority']}<br>" +
                f"Stage: {swimlane}<br>" +
                (f"Area: {item.get('area', 'N/A')}<br>" if 'area' in item else '') +
                (f"Tool: {item.get('tool', 'N/A')}<br>" if 'tool' in item else '') +
                "<extra></extra>"
            ),
            showlegend=False
        ))
    
    # Layout
    fig.update_layout(
        title={
            'text': f'<b>🚀 {company_name} - AI Roadmap 2025-2026</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 28, 'color': '#2c3e50', 'family': 'Arial Black'}
        },
        xaxis=dict(
            title='<b>Timeline</b>',
            titlefont=dict(size=16),
            tickmode='array',
            tickvals=list(range(len(quarters))),
            ticktext=[f'<b>{q}</b>' for q in quarters],
            tickfont=dict(size=12),
            gridcolor='rgba(200,200,200,0.3)',
            showgrid=True,
            range=[-0.5, len(quarters) - 0.5]
        ),
        yaxis=dict(
            title='',
            categoryorder='array',
            categoryarray=swimlanes[::-1],
            tickfont=dict(size=13, family='Arial Black'),
            gridcolor='rgba(200,200,200,0.3)',
            showgrid=True
        ),
        barmode='overlay',
        height=700,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        hovermode='closest',
        margin=dict(l=220, r=50, t=120, b=80)
    )
    
    return fig

# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data
def load_all_data():
    """Load all data from repository"""
    data = {
        'tool_requests': None,
        'companies': {}
    }
    
    # Load tool requests
    pipeline_files = [
        'AI_Tool_Request_Pipeline_1762382492.xlsx',
        'AI_Tool_Request_Pipeline_1762381302.xlsx'
    ]
    
    for f in pipeline_files:
        if os.path.exists(f):
            data['tool_requests'] = load_tool_requests(f)
            if data['tool_requests'] is not None:
                break
    
    # Load company roadmaps
    roadmap_files = [
        'AI_Roadmap_-_Accounting_-_Updated_10_1_2025.xlsx',
        'AI Roadmap - Accounting - Updated 10.1.2025.xlsx'
    ]
    
    for f in roadmap_files:
        if os.path.exists(f):
            try:
                xl = pd.ExcelFile(f)
                for sheet_name in xl.sheet_names:
                    company_name = sheet_name.strip()
                    df = pd.read_excel(f, sheet_name=sheet_name)
                    
                    # Extract tasks
                    tasks = extract_tasks_from_roadmap(df, company_name)
                    if tasks:
                        # Prioritize and assign quarters
                        tasks = prioritize_tasks(tasks)
                        tasks = assign_quarters(tasks)
                        
                        data['companies'][company_name] = {
                            'raw_df': df,
                            'tasks': tasks
                        }
                break
            except Exception as e:
                st.error(f"Error loading {f}: {e}")
    
    return data

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    if not check_password():
        return
    
    # Header
    st.title("🚀 Briefly AI 2025-2026 Roadmap")
    st.markdown("**Comprehensive Visual Roadmaps by Company**")
    st.markdown("*Auto-prioritized tasks and tool requests across quarters*")
    st.markdown("---")
    
    # Load data
    with st.spinner("📊 Loading and analyzing data..."):
        data = load_all_data()
    
    if not data['companies'] and data['tool_requests'] is None:
        st.error("❌ No data found. Please add Excel files to the repository.")
        return
    
    # Success message
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"✅ {len(data['companies'])} Companies Loaded")
    with col2:
        total_tasks = sum(len(c['tasks']) for c in data['companies'].values())
        st.success(f"✅ {total_tasks} Roadmap Tasks")
    with col3:
        if data['tool_requests'] is not None:
            st.success(f"✅ {len(data['tool_requests'])} Tool Requests")
    
    st.markdown("---")
    
    # Company selector
    companies = list(data['companies'].keys())
    view_options = ['📊 All Companies Consolidated'] + [f'🏢 {c}' for c in companies]
    
    selected_view = st.selectbox("**Select Company View:**", view_options, index=0)
    
    st.markdown("---")
    
    # ========================================================================
    # ALL COMPANIES VIEW
    # ========================================================================
    if selected_view == '📊 All Companies Consolidated':
        st.header("All Companies - Consolidated Roadmap")
        
        # Combine all tasks
        all_tasks = []
        for company_name, company_data in data['companies'].items():
            all_tasks.extend(company_data['tasks'])
        
        # Create consolidated roadmap
        fig = create_visual_roadmap('All Companies', all_tasks, data['tool_requests'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Summary stats
        st.subheader("📊 Summary Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Initiatives", len(all_tasks) + (len(data['tool_requests']) if data['tool_requests'] is not None else 0))
        with col2:
            p0_count = len([t for t in all_tasks if t['Priority'] == 'P0'])
            if data['tool_requests'] is not None:
                p0_count += len(data['tool_requests'][data['tool_requests']['Priority'].astype(str).str.upper() == 'P0'])
            st.metric("🔥 P0 Priority", p0_count)
        with col3:
            q1_count = len([t for t in all_tasks if t['Quarter'] == 'Q1 2025'])
            st.metric("Q1 2025", q1_count)
        with col4:
            st.metric("Companies", len(companies))
        with col5:
            discovery = len([t for t in all_tasks if t['Stage'] == 'Discovery'])
            st.metric("Discovery Phase", discovery)
        
        # Tasks by company
        st.markdown("---")
        st.subheader("📋 Tasks by Company")
        
        for company_name, company_data in data['companies'].items():
            with st.expander(f"**{company_name}** ({len(company_data['tasks'])} tasks)", expanded=False):
                tasks_df = pd.DataFrame(company_data['tasks'])
                tasks_df = tasks_df[['Task', 'Quarter', 'Priority', 'Stage', 'Area']]
                tasks_df = tasks_df.sort_values(['Priority', 'Quarter'])
                st.dataframe(tasks_df, use_container_width=True, height=300)
    
    # ========================================================================
    # INDIVIDUAL COMPANY VIEW
    # ========================================================================
    else:
        company_name = selected_view.replace('🏢 ', '')
        
        if company_name not in data['companies']:
            st.warning(f"No data found for {company_name}")
            return
        
        company_data = data['companies'][company_name]
        
        st.header(f"{company_name} - AI Roadmap 2025-2026")
        
        # Filter tool requests for this company
        company_tools = None
        if data['tool_requests'] is not None and 'Stakeholder' in data['tool_requests'].columns:
            company_tools = data['tool_requests'][
                data['tool_requests']['Stakeholder'].astype(str).str.contains(company_name, case=False, na=False)
            ]
        
        # Create roadmap
        fig = create_visual_roadmap(company_name, company_data['tasks'], company_tools)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Company stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = len(company_data['tasks']) + (len(company_tools) if company_tools is not None else 0)
            st.metric("Total Initiatives", total)
        with col2:
            p0_count = len([t for t in company_data['tasks'] if t['Priority'] == 'P0'])
            st.metric("🔥 P0 Priority", p0_count)
        with col3:
            q1_count = len([t for t in company_data['tasks'] if t['Quarter'] == 'Q1 2025'])
            st.metric("Q1 2025 Tasks", q1_count)
        with col4:
            impl = len([t for t in company_data['tasks'] if t['Stage'] == 'Implementation'])
            st.metric("Implementation", impl)
        
        # Detailed breakdown
        st.markdown("---")
        st.subheader(f"📋 {company_name} Detailed Task List")
        
        # Roadmap tasks
        with st.expander("**Roadmap Tasks** (from company roadmap)", expanded=True):
            tasks_df = pd.DataFrame(company_data['tasks'])
            tasks_df['Task'] = tasks_df['Task'].str[:80]
            display_df = tasks_df[['Task', 'Quarter', 'Priority', 'Stage', 'Area', 'AI_Benefit']]
            display_df = display_df.sort_values(['Priority', 'Quarter'])
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # Export
            csv = display_df.to_csv(index=False)
            st.download_button(
                f"📥 Download {company_name} Tasks (CSV)",
                csv,
                f"{company_name}_roadmap_tasks_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        # Tool requests
        if company_tools is not None and len(company_tools) > 0:
            with st.expander(f"**Tool Requests** ({len(company_tools)} tools)", expanded=True):
                tool_display = company_tools[['Name', 'Target_Quarter', 'Priority', 'Stage', 'Tool', 'Department']]
                st.dataframe(tool_display, use_container_width=True, height=300)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #7f8c8d; padding: 2rem;'>
        <p><b>Briefly AI Roadmap Dashboard</b></p>
        <p>Auto-generated from company roadmaps and tool requests</p>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
