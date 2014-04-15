from construct import Struct, UBInt16, BitStruct, \
    Flag, Padding, Enum, Byte, UBInt32, Bytes, Rename, OptionalGreedyRange, Debugger, Adapter, Switch, Pass, Field

MESSAGE_TYPE_DISCOVER = '\x01'
MESSAGE_TYPE_OFFER = '\x02'
MESSAGE_TYPE_REQUEST = '\x03'
MESSAGE_TYPE_DECLINE = '\x04'
MESSAGE_TYPE_ACK = '\x05'


dhcp_option = Struct(
    "dhcp_option",
    Enum(Byte("code"),
         Pad=0,
         Subnet_Mask=1,
         Time_Offset=2,
         Router=3,
         Time_Server=4,
         Name_Server=5,
         Domain_Name_Server=6,
         Log_Server=7,
         Quote_Server=8,
         LPR_Server=9,
         Impress_Server=10,
         Resource_Location_Server=11,
         Host_Name=12,
         Boot_File_Size=13,
         Merit_Dump_File=14,
         Domain_Name=15,
         Swap_Server=16,
         Root_Path=17,
         Extensions_Path=18,
         IP_Forwarding_enabledisable=19,
         Nonlocal_Source_Routing_enabledisable=20,
         Policy_Filter=21,
         Maximum_Datagram_Reassembly_Size=22,
         Default_IP_TTL=23,
         Path_MTU_Aging_Timeout=24,
         Path_MTU_Plateau_Table=25,
         Interface_MTU=26,
         All_Subnets_are_Local=27,
         Broadcast_Address=28,
         Perform_Mask_Discovery=29,
         Mask_supplier=30,
         Perform_router_discovery=31,
         Router_solicitation_address=32,
         Static_routing_table=33,
         Trailer_encapsulation=34,
         ARP_cache_timeout=35,
         Ethernet_encapsulation=36,
         Default_TCP_TTL=37,
         TCP_keepalive_interval=38,
         TCP_keepalive_garbage=39,
         Network_Information_Service_domain=40,
         Network_Information_Servers=41,
         NTP_servers=42,
         Vendor_specific_information=43,
         NetBIOS_over_TCPIP_name_server=44,
         NetBIOS_over_TCPIP_Datagram_Distribution_Server=45,
         NetBIOS_over_TCPIP_Node_Type=46,
         NetBIOS_over_TCPIP_Scope=47,
         X_Window_System_Font_Server=48,
         X_Window_System_Display_Manager=49,
         Requested_IP_Address=50,
         IP_address_lease_time=51,
         Option_overload=52,
         DHCP_message_type=53,
         Server_identifier=54,
         Parameter_request_list=55,
         Message=56,
         Maximum_DHCP_message_size=57,
         Renew_time_value=58,
         Rebinding_time_value=59,
         Class_identifier=60,
         Client_identifier=61,
         NetWareIP_Domain_Name=62,
         NetWareIP_information=63,
         Network_Information_Service_Domain=64,
         Network_Information_Service_Servers=65,
         TFTP_server_name=66,
         Bootfile_name=67,
         Mobile_IP_Home_Agent=68,
         Simple_Mail_Transport_Protocol_Server=69,
         Post_Office_Protocol_Server=70,
         Network_News_Transport_Protocol_Server=71,
         Default_World_Wide_Web_Server=72,
         Default_Finger_Server=73,
         Default_Internet_Relay_Chat_Server=74,
         StreetTalk_Server=75,
         StreetTalk_Directory_Assistance_Server=76,
         User_Class_Information=77,
         SLP_Directory_Agent=78,
         SLP_Service_Scope=79,
         Rapid_Commit=80,
         Fully_Qualified_Domain_Name=81,
         Relay_Agent_Information=82,
         Internet_Storage_Name_Service=83,
         NDS_servers=85,
         NDS_tree_name=86,
         NDS_context=87,
         BCMCS_Controller_Domain_Name_list=88,
         BCMCS_Controller_IPv4_address_list=89,
         Authentication=90,
         Client_last_transaction_time=91,
         Associated_ip=92,
         Client_System_Architecture_Type=93,
         Client_Network_Interface_Identifier=94,
         Lightweight_Directory_Access_Protocol=95,
         Client_Machine_Identifier=97,
         Open_Group_User_Authentication=98,
         Autonomous_System_Number=109,
         NetInfo_Parent_Server_Address=112,
         NetInfo_Parent_Server_Tag=113,
         URL=114,
         Auto_Configure=116,
         Name_Service_Search=117,
         Subnet_Selection=118,
         DNS_domain_search_list=119,
         SIP_Servers_DHCP_Option=120,
         Classless_Static_Route_Option=121,
         CableLabs_Client_Configuration=122,
         GeoConf=123,
         End=255,
    ),
    Switch("value", lambda ctx: ctx.code,
           {
               # codes without any value
               "Pad": Pass,
           },
           # codes followed by length and value fields
           default=Struct("value",
                          Byte("length"),
                          Field("data", lambda ctx: ctx.length),
           )
    )
)


class IpAddressAdapter(Adapter):
    def _encode(self, obj, context):
        if '.' in obj:
            return ''.join(chr(int(b)) for b in obj.split("."))
        return obj

    def _decode(self, obj, context):
        if bytes is str:
            return ".".join(str(ord(b)) for b in obj)
        else:
            return ".".join("%d" % (b,) for b in obj)

class DHCPClientMacAdapter(Adapter):
    def _encode(self, obj, context):
        obj = ''.join([str(chr(int(i, 16))) for i in obj.split(':')])
        return obj + '\x00' * (16 - context.hardware_address_length)

    def _decode(self, obj, context):
        return ":".join('%02X' % ord(i) for i in obj[:context.hardware_address_length])

def IpAddress(name):
    return IpAddressAdapter(Bytes(name, 4))


dhcp_header = Struct(
    "dhcp_header",
    Enum(Byte("opcode"),
         BootRequest=1,
         BootReply=2,
    ),
    Enum(Byte("hardware_type"),
         Ethernet=1,
         Experimental_Ethernet=2,
         ProNET_Token_Ring=4,
         Chaos=5,
         IEEE_802=6,
         ARCNET=7,
         Hyperchannel=8,
         Lanstar=9,
    ),
    Byte("hardware_address_length"),
    Byte("hop_count"),
    UBInt32("transaction_id"),
    UBInt16("elapsed_time"),
    BitStruct("flags",
              Flag("boardcast"),
              Padding(15),
    ),
    IpAddress("client_addr"),
    IpAddress("your_addr"),
    IpAddress("server_addr"),
    IpAddress("gateway_addr"),
    DHCPClientMacAdapter(
        Bytes("client_hardware_addr", 16)),
    Bytes("server_host_name", 64),
    Bytes("boot_filename", 128),
    # BOOTP/DHCP options
    # "The first four bytes contain the (decimal) values 99, 130, 83 and 99"
    # Const(Bytes("magic", 4), six.b("\x63\x82\x53\x63")),
    Bytes("magic", 4),
    Rename("options", OptionalGreedyRange(dhcp_option)),
    allow_overwrite=True
)

def get_message_type(request_packet):
    for option in request_packet.options:
        if not option.code == 'DHCP_message_type':
            continue
        return option.value.data
# if __name__ == "__main__":
#     cap = unhexlify(six.b("0bcc003500280689"))
#     obj = udp_header.parse(cap)
#     print (obj)
#     print (repr(udp_header.build(obj)))

