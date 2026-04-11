import sys
import os
from openenv.core.env_server import create_fastapi_app
from .customer_support_environment import CustomerSupportEnv

# Ensure server can find models.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import SupportAction, SupportObservation

app = create_fastapi_app(CustomerSupportEnv, SupportAction, SupportObservation)