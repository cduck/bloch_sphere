
import argparse

import drawSvg as draw
import latextools

from bloch_sphere import animate_bloch


def render_animation(name, func1, func2, circuit_qcircuit='', equation_latex='',
                     save=False, fps=20, preview=True):
    with draw.animation.AnimationContext(animate_bloch.draw_frame,
                                         jupyter=preview, delay=0
                                        ) as anim:
        state = animate_bloch.AnimState(anim)
        func1(state)
    frames1 = anim.frames

    with draw.animation.AnimationContext(animate_bloch.draw_frame,
                                         jupyter=preview, delay=0
                                        ) as anim:
        state = animate_bloch.AnimState(anim)
        func2(state)
    frames2 = anim.frames

    g = draw.Group()
    # Equals sign
    g.append(draw.Rectangle(-0.4, 0.075, 0.8, 0.075, fill='#000'))
    g.append(draw.Rectangle(-0.4, -0.15, 0.8, 0.075, fill='#000'))
    if circuit_qcircuit:
        circuit_elem = latextools.render_qcircuit(circuit_qcircuit).as_svg()
        g.draw(circuit_elem, x=0, y=2, center=True, scale=0.04)
    if equation_latex:
        equation_elem = latextools.render_snippet(
            equation_latex, latextools.pkg.qcircuit).as_svg()
        g.draw(equation_elem, x=0, y=-0.8, center=True, scale=0.03)
    extra_elements = (g,)

    save_side_by_side(name, frames1, frames2, extra_elements, save=save,
                      fps=fps, preview=preview)

def zip_pad(*iterables):
    '''Same as the builtin zip but pads shorter iterables with their last
    value.'''
    iters = tuple(iter(iterable) for iterable in iterables)
    last_values = [None] * len(iters)
    def try_next(i, it):
        nonlocal end_counter
        try:
            val = next(it)
        except StopIteration:
            end_counter += 1
            return last_values[i]
        last_values[i] = val
        return val
    while True:
        end_counter = 0
        values = tuple(try_next(i, it) for i, it in enumerate(iters))
        if end_counter >= len(iters):
            return
        yield values

def save_side_by_side(name: str, frames1, frames2, extra_elements=(),
                      save=False, fps=20, preview=True):
    with draw.animation.AnimationContext(draw_whole_frame,
                                         jupyter=not save or preview,
                                         delay=0 if save else 1/fps
                                        ) as anim:
        for f1, f2 in zip_pad(frames1, frames2):
            anim.draw_frame(f1, f2, background='white',
                            extra_elements=extra_elements)
    if save == 'mp4':
        anim.save_video(f'{name}.mp4', fps=fps)
    elif save == 'gif' or save is True:
        anim.save_video(f'{name}.gif', duration=1/fps)

def draw_whole_frame(f1, f2, background='white', extra_elements=()):
    d = draw.Drawing(10, 4, origin=(-5, -1.5))
    d.setRenderSize(624*2)
    if background:
        d.append(draw.Rectangle(-100, -100, 200, 200, fill=background))

    d.append(draw.Group([f1.elements[-1]], transform='translate(-2.5)'))
    d.append(draw.Group([f2.elements[-1]], transform='translate(2.5)'))

    d.extend(extra_elements)
    return d

def main(name, gates1, gates2, circuit_qcircuit='', equation_latex='',
         mp4=False, fps=20, preview=False):
    save = 'mp4' if mp4 else 'gif'
    def func1(state):
        state.sphere_fade_in()
        state.apply_gate_list(gates1, final_wait=False)
        state.wait()
        for _ in gates2:
            state.i_gate()
        state.wait()
        state.wait()
        state.sphere_fade_out()
        state.wait()
    def func2(state):
        state.sphere_fade_in()
        for _ in gates1:
            state.i_gate()
        state.wait()
        state.apply_gate_list(gates2, final_wait=False)
        state.wait()
        state.wait()
        state.sphere_fade_out()
        state.wait()
    render_animation(name, func1, func2, circuit_qcircuit, equation_latex,
                     save=save, fps=fps, preview=preview)
    print(f'Saved "{name}.{save}"')

def run_from_command_line():
    parser = argparse.ArgumentParser(
        description='Renders animations of the Bloch sphere for a sequence of '
                    'single-qubit gates.')
    parser.add_argument('name', type=str, help=
        'The file name to save (excluding file extension)')
    parser.add_argument('gates1', type=str, help=
        'List of gates to apply on the left (e.g. h,x,wait,inv_sqrt_y,...)')
    parser.add_argument('gates2', type=str, help=
        'List of gates to apply on the right (e.g. h,x,wait,inv_sqrt_y,...)')
    parser.add_argument('--circuit', type=str, help=
        r'Latex code for a qcircuit digram (e.g. \'& \gate{Y} & \gate{Z} & \qw & \push{=} & & \gate{X} & \qw\'')
    parser.add_argument('--equation', type=str, help=
        r'Latex code for an equation (e.g. \'$ZY\ket{\psi}=X\ket{\psi}$\'')
    parser.add_argument('--mp4', action='store_true', help=
        'Save an mp4 video instead of a GIF')
    parser.add_argument('--fps', type=float, default=20, help=
        'Sets the animation frame rate')
    args = parser.parse_args()
    main(name=args.name, gates1=args.gates1.split(','),
         gates2=args.gates2.split(','),
         circuit_qcircuit=args.circuit, equation_latex=args.equation,
         mp4=args.mp4, fps=args.fps)

if __name__ == '__main__':
    run_from_command_line()
