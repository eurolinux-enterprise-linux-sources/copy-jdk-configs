%global project copy_jdk_configs
%global file %{project}.lua
%global fixFile %{project}_fixFiles.sh
%global rpm_state_dir %{_localstatedir}/lib/rpm-state

Name:    copy-jdk-configs

# hash relevant to version tag
%global  htag 3f9d6c4448f867a95fb166416a41c45c7e795c10
Version: 2.2
Release: 3%{?dist}
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
cp -a %{SOURCE2} $RPM_BUILD_ROOT/%{_libexecdir}/%{fixFile}

%posttrans
# remove file created in pretrans
# echo "removing %{rpm_state_dir}/%{file}" || :
rm "%{rpm_state_dir}/%{file}" 2> /dev/null || :

%files 
%{_libexecdir}/%{file}
%{_libexecdir}/%{fixFile}
%license LICENSE

%changelog
* Mon Jun 19 2017 Jiri Vanek <jvanek@redhat.com> - 2.2-3
- updated to latest head
- Resolves: rhbz#1427463

* Tue Jun 13 2017 Jiri Vanek <jvanek@redhat.com> - 2.2-1
- added "jre/lib/security/blacklisted.certs" to cared files
- moved to newest release 2.1
- moved to new upstream at pagure.io
- added new script of copy_jdk_configs_fixFiles.sh 
- copy_jdk_configs.lua  aligned to it
- Resolves: rhbz#1427463

* Tue Dec 01 2016 Jiri Vanek <jvanek@redhat.com> - 1.3-1
- updated to upstream 1.3 (adding jre/lib/security/cacerts file)
- Resolves: rhbz#1399719

* Tue Aug 09 2016 Jiri Vanek <jvanek@redhat.com> - 1.2-1
- updated to 1,3 which fixing nss minor issue
- Resolves: rhbz#1296430

* Tue Jul 12 2016 Jiri Vanek <jvanek@redhat.com> - 1.1-5
- posttrans silenced, the error is appearing only in state, when there is nothing to copy
- Resolves: rhbz#1296430

* Tue Apr 12 2016 Jiri Vanek <jvanek@redhat.com> - 1.1-3
- commented requires on lua posix to stop blocking composes.
- changed it to 644 to dont mislead by executable flags
- Resolves: rhbz#1296430

* Tue Apr 12 2016 Jiri Vanek <jvanek@redhat.com> - 1.1-3
- inital commit to rhel
- Resolves: rhbz#1296430

* Fri Jan 08 2016 Jiri Vanek <jvanek@redhat.com> - 1.1-3
- pretrasn lua call now done in pcall (protected call)
- also posttrans now always return 0

* Wed Dec 16 2015 Jiri Vanek <jvanek@redhat.com> - 1.1-2
- package now "installs" also during pretrans, so pretrasn scripts can use it
- pretrasn "install" is removed in postrans

* Wed Nov 25 2015 Jiri Vanek <jvanek@redhat.com> - 1.1-1
- initial package
