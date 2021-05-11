################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
build-1315429359:
	@$(MAKE) --no-print-directory -Onone -f subdir_rules.mk build-1315429359-inproc

build-1315429359-inproc: ../release.cfg
	@echo 'Building file: "$<"'
	@echo 'Invoking: XDCtools'
	"C:/ti/ccs1020/xdctools_3_62_00_08_core/xs" --xdcpath="C:/ti/simplelink_cc13x0_sdk_4_10_01_01/source;C:/ti/simplelink_cc13x0_sdk_4_10_01_01/kernel/tirtos/packages;" xdc.tools.configuro -o configPkg -t gnu.targets.arm.M3 -p ti.platforms.simplelink:CC1310F128 -r release -c "C:/ti/ccs1020/ccs/tools/compiler/gcc-arm-none-eabi-7-2017-q4-major-win32" --compileOptions " -DDeviceFamily_CC13X0 " "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

configPkg/linker.cmd: build-1315429359 ../release.cfg
configPkg/compiler.opt: build-1315429359
configPkg/: build-1315429359


