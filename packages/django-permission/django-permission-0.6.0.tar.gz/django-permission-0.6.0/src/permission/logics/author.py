# coding=utf-8
"""
Permission logic module for author based permission system
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
from permission.conf import settings
from permission.logics.base import PermissionLogic


class AuthorPermissionLogic(PermissionLogic):
    """
    Permission logic class for author based permission system
    """
    def __init__(self,
                 field_name=None,
                 any_permission=None,
                 change_permission=None,
                 delete_permission=None):
        """
        Constructor

        Parameters
        ----------
        field_name : string
            A field name of object which store the author as django user model.
            Default value will be taken from
            ``PERMISSION_DEFAULT_APL_FIELD_NAME`` in
            settings.
        any_permission : boolean
            True for give any permission of the specified object to the author
            Default value will be taken from
            ``PERMISSION_DEFAULT_APL_ANY_PERMISSION`` in
            settings.
        change_permission : boolean
            True for give change permission of the specified object to the
            author.
            It will be ignored if :attr:`any_permission` is True.
            Default value will be taken from
            ``PERMISSION_DEFAULT_APL_CHANGE_PERMISSION`` in
            settings.
        delete_permission : boolean
            True for give delete permission of the specified object to the
            author.
            It will be ignored if :attr:`any_permission` is True.
            Default value will be taken from
            ``PERMISSION_DEFAULT_APL_DELETE_PERMISSION`` in
            settings.
        """
        self.field_name = field_name
        self.any_permission = any_permission
        self.change_permission = change_permission
        self.delete_permission = delete_permission

        if self.field_name is None:
            self.field_name = \
                settings.PERMISSION_DEFAULT_APL_FIELD_NAME
        if self.any_permission is None:
            self.any_permission = \
                settings.PERMISSION_DEFAULT_APL_ANY_PERMISSION
        if self.change_permission is None:
            self.change_permission = \
                settings.PERMISSION_DEFAULT_APL_CHANGE_PERMISSION
        if self.delete_permission is None:
            self.delete_permission = \
                settings.PERMISSION_DEFAULT_APL_DELETE_PERMISSION


    def has_perm(self, user_obj, perm, obj=None):
        """
        Check if user have permission (of object)

        If no object is specified, it always return ``False`` so you need to
        add *add* permission to users in normal way.

        If an object is specified, it will return ``True`` if the user is
        specified in ``field_name`` of the object (e.g. ``obj.author``).
        So once user create an object and the object store who is the author in
        ``field_name`` attribute (default: ``author``), the author can change or
        delete the object (you can change this behavior to set
        ``any_permission``, ``change_permissino`` or ``delete_permission``
        attributes of this instance).

        Parameters
        ----------
        user_obj : django user model instance
            A django user model instance which be checked
        perm : string
            `app_label.codename` formatted permission string
        obj : None or django model instance
            None or django model instance for object permission

        Returns
        -------
        boolean
            Wheter the specified user have specified permission (of specified
            object).
        """
        if obj is None:
            return False
        elif user_obj.is_active:
            # construct the permission full name
            app_label = obj._meta.app_label
            model_name = obj._meta.object_name.lower()
            change_permission = "%s.change_%s" % (app_label, model_name)
            delete_permission = "%s.delete_%s" % (app_label, model_name)
            # get author instance
            author = getattr(obj, self.field_name, None)
            if author and author == user_obj:
                if self.any_permission:
                    # have any kind of permissions to the obj
                    return True
                if (self.change_permission and 
                    perm == change_permission):
                    return True
                if (self.delete_permission and 
                    perm == delete_permission):
                    return True
        return False
