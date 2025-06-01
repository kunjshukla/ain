from .models import init_db, save_session, get_session
from .user_models import init_user_db, register_user, track_user_session, get_user_performance

# Initialize both databases when importing the package
init_db()
init_user_db()
