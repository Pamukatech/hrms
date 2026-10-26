from app.db import SessionLocal
from app import models

db = SessionLocal()
try:
    companies = db.query(models.Company).all()
    for c in companies:
        print(f'COMPANY {c.id}: {c.name} active={c.is_active}')
        sub = getattr(c, 'subscription', None)
        if sub:
            print(f'  SUB: plan={sub.plan} status={sub.status} trial_ends={sub.trial_ends_at} period_ends={sub.period_ends_at}')
        else:
            print('  SUB: none')
    print('---')
    users = db.query(models.User).all()
    for u in users:
        print(f'USER {u.id}: {u.email} company_id={u.company_id} role={u.role} platform_admin={u.is_platform_admin}')
finally:
    db.close()
