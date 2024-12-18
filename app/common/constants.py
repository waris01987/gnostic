TRAILING_SLASH = "/"

UNPROTECTED_ROUTE_PATHS = [
    r"/(docs|profile_pictures/.+)$",
    r"/(openapi.json|favicon.ico)$",
    r"/api/v1/(login|request-password-reset|reset-password|send-otp-reset-password|verify-otp-reset-password)$",
    r"/api/v1/registration/(individual|organisation)$",
    r"/api/v1/token/refresh/?$",
    r"/api/v1/oauth/callback/?$",
]

UNPROTECTED_MFA_ROUTE_PATHS = [
    *UNPROTECTED_ROUTE_PATHS,
]
