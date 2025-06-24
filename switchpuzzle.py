"""
Transformaciones de Símbolos
----------------------------
Aplicación Tkinter que permite:

1. Elegir una secuencia inicial y final de cuatro símbolos.
2. Definir varios caminos, cada uno con N combinaciones (permutaciones).
3. Calcular todas las rutas (producto cartesiano) de combinaciones y
   verificar cuáles transforman la secuencia inicial en la final.

Los botones “Simular” y “Resetear” tienen color verde y rojo, respectivamente.
Cada ruta en la salida muestra el índice de la combinación dentro de su camino,
por ejemplo: `3412 (1) -> 2314 (3) -> 2134 (1)`.
"""

import itertools
import tkinter as tk
from tkinter import scrolledtext

# Símbolos para botones (unicode y color)
DEFAULT_SHAPES = [
    ('▲', 'yellow'),  # Triángulo
    ('✚', 'blue'),    # Rombo
    ('●', 'green'),   # Círculo
    ('■', 'red')      # Cuadrado
]


class SymbolTransformerApp:
    """App para transformar secuencias de símbolos mediante permutaciones."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title('Transformaciones de Símbolos')
        root.geometry('800x600')
        root.columnconfigure((0, 1, 2, 3), weight=1)

        self.initial_sequence: list[int] = []
        self.final_sequence: list[int] = []
        self.path_frames: list[dict] = []  # cada dict guarda datos del camino

        self._build_top_frame()
        self._build_middle_frame()
        self._build_bottom_frame()

    # ---------- construcción de interfaz ----------
    def _build_top_frame(self) -> None:
        top = tk.Frame(self.root)
        top.pack(fill='x', padx=10, pady=10)
        top.columnconfigure((1, 2), weight=1)

        # Secuencia inicial
        tk.Label(top, text='Secuencia Inicial:').grid(row=0,
                                                      column=0,
                                                      sticky='e')
        self.initial_display = tk.Label(top,
                                        font=('Arial', 16),
                                        borderwidth=2,
                                        relief='sunken',
                                        width=12)
        self.initial_display.grid(row=0, column=1, sticky='ew')
        self._add_symbol_buttons(top, row=0, col=2,
                                 add_cb=self._add_initial,
                                 clr_cb=self._clear_initial)

        # Secuencia final
        tk.Label(top, text='Secuencia Final:').grid(row=1,
                                                    column=0,
                                                    sticky='e')
        self.final_display = tk.Label(top,
                                      font=('Arial', 16),
                                      borderwidth=2,
                                      relief='sunken',
                                      width=12)
        self.final_display.grid(row=1, column=1, sticky='ew')
        self._add_symbol_buttons(top, row=1, col=2,
                                 add_cb=self._add_final,
                                 clr_cb=self._clear_final)

        # Cantidad de caminos
        tk.Label(top, text='Cantidad de Caminos:').grid(row=2,
                                                        column=0,
                                                        sticky='e')
        self.path_count_entry = tk.Entry(top)
        self.path_count_entry.grid(row=2, column=1, sticky='ew')
        tk.Button(top,
                  text='Generar',
                  command=self._generate_paths).grid(row=2, column=2)

        # Acciones principales
        tk.Button(top,
                  text='Simular',
                  command=self._simulate,
                  bg='seagreen',
                  fg='white',
                  activebackground='darkgreen').grid(row=0,
                                                     column=3,
                                                     rowspan=2,
                                                     padx=10,
                                                     pady=2)
        tk.Button(top,
                  text='Resetear',
                  command=self._reset_all,
                  bg='firebrick',
                  fg='white',
                  activebackground='darkred').grid(row=2,
                                                   column=3,
                                                   padx=10,
                                                   pady=2)

    def _add_symbol_buttons(self,
                            parent: tk.Frame,
                            *,
                            row: int,
                            col: int,
                            add_cb,
                            clr_cb) -> None:
        """Agrega los cuatro botones de símbolos y un botón Borrar."""
        frame = tk.Frame(parent)
        frame.grid(row=row, column=col, sticky='w', padx=5)

        for idx, (sym, colr) in enumerate(DEFAULT_SHAPES, start=1):
            tk.Button(frame,
                      text=sym,
                      fg=colr,
                      font=('Arial', 14),
                      width=3,
                      command=lambda i=idx-1: add_cb(i)).pack(side='left',
                                                              padx=2)
        tk.Button(frame,
                  text='Borrar',
                  command=clr_cb).pack(side='left', padx=2)

    # ---------- secciones inferiores ----------
    def _build_middle_frame(self) -> None:
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def _build_bottom_frame(self) -> None:
        bottom = tk.Frame(self.root)
        bottom.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.output_text = scrolledtext.ScrolledText(bottom)
        self.output_text.pack(fill='both', expand=True)

    # ---------- manejo de secuencias ----------
    def _add_initial(self, idx: int) -> None:
        if len(self.initial_sequence) < 4:
            self.initial_sequence.append(idx)
            self._update_display(self.initial_display,
                                 self.initial_sequence)

    def _clear_initial(self) -> None:
        self.initial_sequence.clear()
        self._update_display(self.initial_display, [])

    def _add_final(self, idx: int) -> None:
        if len(self.final_sequence) < 4:
            self.final_sequence.append(idx)
            self._update_display(self.final_display,
                                 self.final_sequence)

    def _clear_final(self) -> None:
        self.final_sequence.clear()
        self._update_display(self.final_display, [])

    def _update_display(self,
                        label: tk.Label,
                        seq: list[int]) -> None:
        label.config(text=' '.join(DEFAULT_SHAPES[i][0] for i in seq))

    # ---------- caminos ----------
    def _generate_paths(self) -> None:
        """Crea paneles de caminos con cajas dinámicas."""
        for widget in self.middle_frame.winfo_children():
            widget.destroy()
        self.path_frames.clear()

        try:
            count = max(1, int(self.path_count_entry.get()))
        except ValueError:
            count = 1

        for idx in range(count):
            frm = tk.LabelFrame(self.middle_frame, text=f'Camino {idx + 1}')
            frm.pack(fill='x', pady=5)

            # campo cantidad
            tk.Label(frm, text='Combinaciones:').pack(side='left')
            cnt_var = tk.StringVar()
            cnt_entry = tk.Entry(frm, textvariable=cnt_var, width=4)
            cnt_entry.pack(side='left', padx=5)

            # contenedor secuencia
            tk.Label(frm, text='Secuencia:').pack(side='left', padx=(10, 2))
            seq_frame = tk.Frame(frm)
            seq_frame.pack(side='left', padx=2)

            rec = {'cnt_var': cnt_var, 'seq_entries': []}
            self.path_frames.append(rec)

            def refresh(*_, rec=rec, sf=seq_frame):
                for w in sf.winfo_children():
                    w.destroy()
                rec['seq_entries'].clear()
                try:
                    n = int(rec['cnt_var'].get())
                except ValueError:
                    return
                for _ in range(n):
                    ent = tk.Entry(sf, width=6)
                    ent.pack(side='left', padx=1)
                    rec['seq_entries'].append(ent)

            cnt_var.trace_add('write', refresh)

    # ---------- simulación ----------
    def _simulate(self) -> None:
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)

        if not self._validate_sequences():
            return

        dyn_map = {str(i + 1): DEFAULT_SHAPES[idx]
                   for i, idx in enumerate(self.initial_sequence)}
        init_num = ''.join(str(i + 1) for i in self.initial_sequence)
        fin_num = ''.join(str(i + 1) for i in self.final_sequence)

        self._print_initial_final(init_num, fin_num, dyn_map)

        # Leer combos de cada camino
        all_lists: list[list[str]] = []
        for rec in self.path_frames:
            try:
                n = int(rec['cnt_var'].get())
            except ValueError:
                self.output_text.insert(tk.END,
                                        'Error: cantidad inválida.\n')
                self.output_text.config(state='disabled')
                return
            combos = [e.get().strip()
                      for e in rec['seq_entries']
                      if e.get().strip()]
            if len(combos) != n:
                self.output_text.insert(tk.END,
                                        'Error: nº de combos no coincide.\n')
                self.output_text.config(state='disabled')
                return
            all_lists.append(combos)

        # Producto cartesiano de los combos
        for combo_tuple in itertools.product(*all_lists):
            resultado = self._apply_combo_tuple(init_num, combo_tuple)
            self._report_combo_tuple(combo_tuple,
                                     resultado,
                                     fin_num,
                                     dyn_map,
                                     all_lists)

        self.output_text.config(state='disabled')

    def _validate_sequences(self) -> bool:
        if len(self.initial_sequence) != 4 \
                or sorted(self.initial_sequence) != [0, 1, 2, 3]:
            self.output_text.insert(tk.END, 'Error: inicial inválida.\n')
            return False
        if len(self.final_sequence) != 4 \
                or sorted(self.final_sequence) != [0, 1, 2, 3]:
            self.output_text.insert(tk.END, 'Error: final inválida.\n')
            return False
        return True

    # ---------- helpers de simulación ----------
    def _print_initial_final(self,
                             init_num: str,
                             fin_num: str,
                             dyn_map: dict[str, tuple[str, str]]) -> None:
        init_sym = ' '.join(dyn_map[c][0] for c in init_num)
        fin_sym = ' '.join(dyn_map[c][0] for c in fin_num)
        self.output_text.insert(
            tk.END,
            f'Inicial: {init_num} ({init_sym})   '
            f'Final: {fin_num} ({fin_sym})\n\n'
        )

    def _apply_combo_tuple(self,
                           init_num: str,
                           combo_tuple: tuple[str, ...]) -> str:
        current = list(init_num)
        for combo in combo_tuple:
            current = [current[int(c) - 1] for c in combo]
        return ''.join(current)

    def _report_combo_tuple(self,
                            combo_tuple: tuple[str, ...],
                            resultado: str,
                            fin_num: str,
                            dyn_map: dict[str, tuple[str, str]],
                            path_lists: list[list[str]]) -> None:
        """Muestra ruta con índice (n) de la combinación en su camino."""
        # Añadir índice 1-based
        parts = []
        for path_idx, combo in enumerate(combo_tuple):
            pos = path_lists[path_idx].index(combo) + 1
            parts.append(f'{combo} ({pos})')
        combos_str = ' -> '.join(parts)

        # Camino con iconos
        sym_path = ' -> '.join(
            ' '.join(dyn_map[c][0] for c in combo)
            for combo in combo_tuple
        )

        self.output_text.insert(tk.END,
                                f'Ruta: {combos_str}\n  {sym_path}\n')
        if resultado == fin_num:
            self.output_text.insert(tk.END,
                                    '  ✅ ¡Se alcanzó la salida!\n\n')
        else:
            self.output_text.insert(tk.END,
                                    '  ❌ No coincide.\n\n')

    # ---------- reset ----------
    def _reset_all(self) -> None:
        self._clear_initial()
        self._clear_final()
        self.path_count_entry.delete(0, tk.END)

        for rec in self.path_frames:
            rec['cnt_var'].set('')
            for ent in rec['seq_entries']:
                ent.destroy()
            rec['seq_entries'].clear()

        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.config(state='disabled')


if __name__ == '__main__':
    root_app = tk.Tk()
    SymbolTransformerApp(root_app)
    root_app.mainloop()
