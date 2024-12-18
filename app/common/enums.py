from enum import Enum


class UserType(Enum):
    SUPER_ADMIN = 1
    INDIVIDUAL_USER = 2
    ORGANISATION = 3


user_type_choices = [
    (UserType.SUPER_ADMIN.value, "Super Admin"),
    (UserType.INDIVIDUAL_USER.value, "Individual User"),
    (UserType.ORGANISATION.value, "Organisation"),
]


class Gender(Enum):
    MALE = 1
    FEMALE = 2
    NON_BINARY = 3
    OTHERS = 4


gender_choices = [
    (Gender.MALE.value, "Male"),
    (Gender.FEMALE.value, "Female"),
    (Gender.NON_BINARY.value, "Non Binary"),
    (Gender.OTHERS.value, "Others"),
]


class OAuthProvider(Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    YAHOO = "yahoo"
    APPLE = "apple"
    ZOHO = "zoho"


oauth_provider_choices = [
    (OAuthProvider.GOOGLE.value, "Google"),
    (OAuthProvider.FACEBOOK.value, "Facebook"),
    (OAuthProvider.INSTAGRAM.value, "Instagram"),
    (OAuthProvider.LINKEDIN.value, "LinkedIn"),
    (OAuthProvider.TWITTER.value, "Twitter"),
    (OAuthProvider.YAHOO.value, "Yahoo"),
    (OAuthProvider.APPLE.value, "Apple"),
    (OAuthProvider.ZOHO.value, "Zoho"),
]
