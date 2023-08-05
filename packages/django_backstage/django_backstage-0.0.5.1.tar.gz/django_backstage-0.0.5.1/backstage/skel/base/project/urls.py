from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns("",
    ("^admin/", include(admin.site.urls)),
    # HOMEPAGE AS STATIC TEMPLATE
    #url("^$", direct_to_template, {"template": "index.html"}, name="home"),
    # HOMEPAGE AS AN EDITABLE PAGE IN THE PAGE TREE
    url("^$", "mezzanine.pages.views.page", {"slug": "/"}, name="home"),
    # MEZZANINE'S URLS
    ("^", include("mezzanine.urls")),

)

