EMAIL_FORMAT = "^\\S+@\\S+\\.\\S+$"  # Simple email format checking


# --- Studies ---

# HACK: Hardcoded Question IDs (Prolific doesn't have a better way for now)
# [Depends on Prolific] Make this dynamic as soon as possible
ELIGIBILITY_REQUIREMENT_AGE_RANGE_QUESTION_ID = "54ac6ea9fdf99b2204feb893"

# https://docs.prolific.co/docs/api-docs/public/#tag/Studies/The-study-object
# `external_study_url` field
STUDY_URL_PARTICIPANT_ID_PARAM = "participant_id"
STUDY_URL_PARTICIPANT_ID_PARAM_PROLIFIC_VAR = "{{%PROLIFIC_PID%}}"
STUDY_URL_STUDY_ID_PARAM = "study_id"
STUDY_URL_STUDY_ID_PARAM_PROLIFIC_VAR = "{{%STUDY_ID%}}"
STUDY_URL_SUBMISSION_ID_PARAM = "submission_id"
STUDY_URL_SUBMISSION_ID_PARAM_PROLIFIC_VAR = "{{%SESSION_ID%}}"


class ProlificIDOption:
    NOT_REQUIRED = "not_required"
    QUESTION = "question"
    URL_PARAMETERS = "url_parameters"


class StudyAction:
    AUTOMATICALLY_APPROVE = "AUTOMATICALLY_APPROVE"
    MANUALLY_REVIEW = "MANUALLY_REVIEW"
    PUBLISH = "PUBLISH"
    START = "START"
    STOP = "STOP"
    UNPUBLISHED = "UNPUBLISHED"


class StudyStatus:
    """
    Study statuses explained
    https://docs.prolific.co/docs/api-docs/public/#tag/Studies/The-study-object
    """

    UNPUBLISHED = "UNPUBLISHED"
    ACTIVE = "ACTIVE"
    SCHEDULED = "SCHEDULED"
    PAUSED = "PAUSED"
    AWAITING_REVIEW = "AWAITING REVIEW"
    COMPLETED = "COMPLETED"
    # Pseudo status that we will use in `Study.internal_name` as a hack
    _EXPIRED = "EXPIRED"


class StudyCompletionOption:
    CODE = "code"
    URL = "url"


class StudyCodeType:
    COMPLETED = "COMPLETED"
    FAILED_ATTENTION_CHECK = "FAILED_ATTENTION_CHECK"
    FOLLOW_UP_STUDY = "FOLLOW_UP_STUDY"
    GIVE_BONUS = "GIVE_BONUS"
    INCOMPATIBLE_DEVICE = "INCOMPATIBLE_DEVICE"
    NO_CONSENT = "NO_CONSENT"
    OTHER = "OTHER"


# --- Submissions ---

# It must be at least 100 chars long
DEFAULT_REJECTION_CATEGORY_MESSAGE = (
    "This is default automatical rejection message "
    "as Prolific requires some text at least 100 chars long."
)


class SubmissionStatus:
    """
    Submission statuses explained
    https://researcher-help.prolific.co/hc/en-gb/articles/360009094114-Submission-statuses-explained
    """

    RESERVED = "RESERVED"
    ACTIVE = "ACTIVE"
    TIMED_OUT = "TIMED-OUT"
    AWAITING_REVIEW = "AWAITING REVIEW"
    APPROVED = "APPROVED"
    RETURNED = "RETURNED"
    REJECTED = "REJECTED"
    # After you approve or reject a submission, it may have the ‘Processing’ status
    # for a short time before showing as ‘Approved’ or ‘Rejected’.
    PROCESSING = "PROCESSING"


class SubmissionAction:
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class SubmissionRejectionCategory:
    BAD_CODE = "BAD_CODE"
    FAILED_CHECK = "FAILED_CHECK"
    FAILED_INSTRUCTIONS = "FAILED_INSTRUCTIONS"
    INCOMP_LONGITUDINAL = "INCOMP_LONGITUDINAL"
    LOW_EFFORT = "LOW_EFFORT"
    MALINGERING = "MALINGERING"
    NO_CODE = "NO_CODE"
    NO_DATA = "NO_DATA"
    OTHER = "OTHER"
    TOO_QUICKLY = "TOO_QUICKLY"
    TOO_SLOWLY = "TOO_SLOWLY"
    UNSUPP_DEVICE = "UNSUPP_DEVICE"


# --- Workspaces ---


class WorkspaceRole:
    WORKSPACE_ADMIN = "WORKSPACE_ADMIN"
    WORKSPACE_COLLABORATOR = "WORKSPACE_COLLABORATOR"
    PROJECT_EDITOR = "PROJECT_EDITOR"
