typedef struct {
  UINT32  Revision;

  UINT8   PchBiosLock;
  UINT8   UnlockGpioPads;

  UINT8   DeepSxMode;

  UINT32  EnableTimedGpio0;
  UINT32  EnableTimedGpio1;

  UINT32  PmcDbgMsgEn;

  UINT8   PchGpioIrqRoute;

  UINT8   StateAfterG3;
  UINT8   LastStateAfterType8Gr;

  UINT8   IchPort80Route;
  UINT8   EnhancePort8xhDecoding;

  UINT8   PchAdrEn;
  UINT8   PchAdrTimerEn;
  UINT8   PchAdrMultiplierVal;
  UINT8   PchAdrTimer1Val;
  UINT8   PchAdrMultiplier1Val;
  UINT8   PchAdrTimer2Val;
  UINT8   PchAdrMultiplier2Val;
  UINT8   AdrHostPartitionReset;

  UINT8   PchIoApic24119Entries;

  UINT8   PchEspiLgmrEnable;

  UINT8   SmbusSpdWriteDisable;
  UINT8   FprrEnable;

  UINT8   FirmwareConfiguration;

  UINT8   GlobalResetMasksOverride;
  UINT32  GlobalResetEventMask;
  UINT32  GlobalResetTriggerMask;
  UINT8   GlobalResetLockEnable;

  UINT8   ExtendedBiosDecodeRangeEnable;

  UINT8   PchWOLFastSupport;

  UINT8   GlobalSmiEnable;
  UINT8   BiosInterfaceUnlock;
  UINT8   TestFlashLockDown;
  UINT8   SvAdvPchSlpS3Stretch;
  UINT8   SvAdvPchSlpS4tretch;
  UINT8   TestLatchEventsC10Exit;
  UINT8   TestSlpsxStrPolLock;
  UINT8   GlobalSmiLock;

  UINT8   PchAllUnLock;
  UINT8   IblP2sbDevReveal;
  UINT8   IblPmcDevReveal;
  UINT8   IblUartDevReveal;
  UINT8   ReservedForNewVariables[128];
} PCH_SETUP;

formset
  guid     = { 0x4b47d616, 0xa8d6, 0x4552, { 0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9 } },
  title    = STRING_TOKEN(0x0002),
  help     = STRING_TOKEN(0x0003),

  efivarstore PCH_SETUP,
    varid = 0x0001,
    attribute = 0x0007,
    name = PchSetup,
    guid = { 0x4570b7f1, 0xade8, 0x4943, { 0x8d, 0xc3, 0x40, 0x64, 0x72, 0x84, 0x23, 0x84 } };

endformset;