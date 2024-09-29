typedef struct {
  CHAR16    ISCSIIsId[13];
  CHAR16    ISCSIInitiatorIpAddress[16];
  CHAR16    ISCSIInitiatorNetmask[16];
  CHAR16    ISCSIInitiatorGateway[16];
  CHAR16    ISCSITargetName[224];
  CHAR16    ISCSITargetIpAddress[255];
  CHAR16    ISCSILun[21];
  CHAR16    ISCSIChapUsername[127];
  CHAR16    ISCSIChapSecret[17];
  CHAR16    ISCSIReverseChapUsername[127];
  CHAR16    ISCSIReverseChapSecret[17];
} KEYWORD_STR;

typedef struct _ISCSI_CONFIG_IFR_NVDATA {
  CHAR16         InitiatorName[224];
  CHAR16         AttemptName[12];
  UINT8          Enabled;
  UINT8          IpMode;

  UINT8          ConnectRetryCount;
  UINT8          Padding1;
  UINT16         ConnectTimeout;

  UINT8          InitiatorInfoFromDhcp;
  UINT8          TargetInfoFromDhcp;
  CHAR16         LocalIp[16];
  CHAR16         SubnetMask[16];
  CHAR16         Gateway[16];

  CHAR16         TargetName[224];
  CHAR16         TargetIp[255];
  UINT16         TargetPort;
  CHAR16         BootLun[21];

  UINT8          AuthenticationType;

  UINT8          CHAPType;
  CHAR16         CHAPName[127];
  CHAR16         CHAPSecret[17];
  CHAR16         ReverseCHAPName[127];
  CHAR16         ReverseCHAPSecret[17];

  BOOLEAN        MutualRequired;
  UINT8          Padding2;
  CHAR16         KerberosUserName[96];
  CHAR16         KerberosUserSecret[17];
  CHAR16         KerberosKDCName[96];
  CHAR16         KerberosKDCRealm[96];
  CHAR16         KerberosKDCIp[40];
  UINT16         KerberosKDCPort;

  UINT8          DynamicOrderedList[0x08];
  UINT8          DeleteAttemptList[0x08];
  UINT8          AddAttemptList[0x08];
  CHAR16         IsId[13];




  CHAR16         ISCSIMacAddr[96];
  CHAR16         ISCSIAttemptOrder[96];
  CHAR16         ISCSIAddAttemptList[96];
  CHAR16         ISCSIDeleteAttemptList[96];
  CHAR16         ISCSIDisplayAttemptList[96];
  CHAR16         ISCSIAttemptName[96];
  UINT8          ISCSIBootEnableList[0x08];
  UINT8          ISCSIIpAddressTypeList[0x08];
  UINT8          ISCSIConnectRetry[0x08];
  UINT16         ISCSIConnectTimeout[0x08];
  UINT8          ISCSIInitiatorInfoViaDHCP[0x08];
  UINT8          ISCSITargetInfoViaDHCP[0x08];
  UINT16         ISCSITargetTcpPort[0x08];
  UINT8          ISCSIAuthenticationMethod[0x08];
  UINT8          ISCSIChapType[0x08];
  KEYWORD_STR    Keyword[0x08];
} ISCSI_CONFIG_IFR_NVDATA;

formset
  guid     = { 0x4b47d616, 0xa8d6, 0x4552, { 0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9 } },
  title    = STRING_TOKEN(0x0002),
  help     = STRING_TOKEN(0x0003),

  varstore ISCSI_CONFIG_IFR_NVDATA,
    varid = 0x6666,
    name = ISCSI_CONFIG_IFR_NVDATA,
    guid = { 0x4b47d616, 0xa8d6, 0x4552, { 0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9 } };
endformset;