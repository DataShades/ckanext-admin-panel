from __future__ import annotations

from typing import Any

import sqlalchemy as sa

import ckan.lib.dictization.model_dictize as model_dictize
import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.types import ActionResult, Context, DataDict, Query


@tk.side_effect_free
def user_list(context: Context, data_dict: DataDict) -> ActionResult.UserList:
    """Return a list of the site's user accounts.

    :param q: filter the users returned to those whose names contain a string
      (optional)
    :type q: string
    :param email: filter the users returned to those whose email match a
      string (optional) (you must be a sysadmin to use this filter)
    :type email: string
    :param order_by: which field to sort the list by (optional, default:
      ``'display_name'``). Users can be sorted by ``'id'``, ``'name'``,
      ``'fullname'``, ``'display_name'``, ``'created'``, ``'about'``,
      ``'sysadmin'`` or ``'number_created_packages'``.
    :type order_by: string
    :param all_fields: return full user dictionaries instead of just names.
      (optional, default: ``True``)
    :type all_fields: bool
    :param include_site_user: add site_user to the result
      (optional, default: ``False``)
    :type include_site_user: bool

    :rtype: list of user dictionaries. User properties include:
      ``number_created_packages`` which excludes datasets which are private
      or draft state.

    """
    tk.check_access("user_list", context, data_dict)

    q = data_dict.get("q", "")
    email = data_dict.get("email")
    order_by = data_dict.get("order_by", "display_name")
    all_fields = tk.asbool(data_dict.get("all_fields", True))

    if all_fields:
        query: "Query[Any]" = model.Session.query(
            model.User,
            # type_ignore_reason: incomplete SQLAlchemy types
            model.User.name.label("name"),  # type: ignore
            model.User.fullname.label("fullname"),  # type: ignore
            model.User.about.label("about"),  # type: ignore
            model.User.email.label("email"),  # type: ignore
            model.User.created.label("created"),  # type: ignore
            sa.select(
                [sa.func.count(model.Package.id)],
                sa.and_(
                    model.Package.creator_user_id == model.User.id,
                    model.Package.state == "active",
                    model.Package.private is False,
                ),
            ).label("number_created_packages"),
        )
    else:
        query = model.Session.query(model.User.name)

    if not tk.asbool(data_dict.get("include_site_user", False)):
        site_id = tk.config.get("ckan.site_id")
        query = query.filter(model.User.name != site_id)

    if q:
        query = model.User.search(q, query, user_name=context.get("user"))
    if email:
        query = query.filter_by(email=email)

    order_by_field = None
    if order_by == "edits":
        raise tk.ValidationError({"message": "order_by=edits is no longer supported"})
    elif order_by == "number_created_packages":
        order_by_field = order_by
    elif order_by != "display_name":
        try:
            order_by_field = getattr(model.User, order_by)
        except AttributeError:
            pass
    if order_by == "display_name" or order_by_field is None:
        query = query.order_by(
            sa.case(
                [
                    (
                        sa.or_(model.User.fullname is None, model.User.fullname == ""),
                        model.User.name,
                    )
                ],
                else_=model.User.fullname,
            )
        )
    elif (
        order_by_field == "number_created_packages"
        or order_by_field == "fullname"
        or order_by_field == "about"
        or order_by_field == "sysadmin"
    ):
        query = query.order_by(order_by_field, model.User.name)
    else:
        query = query.order_by(order_by_field)

    ## hack for pagination
    if context.get("return_query"):
        return query

    users_list: ActionResult.UserList = []

    if all_fields:
        for user in query.all():
            result_dict = model_dictize.user_dictize(user[0], context)
            users_list.append(result_dict)  # type: ignore
    else:
        for user in query.all():
            users_list.append(user[0])

    return users_list
