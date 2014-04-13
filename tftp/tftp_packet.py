from construct import Struct, UBInt16, CString, Enum, Switch, Embed, OptionalGreedyRange, Pass

tftp_header = Struct(
    'tftp_header',
    Enum(
        UBInt16('opcode'),
        READ_REQ=1,
        WRITE_REQ=2,
        DATA_PACKET=3,
        ACK=4,
        ERROR=5,
        OACK=6,
    ),
    Switch(None,
           lambda ctx: ctx.opcode,
           {
               'READ_REQ':
                   Embed(Struct(None,
                                CString('source_file'),
                                CString('type'))),
               'WRITE_REQ':
                   Embed(Struct(None,
                                CString('dest_file'),
                                CString('type'))),
               'DATA_PACKET':
                   Embed(Struct(None,
                                UBInt16('block'),
                                # String('data', 512) # will just append the text
                   )),
               'ACK':
                   Embed(Struct(None,
                                UBInt16('block'))),
               'ERROR':
                   Embed(Struct(None,
                                UBInt16('error_code'),
                                CString('error_message'))),

               'OACK': Embed(Struct(None)), # tried using Pass, it yelled at me.
           }),
    OptionalGreedyRange(
        Struct('options',
               CString('name'),
               CString('value'))
    )
)