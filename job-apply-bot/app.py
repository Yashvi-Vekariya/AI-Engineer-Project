import streamlit as st
import time
from job_scraper import JobScraper
from notion_client import Client
from agent_manager import AgentManager
from config import JOB_KEYWORDS, JOB_LOCATIONS, validate_config

class NotionClient:
    def __init__(self):
        # Validate configuration first
        if not validate_config():
            st.error("⚠️  Please configure your API keys in the .env file!")
            st.stop()
        
        self.scraper = None
        self.notion = Client()
        self.agent = AgentManager()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'search_in_progress' not in st.session_state:
            st.session_state.search_in_progress = False
        if 'jobs_found' not in st.session_state:
            st.session_state.jobs_found = []
        if 'jobs_saved' not in st.session_state:
            st.session_state.jobs_saved = 0
        if 'search_completed' not in st.session_state:
            st.session_state.search_completed = False
    
    def run_job_search(self, keywords, locations, max_jobs=20):
        """Run the job search workflow"""
        st.session_state.search_in_progress = True
        st.session_state.search_completed = False
        
        try:
            # Initialize scraper
            with st.spinner("🚀 Initializing browser..."):
                self.scraper = JobScraper()
                time.sleep(1)
            
            # Step 1: Search for jobs
            with st.spinner(f"🔍 Scanning job sites for {len(keywords)} keywords in {len(locations)} locations..."):
                jobs = self.scraper.search_jobs(keywords, locations, max_jobs//len(keywords))
                st.session_state.jobs_found = jobs
            
            # Step 2: Save to Notion
            if jobs:
                with st.spinner(f"💾 Saving {len(jobs)} jobs to Notion..."):
                    saved_count = self.notion.save_jobs_batch(jobs)
                    st.session_state.jobs_saved = saved_count
            else:
                st.session_state.jobs_saved = 0
            
            st.session_state.search_completed = True
                
        except Exception as e:
            st.error(f"❌ Error during job search: {str(e)}")
        finally:
            st.session_state.search_in_progress = False
            if self.scraper:
                self.scraper.close()
    
    def display_ui(self):
        """Display the main user interface"""
        st.set_page_config(
            page_title="Job Apply Bot 🤖",
            page_icon="🤖",
            layout="wide"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-header">🤖 Job Apply Bot</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Automatically scan job sites and save opportunities to Notion</div>', unsafe_allow_html=True)
        
        self.initialize_session_state()
        
        # Sidebar for configuration
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Test connections first
            st.subheader("🔌 Test Connections")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Test Notion", use_container_width=True):
                    with st.spinner("Testing..."):
                        if self.notion.test_connection():
                            st.success("✅ Notion OK")
                        else:
                            st.error("❌ Check .env")
            
            with col2:
                if st.button("Test Groq", use_container_width=True):
                    with st.spinner("Testing..."):
                        if self.agent.test_connection():
                            st.success("✅ Groq OK")
                        else:
                            st.error("❌ Check .env")
            
            st.divider()
            
            # Job keywords
            st.subheader("🔍 Job Keywords")
            default_keywords = JOB_KEYWORDS
            keywords_input = st.text_area(
                "Enter job keywords (one per line):",
                value="\n".join(default_keywords),
                height=120,
                help="e.g., 'python developer', 'software engineer'"
            )
            keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]
            
            # Locations
            st.subheader("📍 Locations")
            default_locations = JOB_LOCATIONS
            locations_input = st.text_area(
                "Enter locations (one per line):",
                value="\n".join(default_locations),
                height=100,
                help="e.g., 'remote', 'new york', 'san francisco'"
            )
            locations = [l.strip() for l in locations_input.split('\n') if l.strip()]
            
            # Max jobs
            max_jobs = st.slider("Maximum jobs to find:", 5, 50, 20, 5)
            
            st.divider()
            
            # User profile for AI analysis
            st.subheader("👤 Your Profile")
            user_profile = st.text_area(
                "Enter your profile for AI analysis:",
                value="Software developer with 3+ years experience in Python, JavaScript, and cloud technologies. Looking for backend or full-stack roles with competitive salary and remote work options.",
                height=120,
                help="This helps AI analyze job relevance"
            )
            
            st.divider()
            
            # Start search button
            if st.session_state.search_in_progress:
                st.button("🔄 Search in Progress...", disabled=True, use_container_width=True, type="primary")
            else:
                if st.button("🚀 Start Job Search", type="primary", use_container_width=True):
                    if keywords and locations:
                        self.run_job_search(keywords, locations, max_jobs)
                        st.rerun()
                    else:
                        st.error("Please enter both keywords and locations")
            
            # Info
            st.divider()
            st.caption("💡 Tip: Start with fewer keywords and locations for faster results")
        
        # Main content area
        if st.session_state.search_in_progress:
            st.info("🔄 Job search in progress... Please wait, this may take a few minutes.")
            
            # Progress indicator
            with st.spinner("Searching..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)
                    progress_bar.progress(i + 1)
        
        elif st.session_state.search_completed and st.session_state.jobs_found:
            # Results section
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔍 Jobs Found", len(st.session_state.jobs_found))
            with col2:
                st.metric("💾 Saved to Notion", st.session_state.jobs_saved)
            with col3:
                success_rate = (st.session_state.jobs_saved / len(st.session_state.jobs_found) * 100) if st.session_state.jobs_found else 0
                st.metric("✅ Success Rate", f"{success_rate:.0f}%")
            
            st.success(f"✅ Job search completed! Found {len(st.session_state.jobs_found)} jobs and saved {st.session_state.jobs_saved} to Notion!")
            
            st.divider()
            
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📋 All Jobs", "🤖 AI Analysis", "📊 Statistics"])
            
            with tab1:
                st.subheader("All Jobs Found")
                
                # Display jobs
                for i, job in enumerate(st.session_state.jobs_found):
                    with st.expander(f"🏢 {job['title']} at {job['company']}", expanded=(i < 3)):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Company:** {job['company']}")
                            st.write(f"**Location:** {job['location']}")
                            st.write(f"**Source:** {job['source']}")
                            st.write(f"**Posted:** {job.get('date_posted', 'Recent')}")
                        
                        with col2:
                            if job.get('url'):
                                st.link_button("🔗 Apply Now", job['url'], use_container_width=True)
            
            with tab2:
                st.subheader("AI-Powered Job Analysis")
                
                # Select a job to analyze
                job_titles = [f"{job['title']} at {job['company']}" for job in st.session_state.jobs_found]
                selected_job_index = st.selectbox("Select a job to analyze:", range(len(job_titles)), format_func=lambda x: job_titles[x])
                
                if selected_job_index is not None:
                    selected_job = st.session_state.jobs_found[selected_job_index]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🔍 Analyze Job Relevance", use_container_width=True):
                            with st.spinner("🤖 AI is analyzing..."):
                                analysis = self.agent.analyze_job_relevance(selected_job, user_profile)
                            
                            st.write("### 📊 Relevance Analysis")
                            
                            # Relevance score with color
                            score = analysis.get('relevance_score', 50)
                            if score >= 70:
                                st.success(f"**Relevance Score:** {score}/100 ⭐")
                            elif score >= 50:
                                st.warning(f"**Relevance Score:** {score}/100")
                            else:
                                st.error(f"**Relevance Score:** {score}/100")
                            
                            st.write(f"**Is Relevant:** {'✅ Yes' if analysis.get('is_relevant') else '❌ No'}")
                            st.write(f"**Reasoning:** {analysis.get('reasoning', 'N/A')}")
                            
                            if analysis.get('suggested_actions'):
                                st.write("**Suggested Actions:**")
                                for action in analysis['suggested_actions']:
                                    st.write(f"- {action}")
                    
                    with col2:
                        if st.button("📝 Get Application Strategy", use_container_width=True):
                            with st.spinner("🤖 Generating strategy..."):
                                strategy = self.agent.generate_application_strategy(selected_job)
                            
                            st.write("### 📝 Application Strategy")
                            
                            if strategy.get('key_skills_required'):
                                st.write("**Key Skills Required:**")
                                for skill in strategy['key_skills_required']:
                                    st.write(f"- {skill}")
                            
                            if strategy.get('resume_tips'):
                                st.write("**Resume Tips:**")
                                for tip in strategy['resume_tips']:
                                    st.write(f"- {tip}")
                            
                            if strategy.get('cover_letter_points'):
                                st.write("**Cover Letter Points:**")
                                for point in strategy['cover_letter_points']:
                                    st.write(f"- {point}")
                            
                            st.info(f"⏰ {strategy.get('application_timeline', 'Apply soon')}")
            
            with tab3:
                st.subheader("Search Statistics")
                
                # Jobs by source
                sources = {}
                for job in st.session_state.jobs_found:
                    sources[job['source']] = sources.get(job['source'], 0) + 1
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Jobs by Source:**")
                    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"- {source}: {count}")
                
                with col2:
                    st.write("**Top Companies:**")
                    companies = {}
                    for job in st.session_state.jobs_found:
                        companies[job['company']] = companies.get(job['company'], 0) + 1
                    
                    for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:5]:
                        st.write(f"- {company}: {count}")
                
                # Locations breakdown
                st.write("**Locations:**")
                locations_found = {}
                for job in st.session_state.jobs_found:
                    locations_found[job['location']] = locations_found.get(job['location'], 0) + 1
                
                for location, count in sorted(locations_found.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.write(f"- {location}: {count}")
        
        else:
            # Welcome screen
            st.info("👈 Configure your job search in the sidebar and click **'Start Job Search'** to begin!")
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🔍 Step 1: Configure")
                st.write("Set your job keywords, locations, and profile in the sidebar")
            
            with col2:
                st.markdown("### 🤖 Step 2: Search")
                st.write("Click 'Start Job Search' and let the bot scan multiple job sites")
            
            with col3:
                st.markdown("### 💾 Step 3: Review")
                st.write("Review AI-analyzed jobs saved automatically to your Notion database")
            
            st.markdown("---")
            
            # How to use section
            with st.expander("📖 How to Use This Bot"):
                st.markdown("""
                **Prerequisites:**
                1. ✅ Groq API Key (free at console.groq.com)
                2. ✅ Notion API Key + Database ID
                3. ✅ Chrome browser installed
                
                **Steps:**
                1. **Test Connections** - Click test buttons in sidebar
                2. **Enter Keywords** - Add job titles you're interested in
                3. **Add Locations** - Specify where you want to work
                4. **Add Your Profile** - Help AI analyze relevance
                5. **Start Search** - Click the big button!
                6. **Review Results** - Check AI analysis and strategies
                7. **Apply** - Visit Notion to manage your applications
                
                **Tips:**
                - Start with 2-3 keywords for faster results
                - Use specific locations for better matches
                - Check Notion database for all saved jobs
                - Use AI analysis to prioritize applications
                """)
            
            with st.expander("⚙️ Notion Database Setup"):
                st.markdown("""
                **Your Notion database needs these properties:**
                
                1. **Title** (Title type) - Job title
                2. **Company** (Text type) - Company name
                3. **Location** (Text type) - Job location
                4. **Source** (Select type) - Options: Indeed, LinkedIn, Glassdoor
                5. **URL** (URL type) - Application link
                6. **Status** (Select type) - Options: To Apply, Applied, Interview, Rejected
                
                **Don't forget to:**
                - Share your database with the integration
                - Copy the database ID from the URL
                - Add it to your .env file
                """)
    
    def close(self):
        """Cleanup resources"""
        if self.scraper:
            self.scraper.close()

def main():
    bot = NotionClient()
    try:
        bot.display_ui()
    except Exception as e:
        st.error(f"❌ Application error: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    main()