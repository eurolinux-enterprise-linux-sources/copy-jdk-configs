%global project copy_jdk_configs
%global file %{project}.lua
%global fixFile %{project}_fixFiles.sh
%global rpm_state_dir %{_localstatedir}/lib/rpm-state

Name:    copy-jdk-configs

# hash relevant to version tag
%global  htag de7cb1123c5e519b2d946f3afb9812e976954d0d
Version: 3.3
Release: 9%{?dist}
Summary: JDKs configuration files copier

License:  BSD
URL:      https://pagure.io/%{project}
Source0:  %{URL}/blob/%{htag}/f/%{file}
Source1:  %{URL}/blob/%{htag}/f/LICENSE
Source2:  %{URL}/blob/%{htag}/f/%{fixFile}

# we need to duplicate msot of the percents in that script so they survive rpm expansion (even in that sed they have to be duplicated)
%global pretrans_install %(cat %{SOURCE0} | sed s/%%/%%%%/g | sed s/\\^%%%%/^%%/g) 

BuildArch: noarch

Requires: lua
#Requires: lua-posix

%description
Utility script to transfer JDKs configuration files between updates or for
archiving. With script to fix incorrectly created rpmnew files

%prep
cp -a %{SOURCE1} .


%build
#blob

%pretrans -p <lua>
function createPretransScript()
-- the sript must be available during pretrans, so multiply it to tmp
  os.execute("mkdir -p %{rpm_state_dir}")
  temp_path="%{rpm_state_dir}/%{file}"
-- print("generating " .. temp_path)
  file = io.open(temp_path, "w")
  file:write([[%{pretrans_install}]])
  file:close()
end

-- in netinst, the above call may fail. pcall should save instalation (as there is nothing to copy anyway)
-- https://bugzilla.redhat.com/show_bug.cgi?id=1295701
-- todo, decide whether to check for {rpm_state_dir} and skip on not-existing, or keep creating
if pcall(createPretransScript) then
-- ok
else
--  print("Error running %{name} pretrans.")
end

%install
mkdir -p $RPM_BUILD_ROOT/%{_libexecdir}
cp -a %{SOURCE0} $RPM_BUILD_ROOT/%{_libexecdir}/%{file}
chmod 644 $RPM_BUILD_ROOT/%{_libexecdir}/%{file}
mkdir -p $RPM_BUILD_ROOT/%{_docdir}/%{project}/
cp %{SOURCE1} $RPM_BUILD_ROOT/%{_docdir}/%{project}/
cp -a %{SOURCE2} $RPM_BUILD_ROOT/%{_libexecdir}/%{fixFile}

%posttrans
# remove file created in pretrans
# echo "removing %{rpm_state_dir}/%{file}" || :
rm "%{rpm_state_dir}/%{file}" 2> /dev/null || :

%files 
%{_libexecdir}/%{file}
%{_libexecdir}/%{fixFile}
%doc %{_docdir}/%{project}/LICENSE

%changelog
* Wed Apr 25 2018 Jiri Vanek <jvanek@redhat.com> - 3.3-3
- fixes issue when java.security for openjdk7 was erased
- Resolves: rhbz#1503666

* Fri Nov 03 2017 Jiri Vanek <jvanek@redhat.com> - 3.3-2
- added another subdirs for policies files
- Resolves: rhbz#1503666

* Fri Nov 03 2017 Jiri Vanek <jvanek@redhat.com> - 3.3-1
- updated to 3.3
- Resolves: rhbz#1503666

* Tue Dec 01 2016 Jiri Vanek <jvanek@redhat.com> - 1.3-1
- updated to upstream 1.3 (adding jre/lib/security/cacerts file)
- Resolves: rhbz#1391735

* Tue Aug 09 2016 Jiri Vanek <jvanek@redhat.com> - 1.2-1
- initial import to rhel6
- commented out lua-posix
- the work horse file changed to 644 (as it do not work without lua-posix)
- Resolves: rhbz#1391735

* Tue Aug 09 2016 Jiri Vanek <jvanek@redhat.com> - 1.2-1
- updated to 1,3 which fixing nss minor issue

* Tue Jul 12 2016 Jiri Vanek <jvanek@redhat.com> - 1.1-5
- posttrans silenced, the error is appearing only in state, when there is nothing to copy

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 08 2016 Jiri Vanek <jvanek@redhat.com> - 1.1-3
- pretrasn lua call now done in pcall (protected call)
- also posttrans now always return 0

* Wed Dec 16 2015 Jiri Vanek <jvanek@redhat.com> - 1.1-2
- package now "installs" also during pretrans, so pretrasn scripts can use it
- pretrasn "install" is removed in postrans

* Wed Nov 25 2015 Jiri Vanek <jvanek@redhat.com> - 1.1-1
- initial package
- license handed in "old" way
