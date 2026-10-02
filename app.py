import streamlit as st
from datetime import datetime
import pandas as pd
import streamlit.components.v1 as components
import base64
import os
import json

# Page configuration
st.set_page_config(
    page_title="CIS Opening Tender Committee Declaration System",
    page_icon="📋",
    layout="centered"
)

DB_FILE = "cis_tender_database.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "submissions": [],
        "active_tenders": [
            "T2027/001 - Supply and Delivery of Bulk Ordinary Portland Cement",
            "T2027/002 - Upgrading of Raw Material Handling Conveyor System",
            "T2027/003 - Provision of Scheduled Waste Management & Disposal Services"
        ],
        "site_config": {
            "company_name": "CEMENT INDUSTRIES (SABAH) SDN. BHD.",
            "location_subtitle": "Sepanggar Industrial Estate • Opening Tender Committee Declaration Form"
        },
        "users": [
            {"username": "admin", "password": "admin123", "role": "System Administrator", "access": "Full CRUD on Tenders, Submissions & Config", "status": "Active"},
            {"username": "auditor", "password": "audit123", "role": "Internal Auditor / Compliance", "access": "Read-Only Register & Printable Report", "status": "Active"}
        ]
    }

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_data()

if "submissions" not in st.session_state:
    st.session_state.submissions = db["submissions"]

if "active_tenders" not in st.session_state:
    st.session_state.active_tenders = db["active_tenders"]

if "site_config" not in st.session_state:
    st.session_state.site_config = db.get("site_config", {
        "company_name": "CEMENT INDUSTRIES (SABAH) SDN. BHD.",
        "location_subtitle": "Sepanggar Industrial Estate • Opening Tender Committee Declaration Form"
    })

if "users" not in st.session_state:
    st.session_state.users = db.get("users", [
        {"username": "admin", "password": "admin123", "role": "System Administrator", "access": "Full CRUD on Tenders, Submissions & Config", "status": "Active"},
        {"username": "auditor", "password": "audit123", "role": "Internal Auditor / Compliance", "access": "Read-Only Register & Printable Report", "status": "Active"}
    ])

if "step" not in st.session_state:
    st.session_state.step = 1

def commit_db():
    save_data({
        "submissions": st.session_state.submissions,
        "active_tenders": st.session_state.active_tenders,
        "site_config": st.session_state.site_config,
        "users": st.session_state.users
    })

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpeg;base64,{encoded}"
    return ""

LOGO_BASE64 = get_base64_image("cis_logo.jpg")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.header("📋 CIS Portal Navigation")
    nav_mode = st.radio("Select Portal View", ["Public Declaration Form", "Admin Portal", "Auditor Portal"])
    st.markdown("---")
    st.markdown("### 🔒 Security & Authentication")
    
    if nav_mode == "Admin Portal":
        admin_pass = st.text_input("Enter Admin Password", type="password")
        admin_users = [u["password"] for u in st.session_state.users if u.get("role") == "System Administrator" and u.get("status") == "Active"]
        if admin_pass and admin_pass in admin_users:
            st.success("Admin Access Granted")
            st.session_state.is_admin = True
        else:
            st.session_state.is_admin = False
            if admin_pass:
                st.error("Incorrect Password")
                
    elif nav_mode == "Auditor Portal":
        audit_pass = st.text_input("Enter Auditor Password", type="password")
        auditor_users = [u["password"] for u in st.session_state.users if "Auditor" in u.get("role", "") and u.get("status") == "Active"]
        if audit_pass and audit_pass in auditor_users:
            st.success("Auditor Access Granted")
            st.session_state.is_auditor = True
        else:
            st.session_state.is_auditor = False
            if audit_pass:
                st.error("Incorrect Password")

# --- ADMIN PORTAL VIEW ---
if nav_mode == "Admin Portal":
    st.title("Opening Tender Committee")
    st.subheader("Cement Industries (Sabah) Sdn Bhd - Enterprise Admin Control Center")
    
    if st.session_state.get("is_admin", False):
        total_subs = len(st.session_state.submissions)
        conflicts_flagged = sum(1 for s in st.session_state.submissions if s.get("Status") == "Conflict of Interest Exists")
        active_tenders_count = len(st.session_state.active_tenders)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Submissions", total_subs)
        col_m2.metric("Conflicts Flagged", conflicts_flagged, delta_color="inverse" if conflicts_flagged > 0 else "off")
        col_m3.metric("Active Tenders", active_tenders_count)
        st.markdown("---")
        
        admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5 = st.tabs([
            "📋 Submissions Manager", 
            "🏗️ Tender Management", 
            "⚙️ Site Content & Config",
            "👥 User & Credential Manager",
            "💾 Backup & System"
        ])
        
        with admin_tab1:
            st.markdown("### 📊 Declaration Submissions & Precision Editor")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                search_query = st.text_input("🔍 Search by Name, Emp No, or Dept", "")
            with col_f2:
                status_filter = st.selectbox("Filter by Status", ["All", "No Conflict of Interest", "Conflict of Interest Exists"])
            
            filtered_subs = st.session_state.submissions
            if search_query:
                filtered_subs = [s for s in filtered_subs if search_query.lower() in s.get("Name","").lower() or search_query in s.get("Employee No","") or search_query.lower() in s.get("Department","").lower()]
            if status_filter != "All":
                filtered_subs = [s for s in filtered_subs if s.get("Status") == status_filter]
            
            if total_subs == 0:
                st.info("No declarations submitted yet.")
            elif len(filtered_subs) == 0:
                st.info("No matching submissions found with the applied filters.")
            else:
                sub_options = {f"[{s['Timestamp']}] {s['Name']} (Emp: {s['Employee No']}) - {s['Tender Ref']}": st.session_state.submissions.index(s) for s in filtered_subs}
                selected_sub_label = st.selectbox("Select Submission to Manage", list(sub_options.keys()))
                selected_idx = sub_options[selected_sub_label]
                target_sub = st.session_state.submissions[selected_idx]
                
                st.markdown("")
                with st.container():
                    st.markdown("#### ✏️ Edit Selected Submission Record")
                    col_ed1, col_ed2 = st.columns(2)
                    with col_ed1:
                        edit_name = st.text_input("Committee Member Name", value=target_sub.get("Name", ""), key="admin_edit_name")
                        edit_emp = st.text_input("Employee Number", value=target_sub.get("Employee No", ""), key="admin_edit_emp")
                        edit_pos = st.text_input("Position / Designation", value=target_sub.get("Position", ""), key="admin_edit_pos")
                    with col_ed2:
                        edit_dept = st.text_input("Department / Division", value=target_sub.get("Department", ""), key="admin_edit_dept")
                        edit_status = st.selectbox("Declaration Status", ["No Conflict of Interest", "Conflict of Interest Exists"], index=0 if target_sub.get("Status") == "No Conflict of Interest" else 1, key="admin_edit_status")
                        edit_tender = st.selectbox("Assigned Tender Ref", st.session_state.active_tenders, index=0, key="admin_edit_tender_ref")
                    
                    edit_details = st.text_area("Conflict Details", value=target_sub.get("Conflict Details", ""), key="admin_edit_details")
                    
                    col_btn_update, col_btn_delete = st.columns([2, 1])
                    with col_btn_update:
                        if st.button("💾 Save Changes to Record", type="primary"):
                            st.session_state.submissions[selected_idx]["Name"] = edit_name
                            st.session_state.submissions[selected_idx]["Employee No"] = edit_emp
                            st.session_state.submissions[selected_idx]["Position"] = edit_pos
                            st.session_state.submissions[selected_idx]["Department"] = edit_dept
                            st.session_state.submissions[selected_idx]["Status"] = edit_status
                            st.session_state.submissions[selected_idx]["Tender Ref"] = edit_tender.split(" - ")[0]
                            st.session_state.submissions[selected_idx]["Conflict Details"] = edit_details
                            commit_db()
                            st.success("Submission updated successfully!")
                            st.rerun()
                    with col_btn_delete:
                        if st.button("🗑️ Delete Submission", type="secondary"):
                            st.session_state.submissions.pop(selected_idx)
                            commit_db()
                            st.success("Submission deleted successfully!")
                            st.rerun()
                
                st.markdown("---")
                st.markdown("#### 📑 Filtered Submissions Overview Table")
                st.dataframe(pd.DataFrame(filtered_subs), use_container_width=True)
                
                csv_data = pd.DataFrame(st.session_state.submissions).to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Verified Submissions to CSV",
                    data=csv_data,
                    file_name=f"CIS_Admin_Verified_Declarations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )

        with admin_tab2:
            st.markdown("### 🏗️ Advanced Tender Event Management")
            col_ta1, col_ta2 = st.columns([2, 2])
            with col_ta1:
                if st.button("⚠️ Clear All Tenders", type="secondary"):
                    st.session_state.active_tenders = []
                    commit_db()
                    st.success("All tenders have been cleared.")
                    st.rerun()
            
            st.markdown("---")
            if len(st.session_state.active_tenders) == 0:
                st.info("No active tenders listed. Add a new tender below.")
            else:
                for idx, tender in enumerate(list(st.session_state.active_tenders)):
                    col_t_name, col_t_del = st.columns([5, 1])
                    with col_t_name:
                        st.text_input(f"Tender #{idx+1}", value=tender, key=f"tender_edit_{idx}", disabled=True)
                    with col_t_del:
                        if st.button("🗑️ Remove", key=f"del_tender_{idx}"):
                            st.session_state.active_tenders.pop(idx)
                            commit_db()
                            st.rerun()
            
            st.markdown("---")
            st.markdown("#### ➕ Add New Tender Event")
            new_tender_code = st.text_input("Tender Code / Ref (e.g., T2027/004)")
            new_tender_desc = st.text_input("Tender Description / Title")
            
            if st.button("Add Tender Event"):
                if new_tender_code and new_tender_desc:
                    full_new_tender = f"{new_tender_code} - {new_tender_desc}"
                    if full_new_tender not in st.session_state.active_tenders:
                        st.session_state.active_tenders.append(full_new_tender)
                        commit_db()
                        st.success(f"Added new tender: {full_new_tender}")
                        st.rerun()
                    else:
                        st.warning("Tender already exists.")
                else:
                    st.error("Please provide both tender code and description.")

        with admin_tab3:
            st.markdown("### ⚙️ Site Content & Header Customization")
            new_company_name = st.text_input("Header Company Name", value=st.session_state.site_config.get("company_name", ""))
            new_subtitle = st.text_input("Header Subtitle / Location", value=st.session_state.site_config.get("location_subtitle", ""))
            
            if st.button("💾 Save Site Configuration"):
                st.session_state.site_config["company_name"] = new_company_name
                st.session_state.site_config["location_subtitle"] = new_subtitle
                commit_db()
                st.success("Site configuration updated successfully!")
                st.rerun()

        with admin_tab4:
            st.markdown("### 👥 User & Credential Manager")
            if len(st.session_state.users) > 0:
                user_options = {f"{u['username']} ({u['role']})": idx for idx, u in enumerate(st.session_state.users)}
                selected_user_label = st.selectbox("Select User Account to Modify / Remove", list(user_options.keys()))
                selected_u_idx = user_options[selected_user_label]
                target_user = st.session_state.users[selected_u_idx]
                
                st.markdown("")
                with st.container():
                    st.markdown("#### ✏️ Edit User Details & Password")
                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        edit_username = st.text_input("Username", value=target_user.get("username", ""), key="edit_username_val")
                        edit_password = st.text_input("Password", value=target_user.get("password", ""), type="password", key="edit_password_val")
                    with col_u2:
                        edit_role = st.selectbox("Assigned Role", ["System Administrator", "Internal Auditor / Compliance", "Tender Committee Member"], index=["System Administrator", "Internal Auditor / Compliance", "Tender Committee Member"].index(target_user.get("role")) if target_user.get("role") in ["System Administrator", "Internal Auditor / Compliance", "Tender Committee Member"] else 0, key="edit_role_val")
                        edit_status = st.selectbox("Account Status", ["Active", "Inactive"], index=0 if target_user.get("status") == "Active" else 1, key="edit_status_val")
                    
                    edit_access = st.text_input("Access Description", value=target_user.get("access", ""), key="edit_access_val")
                    
                    col_uu_btn1, col_uu_btn2 = st.columns([2, 1])
                    with col_uu_btn1:
                        if st.button("💾 Update User Account", type="primary"):
                            st.session_state.users[selected_u_idx]["username"] = edit_username
                            st.session_state.users[selected_u_idx]["password"] = edit_password
                            st.session_state.users[selected_u_idx]["role"] = edit_role
                            st.session_state.users[selected_u_idx]["status"] = edit_status
                            st.session_state.users[selected_u_idx]["access"] = edit_access
                            commit_db()
                            st.success("User account updated successfully!")
                            st.rerun()
                    with col_uu_btn2:
                        if st.button("🗑️ Delete User", type="secondary"):
                            if len(st.session_state.users) <= 1:
                                st.error("Cannot delete the last remaining user account.")
                            else:
                                st.session_state.users.pop(selected_u_idx)
                                commit_db()
                                st.success("User account removed successfully!")
                                st.rerun()
            
            st.markdown("---")
            st.markdown("#### ➕ Add New User Account")
            col_nu1, col_nu2 = st.columns(2)
            with col_nu1:
                new_username = st.text_input("New Username", key="new_username_input")
                new_password = st.text_input("New Password", type="password", key="new_password_input")
            with col_nu2:
                new_role = st.selectbox("New User Role", ["System Administrator", "Internal Auditor / Compliance", "Tender Committee Member"], key="new_role_input")
                new_access = st.text_input("Access Description Details", value="Portal Access", key="new_access_input")
            
            if st.button("Create User Account", type="primary"):
                if new_username and new_password:
                    if any(u["username"] == new_username for u in st.session_state.users):
                        st.error("Username already exists.")
                    else:
                        st.session_state.users.append({
                            "username": new_username,
                            "password": new_password,
                            "role": new_role,
                            "access": new_access,
                            "status": "Active"
                        })
                        commit_db()
                        st.success(f"User account '{new_username}' created successfully!")
                        st.rerun()
                else:
                    st.error("Please provide both username and password.")

            st.markdown("---")
            st.markdown("#### 📑 Active System Users Overview")
            st.dataframe(pd.DataFrame(st.session_state.users), use_container_width=True)

        with admin_tab5:
            st.markdown("### 💾 Database Backup & System Restore")
            db_json_str = json.dumps({
                "submissions": st.session_state.submissions,
                "active_tenders": st.session_state.active_tenders,
                "site_config": st.session_state.site_config,
                "users": st.session_state.users
            }, indent=4)
            
            st.download_button(
                label="📥 Download Full System Database (.json)",
                data=db_json_str,
                file_name=f"cis_tender_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    else:
        st.warning("⚠️ Please enter the correct admin password in the sidebar to access management portals.")

# --- AUDITOR PORTAL VIEW ---
elif nav_mode == "Auditor Portal":
    st.title("Opening Tender Committee")
    st.subheader("Cement Industries (Sabah) Sdn Bhd - Auditor Compliance Portal")
    
    if st.session_state.get("is_auditor", False):
        st.markdown("### 📊 Auditor Compliance Dashboard & Official Detailed Register")
        if len(st.session_state.submissions) == 0:
            st.info("No declarations submitted yet.")
        else:
            df = pd.DataFrame(st.session_state.submissions)
            st.dataframe(df, use_container_width=True)
            
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Detailed Audit Register to CSV",
                data=csv_data,
                file_name=f"CIS_Detailed_Audit_Register_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
            
            st.markdown("---")
            logo_html = f'<img src="{LOGO_BASE64}" class="logo" alt="CIS Logo">' if LOGO_BASE64 else '<div style="font-weight:bold; color:#777; margin-bottom:10px;">[ CIS LOGO MISSING / NOT FOUND ]</div>'
            
            total_count = len(df)
            conflicts_count = len(df[df['Status'] == 'Conflict of Interest Exists'])
            clean_count = total_count - conflicts_count

            report_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Times New Roman', Times, serif, Arial, sans-serif; color: #111; padding: 25px; background-color: #f4f6f9; }}
                    .report-container {{ background: #ffffff; border: 1px solid #cbd5e1; padding: 35px; max-width: 950px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
                    .header-table {{ width: 100%; border-bottom: 2px solid #1e293b; padding-bottom: 20px; margin-bottom: 20px; }}
                    .logo {{ max-width: 140px; height: auto; display: block; }}
                    .company-title {{ font-size: 17px; font-weight: 900; letter-spacing: 0.8px; text-transform: uppercase; color: #0f172a; text-align: right; }}
                    .report-subtitle {{ font-size: 11px; font-weight: 700; margin-top: 4px; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; text-align: right; }}
                    .meta-info {{ font-size: 9px; color: #64748b; margin-top: 4px; text-align: right; font-family: monospace; }}
                    
                    .summary-grid {{ display: flex; gap: 15px; margin-bottom: 20px; }}
                    .summary-box {{ flex: 1; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px 15px; text-align: center; }}
                    .summary-label {{ font-size: 9px; text-transform: uppercase; color: #64748b; font-weight: bold; }}
                    .summary-val {{ font-size: 15px; font-weight: bold; color: #0f172a; margin-top: 3px; }}

                    .section-heading {{ font-size: 12px; font-weight: bold; text-transform: uppercase; color: #1e293b; margin-bottom: 8px; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }}
                    
                    table {{ width: 100%; border-collapse: collapse; margin-top: 5px; margin-bottom: 20px; font-size: 9.5px; }}
                    th, td {{ border: 1px solid #94a3b8; padding: 7px; text-align: left; color: #1e293b; vertical-align: top; }}
                    th {{ background-color: #1e293b; color: #ffffff; font-weight: 700; text-transform: uppercase; font-size: 8.5px; letter-spacing: 0.5px; }}
                    tr:nth-child(even) {{ background-color: #f8fafc; }}
                    
                    .signature-section {{ margin-top: 30px; display: flex; justify-content: space-between; page-break-inside: avoid; }}
                    .signature-box {{ width: 45%; border-top: 1px solid #94a3b8; padding-top: 6px; font-size: 10px; color: #334155; }}
                    
                    .print-btn {{ background-color: #1e293b; color: white; border: none; padding: 10px 22px; font-size: 13px; border-radius: 4px; cursor: pointer; margin-bottom: 20px; font-weight: bold; letter-spacing: 0.5px; display: block; margin-left: auto; margin-right: auto; }}
                    .print-btn:hover {{ background-color: #0f172a; }}
                    
                    @media print {{
                        .print-btn {{ display: none; }}
                        body {{ background-color: #fff; padding: 0; }}
                        .report-container {{ border: none; box-shadow: none; padding: 0; max-width: 100%; }}
                        th {{ background-color: #1e293b !important; color: #ffffff !important; -webkit-print-color-adjust: exact; }}
                    }}
                </style>
                <script>function printReport() {{ window.print(); }}</script>
            </head>
            <body>
                <button class="print-btn" onclick="printReport()">🖨️ Print / Save Official Detailed PDF Report</button>
                <div class="report-container">
                    <table class="header-table">
                        <tr>
                            <td style="border: none; padding: 10px 0; width: 35%; vertical-align: middle;">{logo_html}</td>
                            <td style="border: none; padding: 10px 0; width: 65%; vertical-align: middle;">
                                <div class="company-title">{st.session_state.site_config.get('company_name')}</div>
                                <div class="report-subtitle">Official Detailed Conflict of Interest Audit Register</div>
                                <div class="meta-info">Doc Ref: CIS/OTC/COI-DET/{datetime.now().strftime('%Y/%m')} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                            </td>
                        </tr>
                    </table>

                    <div class="summary-grid">
                        <div class="summary-box">
                            <div class="summary-label">Total Submissions</div>
                            <div class="summary-val">{total_count}</div>
                        </div>
                        <div class="summary-box">
                            <div class="summary-label">Clean Declarations</div>
                            <div class="summary-val" style="color: #047857;">{clean_count}</div>
                        </div>
                        <div class="summary-box">
                            <div class="summary-label">Conflicts Flagged</div>
                            <div class="summary-val" style="color: #b45309;">{conflicts_count}</div>
                        </div>
                    </div>

                    <div class="section-heading">Detailed Committee Member Declarations Log</div>
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 3%;">No.</th>
                                <th style="width: 12%;">Timestamp</th>
                                <th style="width: 13%;">Tender Ref</th>
                                <th style="width: 14%;">Member Name</th>
                                <th style="width: 8%;">Emp No</th>
                                <th style="width: 11%;">Position</th>
                                <th style="width: 10%;">Dept</th>
                                <th style="width: 15%;">Status</th>
                                <th style="width: 14%;">Conflict / Tenderer Details</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            for idx, row in df.iterrows():
                details_text = f"<b>Tenderer:</b> {row.get('Tenderer Involved', 'None')}<br><b>Details:</b> {row.get('Conflict Details', 'None')}"
                report_html += f"""
                            <tr>
                                <td>{idx + 1}</td>
                                <td>{row['Timestamp']}</td>
                                <td><b>{row['Tender Ref']}</b></td>
                                <td><b>{row['Name']}</b></td>
                                <td>{row['Employee No']}</td>
                                <td>{row['Position']}</td>
                                <td>{row['Department']}</td>
                                <td><b>{row['Status']}</b></td>
                                <td style="font-size: 8.5px;">{details_text}</td>
                            </tr>
                """
            report_html += f"""
                        </tbody>
                    </table>

                    <div class="signature-section">
                        <div class="signature-box">
                            <b>Verified By (Internal Auditor / Compliance):</b><br><br><br>
                            Signature: __________________________<br>
                            Name: _____________________________<br>
                            Date: _____________________________
                        </div>
                        <div class="signature-box">
                            <b>Acknowledged By (Procurement Head):</b><br><br><br>
                            Signature: __________________________<br>
                            Name: _____________________________<br>
                            Date: _____________________________
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            components.html(report_html, height=750, scrolling=True)
    else:
        st.warning("⚠ Please enter the correct auditor password in the sidebar to view audit records.")

# --- PUBLIC FORM VIEW ---
else:
    logo_img_tag = f'<img src="{LOGO_BASE64}" style="max-height: 55px; width: auto; display: block;" alt="CIS Logo">' if LOGO_BASE64 else '<span style="font-weight:bold; font-size:16px; color:#333;">CIS LOGO</span>'
    
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0b1329 0%, #172a54 100%); padding: 20px 25px; border-radius: 10px; display: flex; align-items: center; gap: 25px; margin-bottom: 20px; box-shadow: 0 6px 12px rgba(0,0,0,0.4); border: 1px solid #28468a;">
            <div style="background-color: #ffffff; padding: 10px 15px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                {logo_img_tag}
            </div>
            <div style="display: flex; flex-direction: column; justify-content: center;">
                <div style="color: #ffffff; font-size: 19px; font-weight: 900; letter-spacing: 1px; text-transform: uppercase;">{st.session_state.site_config.get('company_name')}</div>
                <div style="color: #cbd5e0; font-size: 12px; font-weight: 600; margin-top: 5px; letter-spacing: 0.4px;">{st.session_state.site_config.get('location_subtitle')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    step_num = st.session_state.step
    col_step1, col_step2, col_step3 = st.columns(3)
    with col_step1:
        st.markdown(f"**Step 1:** Member Info {'✅' if step_num > 1 else '🔵'}")
    with col_step2:
        st.markdown(f"**Step 2:** Conflict Disclosure {'✅' if step_num > 2 else ('🔵' if step_num == 2 else '⚪')}")
    with col_step3:
        st.markdown(f"**Step 3:** Confirmation {'🔵' if step_num == 3 else '⚪'}")
    
    st.progress(step_num / 3.0)
    st.markdown("---")

    if step_num == 1:
        st.markdown("### 🏢 Step 1: Tender Selection & Member Information")
        st.markdown("Please select the active tender event you are evaluating and input your official credentials.")
        
        if len(st.session_state.active_tenders) == 0:
            st.warning("⚠️ There are currently no active tenders available for selection. Please contact the administrator.")
        else:
            selected_tender = st.selectbox(
                "Select Active Tender Event *",
                st.session_state.active_tenders,
                index=0 if "selected_tender" not in st.session_state or st.session_state.get("selected_tender") not in st.session_state.active_tenders else st.session_state.active_tenders.index(st.session_state.get("selected_tender"))
            )
            
            st.markdown("---")
            name = st.text_input("Full Name (as per ID/Record) *", value=st.session_state.get("name", ""))
            emp_no = st.text_input("Employee Number *", value=st.session_state.get("emp_no", ""))
            position = st.text_input("Position / Designation *", value=st.session_state.get("position", ""))
            department = st.text_input("Department / Division *", value=st.session_state.get("department", ""))
            
            if st.button("Next: Conflict Disclosure ➡️", type="primary"):
                if not name or not emp_no or not position or not department:
                    st.error("Please fill in all required fields before proceeding.")
                else:
                    st.session_state.selected_tender = selected_tender
                    st.session_state.name = name
                    st.session_state.emp_no = emp_no
                    st.session_state.position = position
                    st.session_state.department = department
                    next_step()
                    st.rerun()

    elif step_num == 2:
        st.markdown(f"### ⚖ Step 2: Conflict Disclosure & Undertakings")
        st.info(f"📌 Declaring for Tender: **{st.session_state.get('selected_tender')}**")
        
        conflict_choice = st.radio(
            "I confirm that I have no direct or indirect personal, financial, or business interest in any bidder, supplier, contractor, or related party participating in this tender. *",
            ["No Conflict of Interest", "Conflict of Interest Exists"],
            index=0 if st.session_state.get("conflict_choice") == "No Conflict of Interest" else 1
        )
        
        conflict_details = st.text_area(
            "Details of actual or potential conflict (if any):",
            value=st.session_state.get("conflict_details", "")
        )
        
        tenderer_involved = st.text_area(
            "Name of Tenderer(s) Involved (if any):",
            value=st.session_state.get("tenderer_involved", "")
        )
        
        st.markdown("---")
        st.markdown("#### 📜 Code of Conduct & Undertakings")
        
        ack_1 = st.radio(
            "1. I shall act with integrity, transparency, and impartiality in accordance with the Company's Code of Conduct, Procurement Policy, and applicable GLC governance requirements.\n"
            "2. I shall not solicit, accept, or receive any gift, hospitality, inducement, or benefit from any tenderer.\n"
            "3. I shall maintain strict confidentiality of all tender-related information.\n"
            "4. I shall immediately declare any conflict of interest that may arise during the tender process.\n"
            "5. I understand that failure to disclose a conflict of interest may result in disciplinary action. *",
            ["Agree", "Disagree"],
            index=0 if st.session_state.get("ack_1") == "Agree" else 1
        )
        
        ack_2 = st.radio(
            "I understand that failure to declare or the provision of false or misleading information may result in disciplinary action, removal from the committee, and/or other actions in accordance with applicable laws, regulations, and Company policies. *",
            ["Agree", "Disagree"],
            index=0 if st.session_state.get("ack_2") == "Agree" else 1
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅ Back to Info"):
                prev_step()
                st.rerun()
        with col2:
            if st.button("Submit Official Declaration ✅", type="primary"):
                if ack_1 == "Disagree" or ack_2 == "Disagree":
                    st.error("You must agree to the terms and undertakings to submit this declaration.")
                else:
                    tender_ref_code = st.session_state.selected_tender.split(" - ")[0]
                    submission_data = {
                        "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "Tender Ref": tender_ref_code,
                        "Name": st.session_state.name,
                        "Employee No": st.session_state.emp_no,
                        "Position": st.session_state.position,
                        "Department": st.session_state.department,
                        "Status": conflict_choice,
                        "Conflict Details": conflict_details if conflict_details else "None",
                        "Tenderer Involved": tenderer_involved if tenderer_involved else "None",
                        "Agreed Terms": "Yes"
                    }
                    st.session_state.submissions.append(submission_data)
                    commit_db()
                    
                    st.session_state.conflict_choice = conflict_choice
                    st.session_state.conflict_details = conflict_details
                    st.session_state.tenderer_involved = tenderer_involved
                    next_step()
                    st.rerun()

    elif step_num == 3:
        status_badge_html = '<span style="background-color: #065f46; color: #d1fae5; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 13px; display: inline-block; border: 1px solid #10b981;">✅ No Conflict of Interest</span>' if st.session_state.get('conflict_choice') == "No Conflict of Interest" else '<span style="background-color: #92400e; color: #fef3c7; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 13px; display: inline-block; border: 1px solid #f59e0b;">⚠️ Conflict of Interest Exists</span>'
        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        st.success("🎉 Declaration submitted successfully! Your record has been securely logged into the CIS compliance database.")
        
        conflict_extra_section = f"""
        <div class="conflict-details-box">
            <div style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px dashed #334155;">
                <div style="color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Conflict Details</div>
                <div style="color: #f8fafc; font-size: 13px; font-weight: 500;">{st.session_state.get('conflict_details')}</div>
            </div>
            <div>
                <div style="color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Tenderer(s) Involved</div>
                <div style="color: #f8fafc; font-size: 13px; font-weight: 500;">{st.session_state.get('tenderer_involved')}</div>
            </div>
        </div>
        """ if st.session_state.get('conflict_choice') == "Conflict of Interest Exists" else ""

        receipt_card_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    background-color: transparent;
                    margin: 0;
                    padding: 5px;
                }}
                .receipt-card {{
                    background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%);
                    border: 1px solid #334155;
                    border-radius: 14px;
                    padding: 24px;
                    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
                }}
                .receipt-title {{
                    font-size: 16px;
                    font-weight: 700;
                    color: #38bdf8;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    border-bottom: 2px solid #334155;
                    padding-bottom: 12px;
                    margin-bottom: 16px;
                    letter-spacing: 0.5px;
                }}
                .tender-box {{
                    background: rgba(15, 23, 42, 0.6);
                    border: 1px solid #475569;
                    padding: 12px 16px;
                    border-radius: 8px;
                    margin-bottom: 16px;
                }}
                .tender-label {{
                    font-size: 11px;
                    color: #94a3b8;
                    font-weight: 600;
                    text-transform: uppercase;
                    margin-bottom: 4px;
                }}
                .tender-val {{
                    font-size: 13px;
                    color: #f8fafc;
                    font-weight: 600;
                }}
                .grid-2 {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                    margin-bottom: 16px;
                }}
                .info-group {{
                    background: rgba(30, 41, 59, 0.5);
                    padding: 10px 14px;
                    border-radius: 8px;
                    border-left: 3px solid #38bdf8;
                }}
                .info-label {{
                    font-size: 11px;
                    color: #94a3b8;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                .info-val {{
                    font-size: 13px;
                    color: #f8fafc;
                    font-weight: 600;
                    margin-top: 2px;
                }}
                .status-section {{
                    background: rgba(15, 23, 42, 0.5);
                    padding: 14px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-top: 16px;
                    border: 1px solid #334155;
                }}
                .conflict-details-box {{
                    background: rgba(30, 41, 59, 0.5);
                    border: 1px solid #334155;
                    border-radius: 8px;
                    padding: 14px;
                    margin-top: 16px;
                }}
                .footer-meta {{
                    margin-top: 16px;
                    padding-top: 12px;
                    border-top: 1px solid #334155;
                    font-size: 11px;
                    color: #64748b;
                    text-align: right;
                    font-family: monospace;
                }}
            </style>
        </head>
        <body>
            <div class="receipt-card">
                <div class="receipt-title">
                    📋 Official Submission Receipt & Summary
                </div>
                
                <div class="tender-box">
                    <div class="tender-label">Tender Event</div>
                    <div class="tender-val">{st.session_state.get('selected_tender')}</div>
                </div>
                
                <div class="grid-2">
                    <div class="info-group">
                        <div class="info-label">Committee Member</div>
                        <div class="info-val">{st.session_state.get('name')}</div>
                    </div>
                    <div class="info-group" style="border-left-color: #818cf8;">
                        <div class="info-label">Employee Number</div>
                        <div class="info-val">{st.session_state.get('emp_no')}</div>
                    </div>
                </div>

                <div class="grid-2">
                    <div class="info-group" style="border-left-color: #34d399;">
                        <div class="info-label">Position / Designation</div>
                        <div class="info-val">{st.session_state.get('position')}</div>
                    </div>
                    <div class="info-group" style="border-left-color: #f472b6;">
                        <div class="info-label">Department / Division</div>
                        <div class="info-val">{st.session_state.get('department')}</div>
                    </div>
                </div>
                
                <div class="status-section">
                    <div>
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Declaration Status</div>
                    </div>
                    <div>
                        {status_badge_html}
                    </div>
                </div>

                {conflict_extra_section}
                
                <div class="footer-meta">
                    Secure Timestamp: {timestamp_str} &bull; Ref: CIS-OTC-{datetime.now().strftime('%Y%m%d%H%M%S')}
                </div>
            </div>
        </body>
        </html>
        """
        
        components.html(receipt_card_html, height=580, scrolling=False)
        
        st.markdown("")
        if st.button("🔄 Submit Another Declaration", type="primary"):
            st.session_state.step = 1
            st.rerun()
