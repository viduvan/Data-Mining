import sys
sys.path.insert(0, 'admission-crawler/src')
from admission_crawler.storage.database import init_db, get_session
from admission_crawler.storage.models import CrawlRun, UniversityRaw, CutoffRaw, CutoffNormalized
from sqlalchemy import func

with get_session() as session:
    runs = session.query(CrawlRun).order_by(CrawlRun.crawl_run_id.desc()).limit(5).all()
    print('=== Recent Runs ===')
    for r in runs:
        print(f'  Run {r.crawl_run_id}: years={r.years}, status={r.status}, started={r.started_at}, finished={r.finished_at}')

    total_unis = session.query(func.count(UniversityRaw.university_raw_id)).scalar()
    total_raw = session.query(func.count(CutoffRaw.cutoff_raw_id)).scalar()
    total_norm = session.query(func.count(CutoffNormalized.cutoff_id)).scalar()
    print(f'\n=== Totals ===')
    print(f'  Universities raw: {total_unis}')
    print(f'  Cutoffs raw: {total_raw}')
    print(f'  Cutoffs normalized: {total_norm}')

    print('\n=== Raw cutoffs by year ===')
    by_year = session.query(CutoffRaw.year, func.count()).group_by(CutoffRaw.year).order_by(CutoffRaw.year).all()
    for y, c in by_year:
        print(f'  {y}: {c}')

    print('\n=== Normalized cutoffs by year ===')
    by_year_n = session.query(CutoffNormalized.year, func.count()).group_by(CutoffNormalized.year).order_by(CutoffNormalized.year).all()
    for y, c in by_year_n:
        print(f'  {y}: {c}')
