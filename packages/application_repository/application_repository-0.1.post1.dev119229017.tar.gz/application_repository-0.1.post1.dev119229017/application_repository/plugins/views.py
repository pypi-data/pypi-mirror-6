import logging
logging.basicConfig(level=logging.INFO)

from django_jsonrpc import jsonrpc_method

import settings
from .models import Plugin as package_class, PluginVersion as version_class
import repository.views 


@jsonrpc_method('plugins.available_packages')
def available_packages(request):
    return repository.views.available_packages(package_class, request)


@jsonrpc_method('plugins.available_plugins')
def available_plugins(request):
    return [p.plugin_name for p in package_class.objects.filter(
            public=True).order_by('plugin_name')]


@jsonrpc_method('plugins.package_name')
def package_name(request, plugin_name):
    logging.error(plugin_name)
    plugin = package_class.objects.get(plugin_name=plugin_name)
    return plugin.name


@jsonrpc_method('plugins.plugin_name')
def plugin_name(request, package_name):
    plugin = package_class.objects.get(name=package_name)
    return plugin.plugin_name


@jsonrpc_method('plugins.package_latest_version')
def package_latest_version(request, package_name):
    return repository.views.package_latest_version(version_class, request,
            package_name)


@jsonrpc_method('plugins.package_versions')
def package_versions(request, package_name):
    return repository.views.package_versions(version_class, request, package_name)


@jsonrpc_method('plugins.package_url')
def package_url(request, package_name, version):
    return repository.views.package_url(version_class, request, package_name,
            version)


def redirect_to_latest(request, package_name):
    return repository.views.redirect_to_latest(version_class, request,
            package_name)
