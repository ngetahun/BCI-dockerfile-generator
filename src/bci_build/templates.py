"""This module contains the Jinja2 templates used to generate the build
descriptions.

"""

import datetime

import jinja2

INFOHEADER_TEMPLATE = f"""
    Copyright (c) {datetime.datetime.now().year} SUSE LLC

All modifications and additions to the file contributed by third parties
remain the property of their copyright owners, unless otherwise agreed
upon.

The content of THIS FILE IS AUTOGENERATED and should not be manually modified.
It is maintained by the BCI team and generated by
https://github.com/SUSE/BCI-dockerfile-generator

Please submit bugfixes or comments via https://bugs.opensuse.org/
You can contact the BCI team via https://github.com/SUSE/bci/discussions
"""


#: Jinja2 template used to generate :file:`Dockerfile`
DOCKERFILE_TEMPLATE = jinja2.Template(
    """# SPDX-License-Identifier: {{ image.license }}
{{ INFOHEADER }}
{% if image.exclusive_arch %}#!ExclusiveArch: {% for arch in image.exclusive_arch %}{{ arch }}{{ " " if not loop.last }}{% endfor %}
{%- endif %}
{% for tag in image.build_tags -%}
#!BuildTag: {{ tag }}
{% endfor -%}
{% if image.build_version %}#!BuildName: {{ image.build_name }}
#!BuildVersion: {{ image.build_version }}
{%- endif %}
{%- if image.build_release %}
#!BuildRelease: {{ image.build_release }}
{%- endif %}
{{ image.dockerfile_from_line }}
{%- if image.from_target_image %}
COPY --from=target / /target
{%- endif %}

{% if image.packages %}{{ DOCKERFILE_RUN }} zypper{% if image.from_target_image %} --installroot /target --gpg-auto-import-keys {% endif %} -n in {% if image.no_recommends %}--no-recommends {% endif %}{{ image.packages }}; zypper -n clean; {{ LOG_CLEAN }}{% endif %}
{% if image.from_target_image %}FROM target
COPY --from=builder /target /{% endif %}
MAINTAINER {{ image.maintainer }}

# Define labels according to https://en.opensuse.org/Building_derived_containers
# labelprefix={{ image.labelprefix }}
LABEL org.opencontainers.image.title="{{ image.title }}"
LABEL org.opencontainers.image.description="{{ image.description }}"
LABEL org.opencontainers.image.version="{{ image.version_label }}"
LABEL org.opencontainers.image.url="{{ image.url }}"
LABEL org.opencontainers.image.created="%BUILDTIME%"
LABEL org.opencontainers.image.vendor="{{ image.vendor }}"
LABEL org.opencontainers.image.source="%SOURCEURL%"
LABEL org.opensuse.reference="{{ image.reference }}"
LABEL org.openbuildservice.disturl="%DISTURL%"
{%- if image.os_version.is_tumbleweed %}
LABEL org.opensuse.lifecycle-url="{{ image.lifecycle_url }}"
LABEL org.opensuse.release-stage="{{ image.release_stage }}"
{%- else %}
LABEL com.suse.supportlevel="{{ image.support_level }}"
{%- if image.supported_until %}
LABEL com.suse.supportlevel.until="{{ image.supported_until }}"
{%- endif %}
LABEL com.suse.eula="{{ image.eula }}"
LABEL com.suse.lifecycle-url="{{ image.lifecycle_url }}"
LABEL com.suse.release-stage="{{ image.release_stage }}"
{%- endif %}
# endlabelprefix
LABEL io.artifacthub.package.readme-url="{{ image.readme_url }}"
{%- if image.logo_url %}
LABEL io.artifacthub.package.logo-url="{{ image.logo_url }}"
{%- endif %}
{%- if image.extra_label_lines %}{{ image.extra_label_lines }}
{%- endif %}

{%- if image.env_lines %}{{- image.env_lines }}{% endif %}
{%- if image.entrypoint_docker %}{{ image.entrypoint_docker }}{% endif %}
{%- if image.cmd_docker %}{{ image.cmd_docker }}{% endif %}
{%- if image.expose_dockerfile %}{{ image.expose_dockerfile }}{% endif %}
{% if image.dockerfile_custom_end %}{{ image.dockerfile_custom_end }}{% endif %}
{%- if image.entrypoint_user %}USER {{ image.entrypoint_user }}{% endif %}
{%- if image.volume_dockerfile %}{{ image.volume_dockerfile }}{% endif %}
"""
)

#: Jinja2 template used to generate :file:`$pkg_name.kiwi`
KIWI_TEMPLATE = jinja2.Template(
    """<?xml version="1.0" encoding="utf-8"?>
<!-- SPDX-License-Identifier: {{ image.license }} -->
<!-- {{ INFOHEADER }}-->
<!-- OBS-AddTag: {% for tag in image.build_tags -%} {{ tag }} {% endfor -%}-->
<!-- OBS-Imagerepo: obsrepositories:/ -->

<image schemaversion="7.4" name="{{ image.uid }}-image" xmlns:suse_label_helper="com.suse.label_helper">
  <description type="system">
    <author>{{ image.vendor }}</author>
    <contact>https://www.suse.com/</contact>
    <specification>{{ image.title }} Container Image</specification>
  </description>
  <preferences>
    <type image="docker"{{ image.kiwi_derived_from_entry }}>
      <containerconfig
          name="{{ image.build_tags[0].split(':')[0] }}"
          tag="{{ image.build_tags[0].split(':')[1] }}"
{%- if image.kiwi_additional_tags %}
          additionaltags="{{ image.kiwi_additional_tags }}"
{%- endif %}
{%- if image.entrypoint_user  %}
          user="{{ image.entrypoint_user }}"
{%- endif %}
          maintainer="{{ image.maintainer }}">
        <labels>
          <suse_label_helper:add_prefix prefix="{{ image.labelprefix }}">
            <label name="org.opencontainers.image.title" value="{{ image.title }}"/>
            <label name="org.opencontainers.image.description" value="{{ image.description }}"/>
            <label name="org.opencontainers.image.version" value="{{ image.version_label }}"/>
            <label name="org.opencontainers.image.created" value="%BUILDTIME%"/>
            <label name="org.opencontainers.image.vendor" value="{{ image.vendor }}"/>
            <label name="org.opencontainers.image.source" value="%SOURCEURL%"/>
            <label name="org.opencontainers.image.url" value="{{ image.url }}"/>
            <label name="org.opensuse.reference" value="{{ image.reference }}"/>
            <label name="org.openbuildservice.disturl" value="%DISTURL%"/>
{%- if not image.os_version.is_tumbleweed %}
            <label name="com.suse.supportlevel" value="{{ image.support_level }}"/>
{%- if image.supported_until %}
            <label name="com.suse.supportlevel.until" value="{{ image.supported_until }}"/>
{%- endif %}
            <label name="com.suse.eula" value="{{ image.eula }}"/>
{%- endif %}
            <label name="{% if image.os_version.is_tumbleweed %}org.opensuse{% else %}com.suse{% endif %}.release-stage" value="{{ image.release_stage }}"/>
            <label name="{% if image.os_version.is_tumbleweed %}org.opensuse{% else %}com.suse{% endif %}.lifecycle-url" value="{{ image.lifecycle_url }}"/>
{{- image.extra_label_xml_lines }}
          </suse_label_helper:add_prefix>
          <label name="io.artifacthub.package.readme-url" value="{{ image.readme_url }}"/>{% if image.logo_url %}
          <label name="io.artifacthub.package.logo-url" value="{{ image.logo_url }}"/>{% endif %}
        </labels>
{%- if image.cmd_kiwi %}{{ image.cmd_kiwi }}{% endif %}
{%- if image.entrypoint_kiwi %}{{ image.entrypoint_kiwi }}{% endif %}
{%- if image.volumes_kiwi %}{{ image.volumes_kiwi }}{% endif %}
{%- if image.exposes_kiwi %}{{ image.exposes_kiwi }}{% endif %}
{{- image.kiwi_env_entry }}
      </containerconfig>
    </type>
    <version>{{ image.kiwi_version }}</version>
    <packagemanager>zypper</packagemanager>
    <rpm-check-signatures>false</rpm-check-signatures>
    <rpm-excludedocs>true</rpm-excludedocs>
  </preferences>
  <repository type="rpm-md">
    <source path="obsrepositories:/"/>
  </repository>
{{ image.kiwi_packages }}
</image>
"""
)

#: Jinja2 template used to generate :file:`_service`.
SERVICE_TEMPLATE = jinja2.Template(
    """<services>
  <service mode="buildtime" name="{{ image.build_recipe_type }}_label_helper"/>
  <service mode="buildtime" name="kiwi_metainfo_helper"/>
{%- for replacement in image.replacements_via_service %}
  <service name="replace_using_package_version" mode="buildtime">
    <param name="file">{% if replacement.file_name != None %}{{replacement.file_name}}{% elif (image.build_recipe_type|string) == "docker" %}Dockerfile{% else %}{{ image.package_name }}.kiwi{% endif %}</param>
    <param name="regex">{{ replacement.regex_in_build_description }}</param>
    <param name="package">{{ replacement.package_name }}</param>{% if replacement.parse_version %}
    <param name="parse-version">{{ replacement.parse_version }}</param>{% endif %}
  </service>{% endfor %}
</services>
"""
)
