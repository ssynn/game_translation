import construct
from scr.public_function import *
# import scr.lmdis as lm

if __name__ == "__main__":
    # print(SNL._split_line('えっ！？いや、そんなつもりは‥‥ないけど。'))
    # SNL.create_dict()

    # MED.unpack()
    # MED.extract_med()
    # MED.fix_dict()
    # MED.output()
    # MED.repack('output')
    # MED.fix_exe('EXSTIAA.EXE')

    # ANIM.extract()
    # ANIM.output()

    # Lilim.extract_for_hook_aos2()
    # Lilim.fix_dixt()
    # Lilim.output_hook_dict()

    # PAC.extract_srp()
    # PAC.output_srp()
    # PAC.repack_pac()

    # RPM.unpack_arc()
    # RPM.repack_arc()
    # print(RPM.formate('　なあ、<WinRubi 福永,ふくなが><WinRubi 裕人,ゆうと>よ！！」'))

    # NEKOSDK.extract_pak_txt()
    # NEKOSDK.output()

    # SILKY.extract()
    # SILKY.output()

    # YU_RIS.extract_ybn()
    # YU_RIS.output_ybn(encrypt=1)
    
    # XFL.extract_gsc()
    # XFL.output_gsc()

    LIVEMAKER.extract()

    # TDecorate = construct.Struct(
    #     "count" / construct.Int32ul,
    #     "unk2" / construct.Int32ul,
    #     "unk3" / construct.Int32ul,
    #     "unk4" / construct.Int32ul,
    #     "unk5" / construct.Byte,
    #     "unk6" / construct.Byte,
    #     "unk7" / construct.IfThenElse(construct.this._._.version < 100, construct.Byte, construct.Int32ul),
    #     "unk8" / construct.PascalString(construct.Int32ul, "cp932"),
    #     "unk9" / construct.PascalString(construct.Int32ul, "cp932"),
    #     "unk10" / construct.If(construct.this._._.version >= 100, construct.Int32ul,),
    #     "unk11" / construct.If(construct.this._._.version >= 100, construct.Int32ul,),
    # )

    # TWdCondition = construct.Struct(
    #     "count" / construct.Int32ul, 
    #     "target" / construct.PascalString(construct.Int32ul, "cp932"),
    # )

    # TWdCondition = construct.Struct(
    #     "count" / construct.Int32ul, 
    #     "target" / construct.PascalString(construct.Int32ul, "cp932"),
    # )

    # TWdLink = construct.Struct(
    #     "count" / construct.Int32ul,
    #     "event" / construct.PascalString(construct.Int32ul, "cp932"),
    #     "unk3" / construct.PascalString(construct.Int32ul, "cp932"),
    # )

    # TpWord = construct.Struct(
    #     "signature" / construct.Const(b"TpWord"),
    #     "version" / construct.Bytes(3),
    #     "decorators" / construct.PrefixedArray(construct.Int32ul, TDecorate),
    #     "conditions" / construct.PrefixedArray(construct.Int32ul, TWdCondition),
    #     "links" / construct.PrefixedArray(construct.Int32ul, TWdLink),
    #     # "body" / construct.PrefixedArray(construct.Int32ul, construct.Select(*select_subcons))
    # )

    
    # # data = b'\x54\x70\x57\x6F\x72\x64\x31\x30\x35\x00\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x06\x00\x00\x00\x00'
    # a  = construct.PascalString(construct.Int32ul, "cp932")
    
    # print(a.parse(b'\x06\x00\x00\x00\x81\x42\x81\x75\x81\x75'))


    pass
