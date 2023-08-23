from __future__ import annotations

from typing import Any, Dict

from ckan.logic.schema import validator_args, default_user_schema

Schema = Dict[str, Any]


@validator_args
def ap_user_new_form_schema(
    unicode_safe,
    ignore_missing,
    user_both_passwords_entered,
    user_password_validator,
    user_passwords_match,
    one_of,
) -> Schema:
    schema = default_user_schema()

    schema["role"] = [ignore_missing, unicode_safe, one_of(["user", "sysadmin"])]
    schema["password1"] = [
        unicode_safe,
        user_both_passwords_entered,
        user_password_validator,
        user_passwords_match,
    ]
    schema["password2"] = [unicode_safe]

    return schema
