"""
This file contains only functions that deal with the version
of the repository. It can set a new version as a tag and look
up the current version.
"""
import subprocess
import logging
import os

from vdt.version.shared import VersionError, VersionNotFound, Version


log = logging.getLogger('vdt.versionplugin.default')


__all__ = ('get_version', 'set_version')


def get_version(version_args):
    """
    Retrieve the version from the repo.
    
    It can be assumed that this script will be ran in the
    root of the repository.
    """
    # First try to get the current version using "git describe".
    args = ['git', 'describe', '--abbrev=0', '--tags']
    version = None
    try:
        line = subprocess.check_output(args, stderr=None)
        version = line.strip()
    except subprocess.CalledProcessError as e:
        log.error("Git error: {0}".format(e))

    if not version:
        raise VersionNotFound("cannot find the current version. Please create an annotated tag x.y.z!")

    log.debug("Extra argument are %s" % version_args)
    return Version(version, extra_args=version_args)



def set_version(version):
    """
    Create a new tag on this repo with the version as specified.
    
    This function should always return the version.
    If the version could not be updated because of an error,
    the current version should be returned, so there will never
    be any packages built out of untagged versions!
    """
    with open(os.devnull, "w") as devnull:        
        find_tags_on_head = ['git', 'describe', '--exact-match', '--tags', 'HEAD']

        # check if the current revision is allready tagged.
        if subprocess.call(find_tags_on_head, stdout=devnull, stderr=devnull) != 0:
            if version.annotated:
                log.debug("writing annotated version {0}".format(version))
                if version.changelog and version.changelog != "":
                    args = ["git", "tag", "-a", str(version), "-m", version.changelog]
                    subprocess.check_call(args)
                else:
                    raise VersionError("Changelog can not be empty when writing an annotated tag.")
            else:
                log.debug("writing version {0}".format(version))
                args = ["git", "tag", str(version)]
                subprocess.check_call(args)

        else:
            tag = subprocess.check_output(find_tags_on_head)
            log.warn("Not tagging, this revision is allready tagged as: {0}".format(tag))
            version = Version(tag, extra_args=version.extra_args)
        
    return version