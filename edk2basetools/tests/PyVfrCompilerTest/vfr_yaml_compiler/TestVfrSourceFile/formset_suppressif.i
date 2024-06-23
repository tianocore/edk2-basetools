typedef struct {
  UINT8   FakeItem;
} FAKE_VARSTORE;


typedef struct {
  UINT8     Configure;
  UINT8     DhcpEnable;
  CHAR16    StationAddress[16];
  CHAR16    SubnetMask[16];
  CHAR16    GatewayAddress[16];
  CHAR16    DnsAddress[255];
} IP4_CONFIG2_IFR_NVDATA;

formset
  guid     = { 0x4b47d616, 0xa8d6, 0x4552, { 0x9d, 0x44, 0xcc, 0xad, 0x2e, 0xf, 0x4c, 0xf9 } },
  title    = STRING_TOKEN(0x0002),
  help     = STRING_TOKEN(0x0003),

  suppressif TRUE;
     text
         help  = STRING_TOKEN(0x0003),
         text  = STRING_TOKEN(0x0003),
         flags = INTERACTIVE,
         key   = 0x1117;
  endif;
endformset;