from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RejectWhitespaceOnlyMixin(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def reject_whitespace_only(cls, value):
        if isinstance(value, str) and value.strip() == "":
            raise ValueError("Field cannot be empty or whitespace only")
        return value


class BusinessDetails(RejectWhitespaceOnlyMixin):
    business_name: str = Field(..., min_length=2, max_length=120)
    industry: str = Field(..., min_length=2, max_length=120)
    location: str = Field(..., min_length=2, max_length=160)
    years_in_business: float = Field(..., ge=0, le=200)
    team_size: int = Field(..., ge=1, le=100000)
    business_stage: Literal["idea", "startup", "growing", "established", "declining"]
    business_description: str = Field(..., min_length=5, max_length=3000)


class Products(RejectWhitespaceOnlyMixin):
    primary_products: list[str] = Field(..., min_length=1, max_length=20)
    average_price: float = Field(..., ge=0)
    best_sellers: list[str] = Field(default_factory=list, max_length=10)
    profit_margin_percent: float | None = Field(default=None, ge=0, le=100)


class Customers(RejectWhitespaceOnlyMixin):
    target_customer: str = Field(..., min_length=5, max_length=1000)
    customer_age_range: str | None = Field(default=None, max_length=80)
    customer_location: str | None = Field(default=None, max_length=160)
    repeat_customer_percent: float | None = Field(default=None, ge=0, le=100)
    customer_pain_points: list[str] = Field(default_factory=list, max_length=15)


class Sales(BaseModel):
    monthly_revenue: float = Field(..., ge=0)
    monthly_orders: int = Field(..., ge=0)
    sales_channels: list[str] = Field(..., min_length=1, max_length=15)
    conversion_rate_percent: float | None = Field(default=None, ge=0, le=100)
    average_order_value: float | None = Field(default=None, ge=0)


class Marketing(BaseModel):
    current_channels: list[str] = Field(default_factory=list, max_length=15)
    monthly_marketing_budget: float = Field(..., ge=0)
    social_media_presence: str | None = Field(default=None, max_length=1000)
    campaigns_that_worked: list[str] = Field(default_factory=list, max_length=10)
    email_list_size: int | None = Field(default=None, ge=0)


class Competition(BaseModel):
    main_competitors: list[str] = Field(default_factory=list, max_length=15)
    competitive_advantage: str = Field(..., min_length=5, max_length=1500)
    price_positioning: Literal["budget", "mid-market", "premium", "luxury", "unknown"]
    market_saturation: Literal["low", "medium", "high", "unknown"]


class Problems(RejectWhitespaceOnlyMixin):
    biggest_challenges: list[str] = Field(..., min_length=1, max_length=15)
    operational_bottlenecks: list[str] = Field(default_factory=list, max_length=15)
    cash_flow_status: Literal["healthy", "tight", "critical", "unknown"]
    urgent_problem: str | None = Field(default=None, max_length=1500)


class GrowthGoals(RejectWhitespaceOnlyMixin):
    primary_goal: str = Field(..., min_length=5, max_length=1000)
    revenue_goal: float | None = Field(default=None, ge=0)
    timeline_months: int = Field(..., ge=1, le=120)
    hiring_goals: str | None = Field(default=None, max_length=1000)
    expansion_plans: str | None = Field(default=None, max_length=1500)


class BusinessInput(BaseModel):
    business_details: BusinessDetails
    products: Products
    customers: Customers
    sales: Sales
    marketing: Marketing
    competition: Competition
    problems: Problems
    growth_goals: GrowthGoals

    @field_validator("*", mode="before")
    @classmethod
    def reject_empty_sections(cls, value):
        if value in ({}, None):
            raise ValueError("All input sections are required")
        return value
