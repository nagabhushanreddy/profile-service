"""Tests for enrichment service with maker-checker."""

import pytest
from app.services.enrichment_service import enrichment_service


@pytest.mark.asyncio
async def test_create_enrichment_success(sample_profile):
    """Test create enrichment (Maker) successfully."""
    enrichment_data = {
        "risk_score": 75.5,
        "risk_grade": "medium",
        "credit_grade": "B",
        "background_check_result": "clear",
        "verification_notes": "All checks passed"
    }
    
    result = await enrichment_service.create_enrichment(
        profile_id=sample_profile["id"],
        enrichment_data=enrichment_data,
        maker_id="maker-123",
        correlation_id="test-corr-id"
    )
    
    assert result["risk_score"] == 75.5
    assert result["risk_grade"] == "medium"
    assert result["status"] == "pending_review"
    assert result["maker_id"] == "maker-123"


@pytest.mark.asyncio
async def test_review_enrichment_approve(sample_profile):
    """Test review enrichment with approval."""
    # Create enrichment first
    enrichment_data = {
        "risk_score": 75.5,
        "risk_grade": "medium",
        "credit_grade": "B",
        "background_check_result": "clear"
    }
    
    enrichment = await enrichment_service.create_enrichment(
        profile_id=sample_profile["id"],
        enrichment_data=enrichment_data,
        maker_id="maker-123"
    )
    
    # Review (approve)
    result = await enrichment_service.review_enrichment(
        enrichment_id=enrichment["id"],
        decision="approve",
        checker_id="checker-456",
        checker_notes="Approved"
    )
    
    assert result["status"] == "approved"
    assert result["checker_id"] == "checker-456"
    assert result["checker_decision"] == "approve"


@pytest.mark.asyncio
async def test_review_enrichment_same_maker_checker(sample_profile):
    """Test review enrichment with same maker and checker (should fail)."""
    # Create enrichment
    enrichment_data = {
        "risk_score": 75.5,
        "risk_grade": "medium",
        "credit_grade": "B",
        "background_check_result": "clear"
    }
    
    enrichment = await enrichment_service.create_enrichment(
        profile_id=sample_profile["id"],
        enrichment_data=enrichment_data,
        maker_id="maker-123"
    )
    
    # Try to review with same user (should fail)
    with pytest.raises(ValueError, match="Checker cannot be the same as maker"):
        await enrichment_service.review_enrichment(
            enrichment_id=enrichment["id"],
            decision="approve",
            checker_id="maker-123",  # Same as maker
            checker_notes="Approved"
        )


@pytest.mark.asyncio
async def test_review_enrichment_reject(sample_profile):
    """Test review enrichment with rejection."""
    # Create enrichment
    enrichment_data = {
        "risk_score": 95.0,
        "risk_grade": "very_high",
        "credit_grade": "E",
        "background_check_result": "flag"
    }
    
    enrichment = await enrichment_service.create_enrichment(
        profile_id=sample_profile["id"],
        enrichment_data=enrichment_data,
        maker_id="maker-123"
    )
    
    # Review (reject)
    result = await enrichment_service.review_enrichment(
        enrichment_id=enrichment["id"],
        decision="reject",
        checker_id="checker-456",
        checker_notes="Need more information"
    )
    
    assert result["status"] == "rejected"
    assert result["checker_decision"] == "reject"
