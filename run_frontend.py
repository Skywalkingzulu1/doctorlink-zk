import sys, os
sys.path.insert(0, r"C:\Users\Doctorsonwheels\zk\doctorlink-health-services")
os.chdir(r"C:\Users\Doctorsonwheels\zk\doctorlink-health-services")
os.environ["STELLAR_SECRET_KEY"] = "SCNUOMFLGHCNSDQLTS7J25OAOP7ME764XH23ZBXM4TXZRJT3SLQAADA6"
import uvicorn
from frontend import app
uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
