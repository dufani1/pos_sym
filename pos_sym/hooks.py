from . import __version__ as app_version

app_name = "pos_sym"
app_title = "Pos Sym"
app_publisher = "."
app_description = "."
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "."
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pos_sym/css/pos_sym.css"
# app_include_js = "/assets/pos_sym/js/pos_sym.js"

# include js, css files in header of web template
# web_include_css = "/assets/pos_sym/css/pos_sym.css"
# web_include_js = "/assets/pos_sym/js/pos_sym.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pos_sym/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "pos_sym.install.before_install"
# after_install = "pos_sym.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "pos_sym.uninstall.before_uninstall"
# after_uninstall = "pos_sym.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pos_sym.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Item": {
		"on_update": [
			"pos_sym.events.item.on_update"
		]
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"pos_sym.tasks.all"
# 	],
# 	"daily": [
# 		"pos_sym.tasks.daily"
# 	],
# 	"hourly": [
# 		"pos_sym.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pos_sym.tasks.weekly"
# 	]
# 	"monthly": [
# 		"pos_sym.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "pos_sym.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pos_sym.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "pos_sym.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"pos_sym.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			["fieldname", "in", (
				"sym_publish_to_local_pos"
				)
			]
		]
	}
]