typedef struct {
  UINT32  Revision;
  UINT8   UserPassword[48];
  UINT8   AdminPassword[48];
  UINT8   Access;
  UINT8   Numlock;
  UINT8   Ps2PortSwap;
  UINT8         TpmEnable;
  UINT8         TpmState;
  UINT8         MorState;
  UINT8  XmlCliReserved[7];
  UINT8  EnforcedPasswd;
  UINT8   ValidationBreakpointType;
  UINT16   bsdBreakpoint;
  UINT8   WakeOnLanS5;
  UINT8   BootNetwork;
  UINT8   VideoSelect;
  UINT8   UefiOptimizedBootToggle;
  UINT8    FanPwmOffset;
  UINT8   ApplicationProfile;
  UINT8   WakeOnLanSupport;
  UINT8   LomDisableByGpio;
  UINT8   FpkPortConfig[4];
  UINT8   WakeOnRTCS4S5;
  UINT8   RTCWakeupTimeHour;
  UINT8   RTCWakeupTimeMinute;
  UINT8   RTCWakeupTimeSecond;
  UINT8   PcieClockGatingDisabled ;
  UINT8   PcieDmiAspm;
  UINT8   PcieSBDE;
  UINT8   GbePciePortNum;
  UINT8   PciePortConfig1;
  UINT8   PciePortConfig2;
  UINT8   PciePortConfig3;
  UINT8   PciePortConfig4;
  UINT8   PciePortConfig5;
  UINT8 GbeEnabled;
  UINT8 PchStepping;
  UINT8   XhciWakeOnUsbEnabled;
  UINT8   SystemErrorEn;
  UINT8   RasLogLevel;
  UINT8   PoisonEn;
  UINT8   ViralEn;
  UINT8   CloakDevHideRegistersOs;
  UINT8   ClearViralStatus;
  UINT8   CeCloakingEn;
  UINT8   UcnaCloakingEn;
  UINT8   UboxToPcuMcaEn;
  UINT8   FatalErrSpinLoopEn;

  UINT8   EmcaEn;
  UINT8   ElogIgnOptin;
  UINT8   EmcaCsmiEn;
  UINT16  EmcaCsmiThreshold;
  UINT8   CsmiDynamicDisable;
  UINT16  CsmiDynamicThreshold;
  UINT8   EmcaMsmiEn;
  UINT8   ElogCorrErrEn;
  UINT8   ElogMemErrEn;
  UINT8   ElogProcErrEn;
  UINT8   EmcaSetFwUpdate;
  UINT8   LmceEn;
  UINT8   OscEn;
  UINT8   UboxErrorMask;

  UINT8   WheaSupportEn;
  UINT8   WheaLogMemoryEn;
  UINT8   WheaLogProcEn;

  UINT8   WheaLogPciEn;
  UINT8   WheaErrorInjSupportEn;
  UINT8   McaBankErrInjEn;
  UINT8   WheaErrInjEn;
  UINT8   WheaPcieErrInjEn;
  UINT8   SgxErrorInjEn;
  UINT8   PcieErrInjActionTable;

  UINT8   CorrMemErrEn;
  UINT8   SpareIntSelect;
  UINT8   PfdEn;
  UINT8   FnvErrorEn;
  UINT8   FnvErrorLowPrioritySignal;
  UINT8   FnvErrorHighPrioritySignal;
  UINT8   NgnAddressRangeScrub;
  UINT8   NgnHostAlertDpa;
  UINT8   NgnHostAlertPatrolScrubUNC;
  UINT8   ReportAlertSPA;
  UINT8   DcpmmUncPoison;
  UINT8   DdrtInternalAlertEn;

  UINT8   IioErrorEn;
  UINT8   OsNativeAerSupport;
  UINT8   IoMcaEn;
  UINT8   IioSev1Pcc;
  UINT8   IioErrRegistersClearEn;
  UINT8   IioErrorPin0En;
  UINT8   IioErrorPin1En;
  UINT8   IioErrorPin2En;
  UINT8   LerEn;
  UINT8   DisableMAerrorLoggingDueToLER;
  UINT8   EdpcEn;
  UINT8   EdpcInterrupt;
  UINT8   EdpcErrCorMsg;
  UINT8   PciePtlpEgrBlk;

  UINT8   IioIrpErrorEn;
  UINT8   IioMiscErrorEn;
  UINT8   IioVtdErrorEn;
  UINT8   IioDmaErrorEn;
  UINT8   IioDmiErrorEn;
  UINT8   IioPcieAerSpecCompEn;
  UINT8   ItcOtcCaMaEnable;
  UINT8   PcieErrEn;
  UINT8   PcieCorrErrEn;
  UINT8   PcieUncorrErrEn;
  UINT8   PcieFatalErrEn;
  UINT8   PcieCorErrCntr;
  UINT32  PcieCorErrThres;
  UINT8   PcieCorErrLimitEn;
  UINT32  PcieCorErrLimit;
  UINT8   PcieAerCorrErrEn;
  UINT8   PcieAerAdNfatErrEn;
  UINT8   PcieAerNfatErrEn;
  UINT8   PcieAerFatErrEn;
  UINT8   PcieAerEcrcEn;
  UINT8   PcieAerSurpriseLinkDownEn;
  UINT8   PcieAerUreEn;
  UINT8   McaSpinLoop;
  UINT8   IioOOBMode;
  UINT8   OobRasSupport;
  UINT8   RasPerformance;
  UINT8   McBankWarmBootClearError;
  UINT8   ShutdownSuppression;

  UINT8   PropagateSerr;
  UINT8   PropagatePerr;
  UINT8   FspMode;
  UINT8   serialDebugMsgLvl;
  UINT8   serialDebugTrace;
  UINT8   serialDebugMsgLvlTrainResults;
  UINT8   ResetOnMemMapChange;
  UINT8   ForceSetup;
  UINT8   BiosGuardEnabled;
  UINT8   BiosGuardPlatformSupported;
  UINT8   EnableAntiFlashWearout;
  UINT8   AntiFlashWearoutSupported;
  UINT8   DfxPopulateBGDirectory;

  UINT8   Use1GPageTable;
  UINT8   FastBoot;
  UINT8   ReserveMem;
  UINT64  ReserveStartAddr;

  UINT8  TagecMem;

  UINT8   UsbMassDevNum;
  UINT8   UsbLegacySupport;
  UINT8   UsbEmul6064;
  UINT8   UsbMassResetDelay;
  UINT8   UsbNonBoot;
  UINT8   UsbStackSupport;


  UINT8   ConsoleRedirection;
  UINT8   FlowControl;
  UINT64  BaudRate;
  UINT8   TerminalType;
  UINT8   LegacyOsRedirection;
  UINT8   TerminalResolution;
  UINT8   DataBits;
  UINT8   Parity;
  UINT8   StopBits;


  UINT8   SystemPageSize;
  UINT8   ARIEnable;
  UINT8   SRIOVEnable;
  UINT8   MRIOVEnable;

  UINT8  LegacyPxeRom;
  UINT8  EfiNetworkSupport;
  UINT32        SerialBaudRate;

  UINT8         BootAllOptions;
  UINT8         SetShellFirst;
  UINT8         ShellEntryTime;
  UINT8         ShellEntryMapPrint;

  UINT8  PlatformOCSupport;
  UINT8  FilterPll;
  UINT8  OverclockingSupport;

  UINT8  CoreMaxOcRatio;
  UINT8  CoreVoltageMode;
  UINT16 CoreVoltageOverride;
  UINT16 CoreVoltageOffset;
  UINT8  CoreVoltageOffsetPrefix;
  UINT16 CoreExtraTurboVoltage;

  UINT8  MemoryVoltage;

  UINT8   ClrMaxOcRatio;
  UINT8   ClrVoltageMode;
  UINT16  ClrVoltageOverride;
  UINT16  ClrVoltageOffset;
  UINT8   ClrVoltageOffsetPrefix;
  UINT16  ClrExtraTurboVoltage;

  UINT8   RingMaxOcRatio;
  UINT8   RingVoltageMode;
  UINT16  RingVoltageOverride;
  UINT16  RingVoltageOffset;
  UINT8   RingVoltageOffsetPrefix;
  UINT16  RingExtraTurboVoltage;

  UINT16   UncoreVoltageOffset;
  UINT8    UncoreVoltageOffsetPrefix;
  UINT16   IoaVoltageOffset;
  UINT8    IoaVoltageOffsetPrefix;
  UINT16   IodVoltageOffset;
  UINT8    IodVoltageOffsetPrefix;

  UINT8   SvidEnable;
  UINT16  SvidVoltageOverride;
  UINT8   FivrFaultsEnable;
  UINT8   FivrEfficiencyEnable;
  UINT16  C01MemoryVoltage;
  UINT16  C23MemoryVoltage;

  UINT16  CpuVccInVoltage;

  UINT8   VccIoVoltage;

  UINT16  VariablePlatId;

  UINT8 DfxAdvDebugJumper;
  UINT8 DfxPpvEnabled;
  UINT8 IerrResetEnabled;

  UINT8   StorageOpROMSuppression;

  UINT8   DfxEmuBiosSkipS3MAccess;

  UINT64  ExpectedBer;
  UINT32  Gen12TimeWindow;
  UINT8   Gen345TimeWindow;
  UINT8   Gen12ErrorThreshold;
  UINT8   Gen345ErrorThreshold;
  UINT8   Gen345ReEqualization;
  UINT8   Gen2LinkDegradation;
  UINT8   Gen3LinkDegradation;
  UINT8   Gen4LinkDegradation;
  UINT8   Gen5LinkDegradation;

  UINT8   CpuCrashLogFeature;
  UINT8   CoreCrashLogDisable;
  UINT8   TorCrashLogDisable;
  UINT8   UncoreCrashLogDisable;
  UINT8   McerrTriggerDisable;
  UINT8   CpuCrashLogClear;
  UINT8   CpuCrashLogReArm;
  UINT8   PchCrashLogFeature;
  UINT8   PchCrashLogOnHostReset;
  UINT8   PchCrashLogClear;
  UINT8   PchCrashLogReArm;

  UINT8   DwrEnable;
  UINT8   DwrStall;
  UINT8   DwrBmcRootPort;

  UINT8   KtiFirstCeLatchEn;
  UINT8   PatrolScrubErrorReporting;
  UINT8   KcsAccessPolicy;

  UINT8   PlatformDeepS5;
  UINT8   DeepS5DelayTime;

  UINT8   EnableClockSpreadSpec;

  UINT8   Avx2RatioOffset;
  UINT8   Avx3RatioOffset;
  UINT8   TjMaxOverride;
  UINT8   BclkAdaptiveVoltage;
  UINT8   CoreVfConfigScope;
  UINT8   PerCoreRatioOverride;
  UINT8   PerCoreRatio[60];
  UINT16  PerCoreVoltageOffset[60];
  UINT8   PerCoreVoltageOffsetPrefix[60];
  UINT8   PerCoreMaxRatio[60];
  UINT8   NumCores;
  UINT8   ActiveCoreCount;

  UINT8   CorePllVoltageOffset;
  UINT8   RingPllVoltageOffset;
  UINT8   McPllVoltageOffset;
  UINT16  VccCfnVoltageOverride;
  UINT16  VccIoVoltageOverride;
  UINT16  VccMdfiaVoltageOverride;
  UINT16  VccMdfiVoltageOverride;
  UINT16  VccDdrdVoltageOverride;
  UINT16  VccDdraVoltageOverride;

  UINT8   TmulRatioOffset;
  UINT8   EnableIMR2Support;

  UINT8   BmcRemoteSetup;
  UINT8   FanControllerEnable;
  UINT8   ForceFullSockets;

  UINT8  TBTEnable;
  UINT8  PcieTunnelingOverTBT;
  UINT8  WakeCapabilityOverTBT;
  UINT8  RunGotoSx;
  UINT8  ExtraBusForRP;
  UINT32 MemoryBelow4GBForHotPlugRP;
  UINT32 MemoryAbove4GBForHotPlugRP;
  UINT8  ReservedforTbt[20];


  UINT8  CxlMefnEn;
  UINT8  CxlMefnEnWithPrimaryMailboxOnly;
  UINT8  FanSpeedProfile;
  UINT8  ElogEn;
  UINT8  OobSruSupport;
  UINT8  ElogMultiError;
  UINT8  CxlMemIsolationEn;
  UINT8  CxlMemIsolationLnkDnEn;
  UINT8  CxlMemTTOEn;
  UINT8  CxlMemTTOVal;

  UINT8  OstuSupport;


  UINT8  PtuSupport;
  UINT8  PtuHardwareChangeOverride;

  UINT8  CpuSmmSyncMode;
  UINT8  Srat;
  UINT8  SratCpuHotPlug;
  UINT8  SerialDevice;
  UINT8  EspiDisableMode;
  UINT8  ClockMode;
  UINT8   NmiInterrupt;
  UINT8  ReservedForNewVariables[125];
} SYSTEM_CONFIGURATION;

formset
  guid     = { 0x4b47d616, 0xa8d6, 0x4552, { 0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9 } },
  title    = STRING_TOKEN(0x0002),
  help     = STRING_TOKEN(0x0003),

  disableif TRUE;
    numeric varid     = SYSTEM_CONFIGURATION.VariablePlatId,
    prompt      = STRING_TOKEN(0x0154),
    help        = STRING_TOKEN(0x0155),
      minimum = 0,
      maximum = 0x1,
      step    = 1,
    endnumeric;
  endif;
endformset;