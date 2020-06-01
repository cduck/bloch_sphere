#!/usr/bin/env python3

from typing import List

import dataclasses
import argparse
import sys
import numpy as np

import drawSvg as draw  # pip install drawSvg
from hyperbolic import euclid3d  # pip install hyperbolic
from hyperbolic.euclid import shapes, intersection


@dataclasses.dataclass
class AnimState:
    anim: draw.Animation
    fps: float = 20
    speed: float = 1
    inner_proj: euclid3d.Projection = euclid3d.identity(3)
    inner_opacity: float = 1
    extra_opacity: float = 0
    label: str = None
    axis: List[float] = None

    @classmethod
    def _interpolate(cls, x):
        return (np.sin(x * np.pi + -np.pi/2) + 1)/2
    def _smooth(self, duration):
        x = np.linspace(0, 1, int(round(self.fps*duration)))
        y = self._interpolate(x)
        return y
    def _wait(self, duration):
        return range(int(round(self.fps*duration)))

    def sphere_fade_in(self):
        for t in self._smooth(0.4):
            self.anim.draw_frame(self.inner_proj, label=self.label,
                                 inner_opacity=t,
                                 extra_opacity=self.extra_opacity,
                                 axis=self.axis)
        self.inner_opacity = 1

    def sphere_fade_out(self):
        for t in self._smooth(0.4):
            self.anim.draw_frame(self.inner_proj, label=self.label,
                                 inner_opacity=1-t,
                                 extra_opacity=self.extra_opacity,
                                 axis=self.axis)
        self.inner_opacity = 0

    def fade_in(self, label, axis):
        assert self.extra_opacity == 0, 'Unexpected previous state'
        self.label = label
        self.axis = axis
        for t in self._smooth(0.4):
            self.anim.draw_frame(self.inner_proj, label=self.label,
                                 inner_opacity=self.inner_opacity,
                                 extra_opacity=t, axis=self.axis)
        self.extra_opacity = 1

    def fade_out(self):
        assert self.extra_opacity == 1, 'Unexpected previous state'
        for t in self._smooth(0.4):
            self.anim.draw_frame(self.inner_proj, label=self.label,
                                 inner_opacity=self.inner_opacity,
                                 extra_opacity=1-t, axis=self.axis)
        self.extra_opacity = 0

    def rotate(self, rads):
        for t in self._smooth(2):
            rotation = euclid3d.rotation3d(self.axis, rads*t)
            self.anim.draw_frame(rotation@self.inner_proj, label=self.label,
                                 inner_opacity=self.inner_opacity,
                                 extra_opacity=self.extra_opacity,
                                 axis=self.axis)
        self.inner_proj = euclid3d.rotation3d(self.axis, rads) @ self.inner_proj

    def wait(self, duration=1):
        for i in self._wait(duration):
            self.anim.draw_frame(self.inner_proj, label=self.label,
                                 inner_opacity=self.inner_opacity,
                                 extra_opacity=self.extra_opacity,
                                 axis=self.axis)

    def i_gate(self):
        self.wait(2.8)

    def do_gate(self, label, axis, radians):
        self.fade_in(label, axis)
        self.rotate(radians)
        self.fade_out()

    def h_gate(self):
        self.do_gate('H Gate:', (1, 0, 1), np.pi)
    def x_gate(self):
        self.do_gate('X Gate:', (1, 0, 0), np.pi)
    def y_gate(self):
        self.do_gate('Y Gate:', (0, 1, 0), np.pi)
    def z_gate(self):
        self.do_gate('Z Gate:', (0, 0, 1), np.pi)
    def sqrt_x_gate(self):
        self.do_gate('√X Gate:', (1, 0, 0), np.pi/2)
    def sqrt_y_gate(self):
        self.do_gate('√Y Gate:', (0, 1, 0), np.pi/2)
    def s_gate(self):
        self.do_gate('S Gate:', (0, 0, 1), np.pi/2)
    def t_gate(self):
        self.do_gate('T Gate:', (0, 0, 1), np.pi/4)
    def inv_h_gate(self):
        self.do_gate('H⁻¹ Gate:', (1, 0, 1), -np.pi)
    def inv_x_gate(self):
        self.do_gate('X⁻¹ Gate:', (1, 0, 0), -np.pi)
    def inv_y_gate(self):
        self.do_gate('Y⁻¹ Gate:', (0, 1, 0), -np.pi)
    def inv_z_gate(self):
        self.do_gate('Z⁻¹ Gate:', (0, 0, 1), -np.pi)
    def inv_sqrt_x_gate(self):
        self.do_gate('√X⁻¹ Gate:', (1, 0, 0), -np.pi/2)
    def inv_sqrt_y_gate(self):
        self.do_gate('√Y⁻¹ Gate:', (0, 1, 0), -np.pi/2)
    def inv_s_gate(self):
        self.do_gate('S⁻¹ Gate:', (0, 0, 1), -np.pi/2)
    def inv_t_gate(self):
        self.do_gate('T⁻¹ Gate:', (0, 0, 1), -np.pi/4)

    def apply_gate_list(self, gates, final_wait=True):
        non_gates = {'wait', 'no_wait'}
        block_gates = {'do'}
        no_wait = False
        for gate in gates:
            gate = gate.replace('-', '_')
            if gate in block_gates:
                print(f'Error: Invalid gate name "{gate}".')
                sys.exit(1)
                return
            if gate == 'no_wait':
                no_wait = True
            elif gate in non_gates:
                getattr(self, gate)()
            else:
                method = getattr(self, gate+'_gate', None)
                if method is not None:
                    method()
                else:
                    print(f'Error: Unknown gate name "{gate}".')
                    sys.exit(1)
                    return
        if not no_wait and final_wait:
            self.wait()

def do_or_save_animation(name: str, save=False, fps=20, preview=True):
    def wrapper(func):
        if save == 'mp4':
            with draw.animate_video(f'{name}.mp4', draw_frame, fps=fps,
                                    jupyter=preview,
                                   ) as anim:
                state = AnimState(anim, fps=fps)
                func(state)
        elif save == 'gif' or save is True:
            with draw.animate_video(f'{name}.gif', draw_frame, duration=1/fps,
                                    jupyter=preview,
                                   ) as anim:
                state = AnimState(anim, fps=fps)
                func(state)
        else:
            with draw.animate_jupyter(draw_frame, delay=1/fps) as anim:
                state = AnimState(anim, fps=fps)
                func(state)
        return func
    return wrapper

def draw_frame(*args, background='white', **kwargs):
    d = draw.Drawing(5, 3, origin='center')
    d.setRenderSize(624)
    if background:
        d.append(draw.Rectangle(-100, -100, 200, 200, fill=background))

    g = draw.Group()
    draw_bloch_sphere(g, background=None, *args, **kwargs)
    d.append(g)
    return d

def draw_bloch_sphere(d, inner_proj=euclid3d.identity(3), label='', axis=None,
                      rot_proj=None, rot_deg=180, extra_opacity=1,
                      inner_opacity=1, background='white'):
    spin = euclid3d.rotation(3, 0, 2, 2*np.pi/16/2*1.001)
    tilt = euclid3d.rotation(3, 1, 2, np.pi/8)
    trans = tilt @ spin @ euclid3d.axis_swap((1, 2, 0))
    proj = euclid3d.perspective3d(np.pi/8, view_size=4) @ trans
    zx = euclid3d.axis_swap((2, 0, 1))
    xy = euclid3d.identity(3)
    yz = euclid3d.axis_swap((1, 2, 0))
    proj_zx = proj @ zx
    proj_xy = proj @ xy
    proj_yz = proj @ yz

    if background:
        d.append(draw.Rectangle(-100, -100, 200, 200, fill=background))

    def draw_band(proj, trans, r_outer=1, r_inner=0.9, color='black', z_mul=1,
                  opacity=1, divs=4, d=d, **kwargs):
        points = np.array([[-1, -1, 1, 1], [-1, 1, 1, -1]]).T
        sqr12 = 0.5**0.5
        overlap = np.pi/500 * (divs != 4)
        start_end_points = [
            np.array([[np.cos(pr-2*np.pi/divs-overlap),
                       np.sin(pr-2*np.pi/divs-overlap)],
                      [np.cos(pr+overlap),  np.sin(pr+overlap)],
                      [np.cos(pr-np.pi/divs), np.sin(pr-np.pi/divs)]])
            for pr in np.linspace(0, 2*np.pi, num=divs, endpoint=False)
        ]
        for i in range(divs):
            p = draw.Path(fill=color, stroke='none', stroke_width=0.002,
                          **kwargs, opacity=opacity)
            z = trans.project_point(
                (r_inner+r_outer)/2*start_end_points[i][2])[2]
            e = shapes.EllipseArc.fromBoundingQuad(
                *proj.project_list(points*r_outer)[:, :2].flatten(),
                *proj.project_list(start_end_points[i]*r_outer
                                  )[:, :2].flatten(),
            )
            if e: e.drawToPath(p)
            if r_inner > 0:
                e = shapes.EllipseArc.fromBoundingQuad(
                    *proj.project_list(points*r_inner)[:, :2].flatten(),
                    *proj.project_list(start_end_points[i]*r_inner
                                      )[:, :2].flatten(),
                )
                if e:
                    e.reversed().drawToPath(p, includeL=True)
            p.Z()
            d.append(p, z=z*z_mul)
            if False:
                d.draw(shapes.EllipseArc.fromBoundingQuad(
                    *proj.project_list((r_outer+r_inner)/2*points
                                      )[:, :2].flatten(),
                    *proj.project_list((r_outer+r_inner)/2*start_end_points[i]
                                      )[:, :2].flatten(),
                ), fill='none', stroke_width=0.02, stroke=color, **kwargs,
                z=z*z_mul)

    draw_band(proj_xy, trans@xy, 1, 0.925, z_mul=10, color='#45e')
    draw_band(proj_yz, trans@yz, 1, 0.925, z_mul=10, color='#e1e144')
    draw_band(proj_zx, trans@zx, 1, 0.925, z_mul=10, color='#9e2')

    # Inner
    g = draw.Group(opacity=inner_opacity)
    d.append(g, z=proj.project_point((0,0,0))[2])
    inner_xy = proj@inner_proj@xy
    # Darker colors: #34b, #a8a833, #7b2
    draw_band(proj@inner_proj@xy, trans@inner_proj@xy, 0.8, 0.7, color='#45e',
              d=g)
    draw_band(proj@inner_proj@yz, trans@inner_proj@yz, 0.8, 0.7,
              color='#e1e144', divs=4, d=g)
    draw_band(proj@inner_proj@zx, trans@inner_proj@zx, 0.8, 0.7, color='#9e2',
              divs=8//2, d=g)
    elevation_lines = False
    if elevation_lines:
        for elevation in (*np.linspace(0, np.pi/2, 4, True)[1:-1],
                          *np.linspace(-np.pi/2, 0, 3, False)[1:]):
            y = 0.75 * np.sin(elevation)
            r = 0.75 * np.cos(elevation)
            draw_band(proj@inner_proj@xy @ euclid3d.translation((0, 0, y)),
                      trans@inner_proj@xy @ euclid3d.translation((0, 0, y)),
                      r_outer=r-0.01, r_inner=r+0.01, color='#bbb', opacity=1,
                      d=g)
    arrow = draw.Marker(-0.1, -0.5, 0.9, 0.5, scale=4, orient='auto')
    arrow.append(draw.Lines(-0.1, -0.5, -0.1, 0.5, 0.9, 0, fill='black',
                            close=True))
    g.append(draw.Line(*inner_xy.p2(-0.65, 0, 0), *inner_xy.p2(0.6, 0, 0),
                       stroke='black', stroke_width=0.015, marker_end=arrow))
    g.append(draw.Line(*inner_xy.p2(0, -0.65, 0), *inner_xy.p2(0, 0.6, 0),
                       stroke='black', stroke_width=0.015, marker_end=arrow))
    g.append(draw.Line(*inner_xy.p2(0, 0, -0.65), *inner_xy.p2(0, 0, 0.6),
                       stroke='black', stroke_width=0.015, marker_end=arrow))

    # Outer arrows and text
    arrow = draw.Marker(-0.1, -0.5, 0.9, 0.5, scale=4, orient='auto')
    arrow.append(draw.Lines(-0.1, -0.5, -0.1, 0.5, 0.9, 0, fill='black',
                            close=True))
    d.append(draw.Line(*proj_xy.p2(1, 0, 0), *proj_xy.p2(1.2, 0, 0),
                       stroke='black', stroke_width=0.02, marker_end=arrow),
                       z=100)
    d.append(draw.Line(*proj_xy.p2(0, 1, 0), *proj_xy.p2(0, 1.2, 0),
                       stroke='black', stroke_width=0.02, marker_end=arrow),
                       z=100)
    d.append(draw.Line(*proj_xy.p2(0, 0, 1), *proj_xy.p2(0, 0, 1.2),
                       stroke='black', stroke_width=0.02, marker_end=arrow),
                       z=100)
    d.append(draw.Line(*proj_xy.p2(-1, 0, 0), *proj_xy.p2(-1.2, 0, 0),
                       stroke='black', stroke_width=0.02))
    d.append(draw.Line(*proj_xy.p2(0, -1, 0), *proj_xy.p2(0, -1.2, 0),
                       stroke='black', stroke_width=0.02))
    d.append(draw.Line(*proj_xy.p2(0, 0, -1), *proj_xy.p2(0, 0, -1.2),
                       stroke='black', stroke_width=0.02))
    d.append(draw.Text(['X'], 0.2, *proj_xy.p2(1.7, 0, 0), center=True,
                       fill='black'), z=100)
    d.append(draw.Text(['Y'], 0.2, *proj_xy.p2(0, 1.35, 0), center=True,
                       fill='black'), z=100)
    d.append(draw.Text(['Z'], 0.2, *proj_xy.p2(0, 0, 1.4), center=True,
                       fill='black'), z=100)

    # Extra annotations
    #label='', axis=None, rot_proj=None
    if label:
        d.append(draw.Text([label], 0.4, -0.6, 1.2, center=True, fill='#c00',
                           text_anchor='end',
                           opacity=extra_opacity))
    if axis:
        g = draw.Group(opacity=extra_opacity)
        axis = np.array(axis, dtype=float)
        axis_len = 1.18
        axis /= np.linalg.norm(axis)
        arrow = draw.Marker(-0.1, -0.5, 0.9, 0.5, scale=3, orient='auto')
        arrow.append(draw.Lines(-0.1, -0.5, -0.1, 0.5, 0.9, 0, fill='#e00',
                                close=True))
        z = 100#10 * proj_xy.project_point(axis*1)[2]
        g.append(draw.Line(*proj_xy.p2(0, 0, 0), *proj_xy.p2(*axis*axis_len),
                           stroke='#e00', stroke_width=0.04, marker_end=arrow))
        d.append(g, z=z)

    if rot_proj is not None:
        rot_proj =  inner_proj @ rot_proj
        r_inner, r_outer = 0.1, 0.16
        points = np.array([[-1, -1, 1, 1], [-1, 1, 1, -1]]).T
        start_end_points = np.array([[1, 0], [-1, 0], [0, 1]])
        p = draw.Path(fill='orange', fill_rule='nonzero', opacity=extra_opacity)
        z = 9 * (trans@rot_proj).project_point(start_end_points[2])[2]
        e = shapes.EllipseArc.fromBoundingQuad(
            *(proj@rot_proj).project_list(points*r_outer)[:, :2].flatten(),
            *(proj@rot_proj).project_list(start_end_points*r_outer
                                         )[:, :2].flatten(),
        )
        if e: e.reversed().drawToPath(p)
        e = shapes.EllipseArc.fromBoundingQuad(
            *(proj@rot_proj).project_list(points*r_inner)[:, :2].flatten(),
            *(proj@rot_proj).project_list(start_end_points*r_inner
                                         )[:, :2].flatten(),
        )
        if e:
            e.drawToPath(p, includeL=True)
        sa = 2.5 * (r_outer-r_inner)
        xa = -(r_inner+r_outer)/2
        p.L(*(proj@rot_proj).p2(xa, 0.3*sa))
        p.L(*(proj@rot_proj).p2(xa+0.5*sa, 0.3*sa))
        p.L(*(proj@rot_proj).p2(xa, -0.7*sa))
        p.L(*(proj@rot_proj).p2(xa-0.5*sa, 0.3*sa))
        p.L(*(proj@rot_proj).p2(xa, 0.3*sa))
        p.Z()
        d.append(p, z=z)

    return d


def main(name, gates, mp4=False, fps=20, preview=False):
    save = 'mp4' if mp4 else 'gif'
    @do_or_save_animation(name, save=save, fps=fps, preview=preview)
    def animate(state):
        state.apply_gate_list(gates)
    print(f'Saved "{name}.{save}" with gate sequence "{"".join(gates)}"')

def run_from_command_line():
    parser = argparse.ArgumentParser(
        description='Renders animations of the Bloch sphere for a sequence of '
                    'single-qubit gates.')
    parser.add_argument('name', type=str, help=
        'The file name to save (excluding file extension)')
    parser.add_argument('gate', type=str, nargs='+', help=
        'List of gates to apply (e.g. h x wait inv_sqrt_y ...)')
    parser.add_argument('--mp4', action='store_true', help=
        'Save an mp4 video instead of a GIF')
    parser.add_argument('--fps', type=float, default=20, help=
        'Sets the animation frame rate')
    args = parser.parse_args()
    main(name=args.name, gates=args.gate, mp4=args.mp4, fps=args.fps)

if __name__ == '__main__':
    run_from_command_line()
