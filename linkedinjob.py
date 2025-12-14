import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime
import random
import pandas as pd

# Page config
st.set_page_config(page_title="🔗 LinkedIn Jobs - FIXED", layout="wide")
st.title("🚀 LinkedIn Job Scraper - CONNECTION FIXED 2025")

# =============================================================================
# 🔑 YOUR COOKIES
# =============================================================================
COOKIES = {
    'LI_AT_COOKIE': 'AQEDATiJgtsFU8dAAAABmvSONBQAAAGbGJq4FFYAcyeBvsF2GHt6BjlgKk911Dd7zlX7FdAhcIIlo6YiV42Sgfz3PjAjuI6oqdysJG4XCo5ekJzbAFWI74-IaVCHZJU6lG70LDTkC_3RypnYvdQgSabF',
    'JSESSIONID': 'ajax:7939693935852710049',
    'LI_SUGR': '73334de9-fea1-4ab9-a2e2-287ab78bf09a',
    'LI_RM': 'AQFoHEngezYNBgAAAZol_Xw4bu9wera4DdVzJVbmSKkBX1-loovqcnVVXt7yx1rWLbxHdpjqnrdOvBfKTunZDLsB-VkhuIRIL3nbX1wSaPH13b0e0SAeEPy_',
    'LIDC': 'b=OB27:s=O:r=O:a=O:p=O:g=6064:u=352:x=1:i=1765039556:t=1765093862:v=2:sig=AQHQYkiIsCHWVuIs8ZRmMiU97FQ7Z7CU',
    'LIAP': 'true',
    'LANG': 'v=2&lang=en-us',
    'LI_THEME': 'light'
}

# =============================================================================
# 🛡️ FIXED SELENIUM - NO PORT CONFLICTS
# =============================================================================
_driver = None

@st.cache_resource(ttl=3600)  # Cache 1 hour, auto-refresh
def get_single_driver():
    """SINGLE driver instance - NO conflicts"""
    global _driver
    if _driver is not None:
        try:
            _driver.current_url
            return _driver
        except:
            pass
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # ✅ KEY FIXES for connection errors
    chrome_options.add_argument("--remote-debugging-port=0")  # Dynamic port
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install(), 
                     service_args=['--verbose', '--log-path=chromedriver.log'])
    
    _driver = webdriver.Chrome(service=service, options=chrome_options)
    _driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    _driver.set_page_load_timeout(30)
    return _driver

def safe_setup_cookies():
    """Safe cookie injection"""
    driver = get_single_driver()
    try:
        driver.get("https://www.linkedin.com")
        time.sleep(3)
        
        for name, value in COOKIES.items():
            try:
                driver.add_cookie({'name': name, 'value': value, 'domain': '.linkedin.com'})
            except:
                pass
        
        driver.refresh()
        time.sleep(5)
        return True
    except:
        return False

# =============================================================================
# 🔍 MAIN SCRAPER - STABLE
# =============================================================================


def scrape_linkedin_jobs(role, location="India", max_jobs=50):
    """Production scraper - INDIA-WIDE + EASY APPLY + ANTI-ASTERISK"""
    driver = get_single_driver()
    
    try:
        if not safe_setup_cookies():
            st.error("❌ Cookie setup failed")
            return pd.DataFrame()
        
        # INDIA-WIDE + Easy Apply filter
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={role.replace(' ', '%20')}&location=India&f_E=1"
        st.info(f"🔍 India-wide Easy Apply: {role}")
        
        driver.get(search_url)
        time.sleep(random.uniform(8, 12))
        
        # Human-like scrolling (beats anti-bot)
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 6))
        
        jobs = []
        attempts = 0
        while len(jobs) < max_jobs and attempts < 3:
            job_cards = driver.find_elements(
                By.CSS_SELECTOR,
                ".base-search-card, [data-test-job-card-primary-footer]"
            )
            
            st.info(f"📊 Found {len(job_cards)} cards (attempt {attempts+1})")
            
            for card in job_cards[:max_jobs - len(jobs)]:
                try:
                    # --- URL FIRST (beats asterisks) ---
                    link_elem = card.find_element(By.CSS_SELECTOR, "a")
                    link = link_elem.get_attribute("href")
                    
                    # --- COMPANY FROM URL ---
                    company = "N/A"
                    if "jobs/view/" in link and "at-" in link:
                        path = link.split("jobs/view/")[1].split("?")[0]
                        if "at-" in path:
                            company_part = path.split("at-")[1].split("-")[0]
                            company = company_part.title()
                    
                    # --- TITLE ---
                    title = "N/A"
                    if "jobs/view/" in link:
                        path = link.split("jobs/view/")[1].split("?")[0]
                        if "at-" in path:
                            title_part = path.split("at-")[0]
                            title = " ".join(word.capitalize() for word in title_part.split("-"))
                        else:
                            title = " ".join(word.capitalize() for word in path.split("-"))
                    
                    # --- LOCATION (fallback if masked) ---
                    location_text = "India"
                    try:
                        loc_elem = card.find_element(By.CSS_SELECTOR, 
                            "[data-test-job-card-location], .job-search-card__location")
                        loc_text = loc_elem.text.strip()
                        if "****" not in loc_text:
                            location_text = loc_text
                    except:
                        pass
                    
                    
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location_text,
                        "link": link,
                        "id": f"job_{len(jobs)+1}"
                    })
                    
                except:
                    continue
            
            attempts += 1
            time.sleep(random.uniform(4, 7))
        
        df = pd.DataFrame(jobs)
        df.fillna("N/A", inplace=True)
        return df
        
    except Exception as e:
        st.error(f"❌ Scrape error: {str(e)[:150]}")
        return pd.DataFrame()



# =============================================================================
# 🎨 UI
# =============================================================================
st.sidebar.header("🔍 Job Search")
role = st.sidebar.selectbox("Role", ["AI Engineer", "ML Engineer", "Data Scientist", "Python Developer"])
location = st.sidebar.text_input("Location", value="India")
max_jobs = st.sidebar.slider("Max Jobs", 5, 50, 20)

# Clear cache button
if st.sidebar.button("🔄 Reset Browser", type="secondary"):
    st.cache_resource.clear()
    st.success("✅ Browser reset! Click SCRAPE again.")
    st.rerun()

if st.sidebar.button("🚀 SCRAPE JOBS", type="primary"):
    if role.strip():
        with st.spinner("🔄 Authenticating & scraping..."):
            jobs_df = scrape_linkedin_jobs(role, location, max_jobs)
        
        if not jobs_df.empty:
            st.success(f"🎉 **{len(jobs_df)}** jobs scraped!")
            
            # Job cards
            for _, job in jobs_df.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{job['title']}**")
                with col2:
                    st.markdown(f"*{job['company']}*")
                    st.caption(job['location'])
                with col3:
                    st.markdown(f"[👉 Apply]({job['link']})")
                st.divider()
            
            # Table
            st.subheader("📋 Export Ready")
            st.dataframe(jobs_df)
            
            csv = jobs_df.to_csv(index=False)
            st.download_button(
                "💾 Download CSV", 
                csv,
                f"linkedin_jobs_{role.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            )
        else:
            st.warning("⚠️ No jobs found. Try: Reset Browser → Different keywords")

st.info("🔧 **Fixed**: Single driver + dynamic ports + auto-scroll")
st.caption("✅ Production ready | Reset browser anytime [memory:11]")