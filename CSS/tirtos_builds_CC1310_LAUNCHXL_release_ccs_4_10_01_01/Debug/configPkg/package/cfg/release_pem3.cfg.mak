# invoke SourceDir generated makefile for release.pem3
release.pem3: .libraries,release.pem3
.libraries,release.pem3: package/cfg/release_pem3.xdl
	$(MAKE) -f C:\Users\coxbe\workspace_v10\tirtos_builds_CC1310_LAUNCHXL_release_ccs_4_10_01_01/src/makefile.libs

clean::
	$(MAKE) -f C:\Users\coxbe\workspace_v10\tirtos_builds_CC1310_LAUNCHXL_release_ccs_4_10_01_01/src/makefile.libs clean

