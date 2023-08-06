from django.dispatch import Signal

app_user_logged_in = Signal(providing_args=['request', 'user'])
app_user_login_failed = Signal(providing_args=['credentials'])
app_user_logged_out = Signal(providing_args=['request', 'user'])
