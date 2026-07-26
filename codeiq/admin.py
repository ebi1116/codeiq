from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig


class CodeIQAdminSite(AdminSite):
    site_header = "CodeIQ Administration"
    site_title = "CodeIQ Admin"
    index_title = "Content Management"

    sidebar_models = {"Category", "Technology", "Company", "InterviewPDF", "Order", "User"}

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        visible_apps = []
        for app in app_list:
            app["models"] = [model for model in app["models"] if model["object_name"] in self.sidebar_models]
            if app["models"]:
                visible_apps.append(app)
        return visible_apps


class CodeIQAdminConfig(AdminConfig):
    default_site = "codeiq.admin.CodeIQAdminSite"
