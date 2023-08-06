#/bin/bash
echo -------------------------------------------------------------------------------
echo Oncilla - Files Gathering
echo -------------------------------------------------------------------------------

export PROJECT_DIRECTORY=$(cd $( dirname "${BASH_SOURCE[0]}" )/..; pwd)

export DOCUMENTATION_DIRECTORY=$PROJECT_DIRECTORY/docs/
export RELEASES_DIRECTORY=$PROJECT_DIRECTORY/releases/
export REPOSITORY_DIRECTORY=$RELEASES_DIRECTORY/repository/
export UTILITIES_DIRECTORY=$PROJECT_DIRECTORY/utilities

#! Gathering folder cleanup.
rm -rf $REPOSITORY_DIRECTORY
mkdir -p $REPOSITORY_DIRECTORY/Oncilla

#! Oncilla Changes gathering.
cp -rf $RELEASES_DIRECTORY/Changes.html $REPOSITORY_DIRECTORY/Oncilla/

#! Oncilla Manual / Help files.
cp -rf $DOCUMENTATION_DIRECTORY/help $REPOSITORY_DIRECTORY/Oncilla/Help
rm $REPOSITORY_DIRECTORY/Oncilla/help/Oncilla_Manual.rst

#! Oncilla Api files.
cp -rf $DOCUMENTATION_DIRECTORY/sphinx/build/html $REPOSITORY_DIRECTORY/Oncilla/Api