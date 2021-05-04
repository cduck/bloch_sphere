#!/usr/bin/env python3

import drawSvg as draw
import latextools
from bloch_sphere.animate_bloch import do_or_save_animation, AnimState
from bloch_sphere.animate_bloch_compare import render_animation


# Add some extra labels
zero_ket = draw.Group()
zero_ket.draw(latextools.render_snippet('$\ket{0}$', latextools.pkg.qcircuit),
              x=0, y=0, center=True, scale=0.015)
one_ket = draw.Group()
one_ket.draw(latextools.render_snippet('$\ket{1}$', latextools.pkg.qcircuit),
             x=0, y=0, center=True, scale=0.015)
zero_ket_inner = draw.Use(zero_ket, 0, 0, transform='scale(0.75)')
one_ket_inner = draw.Use(one_ket, 0, 0, transform='scale(0.75)')

w = 624*2  # Output width
fps = 20
draw_args = dict(
    w = w/2,
    outer_labels=[
        [(0, 0, 1), (-0.15, 0.13), zero_ket],
        [(0, 0, -1), (0.15, -0.13), one_ket],
    ],
    inner_labels=[
        [(0, 0, 0.8), (0, 0), zero_ket_inner],
        [(0, 0, -0.8), (0, 0), one_ket_inner],
    ],
)

def gate_sequence(gates, compared_to_gates=None, first_sequence=True,
                  show_inner_labels=True):
    if isinstance(gates, str):
        gates = gates.split(',')
    gates = tuple(gates)
    if compared_to_gates is not None:
        if isinstance(compared_to_gates, str):
            compared_to_gates = compared_to_gates.split(',')
        compared_to_gates = tuple(compared_to_gates)

    def regular_func(state):
        state.draw_args = dict(draw_args, **state.draw_args)
        if not show_inner_labels:
            state.draw_args['inner_labels'] = []
        state.apply_gate_list(gates)

    def comparison_func(state):
        state.draw_args = dict(draw_args, **state.draw_args)
        if not show_inner_labels:
            state.draw_args['inner_labels'] = []
        state.sphere_fade_in()
        if first_sequence:
            state.apply_gate_list(gates, final_wait=False)
            state.wait()
        for _ in compared_to_gates:
            state.i_gate()
        state.wait()
        if not first_sequence:
            state.apply_gate_list(gates, final_wait=False)
            state.wait()
        state.wait()
        state.sphere_fade_out()
        state.wait()

    if compared_to_gates is not None:
        return comparison_func
    return regular_func


print('Rendering hzh_x_compare')
#$ animate_bloch2 hzh_x_compare h,z,h x --circuit '& \gate{H} & \gate{Z} & \gate{H} & \qw & \push{=} & & \gate{X} & \qw' --equation '$HZH\ket{\psi}=X\ket{\psi}$'
render_animation('hzh_x_compare',
                 gate_sequence('h,z,h', 'x', True, False),
                 gate_sequence('x', 'h,z,h', False, False),
                 r'& \gate{H} & \gate{Z} & \gate{H} & \qw & \push{=} & & \gate{X} & \qw',
                 r'$HZH\ket{\psi}=X\ket{\psi}$',
                 save='gif',  # False, 'gif', or 'mp4'
                 preview=False,
                 fps=fps,
                 w=w)

print('Rendering ry_gate_arrows')
#$ animate_bloch ~/Downloads/rx_gate_arrows --style arrows ry,0.666667 ry,0.666667 ry,0.666667
do_or_save_animation('ry_gate_arrows_again', save='gif', fps=fps, preview=False,
                     style='arrows'
        )(gate_sequence('ry;0.666667,ry;0.666667,ry;0.666667'))

print('Rendering xyss_gate')
#$ animate_bloch xyss_gate x y s s
do_or_save_animation('xyss_gate', save='gif', fps=fps, preview=False
        )(gate_sequence('x,y,s,s'))

print('Rendering xx_gate')
#$ #animate_bloch xx_gate x x
do_or_save_animation('xx_gate', save='gif', fps=fps, preview=False
        )(gate_sequence('x,x'))

print('Rendering yy_gate')
#$ #animate_bloch yy_gate y y
do_or_save_animation('yy_gate', save='gif', fps=fps, preview=False
        )(gate_sequence('y,y'))

print('Rendering zz_gate')
#$ animate_bloch zz_gate z z
do_or_save_animation('zz_gate', save='gif', fps=fps, preview=False
        )(gate_sequence('z,z'))

print('Rendering hh_gate')
#$ animate_bloch hh_gate h h
do_or_save_animation('hh_gate', save='gif', fps=fps, preview=False
        )(gate_sequence('h,h'))

print('Rendering sqrt_xxxx_gate')
#$ animate_bloch sqrt_xxxx_gate sqrt_x sqrt_x sqrt_x sqrt_x
do_or_save_animation('sqrt_xxxx_gate', save='gif', fps=fps, preview=False
        )(gate_sequence('sqrt_x,sqrt_x,sqrt_x,sqrt_x'))

print('Rendering ststs_gate')
#$ animate_bloch ststs_gate s t s t s
do_or_save_animation('ststs_gate', save='gif', fps=fps, preview=False
        )(gate_sequence('s,t,s,t,s'))

print('Rendering xz_y_compare')
#$ animate_bloch2 xz_y_compare x,z y --circuit '& \gate{X} & \gate{Z} & \qw & \push{=} & & \gate{Y} & \qw' --equation '$ZX\ket{\psi}=Y\ket{\psi}$'
render_animation('xz_y_compare',
                 gate_sequence('x,z', 'y', True, False),
                 gate_sequence('y', 'x,z', False, False),
                 r'& \gate{X} & \gate{Z} & \qw & \push{=} & & \gate{Y} & \qw',
                 r'$ZX\ket{\psi}=Y\ket{\psi}$',
                 save='gif',  # False, 'gif', or 'mp4'
                 preview=False,
                 fps=fps,
                 w=w)

print()
print('Please compress the rendered GIFs with https://gifcompressor.com/')
