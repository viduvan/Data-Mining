#!/usr/bin/env python3
"""
cli.py — Main CLI entrypoint for the crawler.
"""

import argparse
import sys
import logging
from datetime import datetime

from admission_crawler.config import settings
from admission_crawler.storage.database import init_db, get_session
from admission_crawler.storage.repositories import CrawlRepository
from admission_crawler.http.client import CrawlerClient
from admission_crawler.pipeline.discover_pipeline import run_discovery
from admission_crawler.pipeline.crawl_pipeline import run_university_crawl
from admission_crawler.pipeline.normalize_pipeline import run_normalization
from admission_crawler.pipeline.export_pipeline import export_data
from admission_crawler.reporting.run_report import generate_run_summary

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("admission_crawler")

def parse_args():
    parser = argparse.ArgumentParser(description="VietNamNet Admission Crawler (Hanoi)")
    parser.add_argument("--years", type=str, default="2025", help="Comma separated list of years, e.g. 2024,2025")
    parser.add_argument("--action", type=str, choices=["crawl", "normalize", "export", "all"], default="all")
    return parser.parse_args()

def main():
    args = parse_args()
    years = [int(y.strip()) for y in args.years.split(',')]
    
    # Init DB
    init_db()
    
    with get_session() as session:
        repo = CrawlRepository(session)
        
        # Start Run
        run = repo.start_run({"years": years, "action": args.action, "environment": "default"})
        logger.info(f"Khởi động run_id={run.crawl_run_id}")
        
        try:
            if args.action in ["crawl", "all"]:
                client = CrawlerClient(session)
                try:
                    for year in years:
                        logger.info(f"==== BẮT ĐẦU CRAWL NĂM {year} ====")
                        # 1. Discovery
                        hanoi_unis = run_discovery(year, client, repo, run.crawl_run_id)
                        if not hanoi_unis:
                            raise RuntimeError(f"Discovery returned no Hanoi universities for {year}")                        
                        # 2. Detail Crawl
                        # Universities are deduplicated globally, so a resumed run can reuse prior discovery rows.
                        from admission_crawler.storage.models import UniversityRaw
                        unis_in_db = session.query(UniversityRaw).filter(
                            UniversityRaw.year == year
                        ).all()

                        detail_universities = [u for u in unis_in_db if u.detail_url]
                        total_universities = len(detail_universities)
                        for index, university in enumerate(detail_universities, start=1):
                            label = university.university_code_raw or university.university_name_raw
                            logger.info(
                                "[Detail %d/%d] %s — bắt đầu",
                                index,
                                total_universities,
                                label,
                            )
                            records_saved = run_university_crawl(
                                university.university_raw_id,
                                university.detail_url,
                                year,
                                client,
                                repo,
                                run.crawl_run_id,
                            )
                            logger.info(
                                "[Detail %d/%d] %s — xong, %d bản ghi",
                                index,
                                total_universities,
                                label,
                                records_saved,
                            )
                finally:
                    client.close()
                    
            if args.action in ["normalize", "all"]:
                logger.info("==== BẮT ĐẦU CHUẨN HÓA ====")
                run_normalization(session, repo, run.crawl_run_id)
                
            if args.action in ["export", "all"]:
                logger.info("==== BẮT ĐẦU XUẤT DỮ LIỆU ====")
                export_data(session, format_type="csv")
                export_data(session, format_type="json")
                
            repo.finish_run(run.crawl_run_id, "success")
            
        except Exception as e:
            logger.exception("Lỗi hệ thống nghiêm trọng!")
            repo.finish_run(run.crawl_run_id, "failed", errors_count=1)
            sys.exit(1)
            
        summary = generate_run_summary(repo, run.crawl_run_id)
        print("Run Summary:", summary)

if __name__ == "__main__":
    main()
