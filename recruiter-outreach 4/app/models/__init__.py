# Makes app/models/ a Python package
from app.models.recruiter import Recruiter, RecruiterCreate, RecruiterRead, RecruiterStatus
from app.models.campaign import Campaign, CampaignRead
from app.models.settings import AppSettings, AppSettingsUpdate, AppSettingsRead
