from app.db import SessionLocal
from app import site_config, models

db = SessionLocal()
try:
    print('maintenance:', site_config.maintenance_mode(db=db))
    ps = db.query(models.PlatformSettings).first()
    if ps:
        print('ps:', ps.maintenance_mode, ps.allow_registration)
    else:
        print('no ps')
finally:
    db.close()
