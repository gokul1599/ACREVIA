"""
KisanVision - Expert Review Workflow Manager.
Applies double-blind consensus rules to validate candidate samples into ground truth.
"""

from typing import Optional, List
from ml.datasets.annotations.annotation_schema import (
    ComprehensiveAnnotation,
    ExpertReviewRecord,
    ReviewAction,
    DiagnosticCertainty,
    LabelRevisionEntry
)


class ExpertReviewManager:
    """Manages the evaluation gate from source label to approved training label."""
    
    @staticmethod
    def initialize_annotation(
        sample_id: str,
        crop: str,
        source_label: str,
        farmer_observation: Optional[str] = None
    ) -> ComprehensiveAnnotation:
        annotation = ComprehensiveAnnotation(
            sample_id=sample_id,
            crop=crop,
            source_dataset_label=source_label,
            farmer_reported_observation=farmer_observation,
            final_approved_training_label=None,
            is_approved_for_training=False
        )
        annotation.revision_history.append(
            LabelRevisionEntry(
                previous_label=None,
                new_label=source_label,
                changed_by_role="SOURCE_IMPORT",
                reason="Initial ingestion from raw source manifest."
            )
        )
        return annotation

    @staticmethod
    def submit_review(
        annotation: ComprehensiveAnnotation,
        review: ExpertReviewRecord
    ) -> ComprehensiveAnnotation:
        annotation.reviews.append(review)
        
        # If expert confirmed or overrode with certainty, update candidate ground truth
        if review.action_taken in (ReviewAction.CONFIRMED, ReviewAction.OVERRIDDEN):
            if review.certainty in (DiagnosticCertainty.CERTAIN, DiagnosticCertainty.PROBABLE):
                old_label = annotation.final_approved_training_label
                annotation.expert_confirmed_label = review.confirmed_class
                annotation.final_approved_training_label = review.confirmed_class
                annotation.is_approved_for_training = True
                
                annotation.revision_history.append(
                    LabelRevisionEntry(
                        previous_label=old_label,
                        new_label=review.confirmed_class,
                        changed_by_role="EXPERT_REVIEWER",
                        reason=f"Action: {review.action_taken.value}. Notes: {review.evidence_notes}"
                    )
                )
        elif review.action_taken in (ReviewAction.INSUFFICIENT_EVIDENCE, ReviewAction.REJECTED_QUALITY):
            annotation.is_approved_for_training = False
            annotation.revision_history.append(
                LabelRevisionEntry(
                    previous_label=annotation.final_approved_training_label,
                    new_label="QUARANTINED_UNCONFIRMED",
                    changed_by_role="EXPERT_REVIEWER",
                    reason=f"Rejected: {review.action_taken.value}. Notes: {review.evidence_notes}"
                )
            )
            
        return annotation
