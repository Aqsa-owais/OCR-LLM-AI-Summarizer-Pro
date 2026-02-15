"""
Secure OCR + AI Summarizer - Enhanced Version
With Analytics, History, Search, Batch Processing, PDF Support
"""
import streamlit as st
from auth import signup_user, login_user, logout_user
from ocr import extract_text_from_image
from llm_agent import summarize_text
from script_analyzer import analyze_script, detect_language
from pdf_ocr import extract_text_from_pdf
from database import (create_users_table, create_ocr_history_table, save_ocr_result, 
                     get_user_history, search_history, get_user_statistics, delete_history_item)
from email_notifications import send_processing_complete_email
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="OCR + AI Pro",
    page_icon="🔒",
    layout="wide"
)

# Initialize tables
create_users_table()
create_ocr_history_table()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def main():
    st.title("🔒 OCR + AI Summarizer Pro")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        
        if not st.session_state.logged_in:
            page = st.radio("Go to", ["Login", "Signup"])
        else:
            st.success(f"👤 {st.session_state.username}")
            page = st.radio("Go to", ["Dashboard", "Script Analyzer", "Analytics", "History", "Batch Process"])
            
            if st.button("🚪 Logout"):
                logout_user()
                st.rerun()
    
    # Route to pages
    if page == "Login":
        show_login_page()
    elif page == "Signup":
        show_signup_page()
    elif page == "Dashboard":
        if st.session_state.logged_in:
            show_dashboard()
        else:
            st.warning("Please login")
    elif page == "Script Analyzer":
        if st.session_state.logged_in:
            show_script_analyzer()
        else:
            st.warning("Please login")
    elif page == "Analytics":
        if st.session_state.logged_in:
            show_analytics()
        else:
            st.warning("Please login")
    elif page == "History":
        if st.session_state.logged_in:
            show_history()
        else:
            st.warning("Please login")
    elif page == "Batch Process":
        if st.session_state.logged_in:
            show_batch_process()
        else:
            st.warning("Please login")

def show_login_page():
    st.header("🔐 Login")
    
    # Check for demo mode or actual Google OAuth
    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    
    # Google Sign-In Section
    st.subheader("Quick Sign In")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Create Google button
        st.markdown("""
        <style>
        .google-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            border: 1px solid #dadce0;
            border-radius: 4px;
            padding: 12px 24px;
            cursor: pointer;
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
            font-weight: 500;
            color: #3c4043;
            transition: background-color 0.3s, box-shadow 0.3s;
            margin: 20px auto;
            width: 100%;
            max-width: 300px;
        }
        .google-btn:hover {
            background-color: #f8f9fa;
            box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
        }
        .google-icon {
            width: 18px;
            height: 18px;
            margin-right: 12px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Google button with demo functionality
        if st.button("🔵 Continue with Google", use_container_width=True, key="google_btn"):
            if google_client_id:
                st.info("🔄 Redirecting to Google Sign-In...")
                st.info("📝 Full OAuth implementation requires Google Cloud setup. See README.")
            else:
                # Demo mode - show input for email
                st.session_state.show_google_demo = True
        
        # Show demo input if button clicked and no client ID
        if not google_client_id and st.session_state.get('show_google_demo', False):
            st.info("📧 Demo Mode: Enter your email to create/login with Google-style account")
            
            with st.form("google_demo_form"):
                demo_email = st.text_input("Email", placeholder="your-email@gmail.com")
                demo_name = st.text_input("Name", placeholder="Your Name")
                demo_submit = st.form_submit_button("Continue")
                
                if demo_submit and demo_email and demo_name:
                    # Create/login user
                    from google_oauth import handle_google_signup
                    user = handle_google_signup(demo_email, demo_name)
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user['username']
                        st.session_state.user_id = user['id']
                        st.success(f"✅ Signed in as {demo_name}!")
                        st.session_state.show_google_demo = False
                        st.rerun()
                    else:
                        st.error("Error creating account")
        
        if google_client_id:
            st.caption("✅ Google OAuth configured")
        else:
            st.caption("⚙️ Demo mode active - Add GOOGLE_CLIENT_ID for full OAuth")
    
    st.divider()
    st.subheader("Or sign in with email")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if email and password:
                result = login_user(email, password)
                if result['success']:
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['message'])
            else:
                st.error("Please fill in all fields")

def show_script_analyzer():
    st.header("💻 Script Analyzer")
    st.info("📸 Upload an image of code/script to analyze it with AI")
    
    # Analysis type selector
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_type = st.selectbox(
            "🔍 Analysis Type",
            ["Full Analysis", "Bug Detection", "Code Review", "Explanation"]
        )
    
    with col2:
        output_language = st.selectbox(
            "🌍 Output Language",
            ["English", "Urdu"]
        )
    
    # File upload tabs
    tab1, tab2 = st.tabs(["📤 Upload Image", "📸 Take Photo"])
    
    uploaded_file = None
    
    with tab1:
        uploaded_file = st.file_uploader("Upload code image", type=['jpg', 'jpeg', 'png'], key="code_img")
    
    with tab2:
        camera_photo = st.camera_input("Take photo of code", key="code_cam")
        if camera_photo:
            uploaded_file = camera_photo
    
    if uploaded_file:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📷 Code Image")
            uploaded_file.seek(0)
            st.image(uploaded_file, use_container_width=True)
        
        with col2:
            if st.button("🚀 Analyze Code", type="primary", use_container_width=True):
                start_time = time.time()
                
                with st.spinner("Extracting code from image..."):
                    uploaded_file.seek(0)
                    extracted_code = extract_text_from_image(uploaded_file, "Auto Detect")
                    
                    if extracted_code and not extracted_code.startswith("ERROR:"):
                        st.success("✅ Code extracted!")
                        
                        # Display extracted code
                        with st.expander("📄 Extracted Code", expanded=False):
                            st.code(extracted_code, language="python")
                        
                        # Detect language
                        with st.spinner("Detecting programming language..."):
                            detected_lang = detect_language(extracted_code)
                            st.info(f"🔍 Detected Language: **{detected_lang}**")
                        
                        # Analyze code
                        with st.spinner(f"Analyzing code ({analysis_type})..."):
                            # If output language is not English, add translation instruction
                            if output_language != "English":
                                analysis_instruction = f"{analysis_type} (Provide analysis in {output_language})"
                            else:
                                analysis_instruction = analysis_type
                            
                            analysis_result = analyze_script(extracted_code, analysis_instruction)
                            
                            if analysis_result['success']:
                                processing_time = time.time() - start_time
                                
                                st.success(f"✅ Analysis complete in {processing_time:.2f}s!")
                                
                                # Display analysis
                                with st.expander("🤖 AI Analysis", expanded=True):
                                    st.markdown(analysis_result['analysis'])
                                
                                # Metrics
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("Language", detected_lang)
                                with col_b:
                                    st.metric("Tokens", analysis_result['tokens'])
                                with col_c:
                                    st.metric("Time", f"{processing_time:.2f}s")
                                
                                # Download buttons
                                col_d, col_e = st.columns(2)
                                
                                with col_d:
                                    st.download_button(
                                        "📥 Download Code",
                                        extracted_code,
                                        file_name="extracted_code.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                                
                                with col_e:
                                    st.download_button(
                                        "📥 Download Analysis",
                                        analysis_result['analysis'],
                                        file_name="code_analysis.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                            else:
                                st.error(f"Error: {analysis_result.get('message')}")
                    else:
                        st.error("No code found in image. Please try another image.")

def show_signup_page():
    st.header("📝 Create Account")
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    result = signup_user(username, email, password)
                    if result['success']:
                        st.success(result['message'])
                        st.info("Please login with your credentials")
                    else:
                        st.error(result['message'])
            else:
                st.error("Please fill in all fields")

def show_dashboard():
    st.header("📸 OCR + AI Dashboard")
    
    # Initialize session state for uploaded file
    if 'uploaded_file_data' not in st.session_state:
        st.session_state.uploaded_file_data = None
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None
    
    # Settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        summary_length = st.selectbox("📏 Length", ["Short", "Medium", "Detailed"])
    
    with col2:
        output_language = st.selectbox("🌍 Summary Language", 
            ["English", "Urdu", "Spanish", "French", "German", "Chinese", "Japanese"])
    
    with col3:
        send_email = st.checkbox("📧 Email me", help="Send results via email")
    
    # OCR is always Auto Detect (English)
    ocr_language = "Auto Detect"
    
    # File type tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload Image", "📸 Camera", "📄 PDF"])
    
    uploaded_file = None
    file_type = "image"
    
    with tab1:
        uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'], key="img")
        if uploaded_file:
            # Store in session state
            uploaded_file.seek(0)
            st.session_state.uploaded_file_data = uploaded_file.read()
            st.session_state.uploaded_file_name = uploaded_file.name
    
    with tab2:
        camera_photo = st.camera_input("Take Photo", key="cam")
        if camera_photo:
            camera_photo.seek(0)
            st.session_state.uploaded_file_data = camera_photo.read()
            st.session_state.uploaded_file_name = camera_photo.name
            uploaded_file = camera_photo
    
    with tab3:
        pdf_file = st.file_uploader("Upload PDF", type=['pdf'], key="pdf")
        if pdf_file:
            pdf_file.seek(0)
            st.session_state.uploaded_file_data = pdf_file.read()
            st.session_state.uploaded_file_name = pdf_file.name
            uploaded_file = pdf_file
            file_type = "pdf"
    
    # Display image from session state
    if st.session_state.uploaded_file_data:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if file_type == "image":
                st.image(st.session_state.uploaded_file_data, use_container_width=True)
            else:
                st.info(f"📄 PDF: {st.session_state.uploaded_file_name}")
        
        with col2:
            if st.button("🚀 Extract & Summarize", type="primary", use_container_width=True):
                start_time = time.time()
                
                with st.spinner(f"Processing {file_type}..."):
                    # Create BytesIO from stored data
                    import io
                    file_obj = io.BytesIO(st.session_state.uploaded_file_data)
                    file_obj.name = st.session_state.uploaded_file_name
                    
                    # Extract text
                    if file_type == "pdf":
                        extracted_text = extract_text_from_pdf(file_obj, ocr_language)
                    else:
                        extracted_text = extract_text_from_image(file_obj, ocr_language)
                    
                    if extracted_text and not extracted_text.startswith("ERROR:"):
                        st.success("✅ Text extracted!")
                        
                        with st.expander("📄 Extracted Text", expanded=False):
                            st.text_area("", extracted_text, height=150, key="ext")
                        
                        # Summarize
                        with st.spinner(f"Generating summary in {output_language}..."):
                            summary_result = summarize_text(extracted_text, summary_length, output_language)
                            
                            if summary_result['success']:
                                processing_time = time.time() - start_time
                                
                                st.success(f"✅ Done in {processing_time:.2f}s!")
                                
                                with st.expander("🤖 AI Summary", expanded=True):
                                    st.markdown(summary_result['summary'])
                                
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("Tokens", summary_result['tokens'])
                                with col_b:
                                    st.metric("Time", f"{processing_time:.2f}s")
                                with col_c:
                                    st.metric("Language", output_language)
                                
                                # Save to history
                                save_ocr_result(
                                    st.session_state.user_id,
                                    uploaded_file.name,
                                    extracted_text,
                                    summary_result['summary'],
                                    summary_length,
                                    output_language,
                                    summary_result['tokens'],
                                    processing_time
                                )
                                
                                # Send email if requested
                                if send_email:
                                    with st.spinner("Sending email..."):
                                        from email_notifications import send_processing_complete_email
                                        from database import get_user_by_id
                                        
                                        user = get_user_by_id(st.session_state.user_id)
                                        if user and user.get('email'):
                                            email_sent = send_processing_complete_email(
                                                user['email'],
                                                user['username'],
                                                uploaded_file.name,
                                                summary_result['summary']
                                            )
                                            if email_sent:
                                                st.success(f"📧 Email sent to {user['email']}!")
                                            else:
                                                st.warning("📧 Email not sent. Please check SMTP settings in .env file")
                                        else:
                                            st.warning("📧 Email not configured")
                                
                                # Download
                                st.download_button(
                                    "📥 Download Summary",
                                    summary_result['summary'],
                                    file_name=f"summary_{output_language}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"Error: {summary_result.get('message')}")
                    else:
                        st.error(extracted_text if extracted_text.startswith("ERROR:") else "No text found")

def show_analytics():
    st.header("📊 Analytics Dashboard")
    
    # Get statistics
    stats = get_user_statistics(st.session_state.user_id)
    
    if stats:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Processed", stats['total_ocr'] or 0)
        
        with col2:
            st.metric("Total Tokens", f"{stats['total_tokens'] or 0:,}")
        
        with col3:
            avg_time = stats['avg_processing_time'] or 0
            st.metric("Avg Time", f"{avg_time:.2f}s")
        
        with col4:
            st.metric("Active Days", stats['active_days'] or 0)
        
        st.divider()
        
        # Recent activity
        st.subheader("📈 Recent Activity")
        history = get_user_history(st.session_state.user_id, limit=5)
        
        if history:
            for item in history:
                with st.expander(f"📄 {item['filename']} - {item['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                    st.write(f"**Language:** {item['language']}")
                    st.write(f"**Tokens:** {item['tokens_used']}")
                    st.write(f"**Summary:** {item['summary'][:200]}...")
        else:
            st.info("No activity yet. Start processing images!")
    else:
        st.info("No statistics available yet.")

def show_history():
    st.header("📚 Processing History")
    
    # Search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search in history", placeholder="Search by filename or content...")
    with col2:
        st.write("")
        st.write("")
        if st.button("Clear", use_container_width=True):
            search_term = ""
    
    # Get history
    if search_term:
        history = search_history(st.session_state.user_id, search_term)
        st.info(f"Found {len(history)} results")
    else:
        history = get_user_history(st.session_state.user_id, limit=50)
    
    if history:
        for item in history:
            with st.expander(f"📄 {item['filename']} - {item['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Language:** {item['language']} | **Length:** {item['summary_length']} | **Tokens:** {item['tokens_used']}")
                    
                    st.write("**Summary:**")
                    st.write(item['summary'])
                    
                    st.write("**Extracted Text:**")
                    st.text_area("", item['extracted_text'], height=150, key=f"txt_{item['id']}", label_visibility="collapsed")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{item['id']}"):
                        if delete_history_item(item['id'], st.session_state.user_id):
                            st.success("Deleted!")
                            st.rerun()
                    
                    st.download_button(
                        "📥 Download",
                        item['summary'],
                        file_name=f"{item['filename']}_summary.txt",
                        key=f"down_{item['id']}"
                    )
    else:
        st.info("No history found. Start processing images!")

def show_batch_process():
    st.header("⚡ Batch Processing")
    st.info("Upload multiple images to process them all at once")
    
    # Settings
    col1, col2 = st.columns(2)
    with col1:
        summary_length = st.selectbox("Length", ["Short", "Medium", "Detailed"], key="batch_len")
    with col2:
        output_language = st.selectbox("Language", ["English", "Urdu"], key="batch_lang")
    
    # OCR is always Auto Detect
    ocr_language = "Auto Detect"
    
    # Multiple file upload
    uploaded_files = st.file_uploader(
        "Upload multiple images",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"📁 {len(uploaded_files)} files selected")
        
        if st.button("🚀 Process All", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processing {idx+1}/{len(uploaded_files)}: {file.name}")
                
                # Determine file type
                file_type = "pdf" if file.name.endswith('.pdf') else "image"
                
                # Extract text
                if file_type == "pdf":
                    extracted_text = extract_text_from_pdf(file, ocr_language)
                else:
                    file.seek(0)
                    extracted_text = extract_text_from_image(file, ocr_language)
                
                if extracted_text and not extracted_text.startswith("ERROR:"):
                    # Summarize
                    summary_result = summarize_text(extracted_text, summary_length, output_language)
                    
                    if summary_result['success']:
                        results.append({
                            'filename': file.name,
                            'summary': summary_result['summary'],
                            'tokens': summary_result['tokens']
                        })
                        
                        # Save to history
                        save_ocr_result(
                            st.session_state.user_id,
                            file.name,
                            extracted_text,
                            summary_result['summary'],
                            summary_length,
                            output_language,
                            summary_result['tokens'],
                            0
                        )
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("✅ Processing complete!")
            
            # Display results
            st.success(f"Processed {len(results)} files successfully!")
            
            for result in results:
                with st.expander(f"📄 {result['filename']}"):
                    st.write(result['summary'])
                    st.write(f"**Tokens used:** {result['tokens']}")
            
            # Download all summaries
            all_summaries = "\n\n" + "="*50 + "\n\n".join([
                f"File: {r['filename']}\n\n{r['summary']}" for r in results
            ])
            
            st.download_button(
                "📥 Download All Summaries",
                all_summaries,
                file_name="batch_summaries.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
