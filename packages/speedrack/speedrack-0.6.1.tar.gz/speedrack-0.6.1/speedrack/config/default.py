# Speedrack configuration file

DEBUG = False

FLASK_DEBUG_TOOLBAR = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

CONFIG_YAML = "config/test.yaml"

# The application's navbar home link. If this is a shared resource for
# your organization, this is a good place to put the organization's
# name.
APP_NAME="speedrack"

# Subpath in shared-host. Leave commented out if not running behind
# shared-proxy. See docs/setup.rst for more details.
#SCRIPT_NAME='/speedrack'
#EMAIL_URL_PREFIX=http://example.com/speedrack

#
# task display
#

# Number of executions to display on a task's summary page.
EXECUTION_DISPLAY = 20

# If a given stdout/stderr file is this size or less, just show the
# whole thing on the execution detail page.
FSIZE_MAX     = 10000 # bytes

# If a given stdout/stderr file is too big to show (greater than
# FSIZE_MAX), show this much on the execution detail page.
FSIZE_SUMMARY = 5000  # bytes

#
# Global error defaults
#

# Nonzero status code is failure.
FAIL_BY_RETCODE = True
# Generating stderr is failure.
FAIL_BY_STDERR = True

# Default number of executions retained for all tasks. False indicates
# to retain results from all executions. Per-task overrides take
# precedent.
MAX_RUNS = False

#
# state and file settings
#

# Default is system temp. You should change this.
#SPEEDRACK_DIR = "/your/favorite/path"

# Individual storage overrides
#JOB_ROOT_DIR = "./jobs"
#JOB_STATE = "./sprack.shelve"
#LOG_DIR = "./logs"
#SUSPENDED_FILE = "./sprack.suspended"

# log (size per file * number of files)
LOG_MAX_SIZE = 1024 * 1024 * 10
LOG_COUNT = 5

#
# notification settings
#

# Global switch, overrides other email settings
EMAIL_DISABLED = False
#EMAIL_SMTP = "smtp.yourdomain.org"
#EMAIL_FROM_ADDRESS = "sample@yourdomain.org"
# if set, all emails are sent to this address, ignoring settings on
# individual tasks
#EMAIL_TO_GLOBAL = "you@yourdomain.org"
