################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
build-82945473:
	@$(MAKE) --no-print-directory -Onone -f subdir_rules.mk build-82945473-inproc

build-82945473-inproc: ../release.cfg
	@echo 'Building file: "$<"'
	@echo 'Invoking: XDCtools'
	"C:/ti/xdctools_3_51_03_28_core/xs" --xdcpath="C:/ti/simplelink_cc13x0_sdk_4_10_01_01/source;C:/ti/simplelink_cc13x0_sdk_4_10_01_01/kernel/tirtos/packages;" xdc.tools.configuro -o configPkg -t ti.targets.arm.elf.M3 -p ti.platforms.simplelink:CC1310F128 -r release -c "C:/ti/ccs1020/ccs/tools/compiler/ti-cgt-arm_20.2.2.LTS" --compileOptions " -DDeviceFamily_CC13X0 " "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

configPkg/linker.cmd: build-82945473 ../release.cfg
configPkg/compiler.opt: build-82945473
configPkg/: build-82945473


