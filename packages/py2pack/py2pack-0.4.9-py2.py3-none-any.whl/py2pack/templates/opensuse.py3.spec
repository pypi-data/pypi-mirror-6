#
# spec file for package python3-{{ name }}
#
# Copyright (c) {{ year }} SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/


Name:           python3-{{ name }}
Version:        {{ version }}
Release:        0
License:        {{ license }}
Summary:        {{ summary_no_ending_dot|default(summary, true) }}
Url:            {{ home_page }}
Group:          Development/Languages/Python
Source:         {{ source_url|replace(version, '%{version}') }}
BuildRequires:  python3-devel {%- if requires_python %} = {{ requires_python }} {% endif %}
{%- for req in requires %}
BuildRequires:  python3-{{ req|replace('(','')|replace(')','') }}
Requires:       python3-{{ req|replace('(','')|replace(')','') }}
{%- endfor %}
{%- for req in install_requires %}
BuildRequires:  python3-{{ req|replace('(','')|replace(')','') }}
Requires:       python3-{{ req|replace('(','')|replace(')','') }}
{%- endfor %}
{%- if source_url.endswith('.zip') %}
BuildRequires:  unzip
{%- endif %}
{%- if extras_require %}
{%- for reqlist in extras_require.values() %}
{%- for req in reqlist %}
Suggests:       python3-{{ req|replace('(','')|replace(')','') }}
{%- endfor %}
{%- endfor %}
{%- endif %}
{%- if not is_extension %}
BuildArch:      noarch
{%- endif %}

%description
{{ description }}

%prep
%setup -q -n {{ name }}-%{version}

%build
{% if is_extension %}CFLAGS="%{optflags}" {% endif %}python3 setup.py build

%install
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}

{%- if testsuite or test_suite %}

%check
  {%- if test_suite %}
python3 setup.py test
  {%- else %}
nosetests
  {%- endif %}
{%- endif %}

%files
%defattr(-,root,root,-)
{%- if doc_files %}
%doc {{ doc_files|join(" ") }}
{%- endif %}
{%- for script in scripts %}
%{_bindir}/{{ script }}
{%- endfor %}
{%- if is_extension %}
%{python_sitearch}/*
{%- else %}
%{python_sitelib}/*
{%- endif %}

%changelog
