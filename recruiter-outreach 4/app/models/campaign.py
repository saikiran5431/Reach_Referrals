"""
app/models/campaign.py — WHY IT EXISTS
========================================
A Campaign is a batch send operation — "send emails to all ready recruiters."
Tracking it lets you see: how many were attempted, succeeded, failed, and when.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Campaign(SQLModel, table=True):
    id:          Optional[int] = Field(default=None, primary_key=True)
    name:        str           = Field(description="Human-readable label, e.g. 'Batch 1 - June 2025'")
    
    total:       int = Field(default=0, description="How many recruiters targeted")
    sent:        int = Field(default=0, description="How many emails delivered")
    failed:      int = Field(default=0, description="How many failed to send")
    
    status:      str = Field(default="pending", description="pending | running | completed | partial")
    
    created_at:  datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)


class CampaignRead(SQLModel):
    id:           int
    name:         str
    total:        int
    sent:         int
    failed:       int
    status:       str
    created_at:   datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
