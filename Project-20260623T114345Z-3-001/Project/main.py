# main.py
import logging
import time
import concurrent.futures

# 1. Import modules from the crawlers directory (SP1)
from crawlers.vnexpress import VnExpressCrawler
from crawlers.bbc import BBCCrawler

# 2. Import modules from the pipeline directory (SP2 & SP3)
from pipeline.text_processor import clean_articles_pipeline
from pipeline.database import initialize_database, save_articles_to_db, export_database_to_files

# 3. Import AI Module (SP4)
from ai_module.sentiment import apply_sentiment_analysis

# 4. Import Analytics & Dashboard Module (SP5)
from analytics_module.dashboard import generate_analytics_dashboard

# 5. Import Reporting Module (SP6 - NEWLY ADDED)
from reporting_module.daily_report import generate_daily_report

# Configure logging to monitor the entire system
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

def run_parallel_crawlers():
    """
    Multi-threading coordinator function for SP1.
    Executes multiple web crawlers concurrently to optimize I/O wait times.
    """
    crawlers = [VnExpressCrawler(), BBCCrawler()]
    all_articles = []

    logging.info("--- STEP 1: INITIALIZE MULTI-THREADED CRAWLERS (SP1) ---")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(crawlers)) as executor:
        future_to_crawler = {executor.submit(crawler.crawl_articles): crawler for crawler in crawlers}

        for future in concurrent.futures.as_completed(future_to_crawler):
            crawler = future_to_crawler[future]
            try:
                data = future.result()
                all_articles.extend(data)
            except Exception as exc:
                logging.error(f"Crawler {crawler.source_name} encountered a critical error: {exc}")
                
    return all_articles

def main():
    start_time = time.time()
    logging.info("========== STARTING NEWS AGGREGATOR SYSTEM ==========")
    
    # STEP A: Initialize Database Schema (SP3)
    initialize_database()
    
    # STEP B: Run the multi-threaded data collection system (SP1)
    raw_data = run_parallel_crawlers()
    
    if not raw_data:
        logging.warning("No data collected. System halting.")
        return

    # STEP C: Pass raw data to the text cleaning pipeline (SP2)
    cleaned_data = clean_articles_pipeline(raw_data)
    
    # STEP C2 (SP4): Apply AI for Multilingual Sentiment Analysis
    analyzed_data = apply_sentiment_analysis(cleaned_data)
    
    # STEP D: Save sentiment-analyzed data to the SQLite Database (SP3)
    save_articles_to_db(analyzed_data)
    
    # STEP E: Export JSON/CSV backup files for downstream tasks (SP3)
    export_database_to_files()
    
    # STEP F (SP5): Analyze data using Pandas and generate Dashboard via Matplotlib
    generate_analytics_dashboard()
    
    # STEP G (NEW - SP6): Generate daily report & Auto-draft Technical Report
    generate_daily_report()
    
    end_time = time.time()
    logging.info(f"========== SYSTEM COMPLETED ENTIRE SESSION IN {end_time - start_time:.2f} SECONDS ==========")

if __name__ == "__main__":
    main()