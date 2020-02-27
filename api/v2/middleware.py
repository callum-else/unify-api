class CustomSessionManager:
    """
    Custom Middleware for creating and closing a session per database request.
    Inspired by: https://eshlox.net/2019/05/28/integrate-sqlalchemy-with-falcon-framework-second-version
    """

    # Setup
    def __init__(self, Session):
        self.db_session = Session

    # Runs on pre-request for session generation.
    def process_resource(self, req, resp, resource, params):
        req.context['db_session'] = self.db_session()
        print('Session Created.')

    # Runs on post-request for session closure / rollback.
    def process_response(self, req, resp, resource, req_succeeded):
        if req.context.get('db_session'):
            if not req_succeeded:
                req.context['db_session'].rollback()
                print('Session Rolled Back.')
            req.context['db_session'].close()
            print('Session Closed.')