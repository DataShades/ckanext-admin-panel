from __future__ import annotations

import random
import string
from datetime import datetime as dt
from datetime import timezone
from typing import Any

from datacite.errors import DataCiteError

import ckan.plugins.toolkit as tk
from ckan.logic import validate

import ckanext.ap_doi.logic.schema as schema
import ckanext.doi.model.crud as doi_crud
from ckanext.ap_doi import config, const
from ckanext.ap_doi.utils import (
    DOIProblemPackageData,
    get_doi_to_update,
    get_packages_to_update,
    package_already_in_flake,
    remove_package_from_flake,
)
from ckanext.doi.lib.api import DataciteClient
from ckanext.doi.lib.metadata import build_metadata_dict, build_xml_dict
from ckanext.doi.model.doi import DOI


@tk.side_effect_free
@validate(schema.ap_doi_get_packages_doi)
def ap_doi_get_packages_doi(
    context: Any, data_dict: dict[str, Any]
) -> list[DOIProblemPackageData]:
    """Retrieve packages data along with DOI identifiers."""
    tk.check_access("ap_doi_get_packages_doi", context, data_dict)

    model = context["model"]
    packages_to_update = get_packages_to_update(const.DOI_FLAKE_NAME)

    results = (
        model.Session.query(
            model.Package.id.label("package_id"),
            model.Package.name.label("package_name"),
            model.Package.title.label("package_title"),
            model.Package.type.label("package_type"),
            model.Package.metadata_modified.label("metadata_modified"),
            DOI.published.label("published"),
            DOI.identifier.label("identifier"),
        )
        .join(DOI, model.Package.id == DOI.package_id, isouter=True)
        .filter(model.Package.type != "harvest")
        .filter(
            model.Package.id.notin_(
                (
                    model.Session.query(model.PackageExtra.package_id.label("id"))
                    .filter(model.PackageExtra.key == "data_source")
                    .filter(model.PackageExtra.value != "")
                    .subquery()
                )
            )
        )
        .all()
    )

    results = _prepare_problem_package_data(results, packages_to_update)
    return _filter_dois(results, data_dict)


def _prepare_problem_package_data(
    results: Any,
    packages_to_update: list[DOIProblemPackageData],
) -> list[DOIProblemPackageData]:
    packages_data: list[DOIProblemPackageData] = []
    outdated_ids = [package["id"] for package in packages_to_update]

    for row in results:
        if row.package_id in outdated_ids:
            continue

        doi_status = "Missing"

        if row.published and row.published < row.metadata_modified:
            doi_status = "Outdated"
        elif row.published:
            doi_status = "Published"

        packages_data.append(
            {
                "id": row.package_id,
                "name": row.package_name,
                "title": row.package_title,
                "doi_status": doi_status,
                "published": row.published,
                "identifier": row.identifier,
                "timestamp": row.metadata_modified,
                "type": row.package_type,
            }
        )

    for package in packages_to_update:
        if package not in packages_data:
            packages_data.append(package)

    # Sort packages_data, prioritizing 'Outdated' status
    return sorted(
        packages_data,
        key=lambda x: (x["doi_status"] == "Outdated", x["timestamp"]),
        # Reverse to get 'Outdated' first
        reverse=True,
    )


def _filter_dois(
    results: list[DOIProblemPackageData], data_dict: dict[str, Any]
) -> list[DOIProblemPackageData]:
    """Filter out packages that do not have a DOI."""

    if q := tk.request.args.get("ap-doi:q"):
        results = [result for result in results if q.lower() in result["title"].lower()]

    if doi_status := tk.request.args.get("ap-doi:doi_status"):
        results = [result for result in results if doi_status == result["doi_status"]]

    return results


def ap_doi_update_doi(context: Any, data_dict: dict[str, Any]) -> dict[str, Any]:
    """Action to update a DOI."""
    tk.check_access("ap_doi_update_doi", context, data_dict)

    package_id = data_dict.get("package_id")

    if not package_id:
        raise tk.ValidationError({"package_id": "Missing package_id for DOI update"})

    if config.is_mock_api_calls():
        errors = _mock_update_doi_metadata(context, package_id)
    else:
        doi_to_update = get_doi_to_update(context["model"], package_id)
        pkg_dict = tk.get_action("package_show")({}, {"id": doi_to_update.package_id})
        errors = _update_doi_metadata(pkg_dict, doi_to_update)

    if not errors and package_already_in_flake(const.DOI_FLAKE_NAME, package_id):
        remove_package_from_flake(const.DOI_FLAKE_NAME, package_id)

    return {
        "status": "success" if not errors else "error",
        "message": "DOI update completed",
        "errors": errors,
    }


def _mock_update_doi_metadata(context: Any, package_id: dict[str, Any]):
    if doi_crud.DOIQuery.read_package(package_id):
        context["model"].Session.query(DOI).filter(DOI.package_id == package_id).update(
            {"published": dt.now(timezone.utc).isoformat()}
        )
    else:
        alphabet = string.ascii_lowercase + string.digits
        doi = f"{config.get_doi_prefix()}/{''.join(random.choices(alphabet, k=8))}"
        doi_crud.DOIQuery.create(doi, package_id, dt.now(timezone.utc).isoformat())

    context["model"].Session.commit()

    return []


def _update_doi_metadata(pkg_dict: dict[str, Any], doi_to_update: DOI):
    """Update the DOI metadata and handle DOI creation or update as necessary."""
    title = pkg_dict.get("title", doi_to_update.package_id)

    if not pkg_dict.get("author"):
        _add_author_to_pkg_dict(pkg_dict)

    metadata_dict = build_metadata_dict(pkg_dict)
    xml_dict = build_xml_dict(metadata_dict)
    return _handle_doi_creation_or_update(doi_to_update, xml_dict, title)


def _add_author_to_pkg_dict(pkg_dict: dict[str, Any]):
    """Set the author full name in the package dictionary."""
    creator = tk.get_action("user_show")({}, {"id": pkg_dict["creator_user_id"]})
    full_name = creator.get("fullname")
    name = creator.get("name")
    pkg_dict["author"] = full_name or name


def _handle_doi_creation_or_update(
    doi_to_update: DOI, xml_dict: dict[str, Any], title: str
):
    """Handle DOI creation or update based on the DOI's publication status."""
    errors = []
    client = DataciteClient()

    if doi_to_update.published is None:
        _create_doi(client, doi_to_update, xml_dict)
    else:
        _update_existing_doi(client, doi_to_update, xml_dict, title, errors)
    return errors


def _create_doi(client: DataciteClient, doi_to_update: DOI, xml_dict: dict[str, Any]):
    """Create a new DOI with the given metadata."""
    client.set_metadata(doi_to_update.identifier, xml_dict)
    client.mint_doi(doi_to_update.identifier, doi_to_update.package_id)


def _update_existing_doi(
    client: DataciteClient,
    doi_to_update: DOI,
    xml_dict: dict[str, Any],
    title: str,
    errors: list[str],
):
    """Update an existing DOI if the metadata has changed."""
    same = client.check_for_update(doi_to_update.identifier, xml_dict)
    if not same:
        try:
            client.set_metadata(doi_to_update.identifier, xml_dict)
        except DataCiteError as e:
            errors.append(
                f'Error while updating "{title}"'
                f" (DOI {doi_to_update.identifier}): {str(e)}"
            )
    else:
        errors.append(f'"{title}" is already up to date')
        remove_package_from_flake(const.DOI_FLAKE_NAME, doi_to_update.package_id)
