import sys
import os
from openenv.core.env_server import create_fastapi_app
from .customer_support_environment import CustomerSupportEnv

# This ensures the server can find your models.py file in the parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import SupportAction, SupportObservation

# We now pass the required Action and Observation classes to satisfy the actual API
app = create_fastapi_app(CustomerSupportEnv, SupportAction, SupportObservation)