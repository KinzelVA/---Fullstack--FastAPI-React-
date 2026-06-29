from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=64,
        examples=["admin"],
    )
    password: str = Field(
        min_length=1,
        max_length=128,
        examples=["admin"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "admin",
            }
        }
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example.signature"
        ]
    )
    token_type: str = Field(default="bearer", examples=["bearer"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example.signature",
                "token_type": "bearer",
            }
        }
    )


class AdminUserResponse(BaseModel):
    id: int = Field(examples=[1])
    username: str = Field(examples=["admin"])
    is_admin: bool = Field(examples=[True])

    model_config = ConfigDict(from_attributes=True)
