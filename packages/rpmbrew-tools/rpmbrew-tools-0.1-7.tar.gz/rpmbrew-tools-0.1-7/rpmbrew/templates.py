repo_template = """
[{REPONAME}]
name={DESCRIPTION}
baseurl={BASEURL}
enabled=1
gpgcheck=0
"""

spec_template = """
%define prefix {PREFIX}

Name:     {NAME}        
Version:  {VERSION}      
Release:  {RELEASE} 
Summary:  {SUMMARY}       

License:  {LICENSE}      
URL:      {URL}     
Source0:  {SOURCE}      

BuildRoot:  %{{_tmppath}}/%{{name}}-%{{version}}-%{{release}}-root-%(%{{__id_u}} -n)

#BuildRequires:  
#Requires:       

%description
{DESCRIPTION}
%prep
rm -rf $RPM_BUILD_DIR/%{{name}}-%{{version}}
 
%install
mkdir -p $RPM_BUILD_ROOT/%{{prefix}}
tar xfzC $RPM_SOURCE_DIR/%{{name}}-%{{version}}.tar.gz $RPM_BUILD_ROOT/%{{prefix}}

%files
%{{prefix}}/%{{name}}-%{{version}}
%doc

%changelog
"""