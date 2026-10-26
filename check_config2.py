from app.db import SessionLocal
from app import site_config, models

db = SessionLocal()
try:
    print('maintenance:', site_config.maintenance_mode(db=db))
    ps = db.query(getattr(models, 'PlatformSetting')).first()
    if ps:
        print('ps:', getattr(ps,'maintenance_mode',None), getattr(ps,'allow_registration',None))
    else:
        print('no ps')
finally:
    db.close()
