__all__ = ('SATISFY_ANY', 'SATISFY_ALL', 'DEFAULT_SATISFY', 'permissions_required', 'all_permissions_required', \
           'any_permission_required', 'edit_dashboard_permission_required')

SATISFY_ANY = 'any'
SATISFY_ALL = 'all'
DEFAULT_SATISFY = SATISFY_ALL

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def permissions_required(perms, satisfy=DEFAULT_SATISFY, login_url=None, raise_exception=False):
    """
    Checks for the permissions given based on the strategy chosen.

    :param iterable perms:
    :param string satisfy: Allowed values are "all" and "any".
    :param string login_url:
    :param bool raise_exception: If set to True, the ``PermissionDenied`` exception is raised on failures.
    :return bool:

    :example:
    >>> @login_required
    >>> @permissions_required(satisfy='any', perms=[
    >>>     'dash.add_dashboardentry', 'dash.change_dashboardentry', 'dash.delete_dashboardentry',
    >>>     'dash.add_dashboardworkspace', 'dash.change_dashboardworkspace', 'dash.delete_dashboardworkspace',
    >>>     'dash.add_dashboardsettings', 'dash.change_dashboardsettings', 'dash.delete_dashboardsettings',
    >>> ])
    >>> def edit_dashboard(request):
    >>>     # your code
    """
    assert satisfy in (SATISFY_ANY, SATISFY_ALL)

    if SATISFY_ALL == satisfy:
        # ``SATISFY_ALL`` case
        def check_perms(user):
            # First check if the user has the permission (even anon users)
            if user.has_perms(perms):
                return True
            # In case the 403 handler should be called raise the exception
            if raise_exception:
                raise PermissionDenied
            # As the last resort, show the login form
            return False
    else:
        # ``SATISFY_ANY`` case
        def check_perms(user):
            # First check if the user has the permission (even anon users)
            for perm in perms:
                if user.has_perm(perm):
                    return True

            # In case the 403 handler should be called raise the exception
            if raise_exception:
                raise PermissionDenied
            # As the last resort, show the login form
            return False

    return user_passes_test(check_perms, login_url=login_url)

def all_permissions_required(perms, login_url=None, raise_exception=False):
    """
    :example:
    >>> @login_required
    >>> @all_permissions_required([
    >>>     'dash.add_dashboardentry', 'dash.change_dashboardentry', 'dash.delete_dashboardentry',
    >>>     'dash.add_dashboardworkspace', 'dash.change_dashboardworkspace', 'dash.delete_dashboardworkspace',
    >>>     'dash.add_dashboardsettings', 'dash.change_dashboardsettings', 'dash.delete_dashboardsettings',
    >>> ])
    >>> def edit_dashboard(request):
    >>>     # your code
    """
    return permissions_required(perms, satisfy=SATISFY_ALL, login_url=login_url, raise_exception=raise_exception)

def any_permission_required(perms, login_url=None, raise_exception=False):
    """
    :example:
    >>> @login_required
    >>> @any_permission_required([
    >>>     'dash.add_dashboardentry', 'dash.change_dashboardentry', 'dash.delete_dashboardentry',
    >>>     'dash.add_dashboardworkspace', 'dash.change_dashboardworkspace', 'dash.delete_dashboardworkspace',
    >>>     'dash.add_dashboardsettings', 'dash.change_dashboardsettings', 'dash.delete_dashboardsettings',
    >>> ])
    >>> def edit_dashboard(request):
    >>>     # your code
    """
    return permissions_required(perms, satisfy=SATISFY_ANY, login_url=login_url, raise_exception=raise_exception)

def edit_dashboard_permission_required(login_url=None, raise_exception=False):
    """
    Checks if user has permissions to edit dashboard. Simply, check is successfull if any of the following
    permission checks are satisfied:
    
        - Can add dashboard entry
        - Can change dashboard entry
        - Can delete dashboard entry
        - Can add dashboard workspace
        - Can change dashboard workspace
        - Can delete dashboard workspace
        - Can add dashboard settings
        - Can change dashboard settings
        - Can delete dashboard settings

    :example:
    >>> @login_required
    >>> @edit_dashboard_permission_required() # Do not forget the brackets!
    >>> def edit_dashboard(request):
    >>>     # your code
    """
    return permissions_required(
        perms = [
            'dash.add_dashboardentry', 'dash.change_dashboardentry', 'dash.delete_dashboardentry',
            'dash.add_dashboardworkspace', 'dash.change_dashboardworkspace', 'dash.delete_dashboardworkspace',
            'dash.add_dashboardsettings', 'dash.change_dashboardsettings', 'dash.delete_dashboardsettings',
        ],
        satisfy = SATISFY_ANY,
        login_url = login_url,
        raise_exception = raise_exception
        )
