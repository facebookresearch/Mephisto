EMAIL_FORMAT = '^\\S+@\\S+\\.\\S+$'  # Simple email format checking


class ProlificIDOption:
    NOT_REQUIRED = 'not_required'
    QUESTION = 'question'
    URL_PARAMETERS = 'url_parameters'


class StudyAction:
    AUTOMATICALLY_APPROVE = 'AUTOMATICALLY_APPROVE'
    MANUALLY_REVIEW = 'MANUALLY_REVIEW'


class StudyCompletionOption:
    CODE = 'code'
    URL = 'url'


class StudyCodeType:
    COMPLETED = 'COMPLETED'
    FAILED_ATTENTION_CHECK = 'FAILED_ATTENTION_CHECK'
    FOLLOW_UP_STUDY = 'FOLLOW_UP_STUDY'
    GIVE_BONUS = 'GIVE_BONUS'
    INCOMPATIBLE_DEVICE = 'INCOMPATIBLE_DEVICE'
    NO_CONSENT = 'NO_CONSENT'
    OTHER = 'OTHER'
