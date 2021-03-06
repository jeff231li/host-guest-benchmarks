"""
This module contains the function that generates the entry point used by pAPRika to run benchmark calculations.
"""

from pathlib import Path
import yaml
import pkg_resources
import logging

logger = logging.getLogger(__name__)

def find_hosts(directory, subdirectory):
    """
    Return the list of hosts that provide a YAML recipe.

    Parameters
    ----------
    directory : Path
        The root path for the benchmarks
    subdirectory : Path
        The path that contains the benchmark systems

    Returns
    -------
    hosts : List[Path]
        The list of directory paths containing YAML recipes.
    """

    hosts = {}
    p = Path(directory).joinpath(subdirectory)
    files = p.resolve().glob("*")
    directories = [i for i in files if i.is_dir()]
    for host in directories:
        hosts[host.stem] = {}
        hosts[host.stem]["path"] = host
        hosts[host.stem]["yaml"] = {}
        for file in host.glob("*.yaml"):
            try:
                orientation = file.stem.split("-")[1]
            except IndexError:
                orientation = "p"
            hosts[host.stem]["yaml"][orientation] = file.resolve()
            logger.debug(f"Found host YAML: {file.resolve()}")
    return hosts


def find_guests(host, wildcard="*"):
    """
    Return the list of guests that provide a YAML recipe, for a given host.

    Parameters
    ----------
    host : List
        A list of YAML files for a given host.

    Returns
    -------
    guests : List[Path]
        The list of directory paths containing YAML recipes.
    """

    guests = {}
    for file in Path(host["path"]).glob(f"*/{wildcard}.yaml"):
        guests[file.parent.stem] = {}
        guests[file.parent.stem]["path"] = file.parent.resolve()
        guests[file.parent.stem]["yaml"] = file.resolve()
        logger.debug(f"Found guest YAML: {file.resolve()}")
    return guests


def find_host_guest_pairs():
    """
    Determine host:guest pairs available to simulate.

    Returns
    -------
    host_guest_systems : Dict
        Directory paths containing YAML recipes for simulations.
    host_guest_measurements : Dict
        Directory paths containing YAML recipes for experimental data.

    """

    host_guest_systems = {}
    host_guest_measurements = {}

    installed_module_location = Path(pkg_resources.resource_filename("taproom", "entry_points.py")).parents[0]
    hosts = find_hosts(installed_module_location, subdirectory="systems")
    for host, host_path in hosts.items():
        host_guest_systems[host] = {}
        host_guest_systems[host]["yaml"] = host_path["yaml"]
        host_guest_systems[host]["path"] = host_path["path"]
        guests = find_guests(host_path, wildcard="guest")
        for guest, guest_path in guests.items():
            host_guest_systems[host][guest] = guest_path

        host_guest_measurements[host] = {}
        guests = find_guests(host_path, wildcard="measurement")
        for guest, guest_path in guests.items():
            host_guest_measurements[host][guest] = guest_path

    return host_guest_systems, host_guest_measurements

host_guest_systems, host_guest_measurements = find_host_guest_pairs()