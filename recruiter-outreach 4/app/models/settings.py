from sqlmodel import SQLModel, Field
from typing import Optional


class AppSettings(SQLModel, table=True):
    id:                 Optional[int] = Field(default=None, primary_key=True)
    sender_name:        str = Field(default="")
    sender_email:       str = Field(default="")
    sender_linkedin:    str = Field(default="")
    sender_role:        str = Field(default="")
    sender_experience:  str = Field(default="")
    gmail_app_password: str = Field(default="")
    gemini_api_key:     str = Field(default="")
    hunter_api_key:     str = Field(default="")
    email_context:      str = Field(default="")
    resume_path:        str = Field(default="")
    resume_filename:    str = Field(default="")


class AppSettingsUpdate(SQLModel):
    sender_name:        Optional[str] = None
    sender_email:       Optional[str] = None
    sender_linkedin:    Optional[str] = None
    sender_role:        Optional[str] = None
    sender_experience:  Optional[str] = None
    gmail_app_password: Optional[str] = None
    gemini_api_key:     Optional[str] = None
    hunter_api_key:     Optional[str] = None
    email_context:      Optional[str] = None


class AppSettingsRead(SQLModel):
    sender_name:        str
    sender_email:       str
    sender_linkedin:    str
    sender_role:        str
    sender_experience:  str
    email_context:      str
    gemini_api_key_set: bool
    hunter_api_key_set: bool
    gmail_configured:   bool
    resume_filename:    str

    class Config:
        from_attributes = True
