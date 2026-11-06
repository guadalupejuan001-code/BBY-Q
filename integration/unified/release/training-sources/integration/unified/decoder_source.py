"""Compile exact Pauli readout for the preserved V3 encoder, not its labels.

For each historical CNOT-chain component, U Z_i U† is Z_(i-1) Z_i
(Z_0 at the boundary), and U X_i U† is the X suffix. Conjugating these
observables through the learned final RY gates recovers the encoded input's
Bloch coordinates. Every expectation executes on the actual native state.
"""
import itertools
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def pauli(axis,sites):
    lines=['fset f21 0']
    for chosen in itertools.product(('X','Z'),repeat=len(sites)):
        if len(sites)==1 and chosen[0]=='Z':
            lines+=['mov r0 r8',f'add r0 {sites[0]}','mul r0 8','add r0 8140000000000310000','fload f0 $r0']
        else:lines+=['fexpect f0 '+' '.join(f'{kind}:$r{4+site}' for site,kind in zip(sites,chosen))]
        sign=1
        for site,kind in zip(sites,chosen):
            sine=(axis=='Z' and kind=='X') or (axis=='X' and kind=='Z')
            lines.append(f'fmul f0 f{8+2*site+int(sine)}')
            if axis=='X' and kind=='Z':sign*=-1
        if sign<0:lines.append('fmul f0 -1')
        lines.append('fadd f21 f0')
    return '\n'.join(lines)+'\n'

def angle():
    lines='''label u2_angle
fmov f6 f0
fmov f7 f1
fmov f2 f0
fmul f2 f2
fsqrt f2 f2
fmov f3 f1
fmul f3 f3
fsqrt f3 f3
set r10 0
fcmp f3 f2
jle u2_angle_cos_axis
set r10 1
fmov f4 f2
fdiv f4 f3
jmp u2_angle_ratio
label u2_angle_cos_axis
fcmp f2 0.000000000001
jle u2_angle_undefined
fmov f4 f3
fdiv f4 f2
label u2_angle_ratio
set r11 0
fcmp f4 0.41421356237309503
jle u2_angle_series
set r11 1
fmov f2 f4
fadd f2 1
fsub f4 1
fdiv f4 f2
label u2_angle_series
fmov f5 f4
fmul f5 f5
fset f0 0.058823529411764705
'''
    for k in range(7,-1,-1):lines+=f'fmul f0 f5\nfadd f0 {(-1.)**k/(2*k+1)!r}\n'
    lines+='''fmul f0 f4
cmp r11 1
jne u2_angle_unswap
fadd f0 0.7853981633974483
label u2_angle_unswap
cmp r10 1
jne u2_angle_quadrant
fset f2 1.5707963267948966
fsub f2 f0
fmov f0 f2
label u2_angle_quadrant
fcmp f6 0
jge u2_angle_sign
fset f2 3.141592653589793
fsub f2 f0
fmov f0 f2
label u2_angle_sign
fcmp f7 0
jge u2_angle_done
fmul f0 -1
label u2_angle_done
ret
label u2_angle_undefined
fset f0 0
ret
'''
    return lines

def decoder():
    lines='''label u2_project
fload f20 8140000000000000112
fstore @B+64 f20
fmov f0 f20
fdiv f0 10
fstore @IN f0
'''
    for q in range(4):
        lines+=f'fstore @IN+{8*(1+4*q)} 0\nfstore @IN+{8*(2+4*q)} 0\nfstore @IN+{8*(3+4*q)} 3.141592653589793\nfstore @IN+{8*(4+4*q)} -3.141592653589793\n'
    lines+='load64 r0 8140000000000000280\ncmp r0 1\nje u2_decode_ablated\nset r8 0\nlabel u2_decode_block\n'
    for q in range(4):
        lines+=f'mov r{4+q} r8\nadd r{4+q} {5000+q}\nmov r0 r8\nadd r0 {q}\nmul r0 8\nadd r0 8140000000000100000\nfload f0 $r0\nfcos f{8+2*q} f0\nfsin f{9+2*q} f0\n'
    for q in range(4):
        # Keep correlation scratch outside IN: its 17th feature occupies
        # B+256. Sharing that address silently corrupts the last channel's
        # running extrema even though each recovered phase is correct.
        lines+=pauli('Z',[q] if q==0 else [q-1,q])+f'fstore @B+{320+8*q} f21\n'
        lines+=pauli('X',list(range(q,4)))+f'fmov f1 f21\nfload f0 @B+{320+8*q}\ncall u2_angle\n'
        lines+=f'mov r0 r8\nadd r0 {q}\nmul r0 8\nadd r0 @PHASE\nfstore $r0 f0\n'
        mean=8*(1+4*q);square=8*(2+4*q);low=8*(3+4*q);high=8*(4+4*q)
        lines+=f'fload f1 @IN+{mean}\nfadd f1 f0\nfstore @IN+{mean} f1\nfmov f1 f0\nfmul f1 f1\nfload f2 @IN+{square}\nfadd f2 f1\nfstore @IN+{square} f2\n'
        lines+=f'fload f1 @IN+{low}\nfcmp f0 f1\njge u2_min_ready_{q}\nfstore @IN+{low} f0\nlabel u2_min_ready_{q}\nfload f1 @IN+{high}\nfcmp f0 f1\njle u2_max_ready_{q}\nfstore @IN+{high} f0\nlabel u2_max_ready_{q}\n'
    lines+='add r8 4\ncmp r8 1000\njlt u2_decode_block\n'
    for q in range(4):
        mean=8*(1+4*q);square=8*(2+4*q);low=8*(3+4*q);high=8*(4+4*q)
        lines+=f'fload f0 @IN+{mean}\nfdiv f0 250\nfload f1 @IN+{square}\nfdiv f1 250\nfmov f2 f0\nfmul f2 f2\nfsub f1 f2\nfmax f1 0\nfsqrt f1 f1\n'
        lines+=f'fload f2 @IN+{low}\nfload f3 @IN+{high}\nfmov f4 f3\nfsub f4 f2\nfdiv f4 2\nfadd f2 f3\nfdiv f2 2\nfsub f0 f2\n'
        # Midrange, mean-minus-midrange, standard deviation and half-range.
        lines+=f'fstore @IN+{mean} f2\nfstore @IN+{square} f0\nfstore @IN+{low} f1\nfstore @IN+{high} f4\n'
    lines+='ret\nlabel u2_decode_ablated\n'
    for i in range(1,17):lines+=f'fstore @IN+{8*i} 0\n'
    return lines+'ret\n'+angle()

def forward():return '''label u2_forward
call u2_normalize
fload f20 @B+64
fload f0 @SKIP
fmul f20 f0
set r2 0
label u2_linear_feature
mov r0 r2
mul r0 8
add r0 @P
fload f0 $r0
mov r0 r2
mul r0 8
add r0 @NORMAL
fload f1 $r0
fmul f0 f1
fadd f20 f0
add r2 1
cmp r2 @NF
jlt u2_linear_feature
fload f0 @OUTBIAS
fadd f20 f0
fset f0 1
fcmp f20 -25
jle u2_saturated
fcmp f20 25
jlt u2_clip_ready
label u2_saturated
fset f0 0
label u2_clip_ready
fstore @B+88 f0
fmax f20 -25
fmin f20 25
fstore @B+80 f20
fmov f21 f20
fmul f21 -1
fexp f21 f21
fadd f21 1
fset f0 1
fdiv f0 f21
fmov f21 f0
fstore @B+72 f21
ret

'''

def backward():return '''label u2_accumulate
fload f22 @B+72
fload f0 @B+96
fsub f22 f0
fload f0 @B+88
fmul f22 f0
fload f0 @GOUTBIAS
fadd f0 f22
fstore @GOUTBIAS f0
fload f0 @B+64
fmul f0 f22
fload f1 @GSKIP
fadd f1 f0
fstore @GSKIP f1
set r2 0
label u2_linear_gradient
mov r0 r2
mul r0 8
add r0 @NORMAL
fload f0 $r0
fmul f0 f22
mov r0 r2
mul r0 8
add r0 @G
fload f1 $r0
fadd f1 f0
fstore $r0 f1
add r2 1
cmp r2 @NF
jlt u2_linear_gradient
load64 r0 @B+32
add r0 1
store64 @B+32 r0
load64 r0 @B+104
add r0 1
store64 @B+104 r0
ret

'''

def source():
    template=(ROOT/'ai/xi/unified/perception-head.xi.in').read_text()
    start=template.index('label u2_project\n');end=template.index('label u2_normalize\n')
    template=template[:start]+decoder()+'\n'+template[end:]
    start=template.index('label u2_forward\n');end=template.index('# Read only the input view')
    template=template[:start]+forward()+template[end:]
    start=template.index('label u2_accumulate\n');end=template.index('label u2_train_cached\n')
    return '# U02 exact Pauli decoder and learned linear readout; generated by decoder_source.py.\n'+template[:start]+backward()+template[end:]

if __name__=='__main__':print(source(),end='')
