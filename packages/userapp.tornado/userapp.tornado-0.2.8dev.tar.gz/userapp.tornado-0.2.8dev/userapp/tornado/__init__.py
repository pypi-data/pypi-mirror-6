import userapp

class Context(object):
    def __init__(self, app_id=None, cookie_name=None):
        self.app_id=app_id
        self.cookie_name=cookie_name

def config(app_id, cookie_name='ua_session_token'):
    """
    Configuration decorator.
    """
    def func(f):
        def wrapper(*args):
            request = args[1]

            request.userapp = Context(app_id, cookie_name)

            return f(*args)
        return wrapper
    return func

def authorized():
    """
    Check whether a user is authorized.
    """
    def func(f):
        def wrapper(*args):
            result = None
            self = args[0]
            context = self.request.userapp

            #if target_app_id == None and hasattr(self.request, 'userapp'):
            #    target_app_id=self.request.userapp.app_id

            try:
                if context.cookie_name in self.cookies:
                    # A good idea would be to add caching here so we don't need to hit the UserApp API every time
                    api = userapp.API(app_id=context.app_id, token=self.get_cookie(context.cookie_name))
                    self.user_id = api.user.get(fields=['user_id'])[0].user_id
                else:
                    result = {'error_code':'USER_NOT_AUTHORIZED', 'message':'User not authorized. Please log in.'}
            except userapp.UserAppServiceException as e:
                result = {'error_code':e.error_code, 'message':e.message}

            if not result is None:
                self.finish(result)
                return None

            return f(*args)
        return wrapper
    return func

def has_permission(permission):
    """
    Check whether a user is authenticated and has certain permissions.
    """
    def func(f):
        def wrapper(*args):
            target_app_id=app_id
            self = args[0]

            if target_app_id == None and hasattr(self.request, 'userapp'):
                target_app_id=self.request.userapp.app_id

            try:
                if cookie_name in self.cookies:
                    # A good idea would be to add caching here so we don't need to hit the UserApp API every time
                    api = userapp.API(app_id=target_app_id, token=self.get_cookie(cookie_name))
                    permission_result = api.user.hasPermission(user_id='self', permissions=permissions)

                    if len(permission_result.missing_permissions) > 0:
                        self.finish({'error_code':'USER_NOT_AUTHORIZED', 'message':'User is not authorized to do this action.'})
            except userapp.UserAppServiceException as e:
                self.finish({'error_code':e.error_code, 'message':e.message})
                return None

            return f(*args)
        return wrapper
    return func