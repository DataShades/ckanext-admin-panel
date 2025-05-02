from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, TypedDict, cast

import ckan.plugins.toolkit as tk
import ckan.types as types

from ckanext.doi.lib.api import DataciteClient
from ckanext.doi.model.doi import DOI


class DOIFlakesData(TypedDict):
    require_doi_update: list[DOIProblemPackageData]


class DOIProblemPackageData(TypedDict):
    id: str
    name: str
    title: str
    doi_status: Optional[str]
    timestamp: datetime
    type: str
    published: str
    identifier: str


def prepare_context() -> types.Context:
    return cast(types.Context, {"ignore_auth": True})


def store_data_in_flake(flake_name: str, data: Any) -> dict[str, Any]:
    """Save the serializable data into the flakes table."""
    return tk.get_action("flakes_flake_override")(
        prepare_context(),
        {"author_id": None, "name": flake_name, "data": data},
    )


def get_data_from_flake(flake_name: str) -> dict[str, Any]:
    """Retrieve a previously stored data from the flake."""
    try:
        return tk.get_action("flakes_flake_lookup")(
            prepare_context(),
            {"author_id": None, "name": flake_name},
        )
    except tk.ObjectNotFound:
        return tk.get_action("flakes_flake_create")(
            prepare_context(),
            {"author_id": None, "name": flake_name, "data": {}},
        )


def package_already_in_flake(flake_name: str, package_id: str) -> bool:
    packages_to_update = get_packages_to_update(flake_name)

    if not packages_to_update:
        return False

    for package in packages_to_update:
        if package["id"] == package_id:
            return True

    return False


def add_package_to_flake(flake_name: str, package_id: str) -> None:
    packages_to_update: list[DOIProblemPackageData] = get_packages_to_update(flake_name)
    package_dict = tk.get_action("package_show")({}, {"id": package_id})

    problem_package_dict: DOIProblemPackageData = {
        "id": package_dict["id"],
        "name": package_dict["name"],
        "title": package_dict["title"],
        "doi_status": "Outdated",
        "timestamp": package_dict["metadata_modified"],
        "identifier": "",
        "published": "",
        "type": package_dict["type"],
    }

    data: DOIFlakesData = {"require_doi_update": [problem_package_dict]}

    if not packages_to_update:
        store_data_in_flake(flake_name, data)
        return

    packages_to_update.append(problem_package_dict)

    store_data_in_flake(flake_name, {"require_doi_update": packages_to_update})


def remove_package_from_flake(flake_name: str, package_id: str) -> None:
    packages_to_update = get_packages_to_update(flake_name)

    if not packages_to_update:
        return

    store_data_in_flake(
        flake_name,
        {
            "require_doi_update": [
                package for package in packages_to_update if package["id"] != package_id
            ]
        },
    )


def get_packages_to_update(flake_name: str) -> list[DOIProblemPackageData]:
    flake = get_data_from_flake(flake_name)

    doi_data = flake["data"].get("require_doi_update")

    if not doi_data:
        return []

    return doi_data


def get_doi_to_update(model: Any, package_id: str) -> DOI:
    """Retrieve the DOI object to be updated,
    or create a new one if it doesn't exist."""
    doi_to_update = model.Session.query(DOI).filter_by(package_id=package_id).first()

    if not doi_to_update:
        identifier = DataciteClient().generate_doi()
        doi_to_update = DOI(package_id=package_id, identifier=identifier)

    return doi_to_update


def set_package_author(pkg_dict: dict[str, Any]):
    creator_id = pkg_dict.get("creator_user_id")

    if not creator_id:
        package = tk.get_action("package_show")({}, {"id": pkg_dict["id"]})
        creator_id = package.get("creator_user_id")

        if package.get("author"):
            pkg_dict["author"] = package.get("author")
            return pkg_dict

    creator = tk.get_action("user_show")({"ignore_auth": True}, {"id": creator_id})

    pkg_dict["author"] = creator.get("fullname") or creator.get("name")

    return pkg_dict
