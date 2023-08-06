# -*- coding: utf-8 -*-
from django.conf import settings as django_settings

# Should urls be case sensitive?
URL_CASE_SENSITIVE = getattr(django_settings, 'WIKI_URL_CASE_SENSITIVE', False)

# Non-configurable (at the moment)
APP_LABEL = 'wiki'


# This slug is used in URLPath if an article has been deleted. The children of the
# URLPath of that article are moved to lost and found. They keep their permissions
# and all their content.
LOST_AND_FOUND_SLUG = getattr(django_settings, 'WIKI_LOST_AND_FOUND_SLUG', 'lost-and-found')

# Do we want to log IPs?
LOG_IPS_ANONYMOUS = getattr(django_settings, 'WIKI_LOG_IPS_ANONYMOUS', True)
LOG_IPS_USERS = getattr(django_settings, 'WIKI_LOG_IPS_USERS', False)

####################################
# PERMISSIONS AND ACCOUNT HANDLING #
####################################

# NB! None of these callables need to handle anonymous users as they are treated
# in separate settings...

# A function returning True/False if a user has permission to
# read contents of an article
# Relevance: viewing articles
CAN_READ = getattr(django_settings, 'WIKI_CAN_READ', None)

# A function returning True/False if a user has permission to
# change contents, ie add new revisions to an article
# Relevance: editing articles, changing revisions
CAN_WRITE = getattr(django_settings, 'WIKI_CAN_WRITE', None)

# A function returning True/False if a user has permission to assign
# permissions on an article
# Relevance: changing owner and group membership
CAN_ASSIGN = getattr(django_settings, 'WIKI_CAN_ASSIGN', None)

# A function returning True/False if the owner of an article has permission to change
# the group to a user's own groups
# Relevance: changing group membership
CAN_ASSIGN_OWNER = getattr(django_settings, 'WIKI_ASSIGN_OWNER', None)

# A function returning True/False if a user has permission to change
# read/write access for groups and others
CAN_CHANGE_PERMISSIONS = getattr(django_settings, 'WIKI_CAN_CHANGE_PERMISSIONS', None)

# Specifies if a user has access to soft deletion of articles
CAN_DELETE = getattr(django_settings, 'WIKI_CAN_DELETE', None)

# A function returning True/False if a user has permission to change
# moderate, ie. lock articles and permanently delete content.
CAN_MODERATE = getattr(django_settings, 'WIKI_CAN_MODERATE', None)

# A function returning True/False if a user has permission to create
# new groups and users for the wiki.
CAN_ADMIN = getattr(django_settings, 'WIKI_CAN_ADMIN', None)

# Treat anonymous (non logged in) users as the "other" user group
ANONYMOUS = getattr(django_settings, 'WIKI_ANONYMOUS', True)

# Globally enable write access for anonymous users, if true anonymous users will be treated
# as the others_write boolean field on models.Article. 
ANONYMOUS_WRITE = getattr(django_settings, 'WIKI_ANONYMOUS_WRITE', False)

# Globally enable create access for anonymous users
# Defaults to ANONYMOUS_WRITE.  
ANONYMOUS_CREATE = getattr(django_settings, 'WIKI_ANONYMOUS_CREATE', ANONYMOUS_WRITE)

# Sign up, login and logout views should be accessible 
ACCOUNT_HANDLING = getattr(django_settings, 'WIKI_ACCOUNT_HANDLING', True)


##################
# OTHER SETTINGS #
##################
# Seconds of timeout before renewing article cache. Articles are automatically
# renewed whenever an edit occurs but article content may be generated from
# other objects that are changed.
CACHE_TIMEOUT = getattr(django_settings, 'WIKI_CACHE_TIMEOUT', 600)

###################
# SPAM PROTECTION #
###################

# Maximum allowed revisions per hour for any given user or IP
REVISIONS_PER_HOUR = getattr(django_settings, 'WIKI_REVISIONS_PER_HOUR', 60)

# Maximum allowed revisions per hour for any given user or IP
REVISIONS_PER_MINUTES = getattr(django_settings, 'WIKI_REVISIONS_PER_MINUTES', 5)

# Maximum allowed revisions per hour for any given user or IP
REVISIONS_PER_HOUR_ANONYMOUS = getattr(django_settings, 'WIKI_REVISIONS_PER_HOUR_ANONYMOUS', 10)

# Maximum allowed revisions per hour for any given user or IP
REVISIONS_PER_MINUTES_ANONYMOUS = getattr(django_settings, 'WIKI_REVISIONS_PER_MINUTES_ANONYMOUS', 2)

# Number of minutes for looking up REVISIONS_PER_MINUTES and REVISIONS_PER_MINUTES_ANONYMOUS
REVISIONS_MINUTES_LOOKBACK = getattr(django_settings, 'WIKI_REVISIONS_MINUTES_LOOKBACK', 2)

####################
# PLANNED SETTINGS #
####################

# Maximum revisions to keep for an article, 0=unlimited
MAX_REVISIONS = getattr(django_settings, 'WIKI_MAX_REVISIONS', 100)

# Maximum age of revisions in days, 0=unlimited
MAX_REVISION_AGE = getattr(django_settings, 'MAX_REVISION_AGE', 365)
